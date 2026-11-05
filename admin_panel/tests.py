from django.test import TestCase
from django.test import override_settings
from django.urls import reverse

from users.models import User


@override_settings(
    EMAIL_ENCRYPTION_KEY="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
)
class DashboardAccessTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="panel-customer@example.com",
            password="CustomerTest123!",
            nome_completo="Panel Customer",
        )
        self.admin = User.objects.create_user(
            email="panel-admin@example.com",
            password="AdminTest123!",
            nome_completo="Panel Admin",
            tipo_usuario="admin",
        )

    def test_dashboard_redirects_unauthenticated_visitors(self):
        response = self.client.get(reverse("admin-dashboard"))

        self.assertRedirects(response, reverse("admin-login"))

    def test_dashboard_redirects_customers(self):
        self.client.force_login(self.customer)

        response = self.client.get(reverse("admin-dashboard"))

        self.assertRedirects(response, reverse("admin-login"))

    def test_dashboard_is_available_to_logged_in_admins(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("admin-dashboard"))

        self.assertEqual(response.status_code, 200)

    def test_deactivated_admin_cannot_reopen_the_dashboard(self):
        self.client.force_login(self.admin)
        self.admin.is_active = False
        self.admin.save(update_fields=["is_active"])

        response = self.client.get(reverse("admin-dashboard"))

        self.assertRedirects(response, reverse("admin-login"))

    def test_admin_login_creates_a_dashboard_session(self):
        response = self.client.post(
            reverse("api-admin-login"),
            {"email": self.admin.email, "password": "AdminTest123!"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.client.get(reverse("admin-dashboard")).status_code,
            200,
        )

    def test_logging_out_ends_the_dashboard_session(self):
        response = self.client.post(
            reverse("api-admin-login"),
            {"email": self.admin.email, "password": "AdminTest123!"},
            content_type="application/json",
        )
        logout_response = self.client.post(
            reverse("logout"),
            {"refresh": response.json()["refresh"]},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {response.json()['access']}",
        )

        self.assertEqual(logout_response.status_code, 200)
        dashboard_response = self.client.get(reverse("admin-dashboard"))

        self.assertRedirects(dashboard_response, reverse("admin-login"))
