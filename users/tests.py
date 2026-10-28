from django.test import TestCase
from django.urls import reverse

from .models import User


class LoginTests(TestCase):
    def setUp(self):
        self.password = "Test123!"
        self.user = User.objects.create_user(
            email="login-test@example.com",
            password=self.password,
            nome_completo="Login Test",
        )

    def test_login_returns_tokens_for_valid_credentials(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.user.email, "password": self.password},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.json())
        self.assertIn("refresh", response.json())
        self.assertEqual(response.json()["user"]["email"], self.user.email)

    def test_login_rejects_invalid_password(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.user.email, "password": "wrong-password"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
