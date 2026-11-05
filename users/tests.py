import os
from unittest.mock import patch

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase, TransactionTestCase
from django.test import override_settings
from django.urls import reverse
from django.core.management import call_command
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from .crypto import email_lookup
from .models import User


TEST_EMAIL_ENCRYPTION_KEY = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="


@override_settings(EMAIL_ENCRYPTION_KEY=TEST_EMAIL_ENCRYPTION_KEY)
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

    def test_account_email_is_encrypted_and_password_is_hashed_in_database(self):
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT email, password FROM users_user WHERE id = %s",
                [self.user.pk],
            )
            stored_email, stored_password = cursor.fetchone()

        self.assertTrue(stored_email.startswith("fernet:v1:"))
        self.assertNotIn(self.user.email, stored_email)
        self.assertNotEqual(stored_password, self.password)
        self.assertTrue(self.user.check_password(self.password))


@override_settings(EMAIL_ENCRYPTION_KEY=TEST_EMAIL_ENCRYPTION_KEY)
class AdminAccessTests(TestCase):
    def setUp(self):
        self.password = "AdminTest123!"
        self.admin = User.objects.create_user(
            email="admin-test@example.com",
            password=self.password,
            nome_completo="Admin Test",
            tipo_usuario="admin",
        )
        self.other_admin = User.objects.create_user(
            email="other-admin@example.com",
            password=self.password,
            nome_completo="Other Admin",
            tipo_usuario="admin",
        )
        self.customer = User.objects.create_user(
            email="customer-test@example.com",
            password=self.password,
            nome_completo="Customer Test",
        )

    def client_for(self, user):
        client = APIClient()
        token = RefreshToken.for_user(user).access_token
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return client

    def test_customer_cannot_log_in_to_admin_panel(self):
        response = self.client.post(
            reverse("api-admin-login"),
            {"email": self.customer.email, "password": self.password},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertNotIn("access", response.json())

    def test_admin_can_log_in_to_admin_panel(self):
        response = self.client.post(
            reverse("api-admin-login"),
            {"email": self.admin.email, "password": self.password},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["tipo_usuario"], "admin")
        self.assertIn("access", response.json())

    def test_admin_cannot_assign_an_email_already_used_by_another_user(self):
        response = self.client_for(self.other_admin).patch(
            reverse("users-detail", args=[self.admin.pk]),
            {"email": self.other_admin.email},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.email, "admin-test@example.com")

    def test_admin_cannot_deactivate_the_account_used_for_request(self):
        response = self.client_for(self.admin).patch(
            reverse("users-detail", args=[self.admin.pk]),
            {"is_active": False},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)

    def test_deactivated_admin_token_is_rejected(self):
        response = self.client_for(self.other_admin).patch(
            reverse("users-detail", args=[self.admin.pk]),
            {"is_active": False},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        response = self.client_for(self.admin).get(reverse("me"))
        self.assertEqual(response.status_code, 401)


@override_settings(EMAIL_ENCRYPTION_KEY=TEST_EMAIL_ENCRYPTION_KEY)
class EnsureAdminCommandTests(TestCase):
    @patch.dict(
        os.environ,
        {
            "INITIAL_ADMIN_EMAIL": "bootstrap@example.com",
            "INITIAL_ADMIN_PASSWORD": "BootstrapAdmin123!Unique",
            "INITIAL_ADMIN_NAME": "Bootstrap Admin",
        },
    )
    def test_command_creates_admin_idempotently_with_hashed_password(self):
        call_command("ensure_admin")
        call_command("ensure_admin")

        user = User.objects.get(
            email_lookup=email_lookup("bootstrap@example.com")
        )
        self.assertEqual(user.tipo_usuario, "admin")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password("BootstrapAdmin123!Unique"))
        self.assertEqual(User.objects.count(), 1)


@override_settings(EMAIL_ENCRYPTION_KEY=TEST_EMAIL_ENCRYPTION_KEY)
class EmailEncryptionMigrationTests(TransactionTestCase):
    def test_migration_encrypts_existing_plaintext_emails(self):
        migrate_from = ("users", "0001_initial")
        migrate_to = ("users", "0002_encrypt_user_emails")

        executor = MigrationExecutor(connection)
        executor.migrate([migrate_from])
        self.addCleanup(self.restore_latest_migrations)
        old_apps = executor.loader.project_state([migrate_from]).apps
        OldUser = old_apps.get_model("users", "User")
        OldUser.objects.create(
            email="Existing.User@example.com",
            password="!",
            nome_completo="Existing User",
            tipo_usuario="cliente",
        )

        executor = MigrationExecutor(connection)
        executor.migrate([migrate_to])
        migrated_apps = executor.loader.project_state([migrate_to]).apps
        MigratedUser = migrated_apps.get_model("users", "User")
        user = MigratedUser.objects.get(
            email_lookup=email_lookup("existing.user@example.com")
        )
        self.assertEqual(user.email, "existing.user@example.com")

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT email FROM users_user WHERE id = %s",
                [user.pk],
            )
            stored_email = cursor.fetchone()[0]
        self.assertTrue(stored_email.startswith("fernet:v1:"))

    def restore_latest_migrations(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
