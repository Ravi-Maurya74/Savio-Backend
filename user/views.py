from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from .serializers import (
    UserSerializer,
    AuthTokenSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str, force_bytes
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render
from django.views import View
from django.db.models import Q
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

# Create your views here.


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""

    serializer_class = UserSerializer


class RetrieveUpdateDestroyUserView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a user"""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = UserSerializer

    def get_object(self):
        user = self.request.user
        return user


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class PasswordResetView(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password reset email has been sent."}, status=status.HTTP_200_OK
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            context = {"uidb64": uidb64, "token": token}
            return render(request, "password_reset_confirm.html", context)
        else:
            return HttpResponseBadRequest("Invalid reset link.")

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
            user = None

        if user is not None and PasswordResetTokenGenerator().check_token(user, token):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            password = serializer.validated_data["password"]
            user.set_password(password)
            user.save()

            return HttpResponseRedirect(reverse("password_reset_complete"))
        else:
            return HttpResponseBadRequest("Invalid reset link.")


# views.py

from django.contrib.auth.views import PasswordResetCompleteView
from django.urls import reverse_lazy


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "password_reset_complete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[
            "message"
        ] = "Your password has been successfully reset. Please login with your new password."
        return context


# ListApiView to search users by name or email. A single string will be searched in both name and email.


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="search", description="Search user by name or email", type=str
            ),
        ]
    )
)
class ListUserView(generics.ListAPIView):
    """Search users by name or email. A single string will be searched in both name and email. Pass the string in search query parameter."""

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = get_user_model().objects.exclude(pk=self.request.user.pk)
        search = self.request.query_params.get("search", None)
        if search is not None:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(email__icontains=search)
            )
        return queryset
