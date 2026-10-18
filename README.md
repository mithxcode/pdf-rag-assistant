# PolicyGPT - PDF RAG (Gemini + Pinecone + Streamlit)

## Setup
```bash
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```
1. `.env` file kholo aur dono keys daalo: `GEMINI_API_KEY`, `PINECONE_API_KEY`
2. Run: `streamlit run app.py`

Pinecone index (`policygpt-gemini`, 768 dim, cosine, serverless) pehli baar apne aap ban jata hai.
Cloud/region badalna ho to `.env` me `PINECONE_CLOUD` / `PINECONE_REGION` set karo.

## Flow
PDF -> page-wise text -> chunks -> Gemini embeddings -> Pinecone -> query -> top-5 -> LLM (Gemini JSON schema output) -> answer + sources (file/page) + confidence (similarity)
