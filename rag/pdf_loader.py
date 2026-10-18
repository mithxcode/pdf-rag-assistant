from pypdf import PdfReader


def load_pdf(path):
    """Returns list of (page_number, text)."""
    reader = PdfReader(path)
    return [(i + 1, (p.extract_text() or "").strip()) for i, p in enumerate(reader.pages)]
