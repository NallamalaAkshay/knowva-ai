import re
from io import BytesIO
from pathlib import Path

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".txt",
    ".md",
}


def extract_docx_text(content: bytes) -> str:
    document = Document(BytesIO(content))
    sections: list[str] = []

    # Read paragraphs and tables in their original document order.
    for element in document.element.body.iterchildren():
        if isinstance(element, CT_P):
            paragraph = Paragraph(element, document)
            text = paragraph.text.strip()

            if text:
                sections.append(text)

        elif isinstance(element, CT_Tbl):
            table = Table(element, document)

            for row in table.rows:
                cells = [
                    cell.text.strip()
                    for cell in row.cells
                    if cell.text.strip()
                ]

                if cells:
                    sections.append(" | ".join(cells))

    return "\n\n".join(sections)


def extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    pages: list[str] = []

    for page in reader.pages:
        page_text = page.extract_text() or ""

        if page_text.strip():
            pages.append(page_text.strip())

    return "\n\n".join(pages)


def extract_text(filename: str, content: bytes) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Supported file types: PDF, DOCX, TXT, and MD"
        )

    if extension == ".pdf":
        return extract_pdf_text(content)

    if extension == ".docx":
        return extract_docx_text(content)

    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(
            "Text files must use UTF-8 encoding"
        ) from exc


def clean_paragraph(paragraph: str) -> str:
    # Remove repeated spaces without deleting paragraph structure.
    return re.sub(r"[ \t]+", " ", paragraph).strip()


def split_large_paragraph(
    paragraph: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    pieces: list[str] = []
    start = 0

    while start < len(paragraph):
        end = min(start + chunk_size, len(paragraph))

        if end < len(paragraph):
            boundary = paragraph.rfind(" ", start, end)

            if boundary > start:
                end = boundary

        piece = paragraph[start:end].strip()

        if piece:
            pieces.append(piece)

        if end >= len(paragraph):
            break

        start = max(end - overlap, start + 1)

    return pieces


def chunk_text(
    text: str,
    chunk_size: int,
    overlap: int,
) -> list[str]:
    if not text.strip():
        return []

    # Keep paragraphs separate so titles, locations and descriptions
    # remain recognizable.
    paragraphs = [
        clean_paragraph(paragraph)
        for paragraph in re.split(r"\n\s*\n|\n+", text)
        if clean_paragraph(paragraph)
    ]

    if not paragraphs:
        return []

    chunks: list[str] = []
    current_paragraphs: list[str] = []
    current_length = 0

    for paragraph in paragraphs:
        # Handle an unusually large paragraph separately.
        if len(paragraph) > chunk_size:
            if current_paragraphs:
                chunks.append(
                    "\n\n".join(current_paragraphs)
                )
                current_paragraphs = []
                current_length = 0

            chunks.extend(
                split_large_paragraph(
                    paragraph,
                    chunk_size,
                    overlap,
                )
            )
            continue

        separator_length = 2 if current_paragraphs else 0
        proposed_length = (
            current_length
            + separator_length
            + len(paragraph)
        )

        if proposed_length <= chunk_size:
            current_paragraphs.append(paragraph)
            current_length = proposed_length
            continue

        # Save the completed chunk.
        if current_paragraphs:
            chunks.append(
                "\n\n".join(current_paragraphs)
            )

        # Preserve complete trailing paragraphs as overlap.
        overlap_paragraphs: list[str] = []
        overlap_length = 0

        for previous_paragraph in reversed(current_paragraphs):
            additional_length = (
                len(previous_paragraph)
                + (2 if overlap_paragraphs else 0)
            )

            if overlap_length + additional_length > overlap:
                break

            overlap_paragraphs.insert(
                0,
                previous_paragraph,
            )
            overlap_length += additional_length

        current_paragraphs = overlap_paragraphs + [paragraph]
        current_length = len(
            "\n\n".join(current_paragraphs)
        )

    if current_paragraphs:
        chunks.append(
            "\n\n".join(current_paragraphs)
        )

    return [
        chunk
        for chunk in chunks
        if chunk.strip()
    ]