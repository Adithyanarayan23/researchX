import os
import io
import logging
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader
from docx import Document as DocxDocument
from app.core.security import sanitize_untrusted_content

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str, filename: str) -> List[Dict[str, Any]]:
    """
    Extracts text sections and pages from PDF, DOCX, TXT, or MD files.
    Returns: List of {"page_number": int, "section": str, "text": str}
    """
    ext = filename.lower().split(".")[-1]
    pages: List[Dict[str, Any]] = []

    if ext == "pdf":
        try:
            reader = PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                raw_text = page.extract_text() or ""
                cleaned_text, _ = sanitize_untrusted_content(raw_text)
                if cleaned_text.strip():
                    pages.append({
                        "page_number": idx + 1,
                        "section": f"Page {idx + 1}",
                        "text": cleaned_text
                    })
        except Exception as e:
            logger.error("Error reading PDF %s: %s", filename, str(e))

    elif ext in ("docx", "doc"):
        try:
            doc = DocxDocument(file_path)
            current_section = "General"
            current_paragraphs: List[str] = []
            page_estimate = 1

            for p in doc.paragraphs:
                text = p.text.strip()
                if not text:
                    continue

                # Check if heading
                if p.style and p.style.name.startswith("Heading"):
                    if current_paragraphs:
                        section_text = "\n".join(current_paragraphs)
                        cleaned_text, _ = sanitize_untrusted_content(section_text)
                        pages.append({
                            "page_number": page_estimate,
                            "section": current_section,
                            "text": cleaned_text
                        })
                        current_paragraphs = []
                    current_section = text
                else:
                    current_paragraphs.append(text)

            if current_paragraphs:
                section_text = "\n".join(current_paragraphs)
                cleaned_text, _ = sanitize_untrusted_content(section_text)
                pages.append({
                    "page_number": page_estimate,
                    "section": current_section,
                    "text": cleaned_text
                })
        except Exception as e:
            logger.error("Error reading DOCX %s: %s", filename, str(e))

    elif ext in ("txt", "md"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            cleaned_text, _ = sanitize_untrusted_content(content)
            pages.append({
                "page_number": 1,
                "section": "Document Body",
                "text": cleaned_text
            })
        except Exception as e:
            logger.error("Error reading text file %s: %s", filename, str(e))

    else:
        logger.warning("Unsupported file type: %s", ext)

    return pages
