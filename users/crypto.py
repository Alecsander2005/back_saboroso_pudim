import hashlib
import hmac

from cryptography.fernet import Fernet
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


_EMAIL_PREFIX = "fernet:v1:"


def normalize_email(email):
    return email.strip().casefold()


def _encryption_key():
    key = getattr(settings, "EMAIL_ENCRYPTION_KEY", "")
    if not key:
        raise ImproperlyConfigured(
            "Configure EMAIL_ENCRYPTION_KEY no ambiente. "
            "Gere uma chave com Fernet.generate_key()."
        )

    try:
        return key.encode("ascii")
    except (AttributeError, UnicodeEncodeError) as error:
        raise ImproperlyConfigured(
            "EMAIL_ENCRYPTION_KEY precisa ser uma chave Fernet válida."
        ) from error


def _fernet():
    try:
        return Fernet(_encryption_key())
    except (ValueError, TypeError) as error:
        raise ImproperlyConfigured(
            "EMAIL_ENCRYPTION_KEY precisa ser uma chave Fernet válida."
        ) from error


def encrypt_email(email):
    if email.startswith(_EMAIL_PREFIX):
        return email

    encrypted = _fernet().encrypt(email.encode("utf-8")).decode("ascii")
    return f"{_EMAIL_PREFIX}{encrypted}"


def decrypt_email(value):
    if not value.startswith(_EMAIL_PREFIX):
        raise ValueError(
            "Foi encontrado e-mail sem criptografia; execute as migrações."
        )

    token = value[len(_EMAIL_PREFIX):].encode("ascii")
    return _fernet().decrypt(token).decode("utf-8")


def email_lookup(email):
    key = hashlib.sha256(
        b"users.email_lookup:v1:" + _encryption_key()
    ).digest()
    normalized = normalize_email(email).encode("utf-8")
    return hmac.new(key, normalized, hashlib.sha256).hexdigest()
