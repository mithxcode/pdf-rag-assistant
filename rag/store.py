import time
from pinecone import Pinecone, ServerlessSpec
import config

_index = None


def get_index():
    global _index
    if _index is None:
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        if not pc.has_index(config.PINECONE_INDEX):
            pc.create_index(
                name=config.PINECONE_INDEX,
                dimension=config.EMBED_DIM,
                metric="cosine",
                spec=ServerlessSpec(cloud=config.PINECONE_CLOUD, region=config.PINECONE_REGION),
            )
            while not pc.describe_index(config.PINECONE_INDEX).status["ready"]:
                time.sleep(1)
        _index = pc.Index(config.PINECONE_INDEX)
    return _index
