from django.urls import path
from user import views
from user.views import PasswordResetView, PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView

urlpatterns = [
    path("create/", views.CreateUserView.as_view(), name="create"),
    path(
        "me/",
        views.RetrieveUpdateDestroyUserView.as_view(),
        name="retrieve-update-destroy",
    ),
    path("token/", views.CreateTokenView.as_view(), name="token"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password_reset_confirm/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_complete/",
        views.CustomPasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]
