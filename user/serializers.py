from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from django.contrib.auth.forms import PasswordResetForm
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from rest_framework.utils.urls import replace_query_param
from django.conf import settings
import requests
from django.contrib.auth.tokens import PasswordResetTokenGenerator


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "password",
            "name",
            "city",
            "total_budget",
            "profile_pic",
        )
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return get_user_model().objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user authentication object"""

    email = serializers.CharField()
    password = serializers.CharField(
        style={"input_type": "password"}, trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"), username=email, password=password
        )
        if not user:
            msg = _("Unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authentication")

        attrs["user"] = user
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise ValidationError("User with this email address does not exist.")
        return value

    def save(self):
        request = self.context.get("request")
        email = self.validated_data["email"]
        print(email)
        user = User.objects.get(email=email)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        reset_url = reverse(
            "password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )
        reset_url = replace_query_param(reset_url, "email", email)
        reset_url = f"{request.scheme}://{request.get_host()}{reset_url}"

        # Send password reset email using Sendinblue API
        url = "https://api.sendinblue.com/v3/smtp/email"
        headers = {
            "Content-Type": "application/json",
            "api-key": settings.SENDINBLUE_API_KEY,
        }
        data = {
            "sender": {"name": "Savio Team", "email": "ravi.maurya47t@gmail.com"},
            "to": [{"email": email}],
            "subject": "Password reset",
            "htmlContent": f"Click <a href='{reset_url}'>here</a> to reset your password.",
        }
        response = requests.post(url, headers=headers, json=data)
        print(response.json())
        response.raise_for_status()


class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, write_only=True)

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data
