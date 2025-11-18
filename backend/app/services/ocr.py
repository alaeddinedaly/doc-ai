"""OCR service wrapper around Tesseract."""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
import pytesseract

from ..core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class OCRLine:
    """Represents a single OCR line and confidence."""

    text: str
    confidence: float


@dataclass
class OCRResult:
    """OCR output container."""

    text: str
    lines: list[OCRLine]


class OCRService:
    """High-level OCR invoker."""

    def __init__(self) -> None:
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    def run(self, image: np.ndarray) -> OCRResult:
        """Execute OCR with configured parameters."""

        config = (
            "--oem 3 --psm 6 "
            "-c tessedit_char_whitelist="
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            "ÀÂÆÇÉÈÊËÏÎÔŒÙÛÜŸàâæçéèêëïîôœùûüÿ.,/-"
        )
        text = pytesseract.image_to_string(image, lang=settings.ocr_languages, config=config)
        data = pytesseract.image_to_data(
            image,
            lang=settings.ocr_languages,
            config=config,
            output_type=pytesseract.Output.DICT,
        )
        lines: list[OCRLine] = []
        for text_line, conf in zip(data["text"], data["conf"]):
            if text_line.strip():
                try:
                    confidence = float(conf) / 100 if int(conf) >= 0 else 0.0
                except ValueError:
                    confidence = 0.0
                lines.append(OCRLine(text=text_line.strip(), confidence=confidence))
        return OCRResult(text=text.strip(), lines=lines)

