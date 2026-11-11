
import mimetypes
import os
from functools import lru_cache
from pathlib import PurePosixPath
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import Storage

from supabase import create_client


@lru_cache(maxsize=1)
def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SECRET_KEY")

    if not url or not key:
        raise ImproperlyConfigured(
            "Configure SUPABASE_URL e SUPABASE_SECRET_KEY."
        )

    return create_client(url, key)


class SupabaseStorage(Storage):

    def __init__(self):
        self.bucket = getattr(
            settings,
            "SUPABASE_STORAGE_BUCKET",
            "products"
        )

    def _save(self, name, content):
        original_path = PurePosixPath(name)

        extension = original_path.suffix.lower()
        folder = str(original_path.parent)

        filename = f"{uuid4().hex}{extension}"

        if folder not in ("", "."):
            path = f"{folder}/{filename}"
        else:
            path = filename

        content.seek(0)
        file_data = content.read()

        content_type = (
            getattr(content, "content_type", None)
            or mimetypes.guess_type(path)[0]
            or "application/octet-stream"
        )

        get_supabase_client().storage.from_(
            self.bucket
        ).upload(
            path=path,
            file=file_data,
            file_options={
                "content-type": content_type,
                "upsert": "false",
            },
        )

        return path

    def _open(self, name, mode="rb"):
        raise NotImplementedError(
            "A abertura direta de arquivos pelo storage não está implementada."
        )

    def delete(self, name):
        if name:
            get_supabase_client().storage.from_(
                self.bucket
            ).remove([name])

    def exists(self, name):
        return False

    def url(self, name):
        return get_supabase_client().storage.from_(
            self.bucket
        ).get_public_url(name)
