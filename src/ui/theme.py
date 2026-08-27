"""
MW4 Weapon Intelligence Lab - Dark Tactical Theme & UI Styling
Modern dark glassmorphism styling, FPS tactical accents, and metric badges.
"""

import streamlit as st


TACTICAL_CSS = """
<style>
/* Main Dark Tactical Background */
.stApp {
    background-color: #0b0e14;
    color: #e2e8f0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Header & Accent Bars */
.main-header {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid rgba(56, 189, 248, 0.2);
    border-left: 4px solid #38bdf8;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
}

.main-title {
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #f8fafc;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.sub-title {
    font-size: 13px;
    color: #94a3b8;
    margin-top: 4px;
    margin-bottom: 0;
}

/* Stat Cards */
.stat-card {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 12px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.stat-card:hover {
    border-color: rgba(56, 189, 248, 0.4);
    transform: translateY(-2px);
}

.stat-card-val {
    font-size: 22px;
    font-weight: 700;
    color: #38bdf8;
    margin: 0;
}

.stat-card-lbl {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    color: #94a3b8;
    margin: 0;
}

/* Badges */
.badge-tier1 {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border: 1px solid rgba(34, 197, 94, 0.4);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}

.badge-tier2 {
    background: rgba(56, 189, 248, 0.15);
    color: #38bdf8;
    border: 1px solid rgba(56, 189, 248, 0.4);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}

.badge-tier4 {
    background: rgba(249, 115, 22, 0.15);
    color: #fb923c;
    border: 1px solid rgba(249, 115, 22, 0.4);
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
}

.badge-buff {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
}

.badge-nerf {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 4px;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #07090e;
    border-right: 1px solid rgba(56, 189, 248, 0.1);
}

/* Custom Alert Boxes */
.alert-box {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 12px;
    color: #cbd5e1;
    margin-bottom: 12px;
}
</style>
"""


def inject_custom_theme() -> None:
    """Injects tactical dark CSS styles into the current Streamlit app page."""
    st.markdown(TACTICAL_CSS, unsafe_allow_html=True)


def render_page_header(
    title: str,
    subtitle: str = "",
    active_version: str = "v1.0.0-beta",
    active_ruleset: str = "core",
    tag: str = None,
    **kwargs
) -> None:
    """Renders standard tactical header across all pages with resilient signature."""
    inject_custom_theme()
    extra_badge = f'<span class="badge-tier4">{tag}</span>' if tag else ""
    header_html = (
        f'<div class="main-header">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">'
        f'<div><h1 class="main-title">{title}</h1><p class="sub-title">{subtitle}</p></div>'
        f'<div style="display: flex; gap: 8px; align-items: center; margin-top: 6px;">'
        f'{extra_badge}'
        f'<span class="badge-tier2">PATCH: {active_version}</span>'
        f'<span class="badge-tier1">RULESET: {active_ruleset.upper()}</span>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)


DARK_LAYOUT = dict(
    paper_bgcolor="rgba(11, 14, 20, 0.9)",
    plot_bgcolor="rgba(15, 23, 42, 0.6)",
    font=dict(color="#cbd5e1", family="Inter, sans-serif"),
    xaxis=dict(
        gridcolor="rgba(148, 163, 184, 0.1)",
        zerolinecolor="rgba(148, 163, 184, 0.2)"
    ),
    yaxis=dict(
        gridcolor="rgba(148, 163, 184, 0.1)",
        zerolinecolor="rgba(148, 163, 184, 0.2)"
    ),
    legend=dict(
        bgcolor="rgba(15, 23, 42, 0.8)",
        bordercolor="rgba(148, 163, 184, 0.2)",
        borderwidth=1
    )
)

