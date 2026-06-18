"""
Multimodal RAG  ·  Streamlit UI
================================
Production-ready single-file frontend for the MultimodalRAG backend.

Run:
    streamlit run streamlit.py

Secrets (create .streamlit/secrets.toml or set in Streamlit Cloud):
    GROQ_API_KEY = "gsk_..."
"""

import os
import tempfile
import time
import shutil
from collections import defaultdict

import streamlit as st

from download_models import download_prerequisites

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  ·  must be the very first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Multimodal RAG",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── reset & base ─────────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

[data-testid="stAppViewContainer"]          { background: #080c14; }
[data-testid="stMainBlockContainer"]        { padding: 1.75rem 2.25rem 3rem; max-width: 900px; }
[data-testid="stSidebar"]                  { background: #0d1120; border-right: 1px solid #1a1f35; }
[data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1rem; }
section[data-testid="stSidebar"] hr        { border-color: #1a1f35; margin: 0.75rem 0; }

/* hide the built-in hamburger / header */
#MainMenu, header[data-testid="stHeader"], footer { display: none; }

/* ── sidebar brand ─────────────────────────────────────────────────────────── */
.sb-brand {
    display: flex; align-items: center; gap: 0.65rem;
    padding: 0 0.25rem 1.25rem; border-bottom: 1px solid #1a1f35;
    margin-bottom: 1rem;
}
.sb-brand-icon { font-size: 1.7rem; line-height: 1; }
.sb-brand-name {
    font-size: 1.05rem; font-weight: 700;
    color: #c7cde8; letter-spacing: -0.01em; line-height: 1.2;
}
.sb-brand-tagline {
    font-size: 0.68rem; color: #3d4565;
    text-transform: uppercase; letter-spacing: 0.08em;
}

/* ── sidebar nav ───────────────────────────────────────────────────────────── */
[data-testid="stRadio"] label {
    display: flex !important; align-items: center;
    gap: 0.5rem; padding: 0.55rem 0.75rem;
    border-radius: 8px; cursor: pointer;
    font-size: 0.88rem; font-weight: 500;
    color: #5c6690; transition: background 0.15s, color 0.15s;
}
[data-testid="stRadio"] label:hover { background: #131929; color: #a0a8cc; }
[data-testid="stRadio"] [aria-checked="true"] + label,
[data-testid="stRadio"] label[data-checked="true"] {
    background: #161f38; color: #818cf8;
}
[data-testid="stRadio"] > div { gap: 0.2rem; }
[data-testid="stRadio"] [data-baseweb="radio"] { display: none; }

/* ── sidebar stat cards ────────────────────────────────────────────────────── */
.sb-stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.4rem; margin-top: 0.5rem; }
.sb-stat {
    background: #0f1525; border: 1px solid #1a1f35; border-radius: 8px;
    padding: 0.5rem 0.65rem;
}
.sb-stat-val { font-size: 1.1rem; font-weight: 700; color: #a5b4fc; }
.sb-stat-lbl { font-size: 0.67rem; color: #3d4565; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.05rem; }
.sb-badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    background: #0f1525; border: 1px solid #1a1f35; border-radius: 6px;
    padding: 0.25rem 0.6rem; font-size: 0.72rem; color: #5c6690;
    margin-top: 0.3rem; width: 100%;
}
.sb-badge strong { color: #818cf8; }

/* ── status dot ────────────────────────────────────────────────────────────── */
.dot {
    width: 7px; height: 7px; border-radius: 50%; display: inline-block;
    flex-shrink: 0;
}
.dot-green { background: #34d399; box-shadow: 0 0 5px #34d39955; }
.dot-amber { background: #fbbf24; box-shadow: 0 0 5px #fbbf2455; }

/* ── page heading ──────────────────────────────────────────────────────────── */
.page-heading {
    font-size: 1.35rem; font-weight: 700;
    color: #d4d8f0; letter-spacing: -0.02em;
    margin-bottom: 0.2rem;
}
.page-subheading {
    font-size: 0.8rem; color: #3d4565;
    text-transform: uppercase; letter-spacing: 0.07em;
    margin-bottom: 1.5rem;
}

/* ── section header ────────────────────────────────────────────────────────── */
.section-hdr {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.1em; color: #3d4565;
    margin: 1.8rem 0 0.75rem; padding-bottom: 0.4rem;
    border-bottom: 1px solid #1a1f35;
}

/* ── chat bubbles ──────────────────────────────────────────────────────────── */
.bubble-wrap { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1rem; }

.msg-user {
    align-self: flex-end; max-width: 76%;
    background: #161f38; border: 1px solid #1e2a4a;
    border-radius: 16px 16px 4px 16px;
    padding: 0.8rem 1.05rem;
    color: #c7cde8; font-size: 0.9rem; line-height: 1.65;
}
.msg-user-label {
    font-size: 0.68rem; text-align: right;
    color: #3d4565; margin-bottom: 0.15rem;
    text-transform: uppercase; letter-spacing: 0.06em;
}

.msg-ai {
    align-self: flex-start; max-width: 86%;
    background: #0d1120; border: 1px solid #1a1f35;
    border-radius: 4px 16px 16px 16px;
    padding: 0.8rem 1.05rem;
    color: #dde1f5; font-size: 0.9rem; line-height: 1.7;
}
.msg-ai-label {
    font-size: 0.68rem; color: #818cf8;
    margin-bottom: 0.15rem;
    text-transform: uppercase; letter-spacing: 0.06em;
}

/* ── source citations ───────────────────────────────────────────────────────── */
.citation-wrap { margin-top: 0.6rem; }
.citation-title {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: #3d4565; margin-bottom: 0.4rem;
}
.citation-card {
    background: #0f1525; border: 1px solid #1a2035;
    border-left: 3px solid #818cf8; border-radius: 8px;
    padding: 0.6rem 0.9rem; margin-bottom: 0.35rem;
}
.citation-doc { font-size: 0.8rem; font-weight: 600; color: #a5b4fc; margin-bottom: 0.3rem; }
.pill {
    display: inline-block;
    background: #141b30; border: 1px solid #232d4a;
    border-radius: 20px; padding: 0.1rem 0.55rem;
    font-size: 0.7rem; color: #6472a8; margin: 0 0.15rem 0.15rem 0;
}
.citation-snippet {
    font-size: 0.76rem; color: #4a5278;
    margin-top: 0.4rem; line-height: 1.55;
    font-style: italic;
}

/* ── doc rows ───────────────────────────────────────────────────────────────── */
.doc-row {
    background: #0d1120; border: 1px solid #1a1f35; border-radius: 10px;
    padding: 0.75rem 1rem; margin-bottom: 0.4rem;
    display: flex; align-items: center; gap: 0.75rem;
}
.doc-row-name { flex: 1; color: #c7cde8; font-size: 0.87rem; font-weight: 600; }
.chip {
    background: #131929; border: 1px solid #1e2545;
    border-radius: 6px; padding: 0.1rem 0.5rem;
    font-size: 0.72rem; color: #818cf8; white-space: nowrap;
}

/* ── metric grid ────────────────────────────────────────────────────────────── */
.metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin-bottom: 1rem; }
.metric-card {
    background: #0d1120; border: 1px solid #1a1f35; border-radius: 10px;
    padding: 0.85rem 1rem;
}
.metric-val { font-size: 1.65rem; font-weight: 700; color: #a5b4fc; }
.metric-lbl { font-size: 0.7rem; color: #3d4565; text-transform: uppercase; letter-spacing: 0.07em; }

/* ── empty state ────────────────────────────────────────────────────────────── */
.empty-state {
    text-align: center; padding: 3.5rem 1.5rem;
    border: 1px dashed #1a1f35; border-radius: 12px;
    margin: 1rem 0;
}
.empty-icon  { font-size: 2.8rem; margin-bottom: 0.75rem; }
.empty-title { font-size: 1rem; font-weight: 600; color: #3d4565; margin-bottom: 0.4rem; }
.empty-hint  { font-size: 0.82rem; color: #2a2f4a; }

/* ── config form ────────────────────────────────────────────────────────────── */
.config-card {
    background: #0d1120; border: 1px solid #1a1f35; border-radius: 12px;
    padding: 1.25rem 1.4rem; margin-bottom: 0.75rem;
}
.config-card-title {
    font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.09em; color: #5c6690; margin-bottom: 1rem;
}

/* ── danger zone ────────────────────────────────────────────────────────────── */
.danger-zone {
    background: #110810; border: 1px solid #2a1020;
    border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.5rem;
}
.danger-title {
    font-size: 0.7rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: #7f2040; margin-bottom: 0.6rem;
}

/* ── Streamlit overrides ────────────────────────────────────────────────────── */
div[data-testid="stExpander"] > details > summary {
    font-size: 0.82rem; color: #5c6690;
}
div[data-testid="stExpander"] > details > summary:hover { color: #818cf8; }
div[data-testid="metric-container"] {
    background: #0d1120 !important; border: 1px solid #1a1f35 !important;
    border-radius: 10px !important;
}
.stButton > button {
    border-radius: 8px !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f56d6, #818cf8) !important;
    border: none !important; color: #fff !important;
}
.stButton > button[kind="secondary"] {
    background: #0d1120 !important;
    border: 1px solid #1e2545 !important;
    color: #818cf8 !important;
}
[data-testid="stFileUploader"] {
    background: #0d1120 !important; border: 1px dashed #1e2545 !important;
    border-radius: 10px !important;
}
div[data-baseweb="select"] { background: #0d1120 !important; }

/* ── Streamlit tab styling ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    display: flex;
    width: 100%;
    gap: 0;
}

.stTabs [data-baseweb="tab"] {
    flex: 1;
    justify-content: center;
    text-align: center;
    min-height: 46px;
}

.stTabs [data-baseweb="tab"] p {
    font-size: 0.88rem;
    font-weight: 500;
}
</style>
""",
    unsafe_allow_html=True,
)



# ─────────────────────────────────────────────────────────────────────────────
# SECRETS  ·  inject GROQ_API_KEY into environment from st.secrets
# ─────────────────────────────────────────────────────────────────────────────
# ── Groq API key — fail early with a clear message ──
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "**GROQ_API_KEY not found.**\n\n"
        "Add it to your Streamlit secrets:\n"
        "```\nGROQ_API_KEY = 'your-key-here'\n```\n"
        "In Streamlit Cloud go to **Settings → Secrets**."
    )
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# BACKEND  ·  cached singleton
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _load_rag():
    """
    Initialise MultimodalRAG exactly once per interpreter lifetime.
    st.cache_resource keeps the object alive across reruns and users.
    """
    try:
        from multimodal_RAG.multimodal_rag import MultimodalRAG
        rag = MultimodalRAG(GROQ_API_KEY=GROQ_API_KEY)
    
    except:
        import traceback
        print(traceback.format_exc())
        raise

    return rag


def get_rag():
    """Return the cached RAG singleton; halt with a friendly error on failure."""
    try:
        return _load_rag()
    except Exception as exc:
        st.error(f"⚠️ Backend failed to load: {exc}")
        st.stop()


def refresh_rag():
    st.cache_resource.clear()
    return get_rag()

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE  ·  defaults initialised once per browser session
# ─────────────────────────────────────────────────────────────────────────────
_SS_DEFAULTS: dict = {
    "page":               "💬  Chat",      # current sidebar nav selection
    "messages":           [],              # [{role, content, sources}]
    "clear_chat_confirm": False,
    "reset_kb_confirm":   False,
    "reset_cfg_confirm":  False,
    "del_confirm":        False,
    "del_target":         None,
}

for _k, _v in _SS_DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


# ─────────────────────────────────────────────────────────────────────────────
# UTILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def _doc_names(rag):
    try:
        return list(rag.mapper.get_documents()) or []
    except Exception:
        return []

def _doc_info(rag):
    try:
        info = rag.mapper.get_documents_info()
        print("\ninfo : ", info, "\n")
        if not info:
            return []
        return info
    except Exception:
        return []

def _cfg(rag) -> dict:
    try:
        c = rag.get_config()
        return c if isinstance(c, dict) else {}
    except Exception:
        return {}


def _has_docs(rag) -> bool:
    return bool(_doc_names(rag))


def _chips_html(doc: dict) -> str:
    mapping = [
        ("total_pages", "📑", "pages"),
        ("total_chunks", "🧩", "chunks"),
        ("total_sections", "📚", "sections"),
        ("total_figures", "🖼️", "figures"),
        ("total_tables", "📊", "tables"),
        ("total_formulas", "∑", "formulas"),
    ]
    out = ""
    for key, icon, label in mapping:
        val = doc.get(key)
        if val is not None:
            out += f'<span class="chip">{icon} {val} {label}</span>'
    return out


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar(rag) -> str:
    """Render the sidebar and return the selected page name."""

    with st.sidebar:

        # ── brand ──────────────────────────────────────────────────────────
        st.markdown(
            """
            <div class="sb-brand">
                <div class="sb-brand-icon">🔍</div>
                <div>
                    <div class="sb-brand-name">Multimodal RAG</div>
                    <div class="sb-brand-tagline">Document Intelligence</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── nav radio ──────────────────────────────────────────────────────
        page = st.radio(
            "Navigation",
            options=["💬  Chat", "⚙️  Configurations"],
            index=["💬  Chat", "⚙️  Configurations"].index(
                st.session_state.page
            ),
            label_visibility="collapsed",
        )
        st.session_state.page = page

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── live stats ─────────────────────────────────────────────────────
        kb_ready   = _has_docs(rag)
        docs       = _doc_info(rag)
        cfg        = _cfg(rag)
        n_docs     = len(docs)
        n_pages    = sum(d.get("total_pages", 0) for d in docs)

        dot_cls  = "dot-green" if kb_ready else "dot-amber"
        kb_label = "Ready" if kb_ready else "Empty"

        st.markdown(
            f"""
            <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.09em;color:#3d4565;margin-bottom:0.5rem;">
                Knowledge Base
            </div>
            <div class="sb-badge">
                <span class="dot {dot_cls}"></span>
                <span>{kb_label} — <strong>{n_docs}</strong> doc{'s' if n_docs!=1 else ''}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="sb-stat-grid" style="margin-top:0.5rem">
                <div class="sb-stat">
                    <div class="sb-stat-val">{n_docs}</div>
                    <div class="sb-stat-lbl">Docs</div>
                </div>
                <div class="sb-stat">
                    <div class="sb-stat-val">{n_pages}</div>
                    <div class="sb-stat-lbl">Pages</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        retrieval_mode = cfg.get("retrieval_type", "—")
        response_mode  = cfg.get("response_mode", "—")

        st.markdown(
            f"""
            <div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;
                        letter-spacing:0.09em;color:#3d4565;margin-bottom:0.5rem;">
                Active Config
            </div>
            <div class="sb-badge">🔎 Retrieval: <strong>{retrieval_mode}</strong></div>
            <div class="sb-badge" style="margin-top:0.3rem">
                💬 Response: <strong>{response_mode}</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return page


# ─────────────────────────────────────────────────────────────────────────────
# CHAT PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_chat(rag) -> None:
    kb_ready = _has_docs(rag)

    st.markdown(
        '<div class="page-heading">💬 Chat</div>'
        '<div class="page-subheading">Ask questions about your indexed documents</div>',
        unsafe_allow_html=True,
    )

    # ── empty-KB guard ─────────────────────────────────────────────────────
    if not kb_ready:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">📂</div>
                <div class="empty-title">No documents indexed yet</div>
                <div class="empty-hint">
                    Go to <strong>⚙️ Configurations → Knowledge Base</strong> to upload
                    and process your documents before chatting.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── message history ────────────────────────────────────────────────────
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">💭</div>
                <div class="empty-title">Start a conversation</div>
                <div class="empty-hint">Your documents are indexed and ready. Ask anything.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(
                    f"""
                    <div class="bubble-wrap">
                        <div class="msg-user-label">You</div>
                        <div class="msg-user">{msg["content"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="bubble-wrap">
                        <div class="msg-ai-label">🔍 Assistant</div>
                        <div class="msg-ai">{msg["content"]}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                # Render source citations
                sources = msg.get("sources", [])
                if sources:
                    _render_citations(sources)

    # ── clear chat button ──────────────────────────────────────────────────
    if st.session_state.messages:
        col_gap, col_btn = st.columns([6, 1])
        with col_btn:
            if st.button("🗑 Clear", use_container_width=True):
                st.session_state.clear_chat_confirm = True
                st.rerun()

    if st.session_state.clear_chat_confirm:
        st.warning("Clear all conversation history? This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, clear", use_container_width=True, key="chat_clr_yes"):
                try:
                    rag.clear_history()
                except Exception:
                    pass
                st.session_state.messages = []
                st.session_state.clear_chat_confirm = False
                st.rerun()
        with c2:
            if st.button("❌ Cancel", use_container_width=True, key="chat_clr_no"):
                st.session_state.clear_chat_confirm = False
                st.rerun()

    # ── chat input ─────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask a question about your documents…")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Generating response…"):
            try:
                result  = rag.ask(user_input)
                answer  = result.get("answer", str(result)) if isinstance(result, dict) else str(result)
                sources = result.get("sources", []) if isinstance(result, dict) else []
            except Exception as exc:
                answer  = f"⚠️ Error: {exc}"
                sources = []

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "sources": sources}
        )
        st.rerun()


def _render_citations(sources: list) -> None:
    """Group sources by document and render elegant citation cards."""
    grouped: dict[str, list] = defaultdict(list)
    for s in sources:
        doc = s.get("document_name") or s.get("document") or "Unknown Source"
        grouped[doc].append(s)

    with st.expander(f"📎 {len(sources)} source{'s' if len(sources)!=1 else ''} cited", expanded=False):
        for doc_name, chunks in grouped.items():
            for chunk in chunks:
                pills = ""
                if chunk.get("page_number") is not None:
                    pills += f'<span class="pill">Page {chunk["page_number"]}</span>'
                if chunk.get("section_title"):
                    pills += f'<span class="pill">§ {chunk["section_title"]}</span>'
                ct = chunk.get("chunk_type", "")
                if ct:
                    icon = {"figure": "🖼️", "table": "📊", "formula": "∑"}.get(ct, "📝")
                    pills += f'<span class="pill">{icon} {ct.capitalize()}</span>'

                raw = chunk.get("content") or chunk.get("text") or ""
                snippet = (raw[:200] + "…") if len(raw) > 200 else raw
                snippet_html = (
                    f'<div class="citation-snippet">{snippet}</div>'
                    if snippet else ""
                )

                st.markdown(
                    f"""
                    <div class="citation-card">
                        <div class="citation-doc">📄 {doc_name}</div>
                        <div>{pills}</div>
                        {snippet_html}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATIONS PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_configurations(rag) -> None:

    st.markdown(
        '<div class="page-heading">⚙️ Configurations</div>'
        '<div class="page-subheading">Manage documents, retrieval settings, and system controls</div>',
        unsafe_allow_html=True,
    )

    # ── inner tabs ─────────────────────────────────────────────────────────
    t_kb, t_docs, t_runtime, t_danger = st.tabs(
        ["📁  Knowledge Base", "📚  Documents", "🛠️  Runtime Config", "⚠️  Danger Zone"]
    )

    # ╔═══════════════════════════════════════════════════════════════════════
    # ║  Knowledge Base  –  Upload
    # ╚═══════════════════════════════════════════════════════════════════════
    with t_kb:

        st.markdown('<div class="section-hdr">Upload Documents</div>', unsafe_allow_html=True)

        mode = st.radio(
            "Upload mode",
            ["Single document", "Multiple documents"],
            horizontal=True,
            label_visibility="collapsed",
        )

        files = st.file_uploader(
            "Drop files here",
            type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
            accept_multiple_files=(mode == "Multiple documents"),
            label_visibility="collapsed",
        )

        # Normalise to list
        if files is None:
            file_list = []
        elif isinstance(files, list):
            file_list = files
        else:
            file_list = [files]

        if file_list:
            st.markdown(
                f"<small style='color:#5c6690'>{len(file_list)} file(s) selected</small>",
                unsafe_allow_html=True,
            )
            if st.button("⚡ Index Documents", type="primary", use_container_width=True):
                prog = st.progress(0, text="Preparing…")
                tmp_paths, errors = [], []

                upload_dir = tempfile.mkdtemp()

                try:
                    for i, f in enumerate(file_list):
                        file_path = os.path.join(upload_dir, f.name)
                        with open(file_path, "wb") as tmp:
                            tmp.write(f.read())
                        tmp_paths.append(file_path)
                        prog.progress(int((i + 1) / len(file_list) * 25), text=f"Saved {f.name}")

                    for idx, file_path in enumerate(tmp_paths):
                        filename = os.path.basename(file_path)

                        pct = 25 + int((idx + 1) / len(tmp_paths) * 70)
                        prog.progress(pct, text=f"Processing {filename}…")

                        try:
                            rag.process_document(file_path)
                        except Exception as exc:
                            errors.append((filename, str(exc)))
                        
                finally:
                    # cleanup after all documents
                    shutil.rmtree(upload_dir, ignore_errors=True)

                prog.progress(100, text="Done!")
                time.sleep(0.35)
                prog.empty()

                for name, err in errors:
                    st.error(f"❌ **{name}**: {err}")

                ok = len(tmp_paths) - len(errors)
                if ok:
                    st.success(f"✅ {ok} document{'s' if ok>1 else ''} indexed successfully.")

                    # Reload RAG instance
                    st.cache_resource.clear()
                
                st.cache_data.clear()
                st.rerun()

    # ╔═══════════════════════════════════════════════════════════════════════
    # ║  Documents  –  View & Delete
    # ╚═══════════════════════════════════════════════════════════════════════
    with t_docs:

        docs = _doc_info(rag)

        if not docs:
            st.markdown(
                """
                <div class="empty-state">
                    <div class="empty-icon">📭</div>
                    <div class="empty-title">No documents indexed</div>
                    <div class="empty-hint">Upload files in the Knowledge Base tab.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            # Aggregate metrics
            n_docs   = len(docs)
            n_pages = sum(d.get("total_pages", 0) for d in docs)
            n_chunks = sum(d.get("total_chunks", 0) for d in docs)

            st.markdown(
                f"""
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-val">{n_docs}</div>
                        <div class="metric-lbl">Documents</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-val">{n_pages}</div>
                        <div class="metric-lbl">Pages</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-val">{n_chunks}</div>
                        <div class="metric-lbl">Chunks</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown('<div class="section-hdr">Indexed Documents</div>', unsafe_allow_html=True)

            for doc in docs:
                name  = doc.get("document_name") or doc.get("name") or "—"
                chips = _chips_html(doc)
                st.markdown(
                    f"""
                    <div class="doc-row">
                        <span class="doc-row-name">📄 {name}</span>
                        {chips}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # ── Delete ─────────────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">Delete a Document</div>', unsafe_allow_html=True)

        names = _doc_names(rag)
        if not names:
            st.info("No documents to delete.", icon="ℹ️")
        else:
            col_sel, col_btn = st.columns([3, 1])
            with col_sel:
                choice = st.selectbox(
                    "Select document",
                    options=names,
                    label_visibility="collapsed",
                )
            with col_btn:
                if st.button("🗑 Delete", type="secondary", use_container_width=True):
                    st.session_state.del_confirm = True
                    st.session_state.del_target  = choice
                    st.rerun()

            if st.session_state.del_confirm and st.session_state.del_target:
                target = st.session_state.del_target
                st.warning(f"Delete **{target}** from the knowledge base?")
                d1, d2 = st.columns(2)
                with d1:
                    if st.button("✅ Yes, delete", use_container_width=True, key="del_yes"):
                        with st.spinner(f"Deleting {target}…"):
                            try:
                                rag.delete_document(target)
                                st.cache_data.clear()
                                st.success(f"✅ Deleted **{target}**.")
                            except Exception as exc:
                                st.error(f"❌ {exc}")
                        st.session_state.del_confirm = False
                        st.session_state.del_target  = None
                        # Reload RAG instance
                        st.cache_resource.clear()
                        st.rerun()
                with d2:
                    if st.button("❌ Cancel", use_container_width=True, key="del_no"):
                        st.session_state.del_confirm = False
                        st.session_state.del_target  = None
                        st.rerun()

    # ╔═══════════════════════════════════════════════════════════════════════
    # ║  Runtime Configuration
    # ╚═══════════════════════════════════════════════════════════════════════
    with t_runtime:

        cfg = _cfg(rag)

        # ── Conversation controls ───────────────────────────────────────────
        st.markdown('<div class="section-hdr">Conversation</div>', unsafe_allow_html=True)

        if st.button("🗑 Clear Conversation History", type="secondary"):
            st.session_state.clear_chat_confirm = True
            st.rerun()

        if st.session_state.clear_chat_confirm:
            st.warning("Clear all chat history from this session?")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("✅ Yes, clear", use_container_width=True, key="cfg_clr_yes"):
                    try:
                        rag.clear_history()
                    except Exception:
                        pass
                    st.session_state.messages = []
                    st.session_state.clear_chat_confirm = False
                    st.rerun()
            with cc2:
                if st.button("❌ Cancel", use_container_width=True, key="cfg_clr_no"):
                    st.session_state.clear_chat_confirm = False
                    st.rerun()

        # ── Retrieval settings ──────────────────────────────────────────────
        st.markdown('<div class="section-hdr">Retrieval & Response</div>', unsafe_allow_html=True)

        with st.form("runtime_cfg_form"):
            col_l, col_r = st.columns(2)

            with col_l:
                retrieval_type = st.selectbox(
                    "Retrieval type",
                    options=["dense", "sparse", "hybrid"],
                    index=["dense", "sparse", "hybrid"].index(
                        cfg.get("retrieval_type", "hybrid")
                    ),
                    help="dense = embedding · sparse = BM25 · hybrid = both",
                )
                response_mode = st.selectbox(
                    "Response mode",
                    options=["precise", "detailed"],
                    index=["precise", "detailed"].index(
                        cfg.get("response_mode", "detailed")
                    ),
                    help="precise = concise · detailed = in-depth",
                )
                enable_query_rewriting = st.toggle(
                    "Query rewriting",
                    value=bool(cfg.get("enable_query_rewriting", True)),
                    help="Automatically reformulate queries to improve retrieval.",
                )

            with col_r:
                retrieval_k = st.slider(
                    "Retrieval k",
                    1, 50,
                    int(cfg.get("retrieval_k", 20)),
                    help="Candidates fetched from the vector store.",
                )
                reranking_k = st.slider(
                    "Reranking k",
                    1, 30,
                    int(cfg.get("reranking_k", 10)),
                    help="Chunks kept after cross-encoder reranking.",
                )
                context_max_chunks = st.slider(
                    "Context chunks",
                    1, 20,
                    int(cfg.get("context_max_chunks", 5)),
                    help="Maximum chunks sent to the LLM as context.",
                )
                conv_history = st.number_input(
                    "Conversation history turns",
                    min_value=1, max_value=50,
                    value=int(cfg.get("conversation_max_history", 10)),
                    help="Number of previous Q&A turns included in each prompt.",
                )

            applied = st.form_submit_button(
                "💾 Apply Configuration", type="primary", use_container_width=True
            )

        if applied:
            new_cfg = {
                "retrieval_type":           retrieval_type,
                "response_mode":            response_mode,
                "enable_query_rewriting":   enable_query_rewriting,
                "retrieval_k":              retrieval_k,
                "reranking_k":              reranking_k,
                "context_max_chunks":       context_max_chunks,
                "conversation_max_history": int(conv_history),
            }
            try:
                rag.update_config(new_cfg)
                st.success("✅ Configuration saved.")
                time.sleep(0.5)
                st.rerun()
            except Exception as exc:
                st.error(f"❌ Could not save: {exc}")

    # ╔═══════════════════════════════════════════════════════════════════════
    # ║  Danger Zone
    # ╚═══════════════════════════════════════════════════════════════════════
    with t_danger:

        st.markdown('<div class="section-hdr">Irreversible Actions</div>', unsafe_allow_html=True)

        # ── Reset knowledge base ────────────────────────────────────────────
        st.markdown(
            """
            <div class="danger-zone">
                <div class="danger-title">⚠️ Reset Knowledge Base</div>
                <p style="font-size:0.83rem;color:#5c3050;margin:0 0 0.75rem">
                    Permanently deletes <strong>all indexed documents</strong> and clears
                    the vector store. This cannot be undone.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not st.session_state.reset_kb_confirm:
            if st.button("🔴 Reset Entire Knowledge Base", type="secondary"):
                st.session_state.reset_kb_confirm = True
                st.rerun()
        else:
            st.error("You are about to wipe the entire knowledge base. Are you sure?")
            r1, r2 = st.columns(2)
            with r1:
                if st.button("✅ Yes, wipe it", use_container_width=True, key="kb_rst_yes"):
                    with st.spinner("Resetting knowledge base…"):
                        try:
                            rag.reset_knowledge_base()
                            st.cache_data.clear()
                            refresh_rag()
                        except Exception as exc:
                            st.error(f"❌ {exc}")
                    st.session_state.reset_kb_confirm = False
                    st.rerun()
            with r2:
                if st.button("❌ Cancel", use_container_width=True, key="kb_rst_no"):
                    st.session_state.reset_kb_confirm = False
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Reset configuration ─────────────────────────────────────────────
        st.markdown(
            """
            <div class="danger-zone">
                <div class="danger-title">↩️ Reset Configuration to Default</div>
                <p style="font-size:0.83rem;color:#5c3050;margin:0 0 0.75rem">
                    Reverts all runtime settings (retrieval type, k values, response mode, etc.)
                    back to factory defaults.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if not st.session_state.reset_cfg_confirm:
            if st.button("↩️ Reset Configuration to Default", type="secondary"):
                st.session_state.reset_cfg_confirm = True
                st.rerun()
        else:
            st.warning("Reset all runtime config to factory defaults?")
            rc1, rc2 = st.columns(2)
            with rc1:
                if st.button("✅ Yes, reset config", use_container_width=True, key="cfg_rst_yes"):
                    with st.spinner("Resetting…"):
                        try:
                            rag.reset_config()
                            refresh_rag()
                            st.success("✅ Configuration reset.")
                        except Exception as exc:
                            st.error(f"❌ {exc}")
                    st.session_state.reset_cfg_confirm = False
                    st.rerun()
            with rc2:
                if st.button("❌ Cancel", use_container_width=True, key="cfg_rst_no"):
                    st.session_state.reset_cfg_confirm = False
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN  ·  wire sidebar + page routing
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    download_prerequisites()
    rag  = get_rag()
    page = render_sidebar(rag)

    if page == "💬  Chat":
        render_chat(rag)
    else:
        render_configurations(rag)


main()