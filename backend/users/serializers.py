from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import update_last_login
from rest_framework.validators import UniqueValidator
from .models import UserJoinCode

User = get_user_model()


def validate_join_code(code):
    join_code = UserJoinCode.objects.filter(code=code).first()
    if not join_code:
        raise serializers.ValidationError({"code": "Invalid QR code. If you believe this is a mistake, contact a teacher/admin."})

    if not join_code.enabled:
        raise serializers.ValidationError({"code": "Invalid QR code. If you believe this is a mistake, contact a teacher/admin."})
    if join_code.is_expired():
        raise serializers.ValidationError({"code": "QR code expired. If you believe this is a mistake, contact a teacher/admin."})
    if join_code.exceeded_max_uses():
        raise serializers.ValidationError({"code": "QR code has been used too many times. If you believe this is a mistake, contact a teacher/admin."})

    return join_code


class VerifyJoinCodeSerializer(serializers.Serializer):
    code = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs["join_code"] = validate_join_code(attrs["code"])
        return attrs


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

        validate_join_code(attrs["code"])

        return attrs

    def create(self, validated_data):
        join_code = UserJoinCode.objects.filter(code=validated_data["code"]).first()
        if join_code is not None:
            join_code.uses += 1
            join_code.save()

        validated_data.pop("password2")
        validated_data.pop("code")
        user = User.objects.create_user(**validated_data)
        return user

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields[self.username_field] # why is this hardcoded as a requirement D:<

    def validate(self, attrs):
        user = User.objects.filter(email__iexact=attrs['email']).first()
        if user:
            authed_user = authenticate(username=user.username, password=attrs['password'])
        else:
            User().set_password(attrs['password']) # trick to prevent timing exploit
            authed_user = None

        if not authed_user:
            raise serializers.ValidationError("Invalid email or password.")
                
        refresh = self.get_token(authed_user)
        update_last_login(None, authed_user)

        return {'refresh': str(refresh), 'access': str(refresh.access_token)}