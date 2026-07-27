"""
Lightweight document parser for maternal health RAG.
Supports: .md, .txt, .pdf
No docling dependency — uses pypdf for PDFs, native reading for text/markdown.
"""

import os
import logging
from pathlib import Path
from typing import Any, List, Tuple


class MedicalDocParser:
    """
    Lightweight parser: .md/.txt (native) + .pdf (pypdf).
    Returns a simple parsed document object compatible with ContentProcessor.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("MedicalDocParser initialized (lightweight mode)")

    def parse_document(
        self,
        document_path: str,
        output_dir: str,
        **kwargs
    ) -> Tuple[Any, List[str]]:
        """
        Parse document and return (parsed_doc, images_list).
        For markdown/text files, returns the text as a simple document object.
        For PDFs, extracts text using pypdf.

        Returns:
            (SimpleDoc, [])  — no images extracted in lightweight mode
        """
        path = Path(document_path)
        suffix = path.suffix.lower()

        os.makedirs(output_dir, exist_ok=True)

        if suffix in ('.md', '.txt'):
            text = self._read_text(document_path)
        elif suffix == '.pdf':
            text = self._read_pdf(document_path)
        else:
            self.logger.warning(f"Unsupported file type: {suffix}, trying as plain text")
            text = self._read_text(document_path)

        self.logger.info(f"Parsed {path.name}: {len(text)} characters")
        return SimpleDoc(text, path.name), []  # no image extraction

    def _read_text(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _read_pdf(self, path: str) -> str:
        try:
            from pypdf import PdfReader
            reader = PdfReader(path)
            pages = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
            return '\n\n'.join(pages)
        except ImportError:
            self.logger.error("pypdf not installed. Run: pip install pypdf")
            return ""
        except Exception as e:
            self.logger.error(f"PDF parse error: {e}")
            return ""


class SimpleDoc:
    """
    Minimal document wrapper that mimics the docling document interface
    used by ContentProcessor.export_to_markdown().
    """

    def __init__(self, text: str, filename: str = "doc"):
        self._text = text
        self.filename = filename
        self.pictures = []  # no pictures
        self.pages = {}     # no page images

    def export_to_markdown(self, page_break_placeholder="", image_placeholder="") -> str:
        """Return the text as-is (already markdown-compatible for .md files)."""
        return self._text