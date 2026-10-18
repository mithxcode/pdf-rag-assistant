import os
import tempfile
import streamlit as st
import config
from main import answer_query
from rag.ingest import ingest_pdf

st.set_page_config(page_title="PolicyGPT", page_icon="📄")
st.title("📄 PolicyGPT - PDF RAG Chatbot")

try:
    config.check_keys()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

up = st.file_uploader("Upload PDF", type="pdf")
if up and st.session_state.get("loaded_file") != (up.name, up.size):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(up.getvalue())
        tmp = f.name
    try:
        with st.spinner("PDF process ho rahi hai..."):
            doc_id, n, existed = ingest_pdf(tmp, display_name=up.name)
        st.session_state.update(loaded_file=(up.name, up.size), doc_id=doc_id)
        st.success("PDF pehle se indexed hai." if existed else f"PDF processed! {n} chunks Pinecone me store hue.")
    except Exception as e:
        st.error(f"Ingest fail: {e}")
    finally:
        os.remove(tmp)

query = st.text_input("PDF se sawal poochho:")
if st.button("Ask") and query.strip():
    with st.spinner("Soch raha hu..."):
        try:
            r = answer_query(query, st.session_state.get("doc_id"))
            st.markdown(r["answer"])
            st.caption(f"Confidence: {r['confidence']}")
            if r["sources"]:
                st.write("**Sources:**", ", ".join(r["sources"]))
        except Exception as e:
            st.error(f"Error: {e}")
