import config
from rag.retrieve import retrieve
from rag.prompt import build_prompt
from utils.gemini_client import ask_llm
from models.schema import AnswerSchema


def answer_query(query, doc_id=None):
    config.check_keys()
    chunks = retrieve(query, doc_id)
    if not chunks:
        return AnswerSchema(answer="Koi document indexed nahi hai.", sources=[], confidence=0.0).model_dump()

    out = ask_llm(build_prompt(query, chunks))
    used = [chunks[i] for i in out.used_chunks if 0 <= i < len(chunks)]
    sources = sorted({f"{c['source']} - page {c['page']}" for c in used})
    # confidence = retrieval similarity (cosine), LLM ke self-report par bharosa nahi
    confidence = round(max((c["score"] for c in used), default=0.0), 3) if out.found_in_context else 0.0
    return AnswerSchema(answer=out.answer, sources=sources, confidence=confidence).model_dump()
