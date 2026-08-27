"""
MW4 Weapon Intelligence Lab - Fastest TTK Leaderboard
Dedicated real-time leaderboard ranking every weapon by theoretical TTK, True Impact TTK,
and Optimal Headshot TTK across all engagement distance brackets with tactical weapon graphics.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.ui.theme import render_page_header, DARK_LAYOUT
from src.ui.state import init_session_state, render_sidebar_controls
from src.ui.weapon_graphics import render_weapon_podium_card
from src.engines.ttk_engine import (
    calculate_shots_to_kill,
    calculate_theoretical_ttk_ms,
    get_damage_at_distance,
    calculate_headshots_for_stk_reduction
)
from src.database.models import WeaponClass
from src.ui.plain_english import render_field_intel_box, get_weapon_plain_summary


st.set_page_config(page_title="Fastest TTK - MW4 Intel", page_icon="⚡", layout="wide")

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="⚡ Fastest Time-to-Kill (TTK) Leaderboard",
    subtitle="Definitive Ranking of the Fastest Killing Weapons in Modern Warfare 4 Beta Across All Distances",
    active_version=selected_ver,
    active_ruleset=selected_rs_id
)

weapons = repo.get_weapons()
if not weapons:
    st.warning("No weapons found in database.")
    st.stop()

# Load Core and Hardcore rulesets
core_ruleset = repo.get_ruleset("core") or active_ruleset
hc_ruleset = repo.get_ruleset("hardcore") or active_ruleset

# Field Intel Explainer Box
render_field_intel_box(
    title="How Time-To-Kill (TTK) & Shots-To-Kill (STK) Work",
    text="<b>Time-to-Kill (TTK)</b> is the exact number of milliseconds it takes to eliminate an enemy.<br>"
         "• <b>Lower number = Faster Kill:</b> A weapon with <b>200ms TTK</b> deletes opponents much faster than a <b>280ms TTK</b> weapon.<br>"
         "• <b>Shots-to-Kill (STK):</b> The exact number of bullets you must connect on target (e.g. 1 shot, 2 shots, 3 shots, 4 shots).<br>"
         "• <b>Core (100 HP) vs Hardcore (30 HP):</b> Switch using the button bar below to see how many shots it takes to kill in Hardcore vs Core!",
    tip="Use the Core / Hardcore buttons below to toggle between 100 HP and 30 HP, or select 'Side-by-Side' to view both simultaneously!"
)

# ---------------------------------------------------------------------------
# 1. Primary Health Mode & Filter Controls
# ---------------------------------------------------------------------------
st.markdown("#### 🎮 1. Select Game Mode & Health Ruleset")

mode_options = [
    "🟢 Core Mode (100 HP Standard Health)",
    "💀 Hardcore Mode (30 HP High Lethality)",
    "⚔️ Core vs Hardcore (Side-by-Side Comparison)"
]
default_mode = mode_options[0] if selected_rs_id != "hardcore" else mode_options[1]

if hasattr(st, "segmented_control"):
    mode_radio = st.segmented_control(
        "Active Health Mode:",
        options=mode_options,
        default=default_mode,
        help="Switches all ballistics calculations between 100 HP Core and 30 HP Hardcore."
    ) or default_mode
else:
    mode_radio = st.radio(
        "Active Health Mode:",
        options=mode_options,
        index=0 if selected_rs_id != "hardcore" else 1,
        horizontal=True,
        help="Switches all ballistics calculations between 100 HP Core and 30 HP Hardcore."
    )

is_side_by_side = "Side-by-Side" in mode_radio
is_hc_mode = "Hardcore" in mode_radio and not is_side_by_side
active_mode_label = "Hardcore (30 HP)" if is_hc_mode else ("Core vs Hardcore" if is_side_by_side else "Core (100 HP)")
target_health_eval = 30.0 if is_hc_mode else 100.0
eval_ruleset = hc_ruleset if is_hc_mode else core_ruleset

st.markdown("#### 🎯 2. Weapon Class & Hitbox Filters")
c1, c2, c3 = st.columns([1.8, 1.2, 1.2])

with c1:
    available_classes = sorted(list({w.weapon_class.value.replace("_", " ").title() for w in weapons}))
    if hasattr(st, "pills"):
        selected_classes = st.pills(
            "Weapon Class Filter",
            options=available_classes,
            default=available_classes,
            selection_mode="multi",
            help="Select one or more weapon classes to compare side-by-side."
        ) or available_classes
    else:
        selected_classes = st.multiselect(
            "Weapon Class Filter",
            options=available_classes,
            default=available_classes,
            help="Select one or more weapon classes to compare side-by-side."
        )

with c2:
    hit_location = st.selectbox(
        "Target Hitbox",
        options=["chest", "head", "neck", "stomach", "limbs"],
        index=0,
        format_func=lambda x: {
            "chest": "Chest / Upper Torso (Standard)",
            "head": "Headshot Only (Skill Ceiling)",
            "neck": "Neck / Upper Collar",
            "stomach": "Stomach / Midsection",
            "limbs": "Limbs (Legs / Arms)"
        }.get(x, x.title())
    )

with c3:
    use_flight_time = st.checkbox("Include Bullet Flight Latency", value=True, help="Adds projectile travel time (Distance / Velocity) for true impact TTK.")
    include_obd = st.checkbox("Include Open-Bolt Delay (OBD)", value=True, help="Factors in trigger chambering delay on heavy LMGs and specific SMGs.")


# ---------------------------------------------------------------------------
# Helper Calculation Function (Computes Core and Hardcore STK)
# ---------------------------------------------------------------------------
def compute_leaderboard_for_distance(eval_dist_m: float):
    data = []
    for w in weapons:
        w_cls_title = w.weapon_class.value.replace("_", " ").title()
        if selected_classes and w_cls_title not in selected_classes:
            continue

        stats = repo.get_weapon_stats(w.weapon_id, selected_ver)
        profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, "core")

        if stats and profiles:
            dmg_at_dist = get_damage_at_distance(eval_dist_m, profiles, hit_location)
            dmg_head = get_damage_at_distance(eval_dist_m, profiles, "head")
            dmg_chest = get_damage_at_distance(eval_dist_m, profiles, "chest")

            # Core STK (100 HP) and Hardcore STK (30 HP)
            stk_core = calculate_shots_to_kill(100.0, dmg_at_dist, 1)
            stk_hc = calculate_shots_to_kill(30.0, dmg_at_dist, 1)

            # Active evaluation STK based on selected mode
            stk_active = stk_hc if is_hc_mode else stk_core

            stk_head = calculate_shots_to_kill(target_health_eval, dmg_head, 1)
            obd_val = (getattr(stats, "open_bolt_delay_ms", 0.0) or 0.0) if include_obd else 0.0

            # Fire TTK
            fire_ttk_core = calculate_theoretical_ttk_ms(
                stk=stk_core,
                rpm=stats.rpm,
                burst_count=getattr(w, "burst_count", 1),
                burst_delay_ms=getattr(w, "burst_delay_ms", 0.0),
                open_bolt_delay_ms=obd_val
            )
            fire_ttk_hc = calculate_theoretical_ttk_ms(
                stk=stk_hc,
                rpm=stats.rpm,
                burst_count=getattr(w, "burst_count", 1),
                burst_delay_ms=getattr(w, "burst_delay_ms", 0.0),
                open_bolt_delay_ms=obd_val
            )

            optimal_head_ttk = calculate_theoretical_ttk_ms(
                stk=stk_head,
                rpm=stats.rpm,
                burst_count=getattr(w, "burst_count", 1),
                burst_delay_ms=getattr(w, "burst_delay_ms", 0.0),
                open_bolt_delay_ms=obd_val
            )

            flight_latency_ms = (eval_dist_m / max(100.0, stats.bullet_velocity_mps)) * 1000.0 if use_flight_time else 0.0
            
            impact_ttk_core = fire_ttk_core + flight_latency_ms
            impact_ttk_hc = fire_ttk_hc + flight_latency_ms
            active_ttk = impact_ttk_hc if is_hc_mode else impact_ttk_core

            headshots_needed = calculate_headshots_for_stk_reduction(
                target_health=target_health_eval,
                body_damage=dmg_chest,
                head_damage=dmg_head
            )

            data.append({
                "weapon_id": w.weapon_id,
                "weapon_name": w.name,
                "weapon_class": w_cls_title,
                "rpm": stats.rpm,
                "mag_size": w.base_mag_size,
                "damage_per_shot": round(dmg_at_dist, 1),
                "stk": int(stk_active),
                "stk_core": int(stk_core),
                "stk_hc": int(stk_hc),
                "fire_ttk_ms": round(fire_ttk_hc if is_hc_mode else fire_ttk_core, 1),
                "flight_ms": round(flight_latency_ms, 1),
                "active_ttk_ms": round(active_ttk, 1),
                "active_ttk_core_ms": round(impact_ttk_core if use_flight_time else fire_ttk_core, 1),
                "active_ttk_hc_ms": round(impact_ttk_hc if use_flight_time else fire_ttk_hc, 1),
                "optimal_head_ttk_ms": round(optimal_head_ttk + (flight_latency_ms if use_flight_time else 0.0), 1),
                "headshot_drop_text": f"{headshots_needed} Headshot{'s' if headshots_needed > 1 else ''}" if headshots_needed is not None and headshots_needed > 0 else "N/A (Max Body STK)",
                "bullet_velocity": stats.bullet_velocity_mps,
                "ads_speed": stats.base_ads_ms
            })

    data.sort(key=lambda x: x["active_ttk_ms"])
    return data


def render_podium_section(leaderboard_data, distance_title):
    if not leaderboard_data:
        return
    st.markdown(f"#### 🏆 Top 3 Fastest Killers — {distance_title} ({active_mode_label})")
    pod_cols = st.columns(3)
    medals = ["🥇 1st Place", "🥈 2nd Place", "🥉 3rd Place"]
    colors = ["#f59e0b", "#94a3b8", "#b45309"]

    for i in range(min(3, len(leaderboard_data))):
        item = leaderboard_data[i]
        with pod_cols[i]:
            st.markdown(
                render_weapon_podium_card(
                    medal_label=medals[i],
                    border_color=colors[i],
                    weapon_name=item['weapon_name'],
                    weapon_class=item['weapon_class'],
                    rpm=item['rpm'],
                    active_ttk_ms=item['active_ttk_ms'],
                    stk=item['stk'],
                    damage_per_shot=item['damage_per_shot'],
                    bullet_velocity=item['bullet_velocity'],
                    weapon_id=item.get('weapon_id')
                ),
                unsafe_allow_html=True
            )


def render_bar_chart(leaderboard_data, distance_m):
    df_chart = pd.DataFrame(leaderboard_data)
    if df_chart.empty:
        return None

    def get_ttk_color(ttk_val):
        if ttk_val <= 60: return "#22c55e" # Ultra fast / Hardcore 1-shot (green)
        if ttk_val <= 180: return "#10b981" # Fast (emerald)
        if ttk_val <= 230: return "#38bdf8" # Competitive (cyan)
        if ttk_val <= 280: return "#fbbf24" # Medium (amber)
        return "#f43f5e" # Slow (red)

    df_chart["color"] = df_chart["active_ttk_ms"].apply(get_ttk_color)
    df_chart["display_label"] = df_chart.apply(lambda r: f"[{r['weapon_class']}]  {r['weapon_name']}", axis=1)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            y=df_chart["display_label"],
            x=df_chart["active_ttk_ms"],
            orientation="h",
            marker=dict(color=df_chart["color"]),
            text=[f"{v:.0f} ms" for v in df_chart["active_ttk_ms"]],
            textposition="outside",
            hovertext=[
                f"<b>{row['weapon_name']}</b> ({row['weapon_class']})<br>"
                f"Mode: <b>{active_mode_label}</b><br>"
                f"Time-to-Kill: <b>{row['active_ttk_ms']} ms</b><br>"
                f"Shots-to-Kill: <b>{row['stk']} rounds</b><br>"
                f"Core STK: {row['stk_core']} | Hardcore STK: {row['stk_hc']}<br>"
                f"Damage: {row['damage_per_shot']} / shot<br>"
                f"Fire Rate: {row['rpm']} RPM<br>"
                f"Velocity: {row['bullet_velocity']} m/s"
                for _, row in df_chart.iterrows()
            ],
            hoverinfo="text"
        )
    )

    fig.update_layout(
        title=f"<b>Time-to-Kill (ms) at {distance_m:.0f}m ({active_mode_label}) - Lower is Faster</b>",
        xaxis_title="Time-to-Kill (Milliseconds)",
        height=max(460, len(df_chart) * 26),
        margin=dict(l=240, r=50, t=50, b=40),
        **DARK_LAYOUT
    )
    fig.update_yaxes(autorange="reversed", tickfont=dict(color="#f8fafc", size=11))
    return fig


# Tabs for Single Distance vs Dual 15m & 25m Dropoff Matrix
st.markdown("---")
tab_dual, tab_single = st.tabs([
    "⚔️ Dual 15m vs 25m Comparison Matrix",
    "🎯 Custom Distance Explorer"
])

# ---------------------------------------------------------------------------
# TAB 1: Dual 15m vs 25m Comparison Matrix
# ---------------------------------------------------------------------------
with tab_dual:
    st.markdown(f"### ⚔️ Side-by-Side 15m Close Quarters vs 25m Mid-Range TTK Analysis ({active_mode_label})")
    st.caption("Compares point-blank and close-quarters dominance (15m) directly against mid-range dropoffs (25m), revealing which weapons suffer severe STK penalties.")

    data_15m = compute_leaderboard_for_distance(15.0)
    data_25m = compute_leaderboard_for_distance(25.0)

    if not data_15m or not data_25m:
        st.info("No weapons match the current filter criteria.")
    else:
        # Dual Podiums Side by Side
        c_p15, c_p25 = st.columns(2)
        with c_p15:
            render_podium_section(data_15m, "Close Range (15m CQB)")
        with c_p25:
            render_podium_section(data_25m, "Mid Range (25m Power Lanes)")

        # Direct Dropoff Delta Table
        st.markdown("---")
        st.markdown(f"#### 📉 15m ➡️ 25m Direct Dropoff TTK(TIME TO KILL) & STK(SHOTS TO KILL) Penalty Matrix ({active_mode_label})")
        st.caption("Highlights TTK slowdown (Delta ms) and STK increase when engaging targets at 25m instead of 15m. Click any column header or select a consecutive sort preset below:")

        map_15 = {d["weapon_id"]: d for d in data_15m}
        map_25 = {d["weapon_id"]: d for d in data_25m}

        delta_rows = []
        for w_id, d15 in map_15.items():
            d25 = map_25.get(w_id)
            if d25:
                delta_ms = round(d25["active_ttk_ms"] - d15["active_ttk_ms"], 1)
                stk_diff = d25["stk"] - d15["stk"]
                
                row_dict = {
                    "Weapon": d15["weapon_name"],
                    "Class": d15["weapon_class"],
                    "_sort_15_stk": d15["stk"],
                    "_sort_15_ttk": d15["active_ttk_ms"],
                    "_sort_25_stk": d25["stk"],
                    "_sort_25_ttk": d25["active_ttk_ms"],
                    "_sort_slowdown": delta_ms,
                    "_sort_rpm": d15["rpm"],
                    "_sort_vel": d15["bullet_velocity"],
                    "_sort_hc_15_stk": d15["stk_hc"],
                    "_sort_core_15_stk": d15["stk_core"],
                    "Fire Rate": round(d15["rpm"]),
                    "Bullet Velocity": round(d15["bullet_velocity"])
                }

                if is_side_by_side:
                    # Side-by-Side Columns
                    row_dict["15m Core STK (100HP)"] = int(d15["stk_core"])
                    row_dict["15m Hardcore STK (30HP)"] = int(d15["stk_hc"])
                    row_dict["25m Core STK (100HP)"] = int(d25["stk_core"])
                    row_dict["25m Hardcore STK (30HP)"] = int(d25["stk_hc"])
                    row_dict["15m Core TTK"] = round(d15["active_ttk_core_ms"])
                    row_dict["15m Hardcore TTK"] = round(d15["active_ttk_hc_ms"])
                else:
                    # Standard Mode Table
                    row_dict["15m TTK (Kill Speed)"] = round(d15["active_ttk_ms"])
                    row_dict["15m STK (Bullets)"] = int(d15["stk"])
                    row_dict["25m TTK (Mid-Range)"] = round(d25["active_ttk_ms"])
                    row_dict["25m STK (Bullets)"] = int(d25["stk"])
                    row_dict["TTK Slowdown"] = round(delta_ms)
                    row_dict["Extra Bullets Needed"] = int(stk_diff)

                delta_rows.append(row_dict)

        # Interactive Sort Controls
        c_sort1, c_sort_info = st.columns([2, 1])
        with c_sort1:
            sort_options = [
                "🎯 15m Shots-to-Kill (1 Shot ➔ 2 ➔ 3 ➔ 4 ➔ 5 Shots)",
                "🎯 15m Shots-to-Kill (5 Shots ➔ 4 ➔ 3 ➔ 2 ➔ 1 Shot)",
                "⚡ 15m TTK Kill Speed (Fastest ➔ Slowest)",
                "⚡ 15m TTK Kill Speed (Slowest ➔ Fastest)",
                "🎯 25m Shots-to-Kill (1 Shot ➔ 2 ➔ 3 ➔ 4 ➔ 5 Shots)",
                "🎯 25m Shots-to-Kill (5 Shots ➔ 4 ➔ 3 ➔ 2 ➔ 1 Shot)",
                "⚡ 25m TTK Mid-Range (Fastest ➔ Slowest)",
                "⚡ 25m TTK Mid-Range (Slowest ➔ Fastest)",
                "📉 TTK Slowdown Penalty (Lowest ➔ Highest)",
                "📉 TTK Slowdown Penalty (Highest ➔ Lowest)",
                "🔥 Fire Rate (RPM - Highest ➔ Lowest)",
                "🚀 Bullet Velocity (Highest ➔ Lowest)"
            ]
            if is_side_by_side:
                sort_options.insert(0, "💀 15m Hardcore STK (1-Shot Killers First)")

            sort_selection = st.selectbox(
                "🔢 Sort Table Consecutively By:",
                options=sort_options,
                index=0,
                key="sort_dropoff_matrix"
            )
        with c_sort_info:
            st.caption("💡 **Pro-Tip**: You can also click directly on **any column header** below to sort ascending or descending instantly!")

        # Apply Sort Ordering
        if "15m Hardcore STK (1-Shot" in sort_selection:
            delta_rows.sort(key=lambda x: (x["_sort_hc_15_stk"], x["_sort_15_ttk"]))
        elif "15m Shots-to-Kill (1 Shot ➔" in sort_selection:
            delta_rows.sort(key=lambda x: (x["_sort_15_stk"], x["_sort_15_ttk"]))
        elif "15m Shots-to-Kill (5 Shots ➔" in sort_selection:
            delta_rows.sort(key=lambda x: (-x["_sort_15_stk"], x["_sort_15_ttk"]))
        elif "15m TTK Kill Speed (Fastest ➔ Slowest)" in sort_selection:
            delta_rows.sort(key=lambda x: x["_sort_15_ttk"])
        elif "15m TTK Kill Speed (Slowest ➔ Fastest)" in sort_selection:
            delta_rows.sort(key=lambda x: -x["_sort_15_ttk"])
        elif "25m Shots-to-Kill (1 Shot ➔" in sort_selection:
            delta_rows.sort(key=lambda x: (x["_sort_25_stk"], x["_sort_25_ttk"]))
        elif "25m Shots-to-Kill (5 Shots ➔" in sort_selection:
            delta_rows.sort(key=lambda x: (-x["_sort_25_stk"], x["_sort_25_ttk"]))
        elif "25m TTK Mid-Range (Fastest ➔ Slowest)" in sort_selection:
            delta_rows.sort(key=lambda x: x["_sort_25_ttk"])
        elif "25m TTK Mid-Range (Slowest ➔ Fastest)" in sort_selection:
            delta_rows.sort(key=lambda x: -x["_sort_25_ttk"])
        elif "TTK Slowdown Penalty (Lowest ➔ Highest)" in sort_selection:
            delta_rows.sort(key=lambda x: x["_sort_slowdown"])
        elif "TTK Slowdown Penalty (Highest ➔ Lowest)" in sort_selection:
            delta_rows.sort(key=lambda x: -x["_sort_slowdown"])
        elif "Fire Rate" in sort_selection:
            delta_rows.sort(key=lambda x: -x["_sort_rpm"])
        elif "Bullet Velocity" in sort_selection:
            delta_rows.sort(key=lambda x: -x["_sort_vel"])

        df_delta = pd.DataFrame(delta_rows)
        display_delta_cols = [c for c in df_delta.columns if not c.startswith("_")]

        # Configure dynamic column formatters
        col_cfg = {
            "Weapon": st.column_config.TextColumn("Weapon", help="Weapon platform name"),
            "Class": st.column_config.TextColumn("Class", help="Weapon category"),
            "Fire Rate": st.column_config.NumberColumn("Fire Rate", format="%d RPM", help="Rounds per minute"),
            "Bullet Velocity": st.column_config.NumberColumn("Bullet Velocity", format="%d m/s", help="Bullet flight speed in m/s")
        }

        if is_side_by_side:
            col_cfg.update({
                "15m Core STK (100HP)": st.column_config.NumberColumn("15m Core STK", format="%d shots", help="Bullets needed to kill at 15m in Core 100 HP"),
                "15m Hardcore STK (30HP)": st.column_config.NumberColumn("15m Hardcore STK", format="%d shots", help="Bullets needed to kill at 15m in Hardcore 30 HP (1-shot vs 2-shot)"),
                "25m Core STK (100HP)": st.column_config.NumberColumn("25m Core STK", format="%d shots", help="Bullets needed to kill at 25m in Core 100 HP"),
                "25m Hardcore STK (30HP)": st.column_config.NumberColumn("25m Hardcore STK", format="%d shots", help="Bullets needed to kill at 25m in Hardcore 30 HP"),
                "15m Core TTK": st.column_config.NumberColumn("15m Core TTK", format="%d ms", help="Core 100 HP Time-to-Kill in milliseconds"),
                "15m Hardcore TTK": st.column_config.NumberColumn("15m Hardcore TTK", format="%d ms", help="Hardcore 30 HP Time-to-Kill in milliseconds (0ms for 1-shot kills)")
            })
        else:
            col_cfg.update({
                "15m TTK (Kill Speed)": st.column_config.NumberColumn(f"15m TTK ({active_mode_label})", format="%d ms", help="Time-to-kill at 15 meters in ms"),
                "15m STK (Bullets)": st.column_config.NumberColumn(f"15m STK ({active_mode_label})", format="%d shots", help="Exact number of bullets required to eliminate"),
                "25m TTK (Mid-Range)": st.column_config.NumberColumn(f"25m TTK ({active_mode_label})", format="%d ms", help="Time-to-kill at 25 meters in ms"),
                "25m STK (Bullets)": st.column_config.NumberColumn(f"25m STK ({active_mode_label})", format="%d shots", help="Exact number of bullets required at 25 meters"),
                "TTK Slowdown": st.column_config.NumberColumn("TTK Slowdown", format="+%d ms", help="Time-to-kill increase due to range falloff"),
                "Extra Bullets Needed": st.column_config.NumberColumn("Extra Bullets Needed", format="+%d", help="Extra bullets needed (0 = same shots to kill)")
            })

        st.dataframe(
            df_delta[display_delta_cols],
            column_config=col_cfg,
            use_container_width=True,
            hide_index=True
        )

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_15 = pd.DataFrame(data_15m).to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download 15m TTK Table ({active_mode_label} CSV)", data=csv_15, file_name=f"mw4_ttk_15m_{'hc' if is_hc_mode else 'core'}.csv", mime="text/csv", key="dl_ttk_15m")
        with col_dl2:
            csv_25 = pd.DataFrame(data_25m).to_csv(index=False).encode('utf-8')
            st.download_button(f"📥 Download 25m TTK Table ({active_mode_label} CSV)", data=csv_25, file_name=f"mw4_ttk_25m_{'hc' if is_hc_mode else 'core'}.csv", mime="text/csv", key="dl_ttk_25m")

        # Side by Side Bar Charts
        st.markdown("---")
        st.markdown(f"#### 📊 Comparative TTK Visualizer (15m vs 25m • {active_mode_label})")
        c_bc1, c_bc2 = st.columns(2)
        with c_bc1:
            fig_15 = render_bar_chart(data_15m, 15.0)
            if fig_15:
                st.plotly_chart(fig_15, use_container_width=True, key="plotly_chart_15m")
        with c_bc2:
            fig_25 = render_bar_chart(data_25m, 25.0)
            if fig_25:
                st.plotly_chart(fig_25, use_container_width=True, key="plotly_chart_25m")


# ---------------------------------------------------------------------------
# TAB 2: Custom Distance Explorer
# ---------------------------------------------------------------------------
with tab_single:
    st.markdown(f"### 🎯 Custom Distance Bracket Explorer ({active_mode_label})")
    
    c_d1, c_d2 = st.columns([1, 2])
    with c_d1:
        dist_mode = st.selectbox(
            "Distance Bracket Preset",
            options=["Point-Blank (5m)", "Close Range (15m)", "Mid Range (25m)", "Long Range (40m)", "Extreme (60m)", "Custom Slider"],
            index=1,
            key="single_dist_preset"
        )
    with c_d2:
        if dist_mode == "Point-Blank (5m)": eval_dist_m = 5.0
        elif dist_mode == "Close Range (15m)": eval_dist_m = 15.0
        elif dist_mode == "Mid Range (25m)": eval_dist_m = 25.0
        elif dist_mode == "Long Range (40m)": eval_dist_m = 40.0
        elif dist_mode == "Extreme (60m)": eval_dist_m = 60.0
        else:
            eval_dist_m = float(st.slider("Custom Engagement Distance (Meters)", min_value=1.0, max_value=80.0, value=20.0, step=1.0, key="single_dist_slider"))

    single_data = compute_leaderboard_for_distance(eval_dist_m)
    if single_data:
        render_podium_section(single_data, f"Fastest Killers at {eval_dist_m:.0f}m")

        fig_single = render_bar_chart(single_data, eval_dist_m)
        if fig_single:
            st.plotly_chart(fig_single, use_container_width=True, key="plotly_chart_single_custom")

        st.markdown(f"#### 📋 Complete TTK Ballistics Table ({eval_dist_m:.0f}m • {active_mode_label})")

        # Sort Selector for Single Distance Table
        c_sort_s1, c_sort_s2 = st.columns([2, 1])
        with c_sort_s1:
            sort_single_sel = st.selectbox(
                "🔢 Sort Ballistics Table Consecutively By:",
                options=[
                    "⚡ Kill Speed (Active TTK - Fastest ➔ Slowest)",
                    "⚡ Kill Speed (Active TTK - Slowest ➔ Fastest)",
                    "🎯 Bullets to Kill (STK - 1 Shot ➔ 2 ➔ 3 ➔ 4 ➔ 5 Shots)",
                    "🎯 Bullets to Kill (STK - 5 Shots ➔ 4 ➔ 3 ➔ 2 ➔ 1 Shot)",
                    "💀 Headshot Ceiling TTK (Fastest ➔ Slowest)",
                    "💥 Damage Per Shot (Highest ➔ Lowest)",
                    "🔥 Fire Rate (RPM - Highest ➔ Lowest)",
                    "🚀 Bullet Velocity (Highest ➔ Lowest)"
                ],
                index=0,
                key="sort_single_table"
            )
        with c_sort_s2:
            st.caption("💡 **Tip**: Headers below are also clickable for instant sorting.")

        if "Kill Speed (Active TTK - Fastest" in sort_single_sel:
            single_data.sort(key=lambda x: x["active_ttk_ms"])
        elif "Kill Speed (Active TTK - Slowest" in sort_single_sel:
            single_data.sort(key=lambda x: -x["active_ttk_ms"])
        elif "Bullets to Kill (STK - 1 Shot ➔" in sort_single_sel:
            single_data.sort(key=lambda x: (x["stk"], x["active_ttk_ms"]))
        elif "Bullets to Kill (STK - 5 Shots ➔" in sort_single_sel:
            single_data.sort(key=lambda x: (-x["stk"], x["active_ttk_ms"]))
        elif "Headshot Ceiling TTK" in sort_single_sel:
            single_data.sort(key=lambda x: x["optimal_head_ttk_ms"])
        elif "Damage Per Shot" in sort_single_sel:
            single_data.sort(key=lambda x: -x["damage_per_shot"])
        elif "Fire Rate" in sort_single_sel:
            single_data.sort(key=lambda x: -x["rpm"])
        elif "Bullet Velocity" in sort_single_sel:
            single_data.sort(key=lambda x: -x["bullet_velocity"])

        t_rows = []
        for idx, row in enumerate(single_data):
            t_row = {
                "Rank": idx + 1,
                "Weapon Platform": row["weapon_name"],
                "Class": row["weapon_class"],
                "Kill Speed (Active TTK)": round(row["active_ttk_ms"]),
                "Bullets to Kill (STK)": int(row["stk"]),
                "Core STK (100HP)": int(row["stk_core"]),
                "Hardcore STK (30HP)": int(row["stk_hc"]),
                "Damage per Shot": float(row["damage_per_shot"]),
                "Fire TTK (Zero Latency)": round(row["fire_ttk_ms"]),
                "Bullet Flight Delay": round(row["flight_ms"]),
                "Headshot Ceiling TTK": round(row["optimal_head_ttk_ms"]),
                "Headshots for -1 STK": row["headshot_drop_text"],
                "Fire Rate (RPM)": round(row["rpm"]),
                "Muzzle Velocity": round(row["bullet_velocity"])
            }
            t_rows.append(t_row)

        st.dataframe(
            pd.DataFrame(t_rows),
            column_config={
                "Rank": st.column_config.NumberColumn("Rank", format="#%d"),
                "Weapon Platform": st.column_config.TextColumn("Weapon Platform"),
                "Class": st.column_config.TextColumn("Class"),
                "Kill Speed (Active TTK)": st.column_config.NumberColumn("Kill Speed (Active TTK)", format="%d ms"),
                "Bullets to Kill (STK)": st.column_config.NumberColumn(f"STK ({active_mode_label})", format="%d shots"),
                "Core STK (100HP)": st.column_config.NumberColumn("Core STK (100HP)", format="%d shots"),
                "Hardcore STK (30HP)": st.column_config.NumberColumn("Hardcore STK (30HP)", format="%d shots"),
                "Damage per Shot": st.column_config.NumberColumn("Damage per Shot", format="%.1f HP"),
                "Fire TTK (Zero Latency)": st.column_config.NumberColumn("Fire TTK (Zero Latency)", format="%d ms"),
                "Bullet Flight Delay": st.column_config.NumberColumn("Bullet Flight Delay", format="+%d ms"),
                "Headshot Ceiling TTK": st.column_config.NumberColumn("Headshot Ceiling TTK", format="%d ms"),
                "Headshots for -1 STK": st.column_config.TextColumn("Headshots for -1 STK"),
                "Fire Rate (RPM)": st.column_config.NumberColumn("Fire Rate (RPM)", format="%d RPM"),
                "Muzzle Velocity": st.column_config.NumberColumn("Muzzle Velocity", format="%d m/s")
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No weapons found for the selected criteria.")
