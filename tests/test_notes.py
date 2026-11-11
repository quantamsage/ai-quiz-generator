import io

import pytest

from notes import MAX_NOTES_CHARS, NotesError, extract_notes

SAMPLE = "Photosynthesis turns light energy into chemical energy. " * 10


def test_reads_text_file():
    text, truncated = extract_notes("bio.txt", SAMPLE.encode("utf-8"))
    assert text.startswith("Photosynthesis") and not truncated


def test_long_notes_are_truncated():
    text, truncated = extract_notes("long.md", ("word " * 20_000).encode())
    assert truncated and len(text) == MAX_NOTES_CHARS


def test_rejects_short_or_unsupported_files():
    with pytest.raises(NotesError):
        extract_notes("tiny.txt", b"too short")
    with pytest.raises(NotesError):
        extract_notes("slides.pptx", SAMPLE.encode())


def test_reads_pdf():
    canvas = pytest.importorskip("reportlab.pdfgen.canvas")
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    y = 800
    for _ in range(6):
        pdf.drawString(40, y, "Photosynthesis turns light energy into chemical energy.")
        y -= 20
    pdf.save()
    text, _ = extract_notes("notes.pdf", buffer.getvalue())
    assert "chemical energy" in text


def test_rejects_broken_pdf():
    with pytest.raises(NotesError):
        extract_notes("broken.pdf", b"%PDF-1.4 this is not really a pdf")
