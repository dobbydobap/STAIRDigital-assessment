"""Main Streamlit app — chat UI, eval page, traces page.

Calls the `pdfagent.service` module directly (no separate API process) so
the deploy story is one process. The FastAPI app is also available for
programmatic clients but isn't required by the UI.

Color palette: see pdfagent.ui.theme.PALETTE ("Aurora") — soft lavender +
pink gradients on a warm-white background, with a hero gradient orb on
the empty state.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

# `pip install -e .` only installs the `pdfagent` package; `eval/` is
# top-level (test data + runner) so we add the project root to sys.path
# before any `from eval.*` imports so the live Eval page can run the
# CLI suite.
_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import streamlit as st

from pdfagent.config import CONFIG  # noqa: F401  (forces dirs to exist)
from pdfagent.orchestrator import to_dict
from pdfagent.registry import PdfRecord, get_registry
from pdfagent.service import chat as svc_chat, ingest_and_index
from pdfagent.trace.logger import read_traces
from pdfagent.ui.eval_page import render_eval_page
from pdfagent.ui.pdf_viewer import page_image_path
from pdfagent.ui.theme import (
    apply_theme,
    brand_row,
    hero_orb_html,
    pill,
    side_section,
)

st.set_page_config(
    page_title="pdfagent · grounded chat",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()


# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

def _init_state() -> None:
    st.session_state.setdefault("active_pdf_id", None)
    st.session_state.setdefault("history", [])      # [{role, content}]
    st.session_state.setdefault("turns", [])        # list of TurnResult dicts
    st.session_state.setdefault("page", "Chat")
    st.session_state.setdefault("queued_query", None)


_init_state()


SUGGESTIONS = [
    {
        "icon": "📄",
        "title": "What is this document about?",
        "body": "Get a grounded summary with citations.",
        "query": "Briefly summarize what this document is about.",
    },
    {
        "icon": "🧭",
        "title": "What are the main sections?",
        "body": "Pulls structure from headings across pages.",
        "query": "What are the main sections, chapters, or topics covered in this document?",
    },
    {
        "icon": "✍️",
        "title": "Who authored this?",
        "body": "Front-matter / colophon lookup.",
        "query": "Who authored, prepared, or published this document?",
    },
    {
        "icon": "🌐",
        "title": "Try a Hindi question",
        "body": "Cross-lingual retrieval, Hindi answer with English-source citations.",
        "query": "इस दस्तावेज़ का मुख्य विषय क्या है?",
    },
]


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(brand_row("pdfagent", "Grounded PDF chat"), unsafe_allow_html=True)

        if st.button("＋ New chat", use_container_width=True):
            st.session_state.history = []
            st.session_state.turns = []
            st.session_state.queued_query = None
            st.rerun()

        st.markdown(side_section("View"), unsafe_allow_html=True)
        st.session_state.page = st.radio(
            "View",
            options=["Chat", "Eval", "Traces"],
            horizontal=True,
            label_visibility="collapsed",
            index=["Chat", "Eval", "Traces"].index(st.session_state.page),
        )

        st.markdown(side_section("Upload"), unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Drop a PDF",
            type=["pdf"],
            label_visibility="collapsed",
            help="Drag a PDF here or click to browse.",
        )
        if uploaded is not None:
            with st.spinner("Ingesting & indexing…"):
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(uploaded.getvalue())
                    tmp_path = Path(tmp.name)
                try:
                    rec = ingest_and_index(tmp_path, original_filename=uploaded.name)
                finally:
                    try:
                        tmp_path.unlink(missing_ok=True)
                    except Exception:
                        pass
            st.success(f"Indexed `{rec.original_filename}` ({rec.num_pages} pages).")
            st.session_state.active_pdf_id = rec.pdf_id
            st.session_state.history = []
            st.session_state.turns = []

        st.markdown(side_section("Indexed PDFs"), unsafe_allow_html=True)
        records = get_registry().list_records()
        if not records:
            st.caption("No PDFs yet.")
        else:
            options = [f"{r.original_filename} · {r.num_pages}p" for r in records]
            current_idx = 0
            if st.session_state.active_pdf_id:
                for i, r in enumerate(records):
                    if r.pdf_id == st.session_state.active_pdf_id:
                        current_idx = i
                        break
            choice = st.selectbox(
                "Active PDF",
                options=options,
                index=current_idx,
                label_visibility="collapsed",
            )
            chosen = records[options.index(choice)]
            if chosen.pdf_id != st.session_state.active_pdf_id:
                st.session_state.active_pdf_id = chosen.pdf_id
                st.session_state.history = []
                st.session_state.turns = []

            chips = []
            if chosen.has_tables:
                chips.append(pill("tables", "info"))
            if chosen.has_ocr:
                chips.append(pill("ocr", "warn"))
            if chips:
                st.markdown(" ".join(chips), unsafe_allow_html=True)

        st.markdown("---")
        st.caption(
            "Llama 3.3 70B + 3.1 8B Instant on Groq · "
            "BAAI/bge-m3 multilingual embeddings · free tier."
        )


# ---------------------------------------------------------------------------
# Chat page
# ---------------------------------------------------------------------------

_CITE_PATTERN = re.compile(r"\[p\.\s*(\d+)([^\]]*)\]")


def _annotate_with_chips(text: str) -> str:
    return _CITE_PATTERN.sub(lambda m: f'<span class="pdf-cite">p.{m.group(1)}</span>', text or "")


def _render_citations_block(turn: dict) -> None:
    citations = turn.get("answer", {}).get("citations", [])
    verification = turn.get("verification", {})
    if not citations:
        return

    st.markdown("**Citations**")
    checks_by_page: dict[int, dict] = {c.get("page"): c for c in (verification.get("checks") or [])}
    pdf_id = turn.get("pdf_id")

    for c in citations:
        pg = c.get("page")
        section = c.get("section") or "—"
        quote = c.get("quoted_span") or ""
        chk = checks_by_page.get(pg, {})
        ok = chk.get("ok", True)
        label = f"p.{pg} · §{section} · " + ("verified ✓" if ok else "unverified ✗")
        with st.expander(label, expanded=False):
            st.markdown(f'<div class="pdf-quote">{quote}</div>', unsafe_allow_html=True)
            img = page_image_path(pdf_id, pg) if pdf_id else None
            if img:
                st.image(str(img), caption=f"page {pg}", use_container_width=True)
            else:
                st.caption("(page preview not cached — re-upload to regenerate)")
            if not ok:
                st.error(chk.get("reason", "verification failed"))


def _render_meta_block(turn: dict) -> None:
    ans = turn.get("answer", {})
    rw = turn.get("rewrite", {})
    cs = turn.get("cost_summary", {})
    lat = turn.get("latency_ms", {})

    pills = []
    scope = ans.get("scope", "in_scope")
    suff = ans.get("sufficiency", "insufficient")
    pills.append(pill(scope.replace("_", " "), "ok" if scope == "in_scope" else "warn"))
    pills.append(pill(
        suff,
        {"sufficient": "ok", "partial": "warn", "insufficient": "fail", "contradictory": "warn"}.get(suff, "info"),
    ))
    pills.append(pill(f"lang {rw.get('language', '?')}", "info"))
    v = turn.get("verification", {})
    if v.get("checks"):
        pills.append(pill("verified ✓" if v.get("ok") else "verifier ✗", "ok" if v.get("ok") else "fail"))
    st.markdown(" ".join(pills), unsafe_allow_html=True)
    st.caption(
        f"latency: rewrite {lat.get('rewrite_ms', 0):.0f}ms · "
        f"retrieve {lat.get('retrieve_ms', 0):.0f}ms · "
        f"answer {lat.get('answer_ms', 0):.0f}ms · "
        f"total {lat.get('total_ms', 0):.0f}ms · "
        f"tokens in/out {cs.get('input_tokens', 0)}/{cs.get('output_tokens', 0)} · "
        f"~${cs.get('cost_usd', 0.0):.4f}"
    )


def _render_hero(rec: PdfRecord | None) -> None:
    if rec is None:
        st.markdown(
            hero_orb_html(
                "Hello there",
                "Upload a PDF to get started.",
            ),
            unsafe_allow_html=True,
        )
        return
    first_name = "there"
    st.markdown(
        hero_orb_html(
            f"Hello, {first_name}",
            "What would you like to ask about this document?",
        ),
        unsafe_allow_html=True,
    )

    # Suggestion cards (4 columns)
    cols = st.columns(4)
    for col, sug in zip(cols, SUGGESTIONS):
        with col:
            card_html = (
                f'<div class="pdf-card">'
                f'<div class="pdf-card-ico">{sug["icon"]}</div>'
                f'<div class="pdf-card-title">{sug["title"]}</div>'
                f'<div class="pdf-card-body">{sug["body"]}</div>'
                f'</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)
            if st.button("Use this prompt", key=f"sug_{sug['title']}", use_container_width=True):
                st.session_state.queued_query = sug["query"]
                st.rerun()


def _run_turn(rec: PdfRecord, prompt: str) -> None:
    """Run a chat turn — updates session_state only, no inline rendering.
    Caller is expected to st.rerun() so the new history renders cleanly."""
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.spinner("Thinking…"):
        try:
            turn = svc_chat(
                pdf_id=rec.pdf_id,
                query=prompt,
                history=st.session_state.history[:-1],
            )
        except Exception as e:
            st.session_state.history.pop()
            st.error(f"Error: {e}")
            return
    td = to_dict(turn)
    st.session_state.turns.append(td)
    ans = td.get("answer", {})
    body = ans.get("answer") or ans.get("refusal_reason") or "(no response)"
    st.session_state.history.append({"role": "assistant", "content": body})


def render_chat_page() -> None:
    rec: PdfRecord | None = None
    if st.session_state.active_pdf_id:
        rec = get_registry().get(st.session_state.active_pdf_id)

    # Process a queued suggestion-card query BEFORE deciding hero vs history,
    # so the page redraws once cleanly with the new turn.
    if st.session_state.queued_query is not None and rec is not None:
        prompt = st.session_state.queued_query
        st.session_state.queued_query = None
        _run_turn(rec, prompt)
        st.rerun()

    # Empty state — show hero + suggestions
    if not st.session_state.history:
        _render_hero(rec)
    elif rec is not None:
        st.markdown(
            f'<div class="pdf-doc-card"><div class="pdf-doc-name">📄 {rec.original_filename}</div>'
            f'<div class="pdf-doc-meta">{rec.num_pages} pages · pdf_id <code>{rec.pdf_id[:10]}…</code></div></div>',
            unsafe_allow_html=True,
        )

    # Replay history
    for i, msg in enumerate(st.session_state.history):
        with st.chat_message(msg["role"]):
            content_html = _annotate_with_chips(msg["content"])
            st.markdown(content_html, unsafe_allow_html=True)
            if msg["role"] == "assistant" and i // 2 < len(st.session_state.turns):
                turn = st.session_state.turns[i // 2]
                _render_meta_block(turn)
                _render_citations_block(turn)

    # Chat input — also goes through _run_turn + rerun for one clean redraw
    placeholder = (
        "Ask anything about this PDF…" if rec is not None else "Upload a PDF in the sidebar to start chatting."
    )
    prompt = st.chat_input(placeholder, disabled=(rec is None))
    if prompt and rec is not None:
        _run_turn(rec, prompt)
        st.rerun()


# ---------------------------------------------------------------------------
# Traces page
# ---------------------------------------------------------------------------

def render_traces_page() -> None:
    st.markdown("## Traces")
    st.caption("Every chat turn writes a JSONL record with retrieval scores, verifier verdict, latency, and tokens.")

    n = st.slider("How many traces", min_value=5, max_value=200, value=25, step=5)
    traces = read_traces(limit=n)
    if not traces:
        st.info("No traces yet. Run a chat turn first.")
        return

    for t in traces:
        ans = t.get("answer", {})
        rw = t.get("rewrite", {})
        v = t.get("verification", {})
        title = f"{t.get('logged_at', '')[:19]} · {ans.get('scope', '?')}/{ans.get('sufficiency', '?')} · {t.get('query', '')[:60]}"
        with st.expander(title):
            st.markdown(
                pill(ans.get("scope", "?"), "ok" if ans.get("scope") == "in_scope" else "warn") +
                pill(ans.get("sufficiency", "?"), {
                    "sufficient": "ok", "partial": "warn", "insufficient": "fail",
                    "contradictory": "warn",
                }.get(ans.get("sufficiency", ""), "info")) +
                (pill("verified ✓" if v.get("ok") else "verifier ✗", "ok" if v.get("ok") else "fail")
                 if v.get("checks") else ""),
                unsafe_allow_html=True,
            )
            st.write(f"**Query:** {t.get('query')}")
            if rw.get("rewritten") and rw["rewritten"] != t.get("query"):
                st.write(f"**Rewritten:** {rw['rewritten']}")
            if rw.get("subqueries"):
                st.write(f"**Subqueries:** {', '.join(rw['subqueries'])}")
            if ans.get("answer"):
                st.markdown("**Answer:**")
                st.write(ans["answer"])
            if ans.get("refusal_reason"):
                st.markdown("**Refusal:**")
                st.write(ans["refusal_reason"])
            retr = t.get("retrieved", [])
            if retr:
                st.markdown("**Retrieval (top-k):**")
                st.dataframe(
                    [
                        {
                            "page": r["page"],
                            "section": r["section"][:48],
                            "type": r["type"],
                            "dense": r["dense"],
                            "sparse": r["sparse"],
                            "combined": r["combined"],
                        }
                        for r in retr
                    ],
                    hide_index=True,
                    use_container_width=True,
                )
            with st.popover("Raw JSON"):
                st.code(json.dumps(t, ensure_ascii=False, indent=2), language="json")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    render_sidebar()
    page = st.session_state.page
    if page == "Chat":
        render_chat_page()
    elif page == "Eval":
        render_eval_page()
    elif page == "Traces":
        render_traces_page()


main()
