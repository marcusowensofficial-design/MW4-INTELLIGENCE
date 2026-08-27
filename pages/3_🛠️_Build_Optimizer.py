import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from src.ui.theme import render_page_header
from src.ui.state import init_session_state, render_sidebar_controls
from src.ui.charts import (
    create_pareto_scatter_chart,
    create_recoil_spray_comparison_chart,
    create_duel_timeline_chart
)
from src.database.models import CustomBuild, AttachmentSlot
from src.engines.attachment_engine import calculate_modified_stats, validate_build_legality
from src.engines.pareto_optimizer import generate_candidate_builds, compute_pareto_frontier
from src.engines.recoil_engine import simulate_recoil_pattern
from src.engines.duel_engine import simulate_1v1_duel, DuelCombatant
from src.engines.share_code import encode_loadout_share_code, decode_loadout_share_code
from src.ui.weapon_assets import get_weapon_img_tag


st.set_page_config(page_title="Build Optimizer - MW4 Intel", page_icon="🛠️", layout="wide")

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="🛠️ Build Optimizer & Gunsmith Intelligence",
    subtitle="Interactive 5-Slot Customizer, 2D Recoil Spray, 1v1 Duel Arena & Multi-Objective Pareto-Frontier Solver",
    active_version=selected_ver,
    active_ruleset=selected_rs_id
)

weapons = repo.get_weapons()
weapon_map = {w.name: w for w in weapons}

# 1. Weapon Selector
col_w, col_mode = st.columns([2, 1])
with col_w:
    chosen_weapon_name = st.selectbox("Select Primary Weapon Platform", options=list(weapon_map.keys()))
    weapon = weapon_map[chosen_weapon_name]

with col_mode:
    img_html = get_weapon_img_tag(weapon.weapon_id, max_height_px=65, max_width_px=180)
    st.markdown(f"<div style='display: flex; align-items: center; justify-content: flex-end; padding-top: 10px;'>{img_html}</div>", unsafe_allow_html=True)

base_stats = repo.get_weapon_stats(weapon.weapon_id, selected_ver)
damage_profiles = repo.get_damage_profiles(weapon.weapon_id, selected_ver, selected_rs_id)
all_attachments = repo.get_attachments(weapon_id=weapon.weapon_id)
attachment_map = {a.attachment_id: a for a in all_attachments}

if not base_stats or not damage_profiles:
    st.error(f"Missing base stats or damage profiles for {weapon.name} under version {selected_ver}.")
    st.stop()

# Tab layout: Manual Gunsmith vs Pareto Optimizer vs 1v1 Duel vs Saved Builds
tab_gunsmith, tab_pareto, tab_duel, tab_saved = st.tabs([
    "🔧 Gunsmith Customizer & 2D Recoil",
    "🏆 Pareto-Frontier Optimizer",
    "⚔️ 1v1 Gunsmith Duel Arena",
    "💾 Saved Loadouts & Share Codes"
])

# Fetch all modifiers for version
all_mods = repo.get_attachment_modifiers(version_id=selected_ver)

# ---------------------------------------------------------------------------
# TAB 1: Gunsmith Customizer
# ---------------------------------------------------------------------------
with tab_gunsmith:
    st.markdown("### 🔧 5-Slot Gunsmith Loadout Customizer")
    st.caption("Select up to 5 attachments. Stats dynamically update in real time with delta comparison against the naked weapon.")

    slots = [
        ("Muzzle", AttachmentSlot.MUZZLE),
        ("Barrel", AttachmentSlot.BARREL),
        ("Laser", AttachmentSlot.LASER),
        ("Optic", AttachmentSlot.OPTIC),
        ("Stock", AttachmentSlot.STOCK),
        ("Underbarrel", AttachmentSlot.UNDERBARREL),
        ("Magazine", AttachmentSlot.MAGAZINE),
        ("Ammunition", AttachmentSlot.AMMUNITION),
        ("Rear Grip", AttachmentSlot.REAR_GRIP)
    ]

    # Quick Meta Presets Selector
    meta_presets = {
        "Custom (Manual Slot Selection)": [],
        "⚡ XM4 CDL Pro Meta (Zero-Recoil Laser)": ["muzzle_vt7_spiritfire", "barrel_cyclone_long", "underbarrel_bruen_heavy_grip", "optic_slate_reflector", "mag_40_round"],
        "⚡ Rival-9 Hyperspeed CQB (Max Sprint-to-Fire)": ["muzzle_shadowstrike_suppressor", "barrel_phantom_short", "laser_ftac_grimline", "underbarrel_dr6_handstop", "stock_skeletonized_cqb"],
        "⚡ MCW Long-Range Anchor (Max Beam Stability)": ["muzzle_vt7_spiritfire", "underbarrel_bruen_heavy_grip", "optic_slate_reflector", "stock_skeletonized_cqb", "mag_40_round"],
        "⚡ BAS-B Heavy Combat (Max 7.62 Punch)": ["barrel_cyclone_long", "underbarrel_bruen_heavy_grip", "optic_slate_reflector", "stock_heavy_tac", "mag_40_round"]
    }

    c_pre1, c_pre2 = st.columns([3, 1])
    with c_pre1:
        chosen_preset = st.selectbox(
            "⚡ Quick-Load Verified Pro Meta Preset",
            options=list(meta_presets.keys()),
            key=f"preset_picker_{weapon.weapon_id}"
        )
    with c_pre2:
        st.write("")
        st.write("")
        if chosen_preset != "Custom (Manual Slot Selection)":
            st.caption("Auto-configured 5 meta slots.")

    preset_att_ids = set(meta_presets[chosen_preset])

    selected_attachments = []

    c_s1, c_s2, c_s3 = st.columns(3)
    for idx, (slot_label, slot_enum) in enumerate(slots):
        slot_atts = [a for a in all_attachments if a.slot == slot_enum]
        
        # Build mapping and labels with verified status
        att_display_map = {}
        preset_idx = 0
        for s_idx, a in enumerate(slot_atts):
            a_mods = [m for m in all_mods if m.attachment_id == a.attachment_id]
            status_tag = "" if a_mods else " [UNVERIFIED DATA]"
            disp_label = f"{a.name}{status_tag}"
            att_display_map[disp_label] = a
            if a.attachment_id in preset_att_ids:
                preset_idx = s_idx + 1 # offset by 1 for "None"

        att_options = ["None"] + list(att_display_map.keys())
        target_col = [c_s1, c_s2, c_s3][idx % 3]

        with target_col:
            choice = st.selectbox(
                f"{slot_label} Slot",
                options=att_options,
                index=preset_idx if preset_idx < len(att_options) else 0,
                key=f"slot_{slot_enum.value}_{chosen_preset[:6]}"
            )
            if choice != "None":
                chosen_att = att_display_map[choice]
                selected_attachments.append(chosen_att)

    st.markdown("---")

    # Validate slot count
    if len(selected_attachments) > 5:
        st.error(f"⚠️ Build exceeds maximum 5 attachments limit (Currently equipped: {len(selected_attachments)})")
    else:
        st.success(f"Equipped: {len(selected_attachments)} / 5 Attachments")

        # Evaluate Build
        try:
            eval_build = calculate_modified_stats(
                weapon=weapon,
                base_stats=base_stats,
                attachments=selected_attachments,
                all_modifiers=all_mods,
                ruleset=active_ruleset,
                damage_profiles=damage_profiles,
                build_label="Active Custom Build"
            )

            # Baseline for delta
            baseline = calculate_modified_stats(
                weapon=weapon,
                base_stats=base_stats,
                attachments=[],
                all_modifiers=all_mods,
                ruleset=active_ruleset,
                damage_profiles=damage_profiles,
                build_label="Naked Baseline"
            )

            # Display stats comparison cards
            st.markdown("#### 📊 Modified Build Performance vs Baseline")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                ads_delta = eval_build.effective_ads_ms - baseline.effective_ads_ms
                st.metric(
                    "ADS Transition",
                    f"{eval_build.effective_ads_ms:.0f} ms",
                    delta=f"{ads_delta:+.0f} ms",
                    delta_color="inverse"
                )
                stf_delta = eval_build.effective_sprint_to_fire_ms - baseline.effective_sprint_to_fire_ms
                st.metric(
                    "Sprint-to-Fire",
                    f"{eval_build.effective_sprint_to_fire_ms:.0f} ms",
                    delta=f"{stf_delta:+.0f} ms",
                    delta_color="inverse"
                )

            with m2:
                recoil_delta = eval_build.recoil_index - baseline.recoil_index
                st.metric(
                    "Recoil Index",
                    f"{eval_build.recoil_index:.1f}",
                    delta=f"{recoil_delta:+.1f}",
                    delta_color="inverse"
                )
                range_delta = (eval_build.range_multiplier - 1.0) * 100.0
                st.metric(
                    "Effective Range",
                    f"{(eval_build.range_multiplier * 100):.0f}%",
                    delta=f"{range_delta:+.0f}%"
                )

            with m3:
                vel_delta = eval_build.effective_bullet_velocity_mps - baseline.effective_bullet_velocity_mps
                st.metric(
                    "Muzzle Velocity",
                    f"{eval_build.effective_bullet_velocity_mps:.0f} m/s",
                    delta=f"{vel_delta:+.0f} m/s"
                )
                mag_delta = eval_build.effective_mag_size - baseline.effective_mag_size
                st.metric(
                    "Magazine Capacity",
                    f"{eval_build.effective_mag_size} rounds",
                    delta=f"{mag_delta:+d}" if mag_delta != 0 else None
                )

            with m4:
                pet_delta = eval_build.close_pet_ms - baseline.close_pet_ms
                st.metric(
                    "Practical Time (15m)",
                    f"{eval_build.close_pet_ms:.0f} ms",
                    delta=f"{pet_delta:+.0f} ms",
                    delta_color="inverse"
                )
                bal_delta = eval_build.balance_score - baseline.balance_score
                st.metric(
                    "Balance Score",
                    f"{eval_build.balance_score:.1f}/100",
                    delta=f"{bal_delta:+.1f}"
                )

            # 2D Recoil Spray Pattern Simulation
            st.markdown("---")
            st.markdown("#### 🎯 2D Wall Recoil Spray Pattern Simulation (30 Rounds at 10m)")
            st.caption("Visualizes the exact bullet trajectory and climb reduction achieved by your Gunsmith attachment build vs the naked baseline.")

            # Calculate base recoil simulation
            base_recoil_sim = simulate_recoil_pattern(
                weapon_id=weapon.weapon_id,
                weapon_name=weapon.name,
                recoil_vertical=base_stats.recoil_vertical,
                recoil_horizontal=base_stats.recoil_horizontal,
                rpm=base_stats.rpm,
                magazine_size=weapon.base_mag_size,
                vertical_modifier_pct=0.0,
                horizontal_modifier_pct=0.0,
                distance_m=10.0
            )

            # Calculate custom build recoil simulation
            vert_mod_total = sum(
                m.mod_value * (100.0 if abs(m.mod_value) <= 1.0 else 1.0)
                for a in selected_attachments
                for m in all_mods
                if m.attachment_id == a.attachment_id and m.stat_key == "recoil_vertical"
            )
            horiz_mod_total = sum(
                m.mod_value * (100.0 if abs(m.mod_value) <= 1.0 else 1.0)
                for a in selected_attachments
                for m in all_mods
                if m.attachment_id == a.attachment_id and m.stat_key == "recoil_horizontal"
            )

            build_recoil_sim = simulate_recoil_pattern(
                weapon_id=weapon.weapon_id,
                weapon_name=f"{weapon.name} Custom",
                recoil_vertical=base_stats.recoil_vertical,
                recoil_horizontal=base_stats.recoil_horizontal,
                rpm=base_stats.rpm,
                magazine_size=eval_build.effective_mag_size,
                vertical_modifier_pct=vert_mod_total,
                horizontal_modifier_pct=horiz_mod_total,
                distance_m=10.0
            )

            fig_recoil = create_recoil_spray_comparison_chart(base_recoil_sim, build_recoil_sim, distance_m=10.0)
            st.plotly_chart(fig_recoil, use_container_width=True)

            # Compact Loadout Share Code Box
            share_code = encode_loadout_share_code(
                weapon_id=weapon.weapon_id,
                attachment_ids=[a.attachment_id for a in selected_attachments],
                game_version_id=selected_ver,
                ruleset_id=selected_rs_id,
                user_label=f"{weapon.name} Custom Setup"
            )

            st.markdown("---")
            st.markdown("#### 🔗 Compact Gunsmith Share Code")
            col_sc_txt, col_sc_btn = st.columns([4, 1])
            with col_sc_txt:
                st.code(share_code, language="text")
            with col_sc_btn:
                st.write("")
                st.caption("Copy this code to share with squadmates or import across lab devices.")

            # Save Build Section
            st.markdown("---")
            st.markdown("#### 💾 Save This Custom Loadout")
            col_bname, col_bnotes, col_bsave = st.columns([2, 3, 1])
            with col_bname:
                custom_name = st.text_input("Build Label", value=f"{weapon.name} Custom Loadout")
            with col_bnotes:
                custom_notes = st.text_input("Build Notes", value="Tuned in Gunsmith")
            with col_bsave:
                st.write("")
                st.write("")
                if st.button("Save Loadout", type="primary"):
                    new_build = CustomBuild(
                        build_id=f"build_{weapon.weapon_id}_{int(datetime.now(timezone.utc).timestamp())}",
                        user_label=custom_name,
                        weapon_id=weapon.weapon_id,
                        game_version_id=selected_ver,
                        ruleset_id=selected_rs_id,
                        attachment_ids=[a.attachment_id for a in selected_attachments],
                        notes=custom_notes
                    )
                    repo.upsert_custom_build(new_build)
                    st.success("Loadout saved to database!")

        except Exception as e:
            st.error(f"Build evaluation error: {str(e)}")

# ---------------------------------------------------------------------------
# TAB 2: Pareto-Frontier Optimizer
# ---------------------------------------------------------------------------
with tab_pareto:
    st.markdown("### 🏆 Multi-Objective Pareto-Frontier Build Optimizer")
    st.caption("Evaluates hundreds of attachment combinations across Practical Engagement Time, Recoil Stability, Mobility, and Range to reveal mathematically non-dominated builds.")

    if st.button("🚀 Run Pareto-Frontier Optimizer", type="primary"):
        with st.spinner(f"Computing Pareto frontier for {weapon.name}..."):
            candidates = generate_candidate_builds(
                weapon=weapon,
                base_stats=base_stats,
                available_attachments=all_attachments,
                all_modifiers=all_mods,
                ruleset=active_ruleset,
                damage_profiles=damage_profiles,
                max_combinations=500
            )

            pareto_front, all_points = compute_pareto_frontier(candidates)
            st.session_state["pareto_front"] = pareto_front
            st.session_state["all_points"] = all_points

    if "pareto_front" in st.session_state and "all_points" in st.session_state:
        pareto_front = st.session_state["pareto_front"]
        all_points = st.session_state["all_points"]

        st.markdown(f"**Evaluated {len(all_points)} builds:** Found **{len(pareto_front)} Non-Dominated Pareto Builds** ⭐")

        # Scatter plot
        fig_pareto = create_pareto_scatter_chart(all_points, title=f"Pareto Tradeoff: PET vs Recoil ({weapon.name})")
        st.plotly_chart(fig_pareto, use_container_width=True)

        st.markdown("#### 📋 Non-Dominated Pareto Build Roster")
        pareto_rows = []
        for idx, p in enumerate(pareto_front):
            pareto_rows.append({
                "Rank": f"⭐ Front #{idx + 1}",
                "Build Label": p.build_label,
                "Practical Time": f"{p.practical_engagement_ms:.0f} ms",
                "Recoil Index": f"{p.recoil_index:.1f}",
                "ADS Speed": f"{p.effective_ads_ms:.0f} ms",
                "Range Bonus": f"+{((p.effective_range_multiplier - 1.0) * 100):.0f}%",
                "Attachments Equipped": ", ".join(p.attachment_names) if p.attachment_names else "Naked (0 Attachments)"
            })

        st.dataframe(pd.DataFrame(pareto_rows), use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# TAB 3: 1v1 Gunsmith Duel Arena
# ---------------------------------------------------------------------------
with tab_duel:
    st.markdown("### ⚔️ 1v1 Gunsmith Duel Arena")
    st.caption("Pits two customized weapon builds against each other in a millisecond-by-millisecond shootout simulation factoring in ADS latency, sprint recovery, projectile flight time, and human accuracy.")

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown(f"#### 🔵 Combatant A (Your {weapon.name} Setup)")
        c_a_name = st.text_input("Player A Name", value="Player A (You)", key="duel_name_a")
        c_a_acc = st.slider("Player A Accuracy (%)", min_value=30, max_value=100, value=75, step=5, key="duel_acc_a") / 100.0
        c_a_react = st.slider("Player A Reaction (ms)", min_value=140, max_value=300, value=190, step=10, key="duel_react_a")
        c_a_sprint = st.checkbox("Player A Sprinting", value=True, key="duel_sprint_a")
        c_a_hit = st.selectbox("Player A Target Zone", options=["chest", "head", "neck", "stomach", "limbs"], key="duel_hit_a")

    with col_d2:
        st.markdown("#### 🔴 Combatant B (Opponent Benchmark)")
        opp_weapon_name = st.selectbox("Opponent Weapon Platform", options=list(weapon_map.keys()), index=min(1, len(weapon_map)-1), key="duel_opp_w")
        opp_weapon = weapon_map[opp_weapon_name]
        opp_stats = repo.get_weapon_stats(opp_weapon.weapon_id, selected_ver)
        opp_profiles = repo.get_damage_profiles(opp_weapon.weapon_id, selected_ver, selected_rs_id)

        c_b_name = st.text_input("Player B Name", value=f"Enemy ({opp_weapon.name})", key="duel_name_b")
        c_b_acc = st.slider("Player B Accuracy (%)", min_value=30, max_value=100, value=65, step=5, key="duel_acc_b") / 100.0
        c_b_react = st.slider("Player B Reaction (ms)", min_value=140, max_value=300, value=220, step=10, key="duel_react_b")
        c_b_sprint = st.checkbox("Player B Sprinting", value=True, key="duel_sprint_b")
        c_b_hit = st.selectbox("Player B Target Zone", options=["chest", "head", "neck", "stomach", "limbs"], key="duel_hit_b")

    duel_dist = st.slider("Engagement Distance (Meters)", min_value=5, max_value=80, value=20, step=5, key="duel_dist")

    if st.button("🔥 Simulate 1v1 Gunfight", type="primary"):
        if not opp_stats or not opp_profiles:
            st.error("Missing stats for opponent weapon.")
        else:
            combatant_a = DuelCombatant(
                name=c_a_name,
                weapon_name=f"{weapon.name} (Tuned)",
                rpm=base_stats.rpm,
                base_ads_ms=eval_build.effective_ads_ms if 'eval_build' in locals() else base_stats.base_ads_ms,
                sprint_to_fire_ms=eval_build.effective_sprint_to_fire_ms if 'eval_build' in locals() else base_stats.sprint_to_fire_ms,
                bullet_velocity_mps=eval_build.effective_bullet_velocity_mps if 'eval_build' in locals() else base_stats.bullet_velocity_mps,
                open_bolt_delay_ms=getattr(base_stats, "open_bolt_delay_ms", 0.0) or 0.0,
                profiles=damage_profiles,
                reaction_ms=float(c_a_react),
                accuracy=c_a_acc,
                is_sprinting=c_a_sprint,
                hit_location=c_a_hit
            )

            combatant_b = DuelCombatant(
                name=c_b_name,
                weapon_name=opp_weapon.name,
                rpm=opp_stats.rpm,
                base_ads_ms=opp_stats.base_ads_ms,
                sprint_to_fire_ms=opp_stats.sprint_to_fire_ms,
                bullet_velocity_mps=opp_stats.bullet_velocity_mps,
                open_bolt_delay_ms=getattr(opp_stats, "open_bolt_delay_ms", 0.0) or 0.0,
                profiles=opp_profiles,
                reaction_ms=float(c_b_react),
                accuracy=c_b_acc,
                is_sprinting=c_b_sprint,
                hit_location=c_b_hit
            )

            duel_res = simulate_1v1_duel(combatant_a, combatant_b, distance_m=float(duel_dist), ruleset=active_ruleset)

            # Winner banner
            is_player_a_winner = (duel_res.winner_name == c_a_name)
            border_col = "#22c55e" if is_player_a_winner else "#ef4444"
            st.markdown(
                f'<div style="background: rgba(15, 23, 42, 0.8); border: 2px solid {border_col}; border-left: 8px solid {border_col}; border-radius: 8px; padding: 14px 18px; margin: 15px 0;">'
                f'<h3 style="color: {border_col}; margin: 0;">{duel_res.summary_verdict}</h3>'
                f'<p style="color: #cbd5e1; font-size: 13px; margin: 6px 0 0 0;">'
                f'<b>Winner Health Remaining:</b> {duel_res.winner_hp_remaining} / {int(duel_res.target_health)} HP &nbsp;•&nbsp; '
                f'<b>Total Time-to-Kill:</b> {duel_res.time_to_kill_ms:.0f} ms'
                f'</p>'
                f'</div>',
                unsafe_allow_html=True
            )

            # Timeline Plot
            fig_duel = create_duel_timeline_chart(duel_res)
            st.plotly_chart(fig_duel, use_container_width=True)

            # Chronological combat event log
            with st.expander("📜 Chronological Millisecond Combat Log", expanded=False):
                log_rows = [
                    {
                        "Time (ms)": f"{ev.timestamp_ms:.1f} ms",
                        "Shooter": ev.shooter_name,
                        "Event": ev.event_type,
                        "Damage": f"{ev.damage_dealt:.1f}",
                        "Target HP Left": f"{ev.target_hp_remaining:.1f}",
                        "Description": ev.description
                    }
                    for ev in duel_res.combat_log
                ]
                st.dataframe(pd.DataFrame(log_rows), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# TAB 4: Saved Builds & Share Codes
# ---------------------------------------------------------------------------
with tab_saved:
    st.markdown("### 💾 Saved Gunsmith Loadouts & Share Codes")

    # Import Share Code Section
    with st.container():
        st.markdown("#### 📥 Import Gunsmith Share Code")
        c_code_in, c_code_btn = st.columns([4, 1])
        with c_code_in:
            pasted_code = st.text_input("Paste Share Code (e.g. MW4-eyJ3...)", key="paste_share_code")
        with c_code_btn:
            st.write("")
            st.write("")
            import_clicked = st.button("Import Code", type="primary")

        if import_clicked and pasted_code:
            success, decoded, msg = decode_loadout_share_code(pasted_code)
            if success and decoded:
                new_build = CustomBuild(
                    build_id=f"build_imported_{int(datetime.now(timezone.utc).timestamp())}",
                    user_label=decoded.user_label or f"{decoded.weapon_id.upper()} Imported Setup",
                    weapon_id=decoded.weapon_id,
                    game_version_id=decoded.game_version_id,
                    ruleset_id=decoded.ruleset_id,
                    attachment_ids=decoded.attachment_ids,
                    notes="Imported via MW4 Share Code"
                )
                repo.upsert_custom_build(new_build)
                st.success(f"✅ Successfully imported build for {decoded.weapon_id.upper()} with {len(decoded.attachment_ids)} attachments!")
                st.rerun()
            else:
                st.error(f"❌ {msg}")

    st.markdown("---")
    st.markdown("#### 📋 Saved Custom Builds for Selected Weapon")
    saved_builds = repo.get_custom_builds(weapon_id=weapon.weapon_id)

    if not saved_builds:
        st.info("No saved custom loadouts for this weapon yet.")
    else:
        for b in saved_builds:
            with st.expander(f"⭐ {b.user_label} ({len(b.attachment_ids)} attachments)", expanded=True):
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    st.write(f"**Version:** {b.game_version_id} • **Ruleset:** {b.ruleset_id.upper()} • **Created:** {b.created_at[:10]}")
                    st.write(f"**Notes:** {b.notes or 'None'}")
                    att_names = [attachment_map[aid].name for aid in b.attachment_ids if aid in attachment_map]
                    st.write(f"**Equipped:** {', '.join(att_names) if att_names else 'Naked'}")
                    # Display share code
                    b_share_code = encode_loadout_share_code(
                        weapon_id=b.weapon_id,
                        attachment_ids=b.attachment_ids,
                        game_version_id=b.game_version_id,
                        ruleset_id=b.ruleset_id,
                        user_label=b.user_label
                    )
                    st.code(b_share_code, language="text")
                with col_del:
                    if st.button("🗑️ Delete", key=f"del_{b.build_id}"):
                        repo.delete_custom_build(b.build_id)
                        st.rerun()
