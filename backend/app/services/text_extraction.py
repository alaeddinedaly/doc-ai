"""File-type aware text extraction service."""

from __future__ import annotations

import io
import logging
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from docx import Document as DocxDocument
from PIL import Image

from ..core.config import settings

logger = logging.getLogger(__name__)


class TextExtractionService:
    """Extracts text from PDFs, images, DOCX and TXT files."""

    def __init__(self) -> None:
        tesseract_cmd = settings.tesseract_cmd
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, file_path: str, mime_type: str | None = None) -> str:
        ext = Path(file_path).suffix.lower()
        logger.info("Extracting text from %s (%s)", file_path, ext or mime_type)

        if ext == ".pdf" or mime_type == "application/pdf":
            return self._read_pdf(file_path)
        if ext in {".docx", ".doc"} or mime_type in {
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }:
            return self._read_docx(file_path)
        if ext in {".txt", ".md", ".log"} or mime_type == "text/plain":
            return self._read_txt(file_path)
        if ext in {".jpg", ".jpeg", ".png", ".bmp", ".tiff"} or (
            mime_type and mime_type.startswith("image/")
        ):
            return self._read_image(file_path)

        logger.warning("Unsupported file type %s; attempting OCR fallback", ext or mime_type)
        return self._read_image(file_path)

    def _read_pdf(self, file_path: str) -> str:
        text_chunks: list[str] = []
        try:
            with fitz.open(file_path) as doc:
                logger.info("PDF %s: %s pages detected.", file_path, len(doc))
                for page_index, page in enumerate(doc, start=1):
                    page_text = page.get_text("blocks")
                    if page_text:
                        collected = "\n".join(
                            block[4] for block in page_text if block[4] and block[4].strip()
                        )
                        if collected.strip():
                            logger.debug(
                                "PDF page %s: extracted %s characters via text blocks.",
                                page_index,
                                len(collected),
                            )
                            text_chunks.append(collected)
                            continue

                    logger.debug("PDF page %s: falling back to OCR.", page_index)
                    ocr_text = self._ocr_pdf_page(page)
                    if ocr_text:
                        text_chunks.append(ocr_text)

            combined = "\n\n".join(text_chunks).strip()
            if combined:
                logger.info("Extracted %s characters from PDF %s.", len(combined), file_path)
            else:
                logger.warning("No text extracted from PDF %s.", file_path)
            return combined
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to read PDF %s: %s", file_path, exc)
            return ""

    def _ocr_pdf_page(self, page: fitz.Page) -> str:
        text_chunks: list[str] = []
        image_list = page.get_images(full=True)
        if image_list:
            for xref, *_rest in image_list:
                try:
                    base_image = page.parent.extract_image(xref)
                    image_bytes = base_image["image"]
                    image = Image.open(io.BytesIO(image_bytes))
                    ocr_text = self._ocr_image(image)
                    if ocr_text:
                        text_chunks.append(ocr_text)
                except Exception as img_err:  # noqa: BLE001
                    logger.debug("Image OCR failed on page %s: %s", page.number + 1, img_err)
        else:
            try:
                mat = fitz.Matrix(300 / 72, 300 / 72)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                ocr_text = self._ocr_image(image)
                if ocr_text:
                    text_chunks.append(ocr_text)
            except Exception as exc:  # noqa: BLE001
                logger.debug("Full-page OCR failed on page %s: %s", page.number + 1, exc)
        return "\n".join(text_chunks).strip()

    def _read_docx(self, file_path: str) -> str:
        try:
            doc = DocxDocument(file_path)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()
            logger.info("Extracted %s characters from DOCX %s.", len(text), file_path)
            return text
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to read DOCX %s: %s", file_path, exc)
            return ""

    def _read_txt(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as handle:
                text = handle.read().strip()
            logger.info("Extracted %s characters from TXT %s.", len(text), file_path)
            return text
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to read TXT %s: %s", file_path, exc)
            return ""

    def _read_image(self, file_path: str) -> str:
        try:
            image = Image.open(file_path)
            text = self._ocr_image(image)
            logger.info("Extracted %s characters via OCR from image %s.", len(text), file_path)
            return text
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to OCR image %s: %s", file_path, exc)
            return ""

    def _ocr_image(self, image: Image.Image) -> str:
        text = pytesseract.image_to_string(image, lang=settings.ocr_languages or "eng").strip()
        return text

