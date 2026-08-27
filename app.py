import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from src.ui.theme import inject_custom_theme, render_page_header
from src.ui.state import init_session_state, render_sidebar_controls
from src.engines.balance_scorer import calculate_balance_score
from src.engines.confidence_scorer import calculate_evidence_confidence
from src.ingestion.web_scraper import PatchNotesScraper
from src.database.connection import db_manager


st.set_page_config(
    page_title="MW4 Weapon Intelligence Lab",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize state and repo
repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="🎯 MW4 Weapon Intelligence Lab",
    subtitle="Evidence-Backed Competitive FPS Ballistics, Gunsmith Optimization & Patch Intelligence",
    active_version=selected_ver,
    active_ruleset=selected_rs_id
)

# ---------------------------------------------------------------------------
# Global 24-Hour Freshness Warning & One-Click Live Update Center
# ---------------------------------------------------------------------------
snapshots = repo.get_source_snapshots()
now_utc = datetime.now(timezone.utc)

is_outdated = False
last_sync_str = "Never"
hours_since_sync = 999.0

if snapshots:
    try:
        latest_snap = snapshots[0]
        # Handle ISO strings with or without timezone
        snap_time_str = latest_snap.fetch_timestamp
        if "+" in snap_time_str or "Z" in snap_time_str:
            snap_dt = datetime.fromisoformat(snap_time_str.replace("Z", "+00:00"))
        else:
            snap_dt = datetime.fromisoformat(snap_time_str).replace(tzinfo=timezone.utc)
        
        diff = now_utc - snap_dt
        hours_since_sync = diff.total_seconds() / 3600.0
        last_sync_str = f"{hours_since_sync:.1f} hours ago"
        if hours_since_sync >= 24.0:
            is_outdated = True
    except Exception:
        is_outdated = True
else:
    is_outdated = True

# Prominent Warning Banner if >= 24 hours outdated
if is_outdated:
    st.markdown(
        f'<div style="background: rgba(239, 68, 68, 0.15); border: 2px solid #ef4444; border-left: 8px solid #ef4444; border-radius: 8px; padding: 14px 18px; margin-bottom: 18px;">'
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">'
        f'<div>'
        f'<h4 style="color:#f87171; margin:0; font-size:16px;">⚠️ OUTDATED INTELLIGENCE ALERT (Last Synchronized: {last_sync_str})</h4>'
        f'<p style="color:#fca5a5; font-size:12px; margin:4px 0 0 0;">'
        f'Weapon stats and patch notes have not been synchronized in over 24 hours. Beta tuning updates or stealth hotfixes may be missing.'
        f'</p>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
else:
    st.markdown(
        f'<div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-left: 6px solid #22c55e; border-radius: 6px; padding: 10px 16px; margin-bottom: 18px;">'
        f'<span style="color:#4ade80; font-size:13px; font-weight:600;">🟢 Intelligence Fresh:</span>'
        f'<span style="color:#cbd5e1; font-size:12px;"> Latest patch notes and live weapon feeds verified {last_sync_str}.</span>'
        f'</div>',
        unsafe_allow_html=True
    )

# One-Click Master Update Action Button
col_btn, col_info = st.columns([1, 2])
with col_btn:
    update_all_clicked = st.button(
        "🚀 UPDATE ALL GUNS AND PATCH NOTES NOW",
        type="primary",
        use_container_width=True,
        help="Scrapes official Call of Duty patch notes, checks candidate month URLs (/2026/08/ and /2026/09/), updates Parquet snapshots, and triggers database verification."
    )

with col_info:
    st.caption("⚡ **Live Sync Action:** Resolves monthly rollover paths, crawls official patch feeds, hashes raw snapshots, and runs background Parquet backup.")

if update_all_clicked:
    with st.spinner("Scraping official Call of Duty patch notes and updating all weapon feeds..."):
        scraper = PatchNotesScraper(repo)
        success, msg, data = scraper.scrape_and_ingest()
        # Trigger Parquet snapshot export
        import os
        snap_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "snapshots")
        db_manager.export_all_to_parquet(snap_dir)
        
        if success:
            st.success(f"✅ {msg}")
            st.toast("Weapon stats & patch notes updated successfully!", icon="🎯")
            st.rerun()
        else:
            st.error(msg)

st.markdown("---")

from src.ui.plain_english import (
    render_tactical_ballistics_codex,
    get_weapon_plain_summary
)

# Overview metrics
st.markdown("### 📊 Operational Intel Summary")

weapons = repo.get_weapons()
versions = repo.get_game_versions()
evidence_entries = repo.get_evidence_ledger()
ai_queue = repo.get_ai_review_queue(status="pending")
custom_builds = repo.get_custom_builds()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(
        f'<div class="stat-card"><p class="stat-card-lbl">Cataloged Weapons</p><p class="stat-card-val">{len(weapons)}</p></div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f'<div class="stat-card"><p class="stat-card-lbl">Active Ruleset HP</p><p class="stat-card-val">{int(active_ruleset.target_health)} HP</p></div>',
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f'<div class="stat-card"><p class="stat-card-lbl">Verified Evidence</p><p class="stat-card-val">{len(evidence_entries)} Records</p></div>',
        unsafe_allow_html=True
    )

with col4:
    stat_deltas_count = len(repo.get_stat_delta_events())
    st.markdown(
        f'<div class="stat-card"><p class="stat-card-lbl">Tracked Patch Deltas</p><p class="stat-card-val" style="color: #38bdf8;">{stat_deltas_count} Events</p></div>',
        unsafe_allow_html=True
    )

with col5:
    st.markdown(
        f'<div class="stat-card"><p class="stat-card-lbl">Saved Custom Builds</p><p class="stat-card-val">{len(custom_builds)}</p></div>',
        unsafe_allow_html=True
    )

# Tactical Ballistics Codex & Jargon Translator
render_tactical_ballistics_codex()

st.markdown("---")

# Quick Intelligence Nav Grid
st.markdown("### 🧭 Intelligence Modules")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(
        '<div class="stat-card"><h4 style="color:#38bdf8; margin:0 0 6px 0;">🎯 Tactical Arsenal Matchmaker</h4><p style="font-size:12px; color:#cbd5e1; margin-bottom:10px;">Interactive 3-question advisor that matches your playstyle to the best gun and 5-slot tournament loadout.</p><a href="/Arsenal_Matchmaker" target="_self" style="color:#38bdf8; font-size:12px; font-weight:600; text-decoration:none;">Launch Matchmaker →</a></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="stat-card"><h4 style="color:#38bdf8; margin:0 0 6px 0;">🏆 META Board & Tier List</h4><p style="font-size:12px; color:#cbd5e1; margin-bottom:10px;">S/A/B/C/D tournament tier classifications with ease-of-control ratings and customizable balance weights.</p><a href="/META_Board" target="_self" style="color:#38bdf8; font-size:12px; font-weight:600; text-decoration:none;">Launch META Board →</a></div>',
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        '<div class="stat-card"><h4 style="color:#4ade80; margin:0 0 6px 0;">🎯 Verified META Builds Hub</h4><p style="font-size:12px; color:#cbd5e1; margin-bottom:10px;">Browse CDL Pro setups, zero-recoil laser classes, and 1-click share codes for all 24 Modern Warfare 4 weapons.</p><a href="/META_Builds" target="_self" style="color:#4ade80; font-size:12px; font-weight:600; text-decoration:none;">Launch META Builds →</a></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="stat-card"><h4 style="color:#4ade80; margin:0 0 6px 0;">⚡ Fastest TTK Leaderboard</h4><p style="font-size:12px; color:#cbd5e1; margin-bottom:10px;">Rank weapons by pure kill speed (Time-To-Kill) and bullets needed to eliminate opponents at any distance.</p><a href="/Fastest_TTK" target="_self" style="color:#4ade80; font-size:12px; font-weight:600; text-decoration:none;">Launch Fastest TTK →</a></div>',
        unsafe_allow_html=True
    )

with c3:
    st.markdown(
        '<div class="stat-card"><h4 style="color:#fb923c; margin:0 0 6px 0;">🔫 Weapon Lab</h4><p style="font-size:12px; color:#cbd5e1; margin-bottom:10px;">Compare continuous TTK curves, human reaction times, and physical gun stats with plain-English ratings.</p><a href="/Weapon_Lab" target="_self" style="color:#fb923c; font-size:12px; font-weight:600; text-decoration:none;">Launch Weapon Lab →</a></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="stat-card"><h4 style="color:#fb923c; margin:0 0 6px 0;">🛠️ Build Optimizer & Gunsmith</h4><p style="font-size:12px; color:#cbd5e1; margin-bottom:10px;">Equip 5-slot attachments with plain-English effect tags and solve for mathematical Pareto-frontier builds.</p><a href="/Build_Optimizer" target="_self" style="color:#fb923c; font-size:12px; font-weight:600; text-decoration:none;">Launch Optimizer →</a></div>',
        unsafe_allow_html=True
    )

st.markdown("---")

# Quick Weapon Roster Overview Table
st.markdown(f"### 📋 Weapon Arsenal Overview ({selected_ver} • {selected_rs_id.upper()})")

roster_rows = []
for w in weapons:
    stats = repo.get_weapon_stats(w.weapon_id, selected_ver)
    profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, selected_rs_id)
    if stats and profiles:
        ev_list = repo.get_evidence_ledger(target_entity_id=w.weapon_id)
        conf = calculate_evidence_confidence(ev_list, selected_ver)
        score_res = calculate_balance_score(w, stats, profiles, active_ruleset, confidence_score=conf)
        plain_dossier = get_weapon_plain_summary(w.weapon_id, w.name, w.weapon_class.value)
        roster_rows.append({
            "Weapon": w.name,
            "Class": w.weapon_class.value.replace("_", " ").title(),
            "Ease of Aim (Recoil)": plain_dossier["ease_label"],
            "Kill Speed (Close TTK)": f"{score_res.raw_close_ttk_ms} ms",
            "Fire Rate (RPM)": f"{stats.rpm} RPM",
            "Quick-Aim (ADS)": f"{stats.base_ads_ms} ms",
            "Sprint-to-Shoot": f"{stats.sprint_to_fire_ms} ms",
            "Bullet Velocity": f"{stats.bullet_velocity_mps} m/s",
            "Mag Size": f"{w.base_mag_size} rds",
            "Competitive Tier": score_res.tier_rating,
            "Balance Score": f"{score_res.composite_balance_score}/100"
        })

if roster_rows:
    df_roster = pd.DataFrame(roster_rows)
    st.dataframe(df_roster, use_container_width=True, hide_index=True)
else:
    st.info(f"No weapon stats recorded yet for version '{selected_ver}' and ruleset '{selected_rs_id}'.")

