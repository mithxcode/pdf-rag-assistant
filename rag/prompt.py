def build_prompt(query, chunks):
    context = "\n\n".join(
        f"[Chunk {i}] (file: {c['source']}, page {c['page']})\n{c['text']}" for i, c in enumerate(chunks)
    )
    return f"""You are a policy document assistant.

Context:
{context}

Question: {query}

STRICT RULES:
- Answer ONLY from the context above. Do not use outside knowledge.
- If the answer is not in the context, set found_in_context=false and say you could not find it.
- In used_chunks list the chunk numbers you actually used.
"""
