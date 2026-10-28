from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView

from . import views

app_name = "api-v1"

urlpatterns = [
    path("registration/", views.RegistrationApiView.as_view(), name="registration"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    path(
        "change_password/",
        views.ChangePasswordView.as_view(),
        name="auth_change_password",
    ),
    path(
        "activation/confirm/<str:token>",
        views.ActivationApiView.as_view(),
        name="activation",
    ),
    path("profile/", views.MeView.as_view(), name="me"),
]
