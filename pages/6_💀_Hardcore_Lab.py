"""
MW4 Weapon Intelligence Lab - Hardcore Tactical Lab
Dedicated 30 HP lethality analysis, 1-shot kill distance breakpoints, and Core vs Hardcore comparison.
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
from src.ui.charts import create_multi_ttk_curve_chart
from src.engines.ttk_engine import generate_ttk_curve, calculate_shots_to_kill


st.set_page_config(page_title="Hardcore Lab - MW4 Intel", page_icon="💀", layout="wide")

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="💀 Hardcore Tactical Lab (30 HP Analytics)",
    subtitle="1-Shot Kill Range Breakpoints, Ultra-Low TTK Dynamics & Side-by-Side Core Comparison",
    active_version=selected_ver,
    active_ruleset="hardcore"
)

# Load hardcore ruleset explicitly
hc_ruleset = repo.get_ruleset("hardcore")
core_ruleset = repo.get_ruleset("core")

if not hc_ruleset or not core_ruleset:
    st.error("Missing Core or Hardcore ruleset definitions in database.")
    st.stop()

weapons = repo.get_weapons()
weapon_map = {w.name: w for w in weapons}

st.markdown(
    '<div class="alert-box"><b>🛡️ Hardcore Analytical Protocol:</b> Target health is strictly fixed at <b>30 HP</b> with zero passive health regeneration. Weapons with damage ≥ 30 deliver instant <b>0 ms 1-Shot Lethality</b>. Range falloff points determine the exact transition to 2-shot lethality.</div>',
    unsafe_allow_html=True
)

# 1. 1-Shot Lethality Roster
st.markdown("### 🎯 1-Shot Kill Range Breakpoints Matrix")

hc_breakdown_rows = []
hc_ttk_curves = []

for w in weapons:
    stats = repo.get_weapon_stats(w.weapon_id, selected_ver)
    hc_profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, "hardcore")
    core_profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, "core")

    if stats and hc_profiles and core_profiles:
        hc_ttk = generate_ttk_curve(
            weapon=w,
            stats=stats,
            profiles=hc_profiles,
            ruleset=hc_ruleset,
            hit_location="chest",
            max_distance_m=80.0
        )
        hc_ttk_curves.append(hc_ttk)

        core_ttk = generate_ttk_curve(
            weapon=w,
            stats=stats,
            profiles=core_profiles,
            ruleset=core_ruleset,
            hit_location="chest",
            max_distance_m=80.0
        )

        max_1shot = hc_ttk.max_1shot_kill_range_m
        has_1shot = max_1shot is not None

        hc_breakdown_rows.append({
            "Weapon": w.name,
            "Class": w.weapon_class.value.replace("_", " ").title(),
            "1-Shot Capable": "✅ YES" if has_1shot else "❌ NO",
            "Max 1-Shot Range": f"{max_1shot:.0f} m" if has_1shot else "N/A (2-Shot Min)",
            "Hardcore Close TTK": f"{hc_ttk.close_range_ttk_ms:.0f} ms",
            "Hardcore Long TTK": f"{hc_ttk.long_range_ttk_ms:.0f} ms",
            "Core Close TTK (100 HP)": f"{core_ttk.close_range_ttk_ms:.0f} ms",
            "STK Core vs HC (Close)": f"{core_ttk.curve_points[5].shots_to_kill} vs {hc_ttk.curve_points[5].shots_to_kill}",
            "ADS Speed": f"{stats.base_ads_ms:.0f} ms",
            "Sprint to Fire": f"{stats.sprint_to_fire_ms:.0f} ms"
        })

if hc_breakdown_rows:
    df_hc = pd.DataFrame(hc_breakdown_rows)
    st.dataframe(df_hc, use_container_width=True, hide_index=True)

st.markdown("---")

# 2. Hardcore TTK Curves Comparison
st.markdown("### 📈 Hardcore Time-To-Kill Step Curves (0 ms = 1-Shot Kill)")
if hc_ttk_curves:
    # Select subset for clarity
    selected_hc_names = st.multiselect(
        "Select Weapons to Plot",
        options=[w.name for w in weapons],
        default=["XM4 Commando", "Rival-9 SpecOps", "BAS-B Battle Rifle", "Longbow Tactical Sniper"],
        key="hc_plot_sel"
    )
    filtered_hc_curves = [c for c in hc_ttk_curves if c.weapon_name in selected_hc_names]
    if filtered_hc_curves:
        fig_hc = create_multi_ttk_curve_chart(
            filtered_hc_curves,
            title="Hardcore (30 HP) TTK vs Distance Step Curves"
        )
        st.plotly_chart(fig_hc, use_container_width=True)

st.markdown("---")

# 3. Interactive Distance Inspection
st.markdown("### 🔍 Interactive Engagement Distance Inspector")
inspect_dist = st.slider("Inspect Distance (m)", min_value=1, max_value=80, value=20, step=1)

dist_inspect_rows = []
for w in weapons:
    stats = repo.get_weapon_stats(w.weapon_id, selected_ver)
    hc_profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, "hardcore")
    core_profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, "core")

    if stats and hc_profiles and core_profiles:
        # Find active HC profile
        hc_active = hc_profiles[-1]
        for p in sorted(hc_profiles, key=lambda x: x.range_start_m):
            if p.range_start_m <= inspect_dist < p.range_end_m:
                hc_active = p
                break

        core_active = core_profiles[-1]
        for p in sorted(core_profiles, key=lambda x: x.range_start_m):
            if p.range_start_m <= inspect_dist < p.range_end_m:
                core_active = p
                break

        hc_stk = calculate_shots_to_kill(30.0, hc_active.damage_chest)
        core_stk = calculate_shots_to_kill(100.0, core_active.damage_chest)
        hc_ttk = 0.0 if hc_stk <= 1 else (hc_stk - 1) * 60000.0 / stats.rpm
        core_ttk = 0.0 if core_stk <= 1 else (core_stk - 1) * 60000.0 / stats.rpm

        dist_inspect_rows.append({
            "Weapon": w.name,
            "Damage at Dist": f"{hc_active.damage_chest:.1f}",
            "Hardcore STK": f"{hc_stk} shot{'s' if hc_stk > 1 else ''}",
            "Hardcore TTK": f"{hc_ttk:.0f} ms",
            "Core STK": f"{core_stk} shots",
            "Core TTK": f"{core_ttk:.0f} ms",
            "Hardcore Lethality Status": "⚡ INSTANT 1-SHOT" if hc_stk == 1 else "⚠️ 2-SHOT REQUIRED"
        })

if dist_inspect_rows:
    st.dataframe(pd.DataFrame(dist_inspect_rows), use_container_width=True, hide_index=True)
