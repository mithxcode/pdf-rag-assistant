import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "policygpt-gemini")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD", "aws")
PINECONE_REGION = os.getenv("PINECONE_REGION", "us-east-1")

EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 768
LLM_MODEL = "gemini-2.5-flash"
TOP_K = 5


def check_keys():
    missing = [k for k, v in {"GEMINI_API_KEY": GEMINI_API_KEY,
                              "PINECONE_API_KEY": PINECONE_API_KEY}.items() if not v]
    if missing:
        raise RuntimeError(f".env file me ye keys add karo: {', '.join(missing)}")
