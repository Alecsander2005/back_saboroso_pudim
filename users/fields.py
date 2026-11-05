from django.db import models

from .crypto import decrypt_email, encrypt_email


class EncryptedEmailField(models.EmailField):
    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return None
        return encrypt_email(value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        return decrypt_email(value)
