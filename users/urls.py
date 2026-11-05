from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView,
    AdminLoginView,
    MeView,
    RegisterView,
    LogoutView,
    UserViewSet,
)

router = DefaultRouter()
router.register("", UserViewSet, basename="users")

urlpatterns = [
    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),

    path(
        "admin-login/",
        AdminLoginView.as_view(),
        name="api-admin-login",
    ),

    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),

    path(
        "me/",
        MeView.as_view(),
        name="me",
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name = "logout",
    ),
] + router.urls