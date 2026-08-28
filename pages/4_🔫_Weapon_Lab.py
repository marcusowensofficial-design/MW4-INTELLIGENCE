"""
MW4 Weapon Intelligence Lab - Weapon Lab & Ballistics Inspector
Interactive TTK curves, Practical Engagement Time breakdown, and Evidence Provenance.
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
from src.ui.charts import (
    create_multi_ttk_curve_chart,
    create_practical_engagement_stacked_chart,
    create_balance_radar_chart
)
from src.engines.ttk_engine import (
    generate_ttk_curve,
    calculate_shots_to_kill,
    calculate_theoretical_ttk_ms,
    calculate_headshots_for_stk_reduction
)
from src.engines.engagement_engine import calculate_practical_engagement_time
from src.engines.balance_scorer import calculate_balance_score
from src.engines.confidence_scorer import calculate_evidence_confidence
from src.ui.plain_english import (
    get_weapon_plain_summary,
    get_weapon_star_ratings,
    render_field_intel_box
)


st.set_page_config(page_title="Weapon Lab - MW4 Intel", page_icon="🔫", layout="wide")

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="🔫 Weapon Lab & Ballistics Inspector",
    subtitle="Theoretical TTK Curves, Practical Engagement Latency, and Evidence Provenance",
    active_version=selected_ver,
    active_ruleset=selected_rs_id
)

weapons = repo.get_weapons()
if not weapons:
    st.warning("No weapons found in database. Please seed or import data in Data Admin.")
    st.stop()

# Field Intel Explainer
render_field_intel_box(
    title="How to Analyze Weapon Ballistics & Step Curves",
    text="• <b>Continuous Step Curves:</b> The lower the colored line on the graph, the faster that weapon eliminates opponents at that distance.<br>"
         "• <b>Damage Dropoffs:</b> When a line steps upwards, the weapon has reached its range limit and requires +1 extra bullet to kill.",
    tip="Assault rifles maintain flat lines out to 30m+, while SMGs melt up close (0-15m) but drop off sharply at longer distances."
)

# Weapon selection & controls
col_sel, col_hit, col_dist, col_mode = st.columns([2, 1, 1, 1])

weapon_names = {w.name: w for w in weapons}

with col_sel:
    selected_weapon_names = st.multiselect(
        "Select Weapons to Compare",
        options=list(weapon_names.keys()),
        default=list(weapon_names.keys())[:3] if len(weapon_names) >= 3 else list(weapon_names.keys()),
        help="Select up to 4 weapons for simultaneous analytical comparison."
    )

with col_hit:
    hit_loc = st.selectbox(
        "Target Hit Location",
        options=["chest", "head", "neck", "stomach", "limbs", "composite"],
        format_func=lambda x: {
            "chest": "Chest / Upper Torso",
            "head": "Headshot (1.4x)",
            "neck": "Neck (1.25x)",
            "stomach": "Stomach (1.0x)",
            "limbs": "Limbs (0.9x)",
            "composite": "Realistic Composite Blend"
        }.get(x, x.title()),
        help="Applies hit-location damage multipliers across distance brackets."
    )

with col_dist:
    max_dist = st.slider("Max Distance (m)", min_value=30, max_value=120, value=75, step=5)

with col_mode:
    st.write("")
    use_impact_ttk_toggle = st.checkbox("Include Bullet Flight Time (Impact TTK)", value=False, help="Adds projectile flight latency (Distance / Bullet Velocity) to theoretical TTK.")

if not selected_weapon_names:
    st.info("Please select at least one weapon above.")
    st.stop()

# Generate TTK curves
ttk_results = []
pet_results = []
balance_results = []

for w_name in selected_weapon_names:
    w = weapon_names[w_name]
    stats = repo.get_weapon_stats(w.weapon_id, selected_ver)
    profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, selected_rs_id)

    if stats and profiles:
        ttk_res = generate_ttk_curve(
            weapon=w,
            stats=stats,
            profiles=profiles,
            ruleset=active_ruleset,
            hit_location=hit_loc,
            max_distance_m=float(max_dist)
        )
        ttk_results.append(ttk_res)

        # Engagement time at 15m
        pet_res = calculate_practical_engagement_time(
            reaction_ms=200.0,
            ads_ms=stats.base_ads_ms,
            sprint_to_fire_ms=stats.sprint_to_fire_ms,
            theoretical_ttk_ms=ttk_res.close_range_ttk_ms,
            stk=ttk_res.curve_points[15].shots_to_kill if len(ttk_res.curve_points) > 15 else 4,
            rpm=stats.rpm,
            accuracy=0.72,
            is_sprinting=True,
            weapon_id=w.weapon_id,
            weapon_name=w.name,
            distance_m=15.0
        )
        pet_results.append(pet_res)

        ev_list = repo.get_evidence_ledger(target_entity_id=w.weapon_id)
        conf = calculate_evidence_confidence(ev_list, selected_ver)
        bal_res = calculate_balance_score(w, stats, profiles, active_ruleset, confidence_score=conf)
        balance_results.append(bal_res)

# 1. Main TTK Curve Plot
if ttk_results:
    st.markdown("### 📈 Continuous Time-To-Kill Step Curves")
    
    # Headshot STK reduction threshold badges
    hs_cols = st.columns(len(ttk_results))
    for i, t_res in enumerate(ttk_results):
        with hs_cols[i]:
            if t_res.headshots_for_stk_drop is not None:
                st.markdown(
                    f'<div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 6px; padding: 6px 10px; margin-bottom: 8px;">'
                    f'<span style="color:#38bdf8; font-size:12px; font-weight:600;">🎯 {t_res.weapon_name}:</span>'
                    f'<span style="color:#cbd5e1; font-size:11px;"> <b>{t_res.headshots_for_stk_drop} Headshot</b> drops STK by -1 shot at close range</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div style="background: rgba(148, 163, 184, 0.08); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 6px; padding: 6px 10px; margin-bottom: 8px;">'
                    f'<span style="color:#94a3b8; font-size:12px; font-weight:600;">🎯 {t_res.weapon_name}:</span>'
                    f'<span style="color:#94a3b8; font-size:11px;"> Flat STK (Headshots don\'t reduce shots needed)</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )

    fig_ttk = create_multi_ttk_curve_chart(
        ttk_results,
        title=f"{'Impact TTK (with Flight Time)' if use_impact_ttk_toggle else 'Theoretical Fire TTK'} vs Distance ({active_ruleset.name} • Hitbox: {hit_loc.title()})",
        use_impact_ttk=use_impact_ttk_toggle
    )
    st.plotly_chart(fig_ttk, use_container_width=True)

st.markdown("---")

# 2. Practical Engagement Time Breakdown & Controls
st.markdown("### ⏱️ Practical Engagement Latency (Human Performance Engine)")
render_field_intel_box(
    title="Real-World Gunfight Speed (Practical Engagement Time)",
    text="In real multiplayer matches, gunfights aren't just about theoretical bullet damage. You have to spot the enemy, aim down sights (ADS Speed), recover from running (Sprint-to-Fire), and land your shots.<br>"
         "• <b>Stacked Latency:</b> This chart combines your human reaction time + weapon handling + bullet TTK.<br>"
         "• <b>Miss Penalty:</b> If your accuracy is under 100%, each missed shot adds time based on how fast the weapon cycles.",
    tip="If you get caught sprinting into rooms often, equip Sprint-to-Fire attachments (DR-6 Handstop / Lasers) to cut down your draw time!"
)

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    react_slider = st.slider("Human Reaction Latency (ms)", min_value=140, max_value=300, value=200, step=10)
with col_p2:
    acc_slider = st.slider("Player Accuracy (%)", min_value=40, max_value=100, value=72, step=2) / 100.0
with col_p3:
    sprint_mode = st.selectbox(
        "Engage Movement State",
        options=["⚡ Standard Sprint", "🚀 Tactical Super-Sprint", "🏃 Walking / Pre-Aim (Already ADS)"],
        index=0
    )

is_sprint = (sprint_mode != "🏃 Walking / Pre-Aim (Already ADS)")
is_tac = (sprint_mode == "🚀 Tactical Super-Sprint")
is_ads = (sprint_mode == "🏃 Walking / Pre-Aim (Already ADS)")

# Recompute PET with user settings & concurrent handling
dynamic_pets = []
for idx, w_name in enumerate(selected_weapon_names):
    w = weapon_names[w_name]
    stats = repo.get_weapon_stats(w.weapon_id, selected_ver)
    if stats and idx < len(ttk_results):
        t_res = ttk_results[idx]
        tac_stf = getattr(stats, "tactical_sprint_to_fire_ms", round(stats.sprint_to_fire_ms * 1.35, 1))
        d_pet = calculate_practical_engagement_time(
            reaction_ms=float(react_slider),
            ads_ms=stats.base_ads_ms,
            sprint_to_fire_ms=stats.sprint_to_fire_ms,
            theoretical_ttk_ms=t_res.close_range_ttk_ms,
            stk=t_res.curve_points[15].shots_to_kill if len(t_res.curve_points) > 15 else 4,
            rpm=stats.rpm,
            accuracy=acc_slider,
            is_sprinting=is_sprint,
            is_already_ads=is_ads,
            is_tactical_sprint=is_tac,
            tactical_sprint_to_fire_ms=tac_stf,
            concurrent_handling=True,
            weapon_id=w.weapon_id,
            weapon_name=w.name,
            distance_m=15.0
        )
        dynamic_pets.append(d_pet)

if dynamic_pets:
    fig_pet = create_practical_engagement_stacked_chart(
        dynamic_pets,
        title=f"Practical Engagement Time Breakdown ({sprint_mode} • Accuracy: {int(acc_slider*100)}%)"
    )
    st.plotly_chart(fig_pet, use_container_width=True)

st.markdown("---")

# 3. Balance Radar Profiles & Primary Weapon Deep-Dive
st.markdown("### 🔬 Primary Weapon Deep-Dive & Evidence Provenance")

primary_name = st.selectbox("Select Primary Weapon for Deep Audit", options=selected_weapon_names)
primary_weapon = weapon_names[primary_name]
primary_stats = repo.get_weapon_stats(primary_weapon.weapon_id, selected_ver)
primary_profiles = repo.get_damage_profiles(primary_weapon.weapon_id, selected_ver, selected_rs_id)

if primary_stats and primary_profiles:
    plain_doss = get_weapon_plain_summary(primary_weapon.weapon_id, primary_weapon.name, primary_weapon.weapon_class.value)
    stars = get_weapon_star_ratings(primary_stats, primary_weapon.weapon_class)
    
    # Plain English Summary Card
    st.markdown(
        f'<div style="background: rgba(15, 23, 42, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-left: 5px solid #38bdf8; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;">'
        f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">'
        f'<div>'
        f'<span style="background: rgba(56, 189, 248, 0.15); color:#38bdf8; border:1px solid rgba(56, 189, 248, 0.4); border-radius:4px; padding:2px 8px; font-size:11px; font-weight:700;">{plain_doss.get("role_title", "Weapon Platform")}</span>'
        f'<h3 style="color:#ffffff; margin:6px 0 2px 0; font-size:18px;">{primary_weapon.name}</h3>'
        f'<p style="color:#cbd5e1; font-size:13px; margin:0 0 8px 0;">{plain_doss.get("summary", "")}</p>'
        f'<p style="color:#94a3b8; font-size:12px; margin:0;">🎯 <b>Best For:</b> {plain_doss.get("best_for", "")}</p>'
        f'</div>'
        f'<div style="background: rgba(30, 41, 59, 0.6); border: 1px solid rgba(148, 163, 184, 0.2); border-radius: 6px; padding: 8px 14px; text-align: right;">'
        f'<div style="font-size: 11px; color: #94a3b8; text-transform: uppercase; font-weight: 700;">Ease of Use</div>'
        f'<div style="font-size: 14px; color: #4ade80; font-weight: 700;">{plain_doss.get("ease_label", "⭐⭐⭐⭐☆ Easy")}</div>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    col_rad, col_stat = st.columns([1, 1])

    ev_list = repo.get_evidence_ledger(target_entity_id=primary_weapon.weapon_id)
    conf = calculate_evidence_confidence(ev_list, selected_ver)
    bal_score = calculate_balance_score(primary_weapon, primary_stats, primary_profiles, active_ruleset, confidence_score=conf)

    with col_rad:
        fig_radar = create_balance_radar_chart(bal_score)
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_stat:
        st.markdown(f"#### 📊 Physical Stats & Ratings ({primary_weapon.name})")
        
        # Star ratings summary row
        st.markdown(
            f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-bottom: 12px;">'
            f'<div style="background: rgba(30, 41, 59, 0.5); padding: 6px 10px; border-radius: 6px; font-size: 11.5px;"><span style="color:#94a3b8;">⚡ Kill Speed:</span> <b style="color:#ffffff;">{stars["kill_speed"][1]}</b></div>'
            f'<div style="background: rgba(30, 41, 59, 0.5); padding: 6px 10px; border-radius: 6px; font-size: 11.5px;"><span style="color:#94a3b8;">🎯 Aim Ease (Recoil):</span> <b style="color:#4ade80;">{stars["ease_of_control"][1]}</b></div>'
            f'<div style="background: rgba(30, 41, 59, 0.5); padding: 6px 10px; border-radius: 6px; font-size: 11.5px;"><span style="color:#94a3b8;">🏃 Scope-In Speed:</span> <b style="color:#ffffff;">{stars["quick_aim_speed"][1]}</b></div>'
            f'<div style="background: rgba(30, 41, 59, 0.5); padding: 6px 10px; border-radius: 6px; font-size: 11.5px;"><span style="color:#94a3b8;">🔭 Long Range Power:</span> <b style="color:#ffffff;">{stars["long_range_power"][1]}</b></div>'
            f'</div>',
            unsafe_allow_html=True
        )

        add_ammo_val = primary_stats.reload_add_ammo_s if getattr(primary_stats, "reload_add_ammo_s", 0.0) > 0 else round(primary_stats.reload_tactical_s * 0.68, 2)
        swap_raise_val = getattr(primary_stats, "swap_speed_raise_ms", 350.0) or 350.0
        swap_stow_val = getattr(primary_stats, "swap_speed_stow_ms", 250.0) or 250.0
        tac_sprint_val = getattr(primary_stats, "tac_sprint_speed_mps", round(primary_stats.move_speed_mps * 1.32, 2)) or 6.8
        
        base_chest_dmg = primary_profiles[0].damage_chest if primary_profiles else 30.0
        total_mag_dmg = round(primary_weapon.base_mag_size * base_chest_dmg, 1)
        close_stk_calc = calculate_shots_to_kill(active_ruleset.target_health, base_chest_dmg, active_ruleset.min_stk_cap)
        kills_per_mag_calc = round(primary_weapon.base_mag_size / max(1, close_stk_calc), 1)

        stat_items = [
            {"Metric": "Fire Rate (RPM)", "Value": f"{primary_stats.rpm} RPM"},
            {"Metric": "Quick-Aim Speed (ADS)", "Value": f"{primary_stats.base_ads_ms} ms"},
            {"Metric": "Sprint-to-Shoot Time", "Value": f"{primary_stats.sprint_to_fire_ms} ms"},
            {"Metric": "⚡ Add-Ammo Reload (Sprint Cancel)", "Value": f"{add_ammo_val:.2f} s (Full: {primary_stats.reload_tactical_s}s)"},
            {"Metric": "⚡ Fast-Swap Speed (Raise / Stow)", "Value": f"{swap_raise_val:.0f} ms / {swap_stow_val:.0f} ms"},
            {"Metric": "💥 Magazine Lethality Capacity", "Value": f"{kills_per_mag_calc} Kills ({total_mag_dmg} Total DMG)"},
            {"Metric": "🏃 Tac-Sprint / Base Sprint", "Value": f"{tac_sprint_val:.2f} m/s / {primary_stats.move_speed_mps:.2f} m/s"},
            {"Metric": "Bullet Velocity", "Value": f"{primary_stats.bullet_velocity_mps} m/s"},
            {"Metric": "Gun Kick / Recoil (H / V)", "Value": f"{primary_stats.recoil_horizontal} / {primary_stats.recoil_vertical}"},
            {"Metric": "Strafe Move Speed", "Value": f"{primary_stats.ads_move_speed_mps} m/s"}
        ]
        st.dataframe(pd.DataFrame(stat_items), use_container_width=True, hide_index=True)

    # Dynamic Hitbox Combo TTK Simulator
    st.markdown("#### 🎯 Interactive Hitbox Combo & Damage Calculator")
    st.caption("Test custom bullet combinations (e.g. 1 Head + 3 Chest) to calculate exact blended damage and lethal TTK thresholds at any distance.")

    hc_col1, hc_col2 = st.columns([1, 2])
    with hc_col1:
        combo_dist = st.slider("Target Distance (m)", 1, 80, 15, key="combo_dist_slider")
        # Get active damage profile bracket for combo_dist
        active_p = next((p for p in primary_profiles if p.range_start_m <= combo_dist < p.range_end_m), primary_profiles[-1])
        st.markdown(f"**Active Range Bracket:** `{active_p.range_start_m:.0f}m - {active_p.range_end_m:.0f}m`")
        
        c_h1, c_h2 = st.columns(2)
        with c_h1:
            n_head = st.number_input("Headshots 🎯", min_value=0, max_value=10, value=1, step=1)
            n_neck = st.number_input("Neck Shots 🧣", min_value=0, max_value=10, value=0, step=1)
            n_chest = st.number_input("Chest Shots 🦺", min_value=0, max_value=10, value=3, step=1)
        with c_h2:
            n_stom = st.number_input("Stomach Shots 🥋", min_value=0, max_value=10, value=0, step=1)
            n_limbs = st.number_input("Limb Shots 🦵", min_value=0, max_value=10, value=0, step=1)

    total_combo_shots = n_head + n_neck + n_chest + n_stom + n_limbs
    total_combo_damage = (
        (n_head * active_p.damage_head) +
        (n_neck * active_p.damage_neck) +
        (n_chest * active_p.damage_chest) +
        (n_stom * active_p.damage_stomach) +
        (n_limbs * active_p.damage_limbs)
    )
    target_hp = active_ruleset.target_health
    is_lethal = total_combo_damage >= target_hp
    obd_ms = getattr(primary_stats, "open_bolt_delay_ms", 0.0) or 0.0
    combo_ttk_ms = 0.0 if total_combo_shots <= 1 else ((total_combo_shots - 1) * 60000.0 / primary_stats.rpm) + obd_ms

    with hc_col2:
        st.markdown("##### 📊 Combat Outcome Analysis")
        if is_lethal:
            rem_hp = 0.0
            st.success(f"☠️ **LETHAL ELIMINATION CONFIRMED** — Total Damage: **{total_combo_damage:.1f} / {target_hp} HP**")
        else:
            rem_hp = target_hp - total_combo_damage
            st.warning(f"⚠️ **ENEMY SURVIVED** — Total Damage: **{total_combo_damage:.1f} / {target_hp} HP** ({rem_hp:.1f} HP Remaining)")

        st.progress(min(1.0, total_combo_damage / target_hp))

        # Metrics display
        m_c1, m_c2, m_c3 = st.columns(3)
        with m_c1:
            st.metric("Total Bullets Fired", f"{total_combo_shots} Shots")
        with m_c2:
            st.metric("Combo Fire TTK", f"{combo_ttk_ms:.1f} ms" if is_lethal else "N/A (Survives)")
        with m_c3:
            pure_chest_stk = calculate_shots_to_kill(target_hp, active_p.damage_chest, active_ruleset.min_stk_cap)
            stk_diff = pure_chest_stk - total_combo_shots
            if is_lethal:
                if stk_diff > 0:
                    st.metric("STK Advantage", f"-{stk_diff} Shot ({stk_diff * (60000.0 / primary_stats.rpm):.0f}ms faster)", delta=f"-{stk_diff} STK")
                elif stk_diff == 0:
                    st.metric("STK Match", "Same as Chest STK")
                else:
                    st.metric("STK Disadvantage", f"+{-stk_diff} Extra Shots", delta=f"+{-stk_diff} STK", delta_color="inverse")
            else:
                st.metric("Status", f"Needs {calculate_shots_to_kill(rem_hp, active_p.damage_chest, 1)} more shots")

    st.markdown("---")

    # Damage brackets table
    st.markdown("#### 🎯 Damage Falloff Profile Matrix")
    bracket_rows = [
        {
            "Range Bracket": f"{p.range_start_m:.0f}m - {p.range_end_m:.0f}m",
            "Headshot": f"{p.damage_head:.1f}",
            "Neck": f"{p.damage_neck:.1f}",
            "Chest": f"{p.damage_chest:.1f}",
            "Stomach": f"{p.damage_stomach:.1f}",
            "Limbs": f"{p.damage_limbs:.1f}",
            "Chest STK": calculate_shots_to_kill(active_ruleset.target_health, p.damage_chest, active_ruleset.min_stk_cap),
            "Chest TTK": f"{((calculate_shots_to_kill(active_ruleset.target_health, p.damage_chest, active_ruleset.min_stk_cap) - 1) * 60000.0 / primary_stats.rpm):.1f} ms"
        }
        for p in primary_profiles
    ]
    st.dataframe(pd.DataFrame(bracket_rows), use_container_width=True, hide_index=True)

    # Evidence ledger entries
    st.markdown("#### 📜 Evidence Ledger & Provenance Records")
    if ev_list:
        ev_rows = [
            {
                "Evidence ID": e.evidence_id,
                "Field": e.field_name,
                "Observed Value": e.observed_value,
                "Source Tier": e.source_tier.value.upper(),
                "Source Name": e.source_name,
                "Test Method": e.test_method,
                "Confidence": f"{int(e.confidence_score * 100)}%",
                "Captured": e.captured_timestamp[:10],
                "Source URL": e.source_url
            }
            for e in ev_list
        ]
        st.dataframe(pd.DataFrame(ev_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No explicit evidence entries recorded yet for this weapon. Stats are operating under default baseline.")
