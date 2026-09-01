from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import UserJoinCode
from .serializers import RegisterSerializer


User = get_user_model()


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
