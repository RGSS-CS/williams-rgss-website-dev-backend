from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import update_last_login
from rest_framework.validators import UniqueValidator

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    code = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "password2", "first_name", "last_name", "code"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords don't match."})
        if attrs["code"] not in []: # TODO: implement qr storing and checks
            raise serializers.ValidationError({"code": "Not implemented. Speak to a developer."})
            raise serializers.ValidationError({"code": "Invalid QR code. If you believe this is a mistake, contact a teacher/admin."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = User.objects.filter(email__iexact=attrs['email']).first()
        authed_user = authenticate(username=user.username, password=attrs['password'])
        if not authed_user:
            raise serializers.ValidationError("Invalid email or password.")
        
        refresh = self.get_token(authed_user)
        if user:
            update_last_login(None, user)

        return {'refresh': str(refresh), 'access': str(refresh.access_token)}
