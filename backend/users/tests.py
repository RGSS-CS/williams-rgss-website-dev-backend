from django.contrib.auth import get_user_model
import base64
from urllib.parse import parse_qs, urlsplit
from datetime import timedelta
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from rest_framework import status
from rest_framework.test import APITestCase

from .models import UserJoinCode
from .qr_codes import build_registration_url
from .serializers import RegisterSerializer


User = get_user_model()


class RegistrationQRCodeTests(TestCase):
    def test_registration_url_contains_an_aes_gcm_encrypted_join_code(self):
        join_code = "registration-code"
        url = build_registration_url("https://frontend.example/", join_code)

        parsed = urlsplit(url)
        encrypted_code = parse_qs(parsed.query)["rel"][0]
        payload = base64.urlsafe_b64decode(encrypted_code.encode("ascii"))
        plaintext = AESGCM(base64.urlsafe_b64decode(settings.AES_KEY)).decrypt(
            payload[:12], payload[12:], None
        )

        self.assertEqual(parsed.path, "/private/authentication/register")
        self.assertEqual(plaintext.decode("utf-8"), join_code)


class CustomUserModelTests(TestCase):
    def test_user_is_active_by_default_and_uses_username_as_string(self):
        user = User.objects.create_user(
            username="council-user",
            email="council@example.com",
            password="StrongPass123!",
        )

        self.assertTrue(user.is_active)
        self.assertEqual(str(user), "council-user")


class RegisterSerializerTests(TestCase):
    def test_disabled_join_code_is_rejected(self):
        UserJoinCode.objects.create(code="disabled-code", enabled=False)

        serializer = RegisterSerializer(
            data={
                "username": "testuser",
                "email": "test@example.com",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
                "first_name": "Test",
                "last_name": "User",
                "code": "disabled-code"
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)

    def test_valid_join_code_allows_registration_and_increments_uses(self):
        join_code = UserJoinCode.objects.create(code="valid-code", enabled=True)

        serializer = RegisterSerializer(
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
                "first_name": "New",
                "last_name": "User",
                "code": "valid-code"
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.username, "newuser")
        join_code.refresh_from_db()
        self.assertEqual(join_code.uses, 1)


class RegistrationAPITests(APITestCase):
    def setUp(self):
        self.join_code = UserJoinCode.objects.create(
            code="api-registration-code", label="Cafeteria", enabled=True
        )

    def test_register_endpoint_creates_user_and_increments_code_usage(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "apiuser",
                "email": "apiuser@example.com",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
                "first_name": "API",
                "last_name": "User",
                "code": self.join_code.code,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        user = User.objects.get(username="apiuser")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertTrue(user.groups.filter(name="Public Verified").exists())
        self.join_code.refresh_from_db()
        self.assertEqual(self.join_code.uses, 1)

    def test_register_endpoint_rejects_disabled_code(self):
        self.join_code.enabled = False
        self.join_code.save()

        response = self.client.post(
            reverse("register"),
            {
                "username": "apiuser",
                "email": "apiuser@example.com",
                "password": "StrongPass123!",
                "password2": "StrongPass123!",
                "first_name": "API",
                "last_name": "User",
                "code": self.join_code.code,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)


class JoinCodeVerificationAPITests(APITestCase):
    def test_verify_endpoint_returns_valid_code_label(self):
        join_code = UserJoinCode.objects.create(
            code="api-verify-code", label="Student Council", enabled=True
        )

        response = self.client.post(
            reverse("verify-register-code"),
            {"code": join_code.code},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertEqual(response.data, {"valid": True, "label": "Student Council"})


class TokenAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tokenuser",
            email="tokenuser@example.com",
            password="StrongPass123!",
        )

    def test_token_endpoint_authenticates_active_user_by_email(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.user.email, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_endpoint_rejects_inactive_user(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])

        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.user.email, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JoinCodeBoundaryTests(APITestCase):
    def test_verification_rejects_unusable_codes_without_consuming_uses(self):
        for options in (
            {'enabled': False},
            {'expiry': timezone.now() - timedelta(seconds=1)},
            {'max_uses': 2, 'uses': 2},
            {'max_uses': 0},
        ):
            with self.subTest(options=options):
                code = UserJoinCode.objects.create(**options)
                uses = code.uses
                response = self.client.post(
                    reverse('verify-register-code'), {'code': code.code}, format='json'
                )
                self.assertEqual(response.status_code, 400)
                self.assertIn('code', response.data)
                code.refresh_from_db()
                self.assertEqual(code.uses, uses)

    def test_verification_does_not_consume_last_available_use(self):
        code = UserJoinCode.objects.create(max_uses=3, uses=2, label='Library')
        response = self.client.post(
            reverse('verify-register-code'), {'code': code.code}, format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {'valid': True, 'label': 'Library'})
        code.refresh_from_db()
        self.assertEqual(code.uses, 2)

    def test_unknown_and_missing_codes_are_rejected(self):
        for data in ({'code': 'unknown'}, {}):
            with self.subTest(data=data):
                response = self.client.post(reverse('verify-register-code'), data, format='json')
                self.assertEqual(response.status_code, 400)
                self.assertIn('code', response.data)


class EmailLoginTests(APITestCase):
    def setUp(self):
        revalidation = patch('requests.post')
        revalidation.start()
        self.addCleanup(revalidation.stop)
        self.user = User.objects.create_user(
            username='student', email='student@example.com', password='StrongPass123!'
        )

    def test_login_is_case_insensitive_and_tokens_include_groups(self):
        from django.contrib.auth.models import Group
        from rest_framework_simplejwt.tokens import AccessToken

        group, _ = Group.objects.get_or_create(name='Public Verified')
        self.user.groups.add(group)
        response = self.client.post(reverse('token_obtain_pair'), {
            'email': 'STUDENT@EXAMPLE.COM', 'password': 'StrongPass123!'
        }, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data['groups'], ['Public Verified'])
        token = AccessToken(response.data['access'])
        self.assertEqual(token['groups'], ['Public Verified'])
        self.assertEqual(str(token['user_id']), str(self.user.pk))
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    def test_wrong_password_and_unknown_email_return_same_error(self):
        errors = []
        for email in (self.user.email, 'unknown@example.com'):
            response = self.client.post(reverse('token_obtain_pair'), {
                'email': email, 'password': 'WrongPassword123!'
            }, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertNotIn('access', response.data)
            errors.append(response.data)
        self.assertEqual(errors[0], errors[1])
        self.user.refresh_from_db()
        self.assertIsNone(self.user.last_login)
