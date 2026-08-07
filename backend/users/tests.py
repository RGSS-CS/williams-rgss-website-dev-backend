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
