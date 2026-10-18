import time
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, EMBED_MODEL, EMBED_DIM, LLM_MODEL
from models.schema import LLMAnswer

_client = None


def client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _retry(fn, tries=5):
    """Free tier me 429 (rate limit) aa sakta hai - thoda ruk kar dobara try."""
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            if i == tries - 1 or not any(s in str(e) for s in ("429", "RESOURCE_EXHAUSTED", "503")):
                raise
            time.sleep(10 * (i + 1))


def embed(texts, task="RETRIEVAL_DOCUMENT", batch=50):
    out = []
    cfg = types.EmbedContentConfig(task_type=task, output_dimensionality=EMBED_DIM)
    for i in range(0, len(texts), batch):
        part = texts[i:i + batch]
        res = _retry(lambda: client().models.embed_content(model=EMBED_MODEL, contents=part, config=cfg))
        out += [e.values for e in res.embeddings]
        if i + batch < len(texts):
            time.sleep(1)
    return out


def embed_query(text):
    return embed([text], task="RETRIEVAL_QUERY")[0]


def ask_llm(prompt: str) -> LLMAnswer:
    cfg = types.GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=LLMAnswer,
        temperature=0,
    )
    res = _retry(lambda: client().models.generate_content(model=LLM_MODEL, contents=prompt, config=cfg))
    return res.parsed if res.parsed else LLMAnswer.model_validate_json(res.text)
