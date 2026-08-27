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

# 1. Controls & Distance Filter
st.markdown("#### 🎯 Filter & Engagement Parameters")
c1, c2, c3 = st.columns([2, 1, 1])

with c1:
    available_classes = sorted(list({w.weapon_class.value.replace("_", " ").title() for w in weapons}))
    selected_classes = st.multiselect(
        "Weapon Class Filter",
        options=available_classes,
        default=available_classes,
        help="Select one or more weapon classes (e.g. Assault Rifle and Submachine Gun) to compare side-by-side."
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


# Helper calculation function
def compute_leaderboard_for_distance(eval_dist_m: float):
    data = []
    for w in weapons:
        w_cls_title = w.weapon_class.value.replace("_", " ").title()
        if selected_classes and w_cls_title not in selected_classes:
            continue

        stats = repo.get_weapon_stats(w.weapon_id, selected_ver)
        profiles = repo.get_damage_profiles(w.weapon_id, selected_ver, selected_rs_id)

        if stats and profiles:
            dmg_at_dist = get_damage_at_distance(eval_dist_m, profiles, hit_location)
            dmg_head = get_damage_at_distance(eval_dist_m, profiles, "head")
            dmg_chest = get_damage_at_distance(eval_dist_m, profiles, "chest")

            stk = calculate_shots_to_kill(active_ruleset.target_health, dmg_at_dist, active_ruleset.min_stk_cap)
            stk_head = calculate_shots_to_kill(active_ruleset.target_health, dmg_head, active_ruleset.min_stk_cap)

            obd_val = (getattr(stats, "open_bolt_delay_ms", 0.0) or 0.0) if include_obd else 0.0

            fire_ttk = calculate_theoretical_ttk_ms(
                stk=stk,
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
            impact_ttk = fire_ttk + flight_latency_ms

            headshots_needed = calculate_headshots_for_stk_reduction(
                target_health=active_ruleset.target_health,
                body_damage=dmg_chest,
                head_damage=dmg_head
            )

            active_ttk = impact_ttk if use_flight_time else fire_ttk

            data.append({
                "weapon_id": w.weapon_id,
                "weapon_name": w.name,
                "weapon_class": w_cls_title,
                "rpm": stats.rpm,
                "mag_size": w.base_mag_size,
                "damage_per_shot": round(dmg_at_dist, 1),
                "stk": stk,
                "fire_ttk_ms": round(fire_ttk, 1),
                "flight_ms": round(flight_latency_ms, 1),
                "active_ttk_ms": round(active_ttk, 1),
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
    st.markdown(f"#### 🏆 Top 3 Fastest Killers — {distance_title}")
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
        if ttk_val <= 180: return "#22c55e" # Super fast (green)
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
                f"Time-to-Kill: <b>{row['active_ttk_ms']} ms</b><br>"
                f"Shots-to-Kill: {row['stk']} rounds<br>"
                f"Damage: {row['damage_per_shot']} / shot<br>"
                f"Fire Rate: {row['rpm']} RPM<br>"
                f"Velocity: {row['bullet_velocity']} m/s"
                for _, row in df_chart.iterrows()
            ],
            hoverinfo="text"
        )
    )

    fig.update_layout(
        title=f"<b>Time-to-Kill (ms) at {distance_m:.0f}m - Lower is Faster</b>",
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
    st.markdown("### ⚔️ Side-by-Side 15m Close Quarters vs 25m Mid-Range TTK Analysis")
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
        st.markdown("#### 📉 15m ➡️ 25m Direct Dropoff & STK Penalty Matrix")
        st.caption("Highlights TTK slowdown (Delta ms) and STK increase when engaging targets at 25m instead of 15m.")

        map_15 = {d["weapon_id"]: d for d in data_15m}
        map_25 = {d["weapon_id"]: d for d in data_25m}

        delta_rows = []
        for w_id, d15 in map_15.items():
            d25 = map_25.get(w_id)
            if d25:
                delta_ms = round(d25["active_ttk_ms"] - d15["active_ttk_ms"], 1)
                stk_diff = d25["stk"] - d15["stk"]
                delta_rows.append({
                    "Weapon": d15["weapon_name"],
                    "Class": d15["weapon_class"],
                    "15m TTK": f"{d15['active_ttk_ms']:.0f} ms",
                    "15m STK": f"{d15['stk']} shots",
                    "25m TTK": f"{d25['active_ttk_ms']:.0f} ms",
                    "25m STK": f"{d25['stk']} shots",
                    "TTK Delta": f"+{delta_ms:.0f} ms" if delta_ms > 0 else "0 ms (No Dropoff)",
                    "STK Delta": f"+{stk_diff} shot{'s' if stk_diff > 1 else ''}" if stk_diff > 0 else "0 (Consistent)",
                    "RPM": f"{d15['rpm']:.0f}",
                    "Velocity": f"{d15['bullet_velocity']:.0f} m/s",
                    "_delta_val": delta_ms,
                    "_ttk_25": d25["active_ttk_ms"]
                })

        delta_rows.sort(key=lambda x: x["_ttk_25"])
        df_delta = pd.DataFrame(delta_rows)

        display_delta_cols = [c for c in df_delta.columns if not c.startswith("_")]
        st.dataframe(df_delta[display_delta_cols], use_container_width=True, hide_index=True)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_15 = pd.DataFrame(data_15m).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download 15m TTK Table (CSV)", data=csv_15, file_name="mw4_ttk_15m.csv", mime="text/csv", key="dl_ttk_15m")
        with col_dl2:
            csv_25 = pd.DataFrame(data_25m).to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download 25m TTK Table (CSV)", data=csv_25, file_name="mw4_ttk_25m.csv", mime="text/csv", key="dl_ttk_25m")

        # Side by Side Bar Charts
        st.markdown("---")
        st.markdown("#### 📊 Comparative TTK Visualizer (15m vs 25m)")
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
    st.markdown("### 🎯 Custom Distance Bracket Explorer")
    
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

        st.markdown("#### 📋 Complete TTK Ballistics Table")
        t_rows = []
        for idx, row in enumerate(single_data):
            t_rows.append({
                "Rank": f"#{idx + 1}",
                "Weapon Platform": row["weapon_name"],
                "Class": row["weapon_class"],
                "Active TTK": f"{row['active_ttk_ms']} ms",
                "Fire TTK (Zero Latency)": f"{row['fire_ttk_ms']} ms",
                "Flight Time": f"+{row['flight_ms']} ms",
                "Headshot Ceiling TTK": f"{row['optimal_head_ttk_ms']} ms",
                "Shots to Kill": f"{row['stk']} shots",
                "Damage per Shot": f"{row['damage_per_shot']} HP",
                "Headshots for -1 STK": row["headshot_drop_text"],
                "Fire Rate (RPM)": f"{row['rpm']} RPM",
                "Muzzle Velocity": f"{row['bullet_velocity']} m/s"
            })
        st.dataframe(pd.DataFrame(t_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No weapons found for the selected criteria.")
