"""Custom theme — "Aurora" palette.

A soft, light premium AI-assistant look: lavender / pink gradient accents
on a warm-white background, with a hero gradient orb on the empty state.
The whole palette and all component CSS lives here so it's easy to retune.
"""
from __future__ import annotations

import streamlit as st

PALETTE = {
    # Surfaces
    "bg":             "#FAF7FF",   # warm lavender-tinted off-white page
    "surface":        "#FFFFFF",   # cards / chat bubbles
    "surface_2":      "#F2EBFF",   # raised section panels
    "surface_3":      "#EBE2FF",   # deeper panel for sidebar groups
    "border":         "#E5DCFF",   # subtle lavender border
    "border_strong":  "#C9B8FF",
    # Text
    "text":           "#1A1429",   # near-black with purple undertone
    "text_secondary": "#6B6585",   # muted purple-grey
    "text_subtle":    "#9C95B5",
    # Brand
    "primary":        "#9B7BFF",   # core lavender
    "primary_dark":   "#6B5FE8",
    "primary_soft":   "#EFE7FF",
    "pink":           "#FF8FCF",
    "pink_soft":      "#FFE4F2",
    # Status
    "success":        "#4ED4A8",
    "success_soft":   "#E1F8EE",
    "amber":          "#FFB85C",
    "amber_soft":     "#FFF1DA",
    "danger":         "#FF6F91",
    "danger_soft":    "#FFE3EA",
    # Citation
    "citation_bg":    "#EFE7FF",
    "citation_fg":    "#4A2FBE",
}


_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');

  :root {{
    --bg: {bg};
    --surface: {surface};
    --surface-2: {surface_2};
    --surface-3: {surface_3};
    --border: {border};
    --border-strong: {border_strong};
    --text: {text};
    --text-2: {text_secondary};
    --text-3: {text_subtle};
    --primary: {primary};
    --primary-dark: {primary_dark};
    --primary-soft: {primary_soft};
    --pink: {pink};
    --pink-soft: {pink_soft};
    --success: {success};
    --success-soft: {success_soft};
    --amber: {amber};
    --amber-soft: {amber_soft};
    --danger: {danger};
    --danger-soft: {danger_soft};
    --cite-bg: {citation_bg};
    --cite-fg: {citation_fg};
    --shadow-sm: 0 2px 8px rgba(106, 86, 200, 0.06);
    --shadow:    0 6px 24px rgba(155, 123, 255, 0.12);
    --shadow-lg: 0 16px 48px rgba(155, 123, 255, 0.18);
    --radius: 16px;
    --radius-lg: 24px;
  }}

  /* ---------- Base ---------- */
  html, body, [class*="stApp"] {{
    background:
      radial-gradient(1200px 600px at 100% -10%, rgba(255,143,207,0.10), transparent 60%),
      radial-gradient(900px 600px at -10% 110%, rgba(155,123,255,0.10), transparent 60%),
      var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  }}
  .block-container {{ padding-top: 1.6rem !important; padding-bottom: 5rem !important; max-width: 1180px; }}

  h1, h2, h3, h4 {{
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
    color: var(--text) !important;
    letter-spacing: -0.025em;
    font-weight: 700 !important;
  }}
  h1 {{ font-size: 2.4rem !important; }}
  h2 {{ font-size: 1.7rem !important; }}
  h3 {{ font-size: 1.2rem !important; }}
  p, li, label, .stMarkdown {{ color: var(--text); }}
  small, .stCaption, [data-testid="stCaptionContainer"] {{ color: var(--text-3) !important; }}

  /* ---------- Sidebar ---------- */
  section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #FFFFFF 0%, #F7F2FF 100%) !important;
    border-right: 1px solid var(--border) !important;
  }}
  section[data-testid="stSidebar"] * {{ color: var(--text) !important; }}
  section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {{ display: none; }}
  section[data-testid="stSidebar"] hr {{ border-color: var(--border) !important; opacity: 0.6; }}
  section[data-testid="stSidebar"] .stRadio label,
  section[data-testid="stSidebar"] .stSelectbox label {{ color: var(--text-2) !important; font-weight: 500; font-size: 0.85rem; }}

  /* ---------- Buttons ---------- */
  .stButton>button, .stDownloadButton>button {{
    background: linear-gradient(135deg, var(--primary) 0%, var(--pink) 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    box-shadow: 0 6px 18px rgba(155,123,255,0.35);
    transition: transform 0.12s ease, box-shadow 0.18s ease;
  }}
  .stButton>button:hover, .stDownloadButton>button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 10px 28px rgba(155,123,255,0.42) !important;
  }}
  .stButton>button:active {{ transform: translateY(0); }}

  /* "Secondary" button variant (used via st.button(type="secondary")) */
  .stButton>button[kind="secondary"] {{
    background: var(--surface) !important;
    color: var(--primary-dark) !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow-sm) !important;
  }}
  .stButton>button[kind="secondary"]:hover {{
    border-color: var(--border-strong) !important;
    background: var(--primary-soft) !important;
  }}

  /* ---------- File uploader ---------- */
  [data-testid="stFileUploader"] section {{
    background: var(--surface) !important;
    border: 1.5px dashed var(--border-strong) !important;
    border-radius: var(--radius) !important;
    color: var(--text-2) !important;
  }}
  [data-testid="stFileUploader"] section:hover {{
    border-color: var(--primary) !important;
    background: var(--primary-soft) !important;
  }}
  [data-testid="stFileUploader"] small {{ color: var(--text-3) !important; }}

  /* ---------- Chat input ---------- */
  [data-testid="stChatInput"] {{
    background: var(--surface) !important;
    border-radius: var(--radius-lg) !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow) !important;
  }}
  [data-testid="stChatInput"] textarea {{
    background: transparent !important;
    color: var(--text) !important;
    border: none !important;
    font-size: 1rem !important;
  }}
  [data-testid="stChatInput"] textarea::placeholder {{ color: var(--text-3) !important; }}
  [data-testid="stChatInput"] button {{
    background: linear-gradient(135deg, var(--primary), var(--pink)) !important;
    border-radius: 999px !important;
    color: white !important;
  }}

  /* ---------- Chat messages ---------- */
  [data-testid="stChatMessage"] {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 22px !important;
    padding: 16px 20px !important;
    box-shadow: var(--shadow-sm) !important;
    margin: 10px 0 !important;
  }}
  [data-testid="stChatMessage"]:has(div[data-testid="stChatMessageAvatarUser"]) {{
    background: linear-gradient(135deg, #F2EBFF 0%, #FFE4F2 100%) !important;
    border-color: transparent !important;
  }}

  /* ---------- Expanders / Citation cards ---------- */
  details, [data-testid="stExpander"] {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-sm) !important;
    overflow: hidden;
  }}
  [data-testid="stExpander"] summary {{ padding: 12px 16px !important; }}
  [data-testid="stExpander"] summary:hover {{ background: var(--primary-soft) !important; }}

  /* ---------- Inline citation chip ---------- */
  .pdf-cite {{
    display: inline-block;
    background: var(--cite-bg);
    color: var(--cite-fg);
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.78em;
    font-weight: 600;
    margin: 0 3px;
    border: 1px solid #D9C9FF;
  }}

  /* ---------- Status pills ---------- */
  .pdf-pill {{
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-right: 6px;
    border: 1px solid transparent;
  }}
  .pdf-pill-ok    {{ background: var(--success-soft); color: #1F8B62; border-color: rgba(78,212,168,0.4); }}
  .pdf-pill-warn  {{ background: var(--amber-soft); color: #B8731A; border-color: rgba(255,184,92,0.4); }}
  .pdf-pill-fail  {{ background: var(--danger-soft); color: #B53253; border-color: rgba(255,111,145,0.4); }}
  .pdf-pill-info  {{ background: var(--primary-soft); color: var(--primary-dark); border-color: rgba(155,123,255,0.3); }}

  /* ---------- Quote box ---------- */
  .pdf-quote {{
    background: linear-gradient(180deg, #FFFFFF 0%, #FAF6FF 100%);
    border-left: 3px solid var(--primary);
    padding: 12px 16px;
    border-radius: 12px;
    color: var(--text);
    font-style: italic;
    font-size: 0.95rem;
    line-height: 1.55;
    box-shadow: var(--shadow-sm);
  }}

  /* ---------- Tables ---------- */
  thead tr th {{ background: var(--surface-2) !important; color: var(--text) !important; font-weight: 600 !important; }}
  tbody tr td {{ background: var(--surface) !important; color: var(--text) !important; }}
  [data-testid="stTable"], [data-testid="stDataFrame"] {{ border-radius: var(--radius) !important; overflow: hidden; box-shadow: var(--shadow-sm); }}

  /* ---------- Hero (gradient orb) ---------- */
  .hero-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 28px 12px 8px 12px;
  }}
  .hero-orb {{
    width: 180px;
    height: 180px;
    border-radius: 50%;
    background:
      radial-gradient(circle at 32% 32%, #FFD2EA 0%, transparent 38%),
      radial-gradient(circle at 70% 70%, #BAA0FF 0%, transparent 50%),
      radial-gradient(circle at 50% 50%, #9B7BFF 0%, #6B5FE8 70%, #4F45BB 100%);
    box-shadow:
      0 30px 80px rgba(155,123,255,0.45),
      inset -20px -25px 60px rgba(255,143,207,0.55),
      inset 20px 20px 40px rgba(255,255,255,0.18);
    filter: saturate(1.05);
    animation: orb-float 7s ease-in-out infinite;
  }}
  .hero-orb::after {{
    content: "";
    position: relative;
    display: block;
    top: 20px; left: 28px;
    width: 50px; height: 50px;
    border-radius: 50%;
    background: rgba(255,255,255,0.28);
    filter: blur(8px);
  }}
  @keyframes orb-float {{
    0%, 100% {{ transform: translateY(0px) scale(1); }}
    50%      {{ transform: translateY(-10px) scale(1.02); }}
  }}
  .hero-greet {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 800;
    font-size: 2.2rem;
    margin-top: 24px;
    background: linear-gradient(90deg, var(--primary) 0%, var(--pink) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.03em;
  }}
  .hero-sub {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 700;
    font-size: 1.6rem;
    color: var(--text);
    margin-top: 2px;
    letter-spacing: -0.02em;
  }}
  .hero-tag {{
    color: var(--text-2);
    margin-top: 8px;
    font-size: 0.95rem;
    max-width: 540px;
  }}

  /* ---------- Suggestion cards ---------- */
  .pdf-card-grid {{ margin-top: 10px; }}
  .pdf-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 16px 18px;
    box-shadow: var(--shadow-sm);
    height: 100%;
    transition: transform 0.14s ease, box-shadow 0.18s ease, border-color 0.18s ease;
  }}
  .pdf-card:hover {{ transform: translateY(-3px); box-shadow: var(--shadow); border-color: var(--border-strong); }}
  .pdf-card-ico {{
    width: 32px; height: 32px;
    border-radius: 10px;
    display: inline-flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, var(--primary-soft), var(--pink-soft));
    color: var(--primary-dark);
    margin-bottom: 10px;
    font-size: 16px;
  }}
  .pdf-card-title {{ font-weight: 700; font-size: 0.98rem; color: var(--text); margin-bottom: 4px; }}
  .pdf-card-body  {{ color: var(--text-2); font-size: 0.85rem; line-height: 1.45; }}

  /* ---------- PDF info card in sidebar ---------- */
  .pdf-doc-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 12px 14px;
    box-shadow: var(--shadow-sm);
  }}
  .pdf-doc-name  {{ font-weight: 600; color: var(--text); font-size: 0.92rem; }}
  .pdf-doc-meta  {{ color: var(--text-3); font-size: 0.78rem; margin-top: 2px; }}

  /* ---------- Selectboxes & inputs ---------- */
  [data-baseweb="select"] > div {{
    background: var(--surface) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
  }}
  [data-baseweb="select"] > div:hover {{ border-color: var(--border-strong) !important; }}
  [data-baseweb="input"] input {{
    background: var(--surface) !important;
    border-radius: 12px !important;
  }}

  /* ---------- Code blocks ---------- */
  code {{ background: var(--primary-soft) !important; color: var(--primary-dark) !important; padding: 2px 7px; border-radius: 6px; font-size: 0.88em; }}
  pre code {{ background: var(--surface-2) !important; }}

  /* ---------- Hide chrome ---------- */
  #MainMenu, footer, [data-testid="stToolbar"] {{ visibility: hidden; }}
  hr {{ border-color: var(--border) !important; opacity: 0.55; }}

  /* ---------- Slider thumb ---------- */
  [data-testid="stSlider"] [role="slider"] {{
    background: linear-gradient(135deg, var(--primary), var(--pink)) !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(155,123,255,0.4);
  }}

  /* ---------- Brand mark ---------- */
  .brand-row {{ display: flex; align-items: center; gap: 10px; padding: 8px 4px 16px 4px; }}
  .brand-mark {{
    width: 34px; height: 34px;
    border-radius: 11px;
    background: linear-gradient(135deg, var(--primary), var(--pink));
    display: inline-flex; align-items: center; justify-content: center;
    color: white;
    font-weight: 800;
    box-shadow: 0 6px 16px rgba(155,123,255,0.4);
  }}
  .brand-name {{ font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; font-size: 1.1rem; color: var(--text); letter-spacing: -0.02em; }}
  .brand-tag {{ color: var(--text-3); font-size: 0.75rem; }}

  /* ---------- Section headers in sidebar ---------- */
  .side-section {{ font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--text-3); margin: 14px 4px 8px 4px; }}
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


def hero_orb_html(greet: str = "Hello there", subtitle: str = "What would you like to know?") -> str:
    return f"""
<div class="hero-wrap">
  <div class="hero-orb"></div>
  <div class="hero-greet">{greet}</div>
  <div class="hero-sub">{subtitle}</div>
  <div class="hero-tag">
    Ask anything about the active PDF. Every answer is grounded in cited
    page-level evidence; out-of-scope questions get an explicit refusal.
  </div>
</div>
"""


def brand_row(name: str = "pdfagent", tag: str = "Grounded PDF chat") -> str:
    return f"""
<div class="brand-row">
  <div class="brand-mark">P</div>
  <div>
    <div class="brand-name">{name}</div>
    <div class="brand-tag">{tag}</div>
  </div>
</div>
"""


def side_section(label: str) -> str:
    return f'<div class="side-section">{label}</div>'
