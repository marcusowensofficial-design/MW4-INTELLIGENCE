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

weapons = [w for w in repo.get_weapons() if str(w.weapon_class.value if hasattr(w.weapon_class, "value") else w.weapon_class).lower() not in ("launcher", "melee")]
weapon_map = {w.name: w for w in weapons}

st.markdown(
    '<div class="alert-box"><b>🛡️ Hardcore Analytical Protocol:</b> Target health is strictly fixed at <b>30 HP</b> with zero passive health regeneration. Weapons with damage ≥ 30 deliver instant <b>0 ms 1-Shot Lethality</b>. Range falloff points determine the exact transition to 2-shot lethality.</div>',
    unsafe_allow_html=True
)

# 0. Shareable Squad Rankings Guide (ARs 1-8 & SMGs 1-5)
st.markdown("### 🏆 Shareable Hardcore Rankings: ARs (1–8) & SMGs (1–5) — Why Each Gun Ranks Here")
st.caption("In Hardcore (30 HP, zero regen), rankings are governed by two strict rules: (1) The 30.0 Damage Breakpoint (0 ms 1-Shot Kill vs 2-Shot Kill) and (2) Snap Handling (ADS / Sprint-to-Fire / Strafe).")

tab_hc_ar, tab_hc_smg, tab_hc_share = st.tabs([
    "💀 Hardcore Assault Rifles (Ranked 1–8)",
    "💀 Hardcore SMGs (Ranked 1–5)",
    "📋 Copy-Paste Squad Summary (For Friends / Discord)"
])

with tab_hc_ar:
    st.markdown("Only **3 of the 8 ARs** deal `>= 30` chest damage to achieve a **0 ms 1-Shot Kill** in Hardcore. The remaining 5 ARs require 2 chest shots (though all 8 can 1-tap to the head up close).")
    hc_ar_guide = [
        {"Rank": 1, "Weapon": "Oden", "HC Score": "69.6 (A)", "1-Shot Chest Range": "Infinite (150m+)", "1-Shot Limb Range": "0 – 58.0m", "HC Close TTK": "0 ms (1-Shot)", "Chest Dmg (C/M/L)": "48.0 / 38.0 / 34.0", "ADS / STF": "320 / 210 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Undisputed Hardcore King: Minimum chest damage at max distance is 34.0 (>= 30 HP) — a 1-shot chest kill at any distance on any map and a 1-shot limb kill out to 58m. Stack 100% ADS/STF attachments."},
        {"Rank": 2, "Weapon": "Hyeon Burst", "HC Score": "68.7 (A)", "1-Shot Chest Range": "0 – 32.0m", "1-Shot Limb Range": "0m (28.9 dmg)", "HC Close TTK": "0 ms (1-Shot)", "Chest Dmg (C/M/L)": "34.0 / 28.0 / 24.0", "ADS / STF": "275 / 210 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Snappier 1-Tap Rifle: Deals 34.0 chest damage out to 32.0m, so the very first bullet of the burst kills instantly (0 ms TTK) with faster ADS (275 ms) and 775 m/s velocity."},
        {"Rank": 3, "Weapon": "Kastov 762", "HC Score": "51.9 (C)", "1-Shot Chest Range": "0 – 31.0m (+11%)", "1-Shot Limb Range": "0m (25.5 dmg)", "HC Close TTK": "0 ms (1-Shot)", "Chest Dmg (C/M/L)": "30.0 / 25.0 / 21.0", "ADS / STF": "280 / 210 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Huge Oct 28 Hardcore Winner: Hits the exact 30.0 chest damage breakpoint for a 0 ms 1-shot kill, with range buffed from 28.0m -> 31.0m on Oct 28."},
        {"Rank": 4, "Weapon": "M4", "HC Score": "47.0 (C)", "1-Shot Chest Range": "0m (Head 1-tap to 26.8m)", "1-Shot Limb Range": "0m", "HC Close TTK": "74 ms (2-Shot)", "Chest Dmg (C/M/L)": "24.0 / 20.0 / 17.0", "ADS / STF": "240 / 210 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Best 2-Shot AR: Deals 24.0 chest damage (2-shot body kill), but class-leading 240 ms ADS, 2.51 m/s strafe, and 811 RPM (74 ms 2-tap) make it the fastest-handling AR."},
        {"Rank": 5, "Weapon": "Han 86", "HC Score": "43.9 (C)", "1-Shot Chest Range": "0m (Head 1-tap to 30.0m)", "1-Shot Limb Range": "0m", "HC Close TTK": "81 ms (2-Shot)", "Chest Dmg (C/M/L)": "26.0 / 22.0 / 18.0", "ADS / STF": "250 / 210 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Oct 28 Normalization Kept It 2-Shot: Deals 26.0 chest damage (81 ms 2-tap) with 35.1 headshot 1-taps extended out to 30.0m."},
        {"Rank": 6, "Weapon": "Axion", "HC Score": "37.3 (D)", "1-Shot Chest Range": "0m (Head 1-tap to 45.0m)", "1-Shot Limb Range": "0m", "HC Close TTK": "85 ms (2-Shot)", "Chest Dmg (C/M/L)": "28.0 / 24.0 / 20.0", "ADS / STF": "260 / 210 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "28 Damage Heartbreaker: Dominant in Core, but falls 2 HP short of a Hardcore 1-shot chest kill (28.0 dmg) and has slow 400 m/s subsonic velocity."},
        {"Rank": 7, "Weapon": "Cronen Squall", "HC Score": "37.3 (D)", "1-Shot Chest Range": "0m (Head 1-tap to 54.0m)", "1-Shot Limb Range": "0m", "HC Close TTK": "89 ms (2-Shot)", "Chest Dmg (C/M/L)": "29.0 / 24.0 / 21.0", "ADS / STF": "305 / 210 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "The 29.0 Damage Trap: Deals 29.0 chest damage (leaving 30 HP enemies on 1 HP!), requiring 2 body shots (89 ms) with sluggish 305 ms ADS."},
        {"Rank": 8, "Weapon": "Patriot XMR", "HC Score": "29.5 (D)", "1-Shot Chest Range": "0m (Head 1-tap to 48.0m)", "1-Shot Limb Range": "0m", "HC Close TTK": "93 ms (2-Shot)", "Chest Dmg (C/M/L)": "27.0 / 23.0 / 19.0", "ADS / STF": "280 / 210 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Core God -> Hardcore Bottom: Deals 27.0 chest damage at 645 RPM (93 ms TTK — slowest 2-tap among ARs) with 280 ms ADS."}
    ]
    st.dataframe(pd.DataFrame(hc_ar_guide), use_container_width=True, hide_index=True)

with tab_hc_smg:
    st.markdown("None of the 5 SMGs deal `>= 30` chest damage (all require 2 body shots), **EXCEPT** the Oct 28 limb buff (`0.95x -> 1.0x`) guarantees that every SMG now 2-taps even on arm/hand hits out to mid-range (`>= 15.0` damage).")
    hc_smg_guide = [
        {"Rank": 1, "Weapon": "VEL 46", "HC Score": "58.9 (B)", "1-Shot Headshot Range": "0 – 15.0m (31.1 dmg)", "2-Shot Body/Limb Range": "Infinite (150m+)", "HC Close TTK": "63 ms (2-Shot)", "Chest/Limb Dmg (C/M/L)": "23.0 / 19.0 / 15.0", "ADS / STF": "230 / 110 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "#1 Hardcore SMG: 230 ms ADS, 110 ms STF, 952 RPM (63 ms 2-tap), 1-shot headshot kill (31.1 dmg) out to 15m, and 15.0 min damage (never drops to a 3-shot kill at any distance, even on limbs!)."},
        {"Rank": 2, "Weapon": "ISO Nightshade", "HC Score": "56.4 (B)", "1-Shot Headshot Range": "0m (29.7 head dmg)", "2-Shot Body/Limb Range": "Infinite (150m+)", "HC Close TTK": "65 ms (2-Shot)", "Chest/Limb Dmg (C/M/L)": "22.0 / 18.0 / 15.0", "ADS / STF": "240 / 110 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Co-#1 Run-and-Gun Laser: Minimum damage is 15.0 across the entire map (guaranteed 2-shot kill at all ranges on chest or arms after the Oct 28 1.0x limb buff) with 65 ms TTK."},
        {"Rank": 3, "Weapon": "X-58 Nyx", "HC Score": "46.7 (C)", "1-Shot Headshot Range": "0m (28.6 head dmg)", "2-Shot Body/Limb Range": "0 – 27.0m", "HC Close TTK": "75 ms (2-Shot)", "Chest/Limb Dmg (C/M/L)": "22.0 / 17.0 / 14.0", "ADS / STF": "255 / 110 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Top Stealth Flanker: Fast 3.26 m/s ADS strafe and 75 ms 2-shot kill out to 27.0m (thanks to the Oct 28 1.0x limb buff), dropping to 14.0 damage (3 shots) past 27m."},
        {"Rank": 4, "Weapon": "PPSh-41", "HC Score": "46.5 (C)", "1-Shot Headshot Range": "0m (24.3 head dmg)", "2-Shot Body/Limb Range": "0 – 24.0m", "HC Close TTK": "54 ms (2-Shot)", "Chest/Limb Dmg (C/M/L)": "18.0 / 15.0 / 12.0", "ADS / STF": "280 / 110 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Fastest 2-Tap (54 ms), Slowest ADS: 1110 RPM gives a 54 ms 2-shot kill to 24m (Oct 28 buffed ADS 300->280 ms and mid-range limb damage to 15.0), but 280 ms ADS is slower to snap than VEL/ISO."},
        {"Rank": 5, "Weapon": "Wz.55 Striga", "HC Score": "29.5 (D)", "1-Shot Headshot Range": "0 – 17.1m (37.8 dmg)", "2-Shot Body/Limb Range": "Infinite (150m+)", "HC Close TTK": "92 ms (2-Shot)", "Chest/Limb Dmg (C/M/L)": "28.0 / 22.0 / 18.0", "ADS / STF": "196 / 96 ms", "Why It Ranks Here (Post-Oct 28 Patch)": "Secret Headshot Specialist: Ranked #5 in composite score due to 651 RPM (92 ms 2-shot body TTK), but has the fastest handling in the game (196 ms ADS / 96 ms STF) and a 0 ms 1-shot headshot kill (37.8 dmg) out to 17.1m!"}
    ]
    st.dataframe(pd.DataFrame(hc_smg_guide), use_container_width=True, hide_index=True)

with tab_hc_share:
    st.markdown("Click the **Copy** icon in the top-right corner of the box below to paste this directly into Discord or group chat:")
    st.code(
        """🎯 MW4 HARDCORE (30 HP) AR & SMG RANKINGS (v1.3.1-patch1 • Updated 10/30/2026) 🎯

💀 HARDCORE ASSAULT RIFLES (1 = Best to 8 = Worst)
1. Oden (0ms 1-Shot) — 48->34 chest dmg = Infinite 1-shot chest kill at any distance + 1-shots limbs to 58m. Stack 100% ADS/STF!
2. Hyeon Burst (0ms 1-Shot) — 34 chest dmg to 32m = 1st bullet of burst 1-taps with faster 275ms ADS & 775m/s velocity.
3. Kastov 762 (0ms 1-Shot) — 30.0 chest dmg = 1-shot kill out to 31m (buffed +11% on Oct 28).
4. M4 (74ms 2-Shot) — 24 chest dmg (2-shot), fastest AR handling (240ms ADS / 811 RPM) + 1-tap headshots to 26.8m.
5. Han 86 (81ms 2-Shot) — 26 chest dmg after Oct 28 1.0x torso normalization; 1-tap headshots to 30m.
6. Axion (85ms 2-Shot) — 28 chest dmg (falls 2 HP short of 1-shot) + slow 400m/s velocity.
7. Cronen Squall (89ms 2-Shot) — 29.0 chest dmg trap (leaves enemies at 1 HP!) + slow 305ms ADS.
8. Patriot XMR (93ms 2-Shot) — 27 chest dmg at 645 RPM = slowest 2-shot TTK among ARs in Hardcore.

💀 HARDCORE SMGs (1 = Best to 5 = Worst)
1. VEL 46 (63ms 2-Shot) — #1 HC SMG: 230ms ADS, 110ms STF, 1-shot headshot to 15m (31.1 dmg) & 15.0 min dmg (infinite 2-shot body/limb kill!).
2. ISO Nightshade (65ms 2-Shot) — Infinite 2-shot body/limb kill (15.0 min dmg) after Oct 28 1.0x limb buff.
3. X-58 Nyx (75ms 2-Shot) — 3.26m/s ADS strafe & 2-shot kill out to 27m.
4. PPSh-41 (54ms 2-Shot) — Fastest 2-tap (1110 RPM, ADS buffed to 280ms), but slowest ADS among SMGs.
5. Wz.55 Striga (92ms 2-Shot / 0ms HS) — Slow 651 RPM body TTK, but fastest ADS in game (196ms) & 1-shot headshot (37.8 dmg) to 17.1m!

💡 TL;DR CLASS TAKEAWAY:
• Best Hardcore AR: Oden (or Kastov 762 / Hyeon Burst) with 100% ADS + Sprint-to-Fire attachments.
• Best Hardcore SMG: VEL 46 (110ms STF, 1-taps head to 15m, guaranteed 63ms 2-shot kill everywhere else).""",
        language="markdown"
    )

st.markdown("---")

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
    all_hc_options = [w.name for w in weapons]
    default_hc = [n for n in ["Patriot XMR", "ISO Nightshade", "Hyeon Burst", "M4"] if n in all_hc_options]
    if not default_hc and all_hc_options:
        default_hc = all_hc_options[:4]
    selected_hc_names = st.multiselect(
        "Select Weapons to Plot",
        options=all_hc_options,
        default=default_hc,
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
