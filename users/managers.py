from django.contrib.auth.base_user import BaseUserManager
from .crypto import email_lookup, normalize_email


class UserManager(BaseUserManager):

    def create_user(
        self,
        email,
        password=None,
        **extra_fields
    ):
        if not email:
            raise ValueError(
                "O usuário precisa ter um e-mail."
            )

        email = normalize_email(email)
        extra_fields.setdefault("email_lookup", email_lookup(email))

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)
        user.save(
            using=self._db
        )

        return user

    def get_by_natural_key(self, username):
        return self.get(email_lookup=email_lookup(normalize_email(username)))

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields
    ):
        extra_fields.setdefault(
            "is_staff",
            True
        )

        extra_fields.setdefault(
            "is_superuser",
            True
        )

        extra_fields.setdefault(
            "is_active",
            True
        )

        extra_fields.setdefault(
            "tipo_usuario",
            "admin"
        )

        if extra_fields.get(
            "is_staff"
        ) is not True:
            raise ValueError(
                "Superusuário precisa ter "
                "is_staff=True."
            )

        if extra_fields.get(
            "is_superuser"
        ) is not True:
            raise ValueError(
                "Superusuário precisa ter "
                "is_superuser=True."
            )

        return self.create_user(
            email,
            password,
            **extra_fields
        )