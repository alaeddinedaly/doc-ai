"""Database models for documents and extractions."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Enum, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

DocumentStatus = Enum(
    "pending",
    "processing",
    "completed",
    "failed",
    name="document_status",
)


class Document(Base):
    """Represents an uploaded document."""

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(DocumentStatus, default="pending")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    extraction: Mapped["Extraction"] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        uselist=False,
    )


class Extraction(Base):
    """Represents structured extraction data for a document."""

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    document_id: Mapped[str] = mapped_column(
        ForeignKey("document.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    document_type: Mapped[str] = mapped_column(Text, nullable=False, default="other")
    extracted_data: Mapped[dict] = mapped_column(
        JSONB().with_variant(Text, "sqlite"),
        default=dict,
    )
    confidence_scores: Mapped[dict] = mapped_column(
        JSONB().with_variant(Text, "sqlite"),
        default=dict,
    )
    ocr_text: Mapped[str] = mapped_column(Text, nullable=False)
    processing_time: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    manually_corrected: Mapped[bool] = mapped_column(default=False)

    document: Mapped[Document] = relationship(back_populates="extraction")

