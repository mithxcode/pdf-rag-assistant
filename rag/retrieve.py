from config import TOP_K
from rag.store import get_index
from rag.ingest import NS
from utils.gemini_client import embed_query


def retrieve(query, doc_id=None):
    """Returns list of dicts: text, source, page, score."""
    kwargs = {"filter": {"doc_id": {"$eq": doc_id}}} if doc_id else {}
    res = get_index().query(vector=embed_query(query), top_k=TOP_K,
                            include_metadata=True, namespace=NS, **kwargs)
    return [{"text": m.metadata["text"], "source": m.metadata["source"],
             "page": int(m.metadata["page"]), "score": float(m.score)} for m in res.matches]
