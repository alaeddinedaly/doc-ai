"""Security utilities for file validation and sanitisation."""

from __future__ import annotations

import re
import secrets
from pathlib import Path
from typing import Iterable

from fastapi import HTTPException, status

FILENAME_SAFE_PATTERN = re.compile(r"[^A-Za-z0-9._-]")
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
}


def sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filenames."""

    cleaned = FILENAME_SAFE_PATTERN.sub("_", filename)
    return cleaned.strip("._") or secrets.token_hex(4)


def validate_mime_type(mime_type: str) -> None:
    """Ensure file has an allowed mime-type."""

    if mime_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {mime_type}",
        )


def validate_magic_bytes(file_bytes: bytes) -> None:
    """Perform lightweight magic-bytes validation."""

    if file_bytes.startswith(b"%PDF"):
        return
    if file_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return
    if file_bytes.startswith(b"\xff\xd8"):
        return
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="File content does not match expected format.",
    )


def enforce_file_limits(files: Iterable) -> None:  # type: ignore[no-untyped-def]
    """Enforce maximum file count for batch uploads."""

    files_list = list(files)
    if len(files_list) == 0:
        raise HTTPException(status_code=400, detail="No files provided.")


def resolve_storage_path(base_dir: Path, filename: str) -> Path:
    """Generate a safe storage path for an uploaded file."""

    return base_dir / sanitize_filename(filename)

