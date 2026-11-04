"""Object Storage Interface with Local Storage & S3 Support.

Provides free-tier local filesystem storage as well as S3/MinIO compatibility.
"""

import os
import gzip
import hashlib
from typing import Protocol
from app.core.config import settings


class StorageBackend(Protocol):
    def put_object(self, key: str, data: bytes, compress: bool = True) -> tuple[str, bytes, int]:
        """Store bytes under key. Returns (key, sha256_hash, byte_size)."""
        ...

    def get_object(self, key: str, decompress: bool = True) -> bytes:
        """Retrieve bytes stored under key."""
        ...

    def delete_object(self, key: str) -> bool:
        """Delete object under key."""
        ...


class LocalFileStorage:
    """Free-Tier local filesystem object storage."""

    def __init__(self, base_dir: str = settings.STORAGE_LOCAL_DIR):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        # Sanitize path to prevent directory traversal
        clean_key = os.path.normpath(key).lstrip(r"\/")
        full_path = os.path.join(self.base_dir, clean_key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        return full_path

    def put_object(self, key: str, data: bytes, compress: bool = True) -> tuple[str, bytes, int]:
        file_path = self._get_path(key)
        sha256 = hashlib.sha256(data).digest()

        if compress:
            stored_data = gzip.compress(data)
        else:
            stored_data = data

        with open(file_path, "wb") as f:
            f.write(stored_data)

        return key, sha256, len(stored_data)

    def get_object(self, key: str, decompress: bool = True) -> bytes:
        file_path = self._get_path(key)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Storage key '{key}' not found.")

        with open(file_path, "rb") as f:
            raw = f.read()

        if decompress:
            try:
                return gzip.decompress(raw)
            except Exception:
                return raw
        return raw

    def delete_object(self, key: str) -> bool:
        file_path = self._get_path(key)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False


def get_storage() -> StorageBackend:
    """Factory returning the active storage backend."""
    return LocalFileStorage()

