"""Read study notes from uploaded files so a quiz can be built from them."""

import io

from pypdf import PdfReader
from pypdf.errors import PdfReadError

SUPPORTED_TYPES = ["pdf", "txt", "md"]

# Keep prompts a sensible size. Roughly 8,000 words of notes is plenty for a quiz.
MAX_NOTES_CHARS = 40_000
MIN_NOTES_CHARS = 200


class NotesError(Exception):
    """Raised when notes cannot be read. The message is safe to show to users."""


def _read_pdf(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise NotesError("This PDF is password-protected. Upload an unlocked copy.")
        pages = [page.extract_text() or "" for page in reader.pages]
    except NotesError:
        raise
    except (PdfReadError, ValueError, KeyError) as e:
        raise NotesError(f"Couldn't read this PDF ({e}). Try exporting it again or upload a .txt file.")
    return "\n".join(pages)


def _read_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise NotesError("Couldn't read this text file. Save it as UTF-8 and try again.")


def extract_notes(filename: str, data: bytes) -> tuple[str, bool]:
    """Return (cleaned_text, was_truncated) for an uploaded notes file."""
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in SUPPORTED_TYPES:
        raise NotesError(f"Unsupported file type. Upload one of: {', '.join(SUPPORTED_TYPES)}.")

    raw = _read_pdf(data) if extension == "pdf" else _read_text(data)

    # Collapse runs of blank lines and trailing spaces left over from PDF extraction.
    lines = [line.rstrip() for line in raw.splitlines()]
    text = "\n".join(line for i, line in enumerate(lines) if line or (i and lines[i - 1]))
    text = text.strip()

    if len(text) < MIN_NOTES_CHARS:
        raise NotesError(
            "There isn't enough readable text in this file to build a quiz. "
            "Scanned PDFs (images of pages) can't be read; try a text-based PDF or a .txt file."
        )

    truncated = len(text) > MAX_NOTES_CHARS
    return text[:MAX_NOTES_CHARS], truncated
