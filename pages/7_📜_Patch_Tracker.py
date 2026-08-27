"""
MW4 Weapon Intelligence Lab - Patch Tracker & Version Diff Engine
Features Chronological Stat Lineage Reconstructions, Time-Machine Patch Walks,
and Side-by-Side Version Diffs with Green/Red Buff/Nerf Classifications.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from src.ui.theme import render_page_header, DARK_LAYOUT
from src.ui.state import init_session_state, render_sidebar_controls
from src.ingestion.diff_engine import compare_weapon_versions, compare_all_weapons_across_versions
from src.engines.stat_lineage_engine import reconstruct_stat_lineage, audit_weapon_patch_continuity


st.set_page_config(page_title="Patch Tracker - MW4 Intel", page_icon="📜", layout="wide")

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="📜 Patch Tracker & Stat Lineage Engine",
    subtitle="Chronological Time-Machine Patch Walks, Cumulative Stat Deltas & Version Diffing",
    active_version=selected_ver,
    active_ruleset=selected_rs_id
)

versions = repo.get_game_versions()
version_ids = [v.version_id for v in versions]
weapons = repo.get_weapons()
weapon_map = {w.name: w for w in weapons}

tab_lineage, tab_diff, tab_audit = st.tabs([
    "⏳ Time-Machine Stat Lineage & Patch Walk",
    "🔬 Version vs Version Diff Engine",
    "🛡️ Patch Continuity & Integrity Audit"
])

# ---------------------------------------------------------------------------
# TAB 1: Time-Machine Stat Lineage & Patch Walk
# ---------------------------------------------------------------------------
with tab_lineage:
    st.markdown("### ⏳ Chronological Stat Lineage & Cumulative Patch Walk")
    st.caption("Reconstructs weapon stats historically step-by-step from Day 1 baseline through every official tuning update, ensuring no intermediate updates are missed.")

    col_lw, col_ls = st.columns([2, 1])
    with col_lw:
        sel_weapon_name = st.selectbox("Select Weapon Platform", options=list(weapon_map.keys()), key="lineage_w")
        sel_weapon = weapon_map[sel_weapon_name]

    events = repo.get_stat_delta_events(weapon_id=sel_weapon.weapon_id)

    if not events:
        st.info(f"No specific granular patch delta events recorded yet for {sel_weapon.name}. Displaying baseline parameters.")
    else:
        stat_names = sorted(list({e.stat_name for e in events}))
        with col_ls:
            sel_stat_name = st.selectbox("Select Target Stat", options=stat_names, key="lineage_stat")

        reconstructed = reconstruct_stat_lineage(events, sel_weapon.weapon_id, sel_stat_name)

        # Timeline KPI Cards
        st.markdown("#### 📊 Cumulative Tuning Trail")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric("Initial Baseline", f"{reconstructed.baseline_value:g}", help=f"Recorded as of {reconstructed.baseline_date}")
        with k2:
            st.metric("Current Value", f"{reconstructed.reconstructed_value:g}", delta=f"{reconstructed.reconstructed_value - reconstructed.baseline_value:+.2f}")
        with k3:
            st.metric("Total Tuning Patches", reconstructed.total_patches_applied)
        with k4:
            status_text = "✅ Continuous & Verified" if reconstructed.is_continuity_verified else "⚠️ Gap Detected"
            st.metric("Lineage Status", status_text)

        # Visual Timeline Graph
        t_dates = [reconstructed.baseline_date] + [ev.effective_date for ev in reconstructed.patch_trail]
        t_vals = [reconstructed.baseline_value] + [ev.new_value for ev in reconstructed.patch_trail]
        t_hover = [f"Initial Baseline ({reconstructed.baseline_date})<br>Value: {reconstructed.baseline_value:g}"] + [
            f"<b>{ev.patch_version_id}</b> ({ev.effective_date})<br>Delta: {ev.delta_value:+g}<br>New Value: {ev.new_value:g}<br>Notes: {ev.developer_notes}"
            for ev in reconstructed.patch_trail
        ]

        fig_lineage = go.Figure()
        fig_lineage.add_trace(
            go.Scatter(
                x=t_dates,
                y=t_vals,
                mode="lines+markers+text",
                line=dict(shape="hv", width=3, color="#38bdf8"),
                marker=dict(size=12, color="#38bdf8", symbol="circle"),
                text=[f"{v:g}" for v in t_vals],
                textposition="top center",
                hovertext=t_hover,
                hoverinfo="text"
            )
        )
        fig_lineage.update_layout(
            title=f"<b>Historical Evolution of {sel_stat_name} ({sel_weapon.name})</b>",
            xaxis_title="Patch Effective Date",
            yaxis_title=f"{sel_stat_name} Value",
            **DARK_LAYOUT
        )
        st.plotly_chart(fig_lineage, use_container_width=True)

        # Detailed Patch Trail Log
        st.markdown("#### 📜 Chronological Patch Change Audit Trail")
        trail_rows = [
            {
                "Patch Version": ev.patch_version_id,
                "Effective Date": ev.effective_date,
                "Previous": f"{ev.previous_value:g}",
                "Delta Applied": f"{ev.delta_value:+g}",
                "New Value": f"{ev.new_value:g}",
                "Developer Rationale": ev.developer_notes,
                "Official URL": ev.official_patch_url
            }
            for ev in reconstructed.patch_trail
        ]
        st.dataframe(pd.DataFrame(trail_rows), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# TAB 2: Version vs Version Diff Engine
# ---------------------------------------------------------------------------
with tab_diff:
    st.markdown("### 🔬 Side-by-Side Version Diff Engine")
    st.caption("Direct statistical delta comparison across all weapon platforms between any two versions in database.")

    if len(version_ids) < 2:
        st.info("At least two game versions are required to compute a patch diff. Currently 1 version recorded.")
    else:
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            v1_id = st.selectbox("Baseline Version (Earlier)", options=version_ids, index=1 if len(version_ids) > 1 else 0)
        with c_v2:
            v2_id = st.selectbox("Comparison Version (Newer)", options=version_ids, index=0)

        if v1_id == v2_id:
            st.warning("Please select two distinct versions to compute patch deltas.")
        else:
            diffs = compare_all_weapons_across_versions(v1_version_id=v1_id, v2_version_id=v2_id, repo=repo)

            if not diffs:
                st.info(f"No statistical changes detected between {v1_id} and {v2_id}.")
            else:
                total_buffs = sum(sum(1 for d in diff.deltas if d.classification == "BUFF") for diff in diffs)
                total_nerfs = sum(sum(1 for d in diff.deltas if d.classification == "NERF") for diff in diffs)

                m1, m2, m3 = st.columns(3)
                with m1:
                    st.metric("Modified Weapon Platforms", len(diffs))
                with m2:
                    st.metric("Total Buffs Applied", total_buffs)
                with m3:
                    st.metric("Total Nerfs Applied", total_nerfs)

                st.markdown("---")

                for diff in diffs:
                    with st.expander(f"📌 {diff.weapon_name} — {diff.summary}", expanded=True):
                        delta_rows = []
                        for d in diff.deltas:
                            if d.classification != "NEUTRAL":
                                arrow = "⬆️" if d.delta > 0 else "⬇️"
                                tag = "🟢 BUFF" if d.classification == "BUFF" else "🔴 NERF"
                                delta_rows.append({
                                    "Attribute": d.display_name,
                                    f"Old ({v1_id})": d.v1_value,
                                    f"New ({v2_id})": d.v2_value,
                                    "Delta": f"{arrow} {d.delta:+g}",
                                    "% Shift": f"{d.pct_change:+.1f}%",
                                    "Impact": tag
                                })

                        if delta_rows:
                            st.dataframe(pd.DataFrame(delta_rows), use_container_width=True, hide_index=True)
                        else:
                            st.write("Identical baseline parameters.")


# ---------------------------------------------------------------------------
# TAB 3: Patch Continuity & Integrity Audit
# ---------------------------------------------------------------------------
with tab_audit:
    st.markdown("### 🛡️ Patch Lineage Continuity & Freshness Audit")
    st.caption("Scans the entire database to guarantee that all patch updates are sequential, non-conflicting, and that newer updates have never been overwritten by stale baselines.")

    all_delta_events = repo.get_stat_delta_events()
    st.markdown(f"**Total Tracked Granular Patch Delta Events:** `{len(all_delta_events)}` across all weapons.")

    audit_summary_rows = []
    for w in weapons:
        w_events = [e for e in all_delta_events if e.weapon_id == w.weapon_id]
        if w_events:
            rep = audit_weapon_patch_continuity(w_events, w.weapon_id)
            audit_summary_rows.append({
                "Weapon Platform": w.name,
                "Class": w.weapon_class.value.replace("_", " ").title(),
                "Tuned Stats Count": rep["tracked_stats"],
                "Total Tuning Events": rep["total_patch_events"],
                "Integrity Status": "🟢 100% Continuous & Verified" if rep["all_continuous"] else "🔴 Gap / Overwrite Detected"
            })

    if audit_summary_rows:
        st.dataframe(pd.DataFrame(audit_summary_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No granular patch events recorded yet.")
