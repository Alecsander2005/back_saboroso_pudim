import os

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email

from users.crypto import email_lookup, normalize_email
from users.models import User


class Command(BaseCommand):
    help = "Cria o administrador inicial a partir das variáveis de ambiente."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-password",
            action="store_true",
            help="Atualiza a senha do admin existente com INITIAL_ADMIN_PASSWORD.",
        )

    def handle(self, *args, **options):
        email = os.getenv("INITIAL_ADMIN_EMAIL", "").strip()
        password = os.getenv("INITIAL_ADMIN_PASSWORD", "")
        name = os.getenv("INITIAL_ADMIN_NAME", "Administrador da loja").strip()

        if not email or not password:
            raise CommandError(
                "Defina INITIAL_ADMIN_EMAIL e INITIAL_ADMIN_PASSWORD."
            )

        email = normalize_email(email)
        try:
            validate_email(email)
        except ValidationError as error:
            raise CommandError("INITIAL_ADMIN_EMAIL não é válido.") from error

        if not name:
            raise CommandError("INITIAL_ADMIN_NAME não pode ficar vazio.")

        existing_user = User.objects.filter(
            email_lookup=email_lookup(email)
        ).first()

        if existing_user:
            if existing_user.tipo_usuario != "admin":
                raise CommandError(
                    "INITIAL_ADMIN_EMAIL já pertence a uma conta que não é admin."
                )

            if options["reset_password"]:
                try:
                    validate_password(password, user=existing_user)
                except ValidationError as error:
                    raise CommandError("; ".join(error.messages)) from error

                existing_user.set_password(password)
                existing_user.save(update_fields=["password"])
                self.stdout.write(
                    self.style.SUCCESS("Senha do administrador atualizada.")
                )
                return

            self.stdout.write("Administrador inicial já existe; conta preservada.")
            return

        user = User(
            email=email,
            nome_completo=name,
            tipo_usuario="admin",
            is_staff=True,
        )
        try:
            validate_password(password, user=user)
        except ValidationError as error:
            raise CommandError("; ".join(error.messages)) from error

        User.objects.create_user(
            email=email,
            password=password,
            nome_completo=name,
            tipo_usuario="admin",
            is_staff=True,
        )
        self.stdout.write(self.style.SUCCESS("Administrador inicial criado."))
