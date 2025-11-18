"""Local storage helper utilities."""

from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile

from ..core.config import settings
from ..core.security import resolve_storage_path, sanitize_filename


class StorageService:
    """Handles persistence for uploaded files."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or settings.uploads_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file: UploadFile) -> Path:
        """Persist an uploaded file and return its path."""

        filename = sanitize_filename(file.filename or "document")
        destination = resolve_storage_path(self.base_dir, filename)
        with destination.open("wb") as dest:
            shutil.copyfileobj(file.file, dest)
        return destination

    def read_bytes(self, path: str | Path) -> bytes:
        """Return file bytes for downstream processing."""

        return Path(path).read_bytes()

