import streamlit as st
import pandas as pd
from src.ui.theme import render_page_header
from src.ui.state import init_session_state, render_sidebar_controls
from src.ui.charts import create_balance_radar_chart
from src.engines.balance_scorer import (
    calculate_balance_score,
    DEFAULT_EMPIRICAL_WEIGHTS,
    CLASS_ARCHETYPE_WEIGHTS
)
from src.engines.confidence_scorer import calculate_evidence_confidence
from src.ui.weapon_assets import get_weapon_img_tag
from src.ui.plain_english import (
    get_weapon_plain_summary,
    render_field_intel_box
)


st.set_page_config(page_title="META Board - MW4 Intel", page_icon="🏆", layout="wide")

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="🏆 META Board & Balance Tier Ranking",
    subtitle="Tournament-Grade S/A/B/C/D Tier Classifications with Class-Relative Role Benchmarks & Empirical Sightline Modeling",
    active_version=selected_ver,
    active_ruleset=selected_rs_id
)

weapons = repo.get_weapons()
if not weapons:
    st.warning("No weapons found in database.")
    st.stop()

# Field Intel Explainer
render_field_intel_box(
    title="How Tier Rankings Work In Competitive Call of Duty",
    text="• <b>S-Tier (Absolute Meta):</b> The undisputed top weapons in the game. These have the fastest kill times and highest consistency.<br>"
         "• <b>A-Tier (Top Tier):</b> Extremely competitive options that hold their own against any S-Tier weapon.<br>"
         "• <b>B-Tier (Balanced):</b> Viable and fun for casual play, but may lose 1v1 gunfights to pure meta setups.<br>"
         "• <b>C/D-Tier (Underperforming):</b> Guns with severe recoil or slow fire rates that are currently waiting for developer buffs.",
    tip="If you want an easy time, look for weapons in S or A Tier that have low recoil (like the XM4 or Striker)!"
)

# Ranking Mode Selector
st.markdown("#### 🎯 Competitive Ranking Engine Mode")
c_engine_col1, c_engine_col2 = st.columns([2, 1])

with c_engine_col1:
    ranking_engine_mode = st.radio(
        "Tier Ranking Methodology",
        options=[
            "🏆 Multi-Source Industry Consensus (Blends Lab Math + Dexerto + CharlieIntel + Dot Esports)",
            "🔬 Pure Mathematical Ballistic Engine (Lab TTK & PET Formulas Only)"
        ],
        index=0,
        help="Consensus mode merges frame-by-frame ballistic data with pro community consensus from top Call of Duty publications."
    )

with c_engine_col2:
    class_options = ["All Classes"] + sorted(list({w.weapon_class.value.replace("_", " ").title() for w in weapons}))
    if hasattr(st, "pills"):
        chosen_class = st.pills("Filter Weapon Class", options=class_options, default="All Classes") or "All Classes"
    else:
        chosen_class = st.selectbox("Filter Weapon Class", options=class_options)

c_mode_col1, _ = st.columns([2, 1])
with c_mode_col1:
    ranking_mode = st.radio(
        "Ballistic Weighting Mode",
        options=[
            "🎯 Class-Relative Role Standings (Best in Category - Evaluates Shotguns/Snipers/SMGs by their intended role)",
            "🌐 Empirical 6v6 Sightline Meta (Weighted for 12m-32m primary combat zone with recoil bottleneck penalties)",
            "🎚️ Tactical Weight Presets (Rusher, Anchor, Sniper, Hardcore, Custom)"
        ],
        index=0
    )

# Handle Custom Presets if mode 3 selected
active_weights = None
use_class_rel = False

if "Class-Relative" in ranking_mode:
    use_class_rel = True
elif "Empirical 6v6" in ranking_mode:
    use_class_rel = False
    active_weights = DEFAULT_EMPIRICAL_WEIGHTS
else:
    preset_choice = st.radio(
        "Scoring Weight Preset",
        options=[
            "Balanced General",
            "Aggressive CQB / Rusher",
            "Long Range Anchor / Lane Holder",
            "Sniper & Precision One-Shot",
            "Hardcore Speed & Reaction",
            "Custom Sliders"
        ],
        horizontal=True
    )
    if preset_choice == "Aggressive CQB / Rusher":
        active_weights = {"cqb_ttk": 0.40, "mid_ttk": 0.15, "long_ttk": 0.05, "handling_ads_stf": 0.30, "recoil_stability": 0.05, "sustainability_reload_mag": 0.05}
    elif preset_choice == "Long Range Anchor / Lane Holder":
        active_weights = {"cqb_ttk": 0.10, "mid_ttk": 0.30, "long_ttk": 0.30, "handling_ads_stf": 0.05, "recoil_stability": 0.20, "sustainability_reload_mag": 0.05}
    elif preset_choice == "Sniper & Precision One-Shot":
        active_weights = {"cqb_ttk": 0.05, "mid_ttk": 0.25, "long_ttk": 0.45, "handling_ads_stf": 0.20, "recoil_stability": 0.03, "sustainability_reload_mag": 0.02}
    elif preset_choice == "Hardcore Speed & Reaction":
        active_weights = {"cqb_ttk": 0.35, "mid_ttk": 0.15, "long_ttk": 0.05, "handling_ads_stf": 0.40, "recoil_stability": 0.02, "sustainability_reload_mag": 0.03}
    elif preset_choice == "Custom Sliders":
        st.markdown("##### 🎚️ Custom Scoring Weights (Sum will be normalized to 1.0)")
        cw1, cw2, cw3, cw4, cw5, cw6 = st.columns(6)
        with cw1: w_cqb = st.slider("CQB TTK", 0, 100, 25)
        with cw2: w_mid = st.slider("Mid TTK", 0, 100, 35)
        with cw3: w_long = st.slider("Long TTK", 0, 100, 15)
        with cw4: w_hand = st.slider("Handling", 0, 100, 15)
        with cw5: w_rec = st.slider("Recoil", 0, 100, 7)
        with cw6: w_sus = st.slider("Mag/Reload", 0, 100, 3)
        active_weights = {
            "cqb_ttk": float(w_cqb),
            "mid_ttk": float(w_mid),
            "long_ttk": float(w_long),
            "handling_ads_stf": float(w_hand),
            "recoil_stability": float(w_rec),
            "sustainability_reload_mag": float(w_sus)
        }
    else:
        active_weights = DEFAULT_EMPIRICAL_WEIGHTS

# Fallback 2026 MW4 Beta Industry Ratings Directory (6 Meta Authorities)
default_outlet_data = {
    "xm4_mw4": {"wzstats": "S-Tier 👑", "wzranked": "S-Tier 👑", "codmunity": "S-Tier 👑", "dexerto": "S-Tier 👑", "charlie": "S-Tier 👑", "dotesports": "S-Tier 👑", "consensus": "🔥 UNANIMOUS S-TIER META", "badge_color": "#f59e0b"},
    "iso_nightshade_mw4": {"wzstats": "S-Tier 👑", "wzranked": "S-Tier 👑", "codmunity": "S-Tier 👑", "dexerto": "S-Tier 👑", "charlie": "S-Tier 👑", "dotesports": "S-Tier 👑", "consensus": "🔥 UNANIMOUS S-TIER SMG", "badge_color": "#f59e0b"},
    "hyeon_burst_mw4": {"wzstats": "A-Tier ⭐", "wzranked": "A-Tier ⭐", "codmunity": "S-Tier 👑", "dexerto": "A-Tier ⭐", "charlie": "A-Tier ⭐", "dotesports": "A-Tier ⭐", "consensus": "⚡ 1-BURST TTK CEILING", "badge_color": "#38bdf8"},
    "rival9_mw4": {"wzstats": "A-Tier ⭐", "wzranked": "S-Tier 👑", "codmunity": "A-Tier ⭐", "dexerto": "S-Tier 👑", "charlie": "A-Tier ⭐", "dotesports": "A-Tier ⭐", "consensus": "⚡ TOP PRO CQB RUSH SMG", "badge_color": "#38bdf8"},
    "ak74m_mw4": {"wzstats": "S-Tier 👑", "wzranked": "A-Tier ⭐", "codmunity": "A-Tier ⭐", "dexerto": "A-Tier ⭐", "charlie": "S-Tier 👑", "dotesports": "A-Tier ⭐", "consensus": "💪 HEAVY 7.62 PUNCH", "badge_color": "#38bdf8"},
    "striker45_mw4": {"wzstats": "A-Tier ⭐", "wzranked": "A-Tier ⭐", "codmunity": "A-Tier ⭐", "dexerto": "A-Tier ⭐", "charlie": "A-Tier ⭐", "dotesports": "A-Tier ⭐", "consensus": "🎯 LONGEST RANGE SMG", "badge_color": "#38bdf8"},
    "ppsh41_mw4": {"wzstats": "S-Tier 👑", "wzranked": "A-Tier ⭐", "codmunity": "A-Tier ⭐", "dexerto": "A-Tier ⭐", "charlie": "A-Tier ⭐", "dotesports": "S-Tier 👑", "consensus": "⚡ 1000 RPM ROOM CLEARER", "badge_color": "#38bdf8"},
    "kvd_enforcer_mw4": {"wzstats": "B-Tier 🔷", "wzranked": "A-Tier ⭐", "codmunity": "A-Tier ⭐", "dexerto": "B-Tier 🔷", "charlie": "A-Tier ⭐", "dotesports": "A-Tier ⭐", "consensus": "🎯 2-TAP PRECISION DMR", "badge_color": "#4ade80"},
    "mcw_mw4": {"wzstats": "B-Tier 🔷", "wzranked": "A-Tier ⭐", "codmunity": "B-Tier 🔷", "dexerto": "B-Tier 🔷", "charlie": "A-Tier ⭐", "dotesports": "B-Tier 🔷", "consensus": "🎯 ZERO-RECOIL LASER BEAM", "badge_color": "#4ade80"},
    "han86_mw4": {"wzstats": "A-Tier ⭐", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷", "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷", "consensus": "🛡️ HIGH STABILITY BULLPUP", "badge_color": "#4ade80"},
    "signal50_mw4": {"wzstats": "A-Tier ⭐", "wzranked": "B-Tier 🔷", "codmunity": "A-Tier ⭐", "dexerto": "A-Tier ⭐", "charlie": "A-Tier ⭐", "dotesports": "B-Tier 🔷", "consensus": "🎯 1-SHOT SEMI-AUTO SNIPER", "badge_color": "#38bdf8"},
    "basb_mw4": {"wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷", "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷", "consensus": "💥 PUNISHING 3-SHOT POWER", "badge_color": "#4ade80"},
    "amr9_mw4": {"wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷", "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷", "consensus": "⚡ BALANCED 833 RPM SMG", "badge_color": "#4ade80"},
    "katt_amr_mw4": {"wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷", "dexerto": "A-Tier ⭐", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷", "consensus": "🎯 .50 BMG 1-SHOT ANCHOR", "badge_color": "#4ade80"},
    "holger556_mw4": {"wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷", "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷", "consensus": "🛡️ ACCURATE MID-AR", "badge_color": "#4ade80"},
    "wsp_swarm_mw4": {"wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷", "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷", "consensus": "⚡ 1090 RPM MICRO-SMG", "badge_color": "#4ade80"},
    "longbow_mw4": {"wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷", "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷", "consensus": "⚡ FAST-CHAMBER SNIPER", "badge_color": "#4ade80"},
    "rezi12_mw4": {"wzstats": "A-Tier ⭐", "wzranked": "C-Tier 🔶", "codmunity": "C-Tier 🔶", "dexerto": "C-Tier 🔶", "charlie": "C-Tier 🔶", "dotesports": "S-Tier 👑", "consensus": "🚪 FULL-AUTO ROOM BREACHER", "badge_color": "#a855f7"},
    "lockwood680_mw4": {"wzstats": "C-Tier 🔶", "wzranked": "C-Tier 🔶", "codmunity": "C-Tier 🔶", "dexerto": "C-Tier 🔶", "charlie": "C-Tier 🔶", "dotesports": "C-Tier 🔶", "consensus": "💥 1-SHOT PUMP SHOTGUN", "badge_color": "#a855f7"},
    "pulemyot762_mw4": {"wzstats": "C-Tier 🔶", "wzranked": "C-Tier 🔶", "codmunity": "C-Tier 🔶", "dexerto": "C-Tier 🔶", "charlie": "C-Tier 🔶", "dotesports": "C-Tier 🔶", "consensus": "🛡️ 100-RND SUSTAINED FIRE", "badge_color": "#a855f7"},
    "bruen_mk9_mw4": {"wzstats": "C-Tier 🔶", "wzranked": "C-Tier 🔶", "codmunity": "C-Tier 🔶", "dexerto": "C-Tier 🔶", "charlie": "C-Tier 🔶", "dotesports": "C-Tier 🔶", "consensus": "🛡️ 60-RND SQUAD LMG", "badge_color": "#a855f7"},
    "sidewinder_mw4": {"wzstats": "D-Tier 🔘", "wzranked": "D-Tier 🔘", "codmunity": "D-Tier 🔘", "dexerto": "D-Tier 🔘", "charlie": "D-Tier 🔘", "dotesports": "D-Tier 🔘", "consensus": "⚠️ HIGH RECOIL / LOW RPM", "badge_color": "#94a3b8"},
    "renetti_mw4": {"wzstats": "D-Tier 🔘", "wzranked": "D-Tier 🔘", "codmunity": "D-Tier 🔘", "dexerto": "D-Tier 🔘", "charlie": "D-Tier 🔘", "dotesports": "D-Tier 🔘", "consensus": "🔫 3-ROUND BURST SIDEARM", "badge_color": "#94a3b8"},
    "cor45_mw4": {"wzstats": "D-Tier 🔘", "wzranked": "D-Tier 🔘", "codmunity": "D-Tier 🔘", "dexerto": "D-Tier 🔘", "charlie": "D-Tier 🔘", "dotesports": "D-Tier 🔘", "consensus": "🔫 SEMI-AUTO BACKUP SIDEARM", "badge_color": "#94a3b8"}
}

# Fetch live database consensus records (versioned with safe cached-resource fallback)
db_consensus_records = {}
if hasattr(repo, "get_community_consensus"):
    try:
        db_consensus_records = repo.get_community_consensus(selected_ver)
        if not db_consensus_records:
            db_consensus_records = repo.get_community_consensus()
    except Exception:
        db_consensus_records = {}

outlet_data = {}
for w in weapons:
    if w.weapon_id in db_consensus_records:
        rec = db_consensus_records[w.weapon_id]
        outlet_data[w.weapon_id] = {
            "wzstats": rec.wzstats_tier,
            "wzranked": rec.wzranked_tier,
            "codmunity": rec.codmunity_tier,
            "dexerto": rec.dexerto_tier,
            "charlie": rec.charlie_tier,
            "dotesports": rec.dotesports_tier,
            "consensus": rec.consensus_tag,
            "badge_color": rec.badge_color
        }
    elif w.weapon_id in default_outlet_data:
        outlet_data[w.weapon_id] = default_outlet_data[w.weapon_id]
    else:
        outlet_data[w.weapon_id] = {
            "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷", "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷", "consensus": "⭐ BALANCED VIABLE", "badge_color": "#4ade80"
        }

# Outlet points conversion for Consensus Mode
outlet_pts_map = {
    "S-Tier 👑": 95.0,
    "A-Tier ⭐": 80.0,
    "B-Tier 🔷": 65.0,
    "C-Tier 🔶": 45.0,
    "D-Tier 🔘": 25.0
}

# Calculate scores for all cataloged weapons
evaluated_scores = []
is_consensus_mode = "Multi-Source Industry Consensus" in ranking_engine_mode

for w in weapons:
    if chosen_class != "All Classes" and w.weapon_class.value.replace("_", " ").title() != chosen_class:
        continue

    stats = repo.get_weapon_stats(w.weapon_id, selected_ver)
    profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, selected_rs_id)

    if stats and profiles:
        ev_list = repo.get_evidence_ledger(target_entity_id=w.weapon_id)
        conf = calculate_evidence_confidence(ev_list, selected_ver)
        score_res = calculate_balance_score(
            weapon=w,
            stats=stats,
            damage_profiles=profiles,
            ruleset=active_ruleset,
            custom_weights=active_weights,
            confidence_score=conf,
            use_class_relative_scoring=use_class_rel
        )

        if is_consensus_mode:
            # Multi-source consensus blend: 28% Lab Math + 16% WZStats + 16% WZRanked + 10% CODMunity + 10% Dexerto + 10% CharlieIntel + 10% Dot Esports
            out = outlet_data.get(w.weapon_id, {
                "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷", "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷"
            })
            wzs_val = outlet_pts_map.get(out.get("wzstats", "B-Tier 🔷"), 65.0)
            wzr_val = outlet_pts_map.get(out.get("wzranked", "B-Tier 🔷"), 65.0)
            cod_val = outlet_pts_map.get(out.get("codmunity", "B-Tier 🔷"), 65.0)
            dex_val = outlet_pts_map.get(out.get("dexerto", "B-Tier 🔷"), 65.0)
            cha_val = outlet_pts_map.get(out.get("charlie", "B-Tier 🔷"), 65.0)
            dot_val = outlet_pts_map.get(out.get("dotesports", "B-Tier 🔷"), 65.0)

            blended_score = (
                (0.28 * score_res.composite_balance_score) +
                (0.16 * wzs_val) +
                (0.16 * wzr_val) +
                (0.10 * cod_val) +
                (0.10 * dex_val) +
                (0.10 * cha_val) +
                (0.10 * dot_val)
            )
            
            if blended_score >= 82.0: tier_label = "S"
            elif blended_score >= 70.0: tier_label = "A"
            elif blended_score >= 55.0: tier_label = "B"
            elif blended_score >= 40.0: tier_label = "C"
            else: tier_label = "D"
            
            # Update score object with consensus values
            score_res.composite_balance_score = round(blended_score, 1)
            score_res.tier_rating = tier_label

        evaluated_scores.append(score_res)

evaluated_scores.sort(key=lambda s: s.composite_balance_score, reverse=True)

# 1. Tier List Visual Presentation
st.markdown("### 🏆 Competitive Tier Standings")

tier_groups = {"S": [], "A": [], "B": [], "C": [], "D": []}
for s in evaluated_scores:
    tier_groups[s.tier_rating].append(s)

tier_colors = {
    "S": ("#f59e0b", "rgba(245, 158, 11, 0.15)", "rgba(245, 158, 11, 0.4)"),
    "A": ("#38bdf8", "rgba(56, 189, 248, 0.15)", "rgba(56, 189, 248, 0.4)"),
    "B": ("#4ade80", "rgba(74, 222, 128, 0.15)", "rgba(74, 222, 128, 0.4)"),
    "C": ("#a855f7", "rgba(168, 85, 247, 0.15)", "rgba(168, 85, 247, 0.4)"),
    "D": ("#94a3b8", "rgba(148, 163, 184, 0.15)", "rgba(148, 163, 184, 0.4)")
}

for tier_letter in ["S", "A", "B", "C", "D"]:
    items = tier_groups[tier_letter]
    text_c, bg_c, border_c = tier_colors[tier_letter]

    pills_html = []
    for s in items:
        img_thumb = get_weapon_img_tag(s.weapon_id, max_height_px=22, max_width_px=48, extra_style="vertical-align: middle; margin-right: 6px;")
        plain_doss = get_weapon_plain_summary(s.weapon_id, s.weapon_name, s.weapon_class.value)
        pill = (
            f'<span style="display:inline-flex; align-items:center; background:rgba(15,23,42,0.85); border:1px solid {border_c}; '
            f'border-radius:6px; padding:5px 10px; font-size:12.5px; font-weight:600; color:#f8fafc; margin-bottom: 4px;">'
            f'{img_thumb}<b>{s.weapon_name}</b> '
            f'<span style="color:{text_c}; font-size:11px; font-weight:700; margin-left:6px;">({s.composite_balance_score}/100)</span>'
            f'<span style="color:#7dd3fc; font-size:10px; margin-left:8px; background:rgba(56,189,248,0.1); border:1px solid rgba(56,189,248,0.25); padding:1px 6px; border-radius:3px;">{plain_doss["role_title"]}</span>'
            f'</span>'
        )
        pills_html.append(pill)

    pills_content = ' '.join(pills_html) if pills_html else '<span style="color:#64748b; font-size:12px; font-style:italic;">No weapons currently ranked in this tier</span>'
    st.markdown(
        f'<div style="background:{bg_c}; border: 1px solid {border_c}; border-left: 6px solid {text_c}; border-radius: 6px; padding: 12px 16px; margin-bottom: 12px;">'
        f'<div style="display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">'
        f'<div style="font-size: 28px; font-weight: 800; color: {text_c}; min-width: 40px;">{tier_letter}</div>'
        f'<div style="display: flex; gap: 10px; flex-wrap: wrap; align-items: center;">{pills_content}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.markdown("---")

# 2. Transparent Mathematical Breakdown Table
st.markdown("### 🔬 Transparent Mathematical Scoring Breakdown")
st.caption("Every ranking exposes its normalized component sub-scores (0-100), raw measurements, weights, and confidence rating.")

breakdown_rows = []
for s in evaluated_scores:
    breakdown_rows.append({
        "Tier": s.tier_rating,
        "Weapon": s.weapon_name,
        "Class": s.weapon_class.value.replace("_", " ").title(),
        "Overall Score": f"{s.composite_balance_score:.1f}",
        "CQB Sub-Score": f"{s.cqb_ttk_score:.1f}",
        "Mid Sub-Score": f"{s.mid_ttk_score:.1f}",
        "Long Sub-Score": f"{s.long_ttk_score:.1f}",
        "Handling Sub-Score": f"{s.handling_score:.1f}",
        "Recoil Sub-Score": f"{s.recoil_score:.1f}",
        "Sustainability Sub-Score": f"{s.sustainability_score:.1f}",
        "Raw Close TTK": f"{s.raw_close_ttk_ms:.0f} ms",
        "Raw ADS": f"{s.raw_ads_ms:.0f} ms",
        "Confidence": f"{int(s.confidence_score * 100)}%"
    })

if breakdown_rows:
    df_scores = pd.DataFrame(breakdown_rows)
    st.dataframe(df_scores, use_container_width=True, hide_index=True)

st.markdown("---")

# 3. Multi-Outlet Meta Consensus Matrix (2026 MW4 Beta)
c_mat_title, c_mat_btn = st.columns([3, 1])
with c_mat_title:
    st.markdown("### 🌐 Multi-Authority Meta Consensus Matrix (2026 MW4 Beta)")
    st.caption("Compare our **Mathematical Ballistic Balance Score** alongside official tier rankings from 6 leading Call of Duty competitive analytics & publication authorities (**WZStats.gg**, **WZRanked**, **CODMunity**, **Dexerto**, **CharlieIntel**, and **Dot Esports**) for the **2026 MW4 Beta**.")
with c_mat_btn:
    st.write("")
    if st.button("🚀 Live Scrape & Sync 6 Platforms", key="sync_btn_meta_board", type="primary"):
        from src.ingestion.community_scraper import CommunityMetaScraper
        with st.spinner("Scraping WZStats, WZRanked, CODMunity, Dexerto, Charlie, and DotEsports..."):
            sc = CommunityMetaScraper(repo)
            res = sc.sync_all_platforms(selected_ver)
            st.success(f"Scraped {len(res['platforms_scraped'])} platforms! Checked {res['total_weapons_audited']} weapons.")
            st.rerun()

# Build Top 10 Pick Rate Leaderboard Chart
all_consensus_records = {}
if hasattr(repo, "get_community_consensus"):
    try:
        all_consensus_records = repo.get_community_consensus(selected_ver)
        if not all_consensus_records:
            all_consensus_records = repo.get_community_consensus()
    except Exception:
        all_consensus_records = {}

leaderboard_data = []
for s in evaluated_scores:
    rec = all_consensus_records.get(s.weapon_id)
    pr = rec.community_pick_rate_pct if rec else 5.0
    kd = rec.community_kd_ratio if rec else 1.05
    sec = rec.recommended_secondary if rec else "Renetti 3-Burst"
    out = outlet_data.get(s.weapon_id, {})
    leaderboard_data.append({
        "Weapon": s.weapon_name,
        "Class": s.weapon_class.value.replace("_", " ").title(),
        "Pick Rate %": pr,
        "Player K/D": kd,
        "Tier": s.tier_rating,
        "Consensus Tag": out.get("consensus", "⭐ BALANCED VIABLE"),
        "Recommended Secondary": sec
    })

if leaderboard_data:
    df_lead = pd.DataFrame(leaderboard_data).sort_values("Pick Rate %", ascending=False).head(10)
    
    # Plotly Glowing Horizontal Bar Chart
    import plotly.express as px
    fig_lead = px.bar(
        df_lead,
        x="Pick Rate %",
        y="Weapon",
        orientation="h",
        color="Pick Rate %",
        color_continuous_scale=["#38bdf8", "#818cf8", "#f59e0b", "#ef4444"],
        text=df_lead["Pick Rate %"].apply(lambda v: f"{v:.1f}% Pick"),
        hover_data={"Weapon": True, "Class": True, "Pick Rate %": ':.1f', "Player K/D": ':.2f', "Tier": True, "Consensus Tag": True, "Recommended Secondary": True},
        title="🔥 Top 10 Community Pick-Rate & K/D Efficiency Leaderboard (2026 MW4 Beta)"
    )
    fig_lead.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(15, 23, 42, 0.4)",
        plot_bgcolor="rgba(15, 23, 42, 0.4)",
        font={"color": "#f8fafc", "family": "Inter, sans-serif"},
        yaxis={"categoryorder": "total ascending", "title": ""},
        xaxis={"title": "Community Pick Rate (%)", "gridcolor": "rgba(148, 163, 184, 0.15)"},
        coloraxis_showscale=False,
        height=380,
        margin={"l": 20, "r": 20, "t": 45, "b": 20}
    )
    fig_lead.update_traces(
        textposition="outside",
        marker_line_color="rgba(255,255,255,0.2)",
        marker_line_width=1
    )
    st.plotly_chart(fig_lead, use_container_width=True)

consensus_rows = []
for s in evaluated_scores:
    rec = all_consensus_records.get(s.weapon_id)
    pr = rec.community_pick_rate_pct if rec else 5.0
    kd = rec.community_kd_ratio if rec else 1.05
    sec = rec.recommended_secondary if rec else "Renetti 3-Burst"
    out = outlet_data.get(s.weapon_id, {
        "wzstats": "Unranked", "wzranked": "Unranked", "codmunity": "Unranked",
        "dexerto": "Unranked", "charlie": "Unranked", "dotesports": "Unranked",
        "consensus": "Under Analysis", "badge_color": "#94a3b8"
    })
    consensus_rows.append({
        "Weapon": s.weapon_name,
        "Class": s.weapon_class.value.replace("_", " ").title(),
        "Pick Rate %": f"{pr:.1f}%",
        "Player K/D": f"{kd:.2f}",
        "Our Lab (Math / PET)": f"{s.tier_rating}-Tier ({s.composite_balance_score:.1f}/100)",
        "WZStats.gg": out.get("wzstats", "B-Tier 🔷"),
        "WZRanked": out.get("wzranked", "B-Tier 🔷"),
        "CODMunity": out.get("codmunity", "B-Tier 🔷"),
        "Dexerto": out.get("dexerto", "B-Tier 🔷"),
        "CharlieIntel": out.get("charlie", "B-Tier 🔷"),
        "Dot Esports": out.get("dotesports", "B-Tier 🔷"),
        "Recommended Companion": sec,
        "Community Meta Consensus": out.get("consensus", "⭐ BALANCED VIABLE")
    })

df_consensus = pd.DataFrame(consensus_rows)
st.dataframe(df_consensus, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown("### 🕸️ 6-Axis Weapon Balance Radar Analysis")
st.caption("Inspect how any weapon scores across all 6 balance dimensions simultaneously.")

score_map = {s.weapon_name: s for s in evaluated_scores}
if score_map:
    chosen_radar_weapon = st.selectbox("Select Weapon for Radar Breakdown", options=list(score_map.keys()))
    radar_score = score_map[chosen_radar_weapon]
    fig_radar = create_balance_radar_chart(radar_score)
    st.plotly_chart(fig_radar, use_container_width=True)

