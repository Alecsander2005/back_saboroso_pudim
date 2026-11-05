from django.db import migrations, models

import users.crypto
import users.fields


def encrypt_existing_emails(apps, schema_editor):
    User = apps.get_model("users", "User")
    database = schema_editor.connection.alias
    records = list(
        User.objects.using(database).values_list("pk", "email")
    )

    lookup_by_id = {}
    seen_lookups = set()
    for user_id, email in records:
        normalized_email = users.crypto.normalize_email(email)
        lookup = users.crypto.email_lookup(normalized_email)
        if lookup in seen_lookups:
            raise RuntimeError(
                "Existem e-mails de usuário duplicados após normalização; "
                "corrija-os antes de aplicar esta migração."
            )
        seen_lookups.add(lookup)
        lookup_by_id[user_id] = lookup

    for user_id, email in records:
        User.objects.using(database).filter(pk=user_id).update(
            email=users.crypto.encrypt_email(
                users.crypto.normalize_email(email)
            ),
            email_lookup=lookup_by_id[user_id],
        )


def decrypt_emails(apps, schema_editor):
    User = apps.get_model("users", "User")
    database = schema_editor.connection.alias

    for user_id, encrypted_email in User.objects.using(database).values_list(
        "pk", "email"
    ).iterator():
        User.objects.using(database).filter(pk=user_id).update(
            email=users.crypto.decrypt_email(encrypted_email),
            email_lookup=None,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email_lookup",
            field=models.CharField(
                editable=False,
                max_length=64,
                null=True,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=512, unique=True),
        ),
        migrations.RunPython(
            encrypt_existing_emails,
            reverse_code=decrypt_emails,
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=users.fields.EncryptedEmailField(max_length=512, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="email_lookup",
            field=models.CharField(
                editable=False,
                max_length=64,
                unique=True,
            ),
        ),
    ]
