"""
MW4 Weapon Intelligence Lab - Tactical Arsenal Matchmaker & Combat Role Advisor
Dedicated interactive loadout recommendation tool for casual and competitive players.
"""

import os
import sys

# Ensure repository root is in sys.path for Streamlit Cloud deployment
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
from src.ui.theme import render_page_header
from src.ui.state import init_session_state, render_sidebar_controls
from src.ui.weapon_assets import get_weapon_img_tag
from src.ui.plain_english import (
    get_matchmaker_recommendation,
    get_weapon_plain_summary,
    get_weapon_star_ratings,
    get_attachment_plain_effects,
    get_attachment_unlock_level,
    render_field_intel_box,
    render_tactical_ballistics_codex
)
from src.engines.share_code import encode_loadout_share_code


st.set_page_config(
    page_title="Arsenal Matchmaker - MW4 Intel",
    page_icon="🎯",
    layout="wide"
)

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="🎯 Tactical Arsenal Matchmaker & Combat Role Advisor",
    subtitle="Zero-Guesswork Loadout Intelligence • Tailored 5-Slot Classes for Every Playstyle & Skill Level",
    active_version=selected_ver,
    active_ruleset=selected_rs_id,
    tag="2026 MW4 BETA"
)

weapons = repo.get_weapons()
if not weapons:
    st.warning("No weapons found in database.")
    st.stop()

# Field Intel Explainer Box
render_field_intel_box(
    title="How The Matchmaker Finds Your Perfect Weapon",
    text="Answer 3 simple questions below about how you like to play. The Matchmaker analyzes all 24 Modern Warfare 4 weapons, "
         "tournament pro presets, and ballistic recoil tensors to give you an <b>optimal weapon + ready-to-copy 5-slot loadout</b> with zero confusion.",
    tip="If you're a casual player who hates weapon kick, pick 'Zero-Kick Laser Beam' with 'Maximum Stability'!"
)

# ---------------------------------------------------------------------------
# 1. Interactive 3-Step Guided Questionnaire
# ---------------------------------------------------------------------------
st.markdown("### 🎛️ Step-by-Step Combat Role Questionnaire")

col_q1, col_q2, col_q3 = st.columns(3)

with col_q1:
    playstyle_sel = st.selectbox(
        "1. Combat Playstyle & Vibe",
        options=[
            "🎯 Zero-Kick Laser Beam (Easy Control / Minimal Recoil)",
            "⚡ Aggressive CQB Rusher (Run & Gun / Slide-Canceling)",
            "🛡️ Balanced All-Rounder (Reliable in Every Fight)",
            "🔭 Long-Range Lane Anchor (Precision Sightline Beamer)",
            "💥 Heavy Punch / Max Impact (High Stopping Power)",
            "🎯 Precision Quick-Scope Sniper (1-Shot Lethal)"
        ],
        index=0,
        help="Select how you naturally prefer to engage opponents on the map."
    )

with col_q2:
    dist_sel = st.selectbox(
        "2. Combat Distance & Map Size",
        options=[
            "🗺️ Standard 6v6 Multiplayer (15m - 35m Mid-Range)",
            "🏃 Close Quarters / Small Maps (0m - 15m Point Blank)",
            "🏔️ Large Sightlines / Ground War (35m+ Long Range)"
        ],
        index=0,
        help="The typical distance where most of your gunfights happen."
    )

with col_q3:
    control_sel = st.selectbox(
        "3. Aim & Handling Priority",
        options=[
            "🟢 Maximum Stability & Forgiving Aim (Easiest to Control)",
            "⚡ Super Fast Scope-In & Sprint Reaction Speed",
            "🔋 High Magazine Capacity (Multi-Kills Without Reloading)",
            "🎯 Pinpoint Optical Sight with Zero Visual Clutter"
        ],
        index=0,
        help="Your mechanical preference for weapon handling and control."
    )

# Compute match
rec = get_matchmaker_recommendation(playstyle_sel, dist_sel, control_sel)
matched_w_id = rec["weapon_id"]
matched_w = next((w for w in weapons if w.weapon_id == matched_w_id), weapons[0])
stats = repo.get_weapon_stats(matched_w.weapon_id, selected_ver)
plain_doss = get_weapon_plain_summary(matched_w.weapon_id, matched_w.name, matched_w.weapon_class.value)
stars = get_weapon_star_ratings(stats, matched_w.weapon_class) if stats else {}

st.markdown("---")

# ---------------------------------------------------------------------------
# 2. Matched Weapon Showcase Card
# ---------------------------------------------------------------------------
st.markdown("### 🏆 Your Tailored Tactical Match")

card_col_img, card_col_details = st.columns([1.2, 2])

with card_col_img:
    img_html = get_weapon_img_tag(matched_w.weapon_id, max_height_px=140, max_width_px=340)
    st.markdown(
        f'<div style="background: linear-gradient(145deg, rgba(15,23,42,0.9) 0%, rgba(30,41,59,0.8) 100%); '
        f'border: 2px solid rgba(56,189,248,0.4); border-radius: 12px; padding: 20px; text-align: center; box-shadow: 0 8px 24px rgba(0,0,0,0.4);">'
        f'<span style="background: rgba(56,189,248,0.2); color: #38bdf8; border: 1px solid rgba(56,189,248,0.5); '
        f'border-radius: 6px; padding: 4px 12px; font-size: 12px; font-weight: 700; text-transform: uppercase;">{rec["role_badge"]}</span>'
        f'<h2 style="color: #ffffff; margin: 12px 0 4px 0; font-size: 24px;">{rec["weapon_name"]}</h2>'
        f'<div style="color: #94a3b8; font-size: 13px; margin-bottom: 12px;">{matched_w.weapon_class.value.replace("_", " ").title()} • {matched_w.firing_mode.value.replace("_", " ").title()}</div>'
        f'{img_html}'
        f'<div style="margin-top: 14px; background: rgba(34,197,94,0.15); border: 1px solid rgba(34,197,94,0.4); border-radius: 6px; padding: 6px 12px;">'
        f'<span style="color: #4ade80; font-size: 13px; font-weight: 700;">Ease of Use: {rec["ease_rating"]}</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # 1-5 Star Ratings
    if stars:
        st.markdown(
            f'<div style="background: rgba(15,23,42,0.7); border: 1px solid rgba(148,163,184,0.2); border-radius: 8px; padding: 12px; margin-top: 10px;">'
            f'<div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 700; margin-bottom: 6px;">Tactical Ratings Breakdown</div>'
            f'<div style="font-size: 12px; color: #cbd5e1; margin-bottom: 4px;">⚡ <b>Kill Speed:</b> {stars["kill_speed"][1]}</div>'
            f'<div style="font-size: 12px; color: #4ade80; margin-bottom: 4px;">🎯 <b>Aim Control (Recoil):</b> {stars["ease_of_control"][1]}</div>'
            f'<div style="font-size: 12px; color: #cbd5e1; margin-bottom: 4px;">🏃 <b>Scope-In Speed:</b> {stars["quick_aim_speed"][1]}</div>'
            f'<div style="font-size: 12px; color: #cbd5e1;">🔭 <b>Long Range Punch:</b> {stars["long_range_power"][1]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

with card_col_details:
    st.markdown(
        f'<div style="background: rgba(15,23,42,0.85); border: 1px solid rgba(56,189,248,0.3); border-radius: 12px; padding: 20px; box-shadow: 0 4px 16px rgba(0,0,0,0.3);">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">'
        f'<span style="color: #38bdf8; font-size: 18px; font-weight: 700;">🔧 Recommended Loadout: <b>{rec["build_name"]}</b></span>'
        f'</div>'
        f'<p style="color: #e2e8f0; font-size: 13.5px; line-height: 1.5; margin-bottom: 14px;"><b>💬 Why This Gun Dominates:</b> {rec["why_it_works"]}</p>'
        f'<div style="font-size: 12px; color: #94a3b8; text-transform: uppercase; font-weight: 700; margin-bottom: 8px;">5-Slot Tournament Attachments:</div>',
        unsafe_allow_html=True
    )

    # 5 Attachments Grid
    for slot, att_name, purpose in rec["attachments"]:
        unlock_lvl = get_attachment_unlock_level(att_name)
        st.markdown(
            f'<div style="background: rgba(30,41,59,0.7); border: 1px solid rgba(148,163,184,0.2); border-left: 4px solid #38bdf8; border-radius: 6px; padding: 8px 14px; margin-bottom: 6px;">'
            f'<span style="color: #94a3b8; font-size: 11px; text-transform: uppercase; font-weight: 700;">{slot}:</span> '
            f'<span style="color: #ffffff; font-size: 13px; font-weight: 600;">{att_name}</span> '
            f'<span style="color: #fbbf24; font-size: 11.5px; font-weight: 600; margin-left: 4px;">(Unlocked: Weapon Level {unlock_lvl})</span> '
            f'<span style="color: #4ade80; font-size: 12px; margin-left: 8px;">➔ {purpose}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    # How to shoot it tip
    st.markdown(
        f'<div style="background: rgba(56,189,248,0.12); border: 1px dashed rgba(56,189,248,0.35); border-radius: 6px; padding: 10px 14px; margin-top: 12px; font-size: 12.5px; color: #7dd3fc;">'
        f'🎯 <b>10-Second Combat Strategy:</b> {rec["combat_tip"]}'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# 3. Quick-Click Archetype Cards (Instant 1-Click Loadouts)
# ---------------------------------------------------------------------------
st.markdown("### ⚡ Quick-Select Popular Weapon Playstyles")
st.caption("Click any combat role to instantly see the top-ranked weapon and build for that exact style:")

c_arch1, c_arch2, c_arch3, c_arch4 = st.columns(4)

with c_arch1:
    st.markdown(
        '<div style="background: rgba(15,23,42,0.7); border: 1px solid rgba(56,189,248,0.3); border-radius: 8px; padding: 14px; text-align: center;">'
        '<div style="font-size: 24px; margin-bottom: 4px;">👑</div>'
        '<h4 style="color:#ffffff; margin:0 0 4px 0; font-size:15px;">Zero-Recoil Laser</h4>'
        '<p style="color:#94a3b8; font-size:11.5px; margin-bottom:8px;"><b>XM4 (Assault Rifle)</b><br>Easiest gun in the game to shoot straight.</p>'
        '<span style="color:#38bdf8; font-size:11px; font-weight:700;">⭐⭐⭐⭐⭐ Very Easy</span>'
        '</div>',
        unsafe_allow_html=True
    )

with c_arch2:
    st.markdown(
        '<div style="background: rgba(15,23,42,0.7); border: 1px solid rgba(56,189,248,0.3); border-radius: 8px; padding: 14px; text-align: center;">'
        '<div style="font-size: 24px; margin-bottom: 4px;">⚡</div>'
        '<h4 style="color:#ffffff; margin:0 0 4px 0; font-size:15px;">Fast CQB Rusher</h4>'
        '<p style="color:#94a3b8; font-size:11.5px; margin-bottom:8px;"><b>ISO Nightshade (SMG)</b><br>Fastest 923-RPM sprint & close-range TTK.</p>'
        '<span style="color:#38bdf8; font-size:11px; font-weight:700;">⭐⭐⭐⭐☆ Super Snappy</span>'
        '</div>',
        unsafe_allow_html=True
    )

with c_arch3:
    st.markdown(
        '<div style="background: rgba(15,23,42,0.7); border: 1px solid rgba(56,189,248,0.3); border-radius: 8px; padding: 14px; text-align: center;">'
        '<div style="font-size: 24px; margin-bottom: 4px;">🛡️</div>'
        '<h4 style="color:#ffffff; margin:0 0 4px 0; font-size:15px;">100-Round Turret</h4>'
        '<p style="color:#94a3b8; font-size:11.5px; margin-bottom:8px;"><b>Type 73 (LMG)</b><br>821-RPM high-cadence drum. Wipes entire squads.</p>'
        '<span style="color:#38bdf8; font-size:11px; font-weight:700;">⭐⭐⭐⭐⭐ Zero Kick</span>'
        '</div>',
        unsafe_allow_html=True
    )

with c_arch4:
    st.markdown(
        '<div style="background: rgba(15,23,42,0.7); border: 1px solid rgba(56,189,248,0.3); border-radius: 8px; padding: 14px; text-align: center;">'
        '<div style="font-size: 24px; margin-bottom: 4px;">💥</div>'
        '<h4 style="color:#ffffff; margin:0 0 4px 0; font-size:15px;">7.62 Heavy Punch</h4>'
        '<p style="color:#94a3b8; font-size:11.5px; margin-bottom:8px;"><b>Patriot XMR (AR)</b><br>4-shot lethal laser stopping power.</p>'
        '<span style="color:#38bdf8; font-size:11px; font-weight:700;">⭐⭐⭐⭐☆ Heavy Hitter</span>'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown("---")

# Tactical Ballistics Codex & Jargon Translator
render_tactical_ballistics_codex()
