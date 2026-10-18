import html
import os
import tempfile

import streamlit as st

import config
from main import answer_query
from rag.ingest import ingest_pdf

st.set_page_config(page_title="PolicyGPT | Chat with your PDF", page_icon="📄",
                   layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 2.2rem; max-width: 820px;}
.hero {text-align: center; padding: 1.2rem 0 0.6rem;}
.hero h1 {font-size: 2.6rem; font-weight: 800; margin: 0;
  background: linear-gradient(90deg, #7C6CFF, #38BDF8); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;}
.hero p {color: #9AA4C7; font-size: 1.05rem; margin-top: .4rem;}
.card {background: #141B33; border: 1px solid #232C4F; border-radius: 14px; padding: 1.1rem 1.3rem;}
.empty {text-align: center; padding: 2.2rem 1rem;}
.empty h3 {margin-bottom: .3rem;}
.empty span {color: #9AA4C7;}
.chip {display: inline-block; background: rgba(124,108,255,.14); border: 1px solid rgba(124,108,255,.45);
  color: #CFC9FF; padding: .15rem .65rem; border-radius: 8px; font-size: .8rem; margin: .2rem .3rem 0 0;}
.stButton > button {border-radius: 10px; border: 1px solid #2B376B; background: #141B33;}
.stButton > button:hover {border-color: #7C6CFF; color: #fff;}
section[data-testid="stSidebar"] {border-right: 1px solid #1E2748;}
.step {color: #9AA4C7; font-size: .9rem; margin: .25rem 0;}
</style>
""", unsafe_allow_html=True)

# ---------- keys ----------
try:
    config.check_keys()
except RuntimeError as e:
    st.error(str(e))
    st.stop()

ss = st.session_state
ss.setdefault("messages", [])
ss.setdefault("doc", None)

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### 📄 PolicyGPT")
    st.caption("Chat with your PDF. Answers come with page-level sources.")
    up = st.file_uploader("Upload a PDF", type="pdf", label_visibility="collapsed")

    if up and (ss.doc is None or ss.doc["key"] != (up.name, up.size)):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            f.write(up.getvalue())
            tmp = f.name
        try:
            with st.spinner("Reading and indexing your PDF…"):
                doc_id, n, existed = ingest_pdf(tmp, display_name=up.name)
            ss.doc = {"key": (up.name, up.size), "name": up.name, "id": doc_id, "chunks": n, "existed": existed}
            ss.messages = []
        except Exception as e:
            st.error(f"Could not process the PDF: {e}")
        finally:
            os.remove(tmp)

    if ss.doc:
        st.markdown(f'<div class="card">✅ <b>{html.escape(ss.doc["name"])}</b><br>'
                    f'<span style="color:#9AA4C7">{"Already indexed" if ss.doc["existed"] else str(ss.doc["chunks"]) + " chunks indexed"}'
                    f'</span></div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear chat", use_container_width=True):
            ss.messages = []
            st.rerun()

    st.markdown("---")
    st.markdown("**How it works**")
    for i, s in enumerate(["Upload a PDF", "Text is split into chunks and embedded",
                           "Best chunks are fetched from Pinecone", "Gemini answers only from those chunks"], 1):
        st.markdown(f'<div class="step">{i}. {s}</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Built by [Mithilesh Kumar](https://github.com/mithxcode) · Gemini · Pinecone · Streamlit")

# ---------- hero ----------
st.markdown('<div class="hero"><h1>PolicyGPT</h1>'
            '<p>Ask questions about any PDF and get answers with sources.</p></div>', unsafe_allow_html=True)


def render_answer(m):
    st.markdown(m["answer"])
    if m["sources"]:
        st.markdown("".join(f'<span class="chip">📎 {html.escape(s)}</span>' for s in m["sources"]),
                    unsafe_allow_html=True)
    c = m["confidence"]
    label = "High" if c >= 0.7 else "Medium" if c >= 0.5 else "Low"
    st.caption(f"Relevance: **{label}** ({c:.0%})")


# ---------- empty state ----------
if not ss.doc:
    st.markdown('<div class="card empty"><h3>👈 Upload a PDF to get started</h3>'
                '<span>Policies, reports, notes or papers. Text-based PDFs only (no scans).</span></div>',
                unsafe_allow_html=True)
    st.stop()

# ---------- suggestions ----------
pending = None
if not ss.messages:
    st.markdown("**Try asking:**")
    cols = st.columns(3)
    for col, q in zip(cols, ["Summarize this document", "What are the key points?", "List important dates or rules"]):
        if col.button(q, use_container_width=True):
            pending = q

# ---------- history ----------
for m in ss.messages:
    with st.chat_message(m["role"], avatar="🧑‍💻" if m["role"] == "user" else "🤖"):
        if m["role"] == "user":
            st.markdown(m["content"])
        else:
            render_answer(m)

# ---------- new question ----------
question = st.chat_input("Ask something about your PDF…") or pending
if question:
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(question)
    ss.messages.append({"role": "user", "content": question})
    with st.chat_message("assistant", avatar="🤖"):
        try:
            with st.spinner("Searching the document…"):
                r = answer_query(question, ss.doc["id"])
            msg = {"role": "assistant", **r}
            render_answer(msg)
            ss.messages.append(msg)
        except Exception as e:
            st.error(f"Something went wrong: {e}")