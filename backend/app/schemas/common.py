"""Common schema helpers."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class Pagination(BaseModel):
    """Pagination metadata."""

    page: int = Field(ge=1, default=1)
    limit: int = Field(ge=1, le=100, default=20)


class DocumentBase(BaseModel):
    """Shared document fields."""

    filename: str
    mime_type: str
    file_size: int
    status: str
    uploaded_at: datetime
    processed_at: datetime | None


class ExtractionBase(BaseModel):
    """Shared extraction fields."""

    document_type: str
    extracted_data: dict
    confidence_scores: dict
    ocr_text: str
    processing_time: float
    manually_corrected: bool


class TaskStatus(BaseModel):
    """Status payload for background processing."""

    task_id: str
    status: str
    message: str | None = None
    current_step: int = 0
    total_steps: int = 0
    result_id: str | None = None

