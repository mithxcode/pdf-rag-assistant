import hashlib
import os
from rag.pdf_loader import load_pdf
from rag.store import get_index
from utils.gemini_client import embed

NS = "pdf_docs"


def chunk_text(text, size=800, overlap=150):
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):  # sentence/space par todo, beech word me nahi
            cut = max(text.rfind(". ", start, end), text.rfind("\n", start, end), text.rfind(" ", start, end))
            if cut > start + size // 2:
                end = cut + 1
        chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = end - overlap
    return [c for c in chunks if c]


def file_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:12]


def ingest_pdf(path, display_name=None):
    """Returns (doc_id, num_chunks, already_indexed)."""
    name = display_name or os.path.basename(path)
    doc_id = file_hash(path)
    index = get_index()

    if index.fetch(ids=[f"{doc_id}-0"], namespace=NS).vectors:
        return doc_id, 0, True

    items = []
    for page, text in load_pdf(path):
        for c in chunk_text(text):
            items.append((page, c))
    if not items:
        raise ValueError("PDF se text nahi mila (shayad scanned PDF hai - OCR chahiye).")

    vectors = embed([c for _, c in items])
    records = [
        {"id": f"{doc_id}-{i}", "values": v,
         "metadata": {"text": c, "source": name, "page": page, "doc_id": doc_id}}
        for i, ((page, c), v) in enumerate(zip(items, vectors))
    ]
    for i in range(0, len(records), 100):
        index.upsert(vectors=records[i:i + 100], namespace=NS)
    return doc_id, len(records), False
