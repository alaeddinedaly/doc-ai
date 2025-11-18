"""Document related schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExtractionPayload(BaseModel):
    """Validated extraction payload."""

    document_type: str = Field(default="other")
    document_type_confidence: float | None = None
    invoice_number: str | None = None
    supplier: str | None = None
    date: str | None = None
    amount_ht: float | None = None
    tva: float | None = None
    amount_ttc: float | None = None
    currency: str | None = None
    confidence_score: float | None = None


class DocumentResponse(BaseModel):
    """Document response schema."""

    id: str
    filename: str
    mime_type: str
    file_size: int
    status: str
    uploaded_at: datetime
    processed_at: datetime | None
    error_message: str | None = None
    extracted_data: dict[str, Any] | None = None
    confidence_scores: dict[str, float] | None = None
    document_type: str | None = None
    download_url: str | None = None


class DocumentListResponse(BaseModel):
    """Paginated list response."""

    data: list[DocumentResponse]
    total: int
    page: int
    limit: int


class DocumentUpdatePayload(BaseModel):
    """Payload for manual corrections."""

    extracted_data: dict[str, Any]
    confidence_scores: dict[str, float] | None = None


class ExportRequest(BaseModel):
    """Request body for exports."""

    document_ids: list[str]
    format: str = Field(pattern="^(json|csv|excel)$")

