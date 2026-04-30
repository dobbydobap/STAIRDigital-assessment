"""Custom theme for the Streamlit UI.

Palette: "Monsoon" — deep midnight base with teal/amber accents and a
mustard citation chip. Designed to feel deliberate and not stock.

Usage:
    from pdfagent.ui.theme import apply_theme
    apply_theme()
"""
from __future__ import annotations

import streamlit as st

PALETTE = {
    "bg": "#0F1226",
    "surface": "#1B1F3A",
    "surface_2": "#252A4A",
    "border": "#2E3457",
    "text": "#E8EBFF",
    "muted": "#9FA6CC",
    "primary": "#34D1BF",
    "primary_hover": "#5CE2D2",
    "amber": "#F4B860",
    "success": "#7FC8A9",
    "danger": "#E26D5C",
    "citation_bg": "#F2D479",
    "citation_fg": "#0F1226",
}


_CSS = """
<style>
  :root {{
    --pdf-bg: {bg};
    --pdf-surface: {surface};
    --pdf-surface-2: {surface_2};
    --pdf-border: {border};
    --pdf-text: {text};
    --pdf-muted: {muted};
    --pdf-primary: {primary};
    --pdf-primary-hover: {primary_hover};
    --pdf-amber: {amber};
    --pdf-success: {success};
    --pdf-danger: {danger};
    --pdf-citation-bg: {citation_bg};
    --pdf-citation-fg: {citation_fg};
  }}

  html, body, [class*="stApp"] {{
    background: var(--pdf-bg) !important;
    color: var(--pdf-text) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  }}

  .block-container {{ padding-top: 1.4rem; padding-bottom: 4rem; max-width: 1100px; }}

  h1, h2, h3, h4 {{
    font-family: 'IBM Plex Serif', 'Georgia', serif !important;
    color: var(--pdf-text) !important;
    letter-spacing: -0.01em;
  }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{ background: var(--pdf-surface) !important; }}
  section[data-testid="stSidebar"] * {{ color: var(--pdf-text) !important; }}
  section[data-testid="stSidebar"] .stRadio label,
  section[data-testid="stSidebar"] .stSelectbox label {{ color: var(--pdf-muted) !important; }}

  /* Buttons */
  .stButton>button, .stDownloadButton>button {{
    background: var(--pdf-primary) !important;
    color: #0B1024 !important;
    border: none !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    padding: 0.45rem 1.1rem !important;
    transition: background 0.15s ease;
  }}
  .stButton>button:hover, .stDownloadButton>button:hover {{
    background: var(--pdf-primary-hover) !important;
  }}

  /* File uploader */
  [data-testid="stFileUploader"] section {{
    background: var(--pdf-surface-2) !important;
    border: 1px dashed var(--pdf-border) !important;
    border-radius: 14px !important;
  }}

  /* Chat input */
  [data-testid="stChatInput"] textarea {{
    background: var(--pdf-surface-2) !important;
    color: var(--pdf-text) !important;
    border: 1px solid var(--pdf-border) !important;
  }}

  /* Chat messages */
  [data-testid="stChatMessage"] {{
    background: var(--pdf-surface) !important;
    border: 1px solid var(--pdf-border) !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
  }}

  /* Expanders */
  details, .streamlit-expanderHeader {{
    background: var(--pdf-surface) !important;
    border: 1px solid var(--pdf-border) !important;
    border-radius: 12px !important;
  }}

  /* Inline citation chip */
  .pdf-cite {{
    display: inline-block;
    background: var(--pdf-citation-bg);
    color: var(--pdf-citation-fg);
    padding: 1px 8px;
    border-radius: 999px;
    font-size: 0.78em;
    font-weight: 600;
    margin: 0 2px;
    text-decoration: none;
    border: 1px solid #d4b659;
  }}

  /* Status pills */
  .pdf-pill {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    margin-right: 6px;
  }}
  .pdf-pill-ok      {{ background: rgba(127,200,169,0.16); color: var(--pdf-success); border: 1px solid rgba(127,200,169,0.4); }}
  .pdf-pill-warn    {{ background: rgba(244,184,96,0.16);  color: var(--pdf-amber);   border: 1px solid rgba(244,184,96,0.4); }}
  .pdf-pill-fail    {{ background: rgba(226,109,92,0.16);  color: var(--pdf-danger);  border: 1px solid rgba(226,109,92,0.4); }}
  .pdf-pill-info    {{ background: rgba(52,209,191,0.14);  color: var(--pdf-primary); border: 1px solid rgba(52,209,191,0.35); }}

  /* Quote box for citation expanders */
  .pdf-quote {{
    background: var(--pdf-surface-2);
    border-left: 3px solid var(--pdf-amber);
    padding: 10px 14px;
    border-radius: 6px;
    color: var(--pdf-text);
    font-style: italic;
  }}

  /* Score bar */
  .pdf-score-bar {{
    height: 4px; border-radius: 999px;
    background: linear-gradient(90deg, var(--pdf-primary), var(--pdf-amber));
  }}

  /* Tables */
  thead tr th {{ background: var(--pdf-surface-2) !important; color: var(--pdf-text) !important; }}
  tbody tr td {{ background: var(--pdf-surface) !important; color: var(--pdf-text) !important; }}

  /* Hide default streamlit footer/menu */
  #MainMenu {{ visibility: hidden; }}
  footer {{ visibility: hidden; }}

  /* Subtle hr */
  hr {{ border-color: var(--pdf-border) !important; }}

  /* Code */
  code {{ background: var(--pdf-surface-2) !important; color: var(--pdf-amber) !important; padding: 2px 6px; border-radius: 4px; }}
</style>
""".format(**PALETTE)


def apply_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def pill(label: str, kind: str = "info") -> str:
    cls = {
        "ok": "pdf-pill-ok",
        "warn": "pdf-pill-warn",
        "fail": "pdf-pill-fail",
        "info": "pdf-pill-info",
    }.get(kind, "pdf-pill-info")
    return f'<span class="pdf-pill {cls}">{label}</span>'
