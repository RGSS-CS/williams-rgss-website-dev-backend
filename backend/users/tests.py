from django.test import TestCase

from .models import UserJoinCode
from .serializers import RegisterSerializer


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
                "code": "disabled-code",
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
                "code": "valid-code",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.username, "newuser")
        join_code.refresh_from_db()
        self.assertEqual(join_code.uses, 1)
