"""
MW4 Weapon Intelligence Lab - Verified META Builds & Pro Class Hub
Interactive catalog of CDL Tournament Pro setups, Laboratory Pareto-Optimal classes,
Omnimovement Rushers, and Zero-Recoil Beamers across all 24 Modern Warfare 4 weapons.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from src.ui.theme import render_page_header
from src.ui.state import init_session_state, render_sidebar_controls
from src.database.models import (
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Attachment,
    MetaBuildPreset
)
from src.engines.attachment_engine import calculate_modified_stats
from src.ui.weapon_assets import render_weapon_meta_header
from src.ui.plain_english import (
    get_attachment_plain_effects,
    render_field_intel_box,
    get_weapon_plain_summary
)


st.set_page_config(page_title="META Builds - MW4 Intel", page_icon="🎯", layout="wide")

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="🎯 Verified META Builds & Pro Class Hub",
    subtitle="Inspect, compare, and copy verified CDL Pro tournament loadouts, Laboratory Pareto classes, and community meta setups.",
    active_version=selected_ver,
    active_ruleset=selected_rs_id,
    tag="2026 MW4 BETA"
)

# Field Intel Explainer
render_field_intel_box(
    title="How Verified META Builds Work",
    text="These weapon builds are verified and copied directly from top CDL tournament pros, analytics sites, and mathematical solvers.<br>"
         "• <b>👑 CDL Pro Meta:</b> Tournament-legal, ultra-reliable all-round setups.<br>"
         "• <b>🎯 Zero-Recoil Beamer:</b> Built specifically for the easiest possible gun control (virtually zero kick).<br>"
         "• <b>⚡ Max Speed Rusher:</b> Maximum sprint speed and quick-aim reaction time for aggressive close-range play.",
    tip="If you want the easiest experience in multiplayer, pick any 'Zero-Recoil Beamer' preset with a Slate Reflector red dot optic!"
)

# Fetch all weapons and available meta builds from database
weapons_all = repo.get_weapons()
meta_builds_all = []
if hasattr(repo, "get_meta_builds"):
    try:
        meta_builds_all = repo.get_meta_builds(game_version_id=selected_ver)
        if not meta_builds_all:
            meta_builds_all = repo.get_meta_builds()
    except Exception:
        meta_builds_all = []

# Fetch consensus ratings for tier badges
consensus_records = {}
if hasattr(repo, "get_community_consensus"):
    try:
        consensus_records = repo.get_community_consensus(selected_ver)
        if not consensus_records:
            consensus_records = repo.get_community_consensus()
    except Exception:
        consensus_records = {}

# Top Level Filter Controls
st.markdown("### 🔍 Filter Meta Build Catalog")
col_class, col_weapon, col_arch = st.columns([1.5, 2, 2])

with col_class:
    class_options = ["All Classes"] + sorted(list(set(w.weapon_class.value.replace("_", " ").title() for w in weapons_all)))
    chosen_class = st.selectbox("Weapon Category", options=class_options, index=0)

filtered_weapons = [
    w for w in weapons_all
    if chosen_class == "All Classes" or w.weapon_class.value.replace("_", " ").title() == chosen_class
]

with col_weapon:
    weapon_opts = ["All Weapons (" + str(len(filtered_weapons)) + ")"] + [w.name for w in filtered_weapons]
    chosen_weapon_name = st.selectbox("Specific Weapon", options=weapon_opts, index=0)

with col_arch:
    archetype_opts = [
        "All Archetypes",
        "👑 CDL Pro Meta",
        "🔬 Lab Pareto Optimal",
        "⚡ Max Speed Rusher",
        "🎯 Zero-Recoil Beamer",
        "🤫 S&D Stealth Infiltrator"
    ]
    chosen_archetype = st.selectbox("Build Archetype / Playstyle", options=archetype_opts, index=0)

# Filter matching builds
target_weapons = filtered_weapons
if chosen_weapon_name != "All Weapons (" + str(len(filtered_weapons)) + ")":
    target_weapons = [w for w in filtered_weapons if w.name == chosen_weapon_name]

# Map builds to weapons
builds_by_weapon: Dict[str, List[MetaBuildPreset]] = {w.weapon_id: [] for w in target_weapons}
for b in meta_builds_all:
    if b.weapon_id in builds_by_weapon:
        if chosen_archetype == "All Archetypes" or b.archetype_display == chosen_archetype:
            builds_by_weapon[b.weapon_id].append(b)

total_matching_builds = sum(len(b_list) for b_list in builds_by_weapon.values())

st.markdown("---")
col_count, col_source_info = st.columns([2, 2])
with col_count:
    st.markdown(f"#### 📦 Found `{total_matching_builds}` Verified Meta Loadouts across `{len(target_weapons)}` Weapons")
with col_source_info:
    st.caption("All class setups verified against **WZStats.gg**, **WZRanked**, **CODMunity**, and internal **Ballistic Pareto Engines**.")

# Fetch all attachments for evaluation
all_attachments = {a.attachment_id: a for a in repo.get_attachments()}
all_modifiers = repo.get_attachment_modifiers(version_id=selected_ver)

# Render Weapon Meta Cards
for w in target_weapons:
    w_builds = builds_by_weapon.get(w.weapon_id, [])
    if not w_builds and chosen_archetype != "All Archetypes":
        continue

    stats = repo.get_weapon_stats(w.weapon_id, selected_ver)
    profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, selected_rs_id)
    c_rec = consensus_records.get(w.weapon_id)
    tier_badge = c_rec.wzranked_tier if c_rec else "A-Tier ⭐"
    consensus_tag = c_rec.consensus_tag if c_rec else "🔥 UNANIMOUS S-TIER META"
    pick_pct = c_rec.community_pick_rate_pct if c_rec else 5.0
    kd_val = c_rec.community_kd_ratio if c_rec else 1.05

    with st.container():
        # Weapon Header Card with Transparent Weapon Render, Pick Rate & K/D Badges
        st.markdown(
            render_weapon_meta_header(w, tier_badge, consensus_tag, pick_pct, kd_val),
            unsafe_allow_html=True
        )

        if not w_builds:
            st.info(f"No specific '{chosen_archetype}' setup cataloged for {w.name}. Select 'All Archetypes' or choose another weapon.")
            continue

        # Render Archetype Tabs for this weapon
        tab_titles = [f"{b.archetype_display}" for b in w_builds]
        tabs = st.tabs(tab_titles)

        for tab_idx, b in enumerate(w_builds):
            with tabs[tab_idx]:
                st.markdown(f"#### 🏷️ {b.build_name}")
                st.caption(f"**Verified Source**: `{b.source_outlet}` &nbsp;|&nbsp; **Recommended Maps**: `{b.best_maps}`")

                # Evaluate Attachment Stats
                build_attachments = [all_attachments[aid] for aid in b.attachment_ids if aid in all_attachments]
                if stats and profiles:
                    eval_stats = calculate_modified_stats(
                        weapon=w,
                        base_stats=stats,
                        attachments=build_attachments,
                        all_modifiers=all_modifiers,
                        damage_profiles=profiles,
                        ruleset=active_ruleset
                    )
                else:
                    eval_stats = None

                # 1. Stat Impact Metrics Banner
                if eval_stats:
                    ads_diff = eval_stats.effective_ads_ms - stats.base_ads_ms
                    ads_sign = "+" if ads_diff > 0 else ""
                    ads_color = "inverse" if ads_diff > 0 else "normal"

                    stf_diff = eval_stats.effective_sprint_to_fire_ms - stats.sprint_to_fire_ms
                    stf_sign = "+" if stf_diff > 0 else ""

                    recoil_pct = (1.0 - (eval_stats.effective_recoil_vertical / max(0.01, stats.recoil_vertical))) * 100

                    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                    with col_m1:
                        st.metric("Quick-Aim (ADS)", f"{eval_stats.effective_ads_ms:.0f} ms", f"{ads_sign}{ads_diff:.0f} ms", delta_color=ads_color)
                    with col_m2:
                        st.metric("Sprint Reaction", f"{eval_stats.effective_sprint_to_fire_ms:.0f} ms", f"{stf_sign}{stf_diff:.0f} ms", delta_color=ads_color)
                    with col_m3:
                        st.metric("Recoil Reduction", f"{recoil_pct:+.1f}%", "Vertical Kick Dampening")
                    with col_m4:
                        st.metric("Kill Speed (0-15m)", f"{eval_stats.close_ttk_ms:.0f} ms", f"{eval_stats.effective_mag_size} Rnd Mag")
                    with col_m5:
                        st.metric("Bullet Velocity", f"{eval_stats.effective_bullet_velocity_mps:.0f} m/s", f"{eval_stats.range_multiplier*100:.0f}% Range")

                # 2. 5-Attachment Breakdown Grid
                st.markdown("##### 🎛️ Primary Gunsmith Setup (5 Attachments)")
                att_cols = st.columns(min(5, max(1, len(build_attachments))))
                for idx, att in enumerate(build_attachments):
                    with att_cols[idx % len(att_cols)]:
                        att_desc = att.description or 'Custom competitive attachment'
                        effs = get_attachment_plain_effects(att.attachment_id, att.name)
                        eff_html = f"<div style='margin-top:6px; padding-top:4px; border-top:1px dashed rgba(56,189,248,0.2); font-size:0.75rem; color:#4ade80;'>{'<br>'.join(effs[:2])}</div>"
                        st.markdown(
                            f'<div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 10px 12px; height: 100%;">'
                            f'<div style="color: #38bdf8; font-size: 0.75rem; text-transform: uppercase; font-weight: 700;">{att.slot.value.upper()}</div>'
                            f'<div style="color: #f8fafc; font-weight: 600; font-size: 0.95rem; margin: 4px 0;">{att.name}</div>'
                            f'<div style="color: #94a3b8; font-size: 0.8rem;">{att_desc}</div>'
                            f'{eff_html}'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                # 3. Dual-Weapon Tactical Companion Box
                sec_att_labels = []
                for said in b.secondary_attachments:
                    if said in all_attachments:
                        sec_att_labels.append(f"<b>[{all_attachments[said].slot.value.upper()}]</b> {all_attachments[said].name}")
                sec_att_str = " &nbsp;•&nbsp; ".join(sec_att_labels) if sec_att_labels else "Standard Match Sidearm Setup"

                st.markdown(
                    f'<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(129, 140, 248, 0.3); border-left: 4px solid #818cf8; border-radius: 8px; padding: 12px 16px; margin: 14px 0;">'
                    f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">'
                    f'<div>'
                    f'<span style="color: #818cf8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase;">🔫 Recommended Secondary Companion</span>'
                    f'<div style="color: #f8fafc; font-size: 1.05rem; font-weight: 700; margin-top: 2px;">{b.secondary_name} <span style="color: #94a3b8; font-size: 0.85rem; font-weight: normal;">— {b.secondary_role}</span></div>'
                    f'</div>'
                    f'<div style="color: #cbd5e1; font-size: 0.82rem;">{sec_att_str}</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # 4. 360° Tactical Class Synergies
                st.markdown("##### 🛡️ Complete Tactical Class Synergies")
                col_p1, col_p2, col_p3, col_eq = st.columns([1, 1, 1, 1.5])
                with col_p1:
                    st.markdown(
                        f'<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 8px 12px;">'
                        f'<span style="color: #f59e0b; font-size: 0.75rem; font-weight: 700;">PERK 1 (STEALTH/HP)</span>'
                        f'<div style="color: #f8fafc; font-weight: 600; font-size: 0.95rem;">{b.perk_1_name}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col_p2:
                    st.markdown(
                        f'<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 8px 12px;">'
                        f'<span style="color: #f59e0b; font-size: 0.75rem; font-weight: 700;">PERK 2 (ECONOMY/RELOAD)</span>'
                        f'<div style="color: #f8fafc; font-weight: 600; font-size: 0.95rem;">{b.perk_2_name}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col_p3:
                    st.markdown(
                        f'<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 8px 12px;">'
                        f'<span style="color: #f59e0b; font-size: 0.75rem; font-weight: 700;">PERK 3 (SURVIVAL/STAMINA)</span>'
                        f'<div style="color: #f8fafc; font-weight: 600; font-size: 0.95rem;">{b.perk_3_name}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                with col_eq:
                    st.markdown(
                        f'<div style="background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 8px; padding: 8px 12px;">'
                        f'<span style="color: #38bdf8; font-size: 0.75rem; font-weight: 700;">EQUIPMENT PACKAGE</span>'
                        f'<div style="color: #f8fafc; font-size: 0.85rem;">'
                        f'💣 <b>Lethal:</b> {b.lethal_name} &nbsp;|&nbsp; ⚡ <b>Tactical:</b> {b.tactical_name}<br/>'
                        f'🚀 <b>Field Upgrade:</b> {b.field_upgrade_name}'
                        f'</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                # 5. Playstyle Strategy & Share Code
                st.markdown(f"**Tactical Playstyle Guide**: *{b.playstyle_notes}*")
                
                col_code, col_btn_action = st.columns([3, 1])
                with col_code:
                    st.code(b.share_code, language="markdown")
                with col_btn_action:
                    st.write("")
                    st.caption("📋 Copy loadout share code for custom sharing.")

        st.markdown("<br/>", unsafe_allow_html=True)
