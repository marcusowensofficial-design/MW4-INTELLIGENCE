"""
MW4 Weapon Intelligence Lab - Data Administration & Ingestion Suite
CSV batch imports, screenshot OCR ingestion, Parquet snapshot management, and APScheduler controls.
"""

import os
import sys

# Ensure repository root is in sys.path for Streamlit Cloud deployment
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from src.ui.theme import render_page_header
from src.ui.state import init_session_state, render_sidebar_controls
from src.database.connection import db_manager
from src.database.seed_data import seed_database
from src.database.models import CommunityMetaConsensus, MetaBuildPreset, EvidenceLedgerEntry, SourceTier, VerificationStatus
from src.ingestion.csv_importer import import_weapon_stats_csv, import_damage_profiles_csv
from src.ingestion.ocr_parser import parse_weapon_card_screenshot
from src.ingestion.web_scraper import PatchNotesScraper
from src.ingestion.community_scraper import CommunityMetaScraper
from src.scheduler.jobs import lab_scheduler


st.set_page_config(page_title="Data Admin - MW4 Intel", page_icon="⚙️", layout="wide")

repo = init_session_state()
selected_ver, selected_rs_id, active_ruleset = render_sidebar_controls(repo)

render_page_header(
    title="⚙️ Data Administration & Ingestion Suite",
    subtitle="Live Web Scraping, CSV Batch Imports, Screenshot OCR Extraction & Parquet Backups",
    active_version=selected_ver,
    active_ruleset=selected_rs_id
)

tab_scraper, tab_consensus, tab_metabuilds, tab_csv, tab_ocr, tab_parquet, tab_scheduler, tab_seed = st.tabs([
    "🌐 Official Patch Scraper",
    "📰 Community Consensus Sync",
    "🎯 META Builds Management",
    "📥 CSV Batch Importer",
    "📷 Screenshot OCR Ingest",
    "📦 Parquet Snapshot Backups",
    "⏱️ APScheduler Maintenance",
    "🔄 Database Re-Seed & Reset"
])

# ---------------------------------------------------------------------------
# TAB 1: Official Patch Scraper
# ---------------------------------------------------------------------------
with tab_scraper:
    st.markdown("### 🌐 Automated Patch Notes Scraper & Aggregator")
    st.caption("Scrapes official Activision patch notes and blog announcements with intelligent monthly rollover resolution (/2026/08/ -> /2026/09/).")

    col_sc1, col_sc2 = st.columns([3, 1])
    with col_sc1:
        custom_url_input = st.text_input(
            "Target Patch Notes URL (or leave blank to auto-crawl candidate month URLs)",
            value="https://www.callofduty.com/patchnotes/2026/08/call-of-duty-modern-warfare-4-beta-patch-notes"
        )
        auto_promote_check = st.checkbox("🛡️ Auto-Validate & Apply Directly to Database (Zero Review Friction)", value=True, help="Validates incoming stats against strict physical and mathematical guardrails, applying verified changes directly to DuckDB with evidence records.")
    with col_sc2:
        st.write("")
        st.write("")
        trigger_scrape = st.button("🚀 Scrape & Update Database", type="primary")

    if trigger_scrape:
        with st.spinner("Scraping patch notes, running mathematical guardrails, and updating database..."):
            scraper = PatchNotesScraper(repo)
            success, msg, data = scraper.scrape_and_ingest(
                target_url=custom_url_input.strip() if custom_url_input else None,
                auto_promote_tier1=auto_promote_check
            )
            if success:
                st.success(msg)
                if "promotion_report" in data:
                    rep = data["promotion_report"]
                    st.markdown(f"**Guardrail Report:** `{rep['applied_count']}` applied, `{rep['rejected_count']}` rejected.")
                    if rep.get("audit_trail"):
                        st.dataframe(pd.DataFrame(rep["audit_trail"]), use_container_width=True, hide_index=True)
                else:
                    st.json(data)
            else:
                st.error(msg)

    st.markdown("---")
    st.markdown("#### 🔄 Dynamic Month Rollover Resolution Table")
    scraper_preview = PatchNotesScraper(repo)
    cand_urls = scraper_preview.generate_candidate_urls(year=2026, month=8)
    cand_rows = [
        {"Target Month / Destination": "August 2026 (Current)", "Candidate URL": cand_urls[0]},
        {"Target Month / Destination": "August 2026 (Blog Fallback)", "Candidate URL": cand_urls[1]},
        {"Target Month / Destination": "September 2026 (Rollover)", "Candidate URL": cand_urls[2]},
        {"Target Month / Destination": "July 2026 (Archive)", "Candidate URL": cand_urls[3]},
        {"Target Month / Destination": "Central Patch Notes Hub", "Candidate URL": cand_urls[4]}
    ]
    st.dataframe(pd.DataFrame(cand_rows), use_container_width=True, hide_index=True)


# ---------------------------------------------------------------------------
# TAB 2: Community Meta Consensus Sync
# ---------------------------------------------------------------------------
with tab_consensus:
    st.markdown("### 📰 Community Meta Tier Sync (Dexerto, CharlieIntel, Dot Esports)")
    st.caption("Manage, sync, and update cross-outlet tier ratings when mid-beta balance updates or weekend 2 patches drop.")

    weapons_all = repo.get_weapons()
    consensus_map = {}
    if hasattr(repo, "get_community_consensus"):
        try:
            consensus_map = repo.get_community_consensus(selected_ver)
            if not consensus_map:
                consensus_map = repo.get_community_consensus()
        except Exception:
            consensus_map = {}

    # Display current consensus records in database
    st.markdown("#### 📋 Current Database Consensus Records (6 Meta Authorities)")
    c_table_rows = []
    for w in weapons_all:
        rec = consensus_map.get(w.weapon_id)
        if rec:
            c_table_rows.append({
                "Weapon": w.name,
                "Class": w.weapon_class.value.replace("_", " ").title(),
                "WZStats": rec.wzstats_tier,
                "WZRanked": rec.wzranked_tier,
                "CODMunity": rec.codmunity_tier,
                "Dexerto": rec.dexerto_tier,
                "CharlieIntel": rec.charlie_tier,
                "Dot Esports": rec.dotesports_tier,
                "Consensus Tag": rec.consensus_tag,
                "Last Updated": rec.last_updated[:19].replace("T", " ")
            })
    if c_table_rows:
        st.dataframe(pd.DataFrame(c_table_rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### ⚡ Quick Tier Ingest / Balance Override")
    st.caption("Adjust any weapon's standing across all 6 meta tracking platforms following a balance patch or tournament shift.")

    w_names = {w.name: w for w in weapons_all}
    col_sel_w, col_btn_sync = st.columns([2, 1])
    with col_sel_w:
        edit_w_name = st.selectbox("Select Weapon to Update", options=list(w_names.keys()))
    with col_btn_sync:
        st.write("")
        st.write("")
        if st.button("🚀 Live Scrape & Sync All 6 Platforms", type="primary"):
            with st.spinner("Scraping WZStats, WZRanked, CODMunity, Dexerto, CharlieIntel, and Dot Esports..."):
                comm_scraper = CommunityMetaScraper(repo)
                sync_res = comm_scraper.sync_all_platforms(selected_ver)
                st.success(f"Successfully scraped all {len(sync_res['platforms_scraped'])} platforms! Checked {sync_res['total_weapons_audited']} weapons across all categories.")
                if sync_res["changes_detected_count"] > 0:
                    st.info(f"Applied `{sync_res['changes_detected_count']}` meta tier adjustments to database.")
                    st.dataframe(pd.DataFrame(sync_res["changes"]), use_container_width=True, hide_index=True)
                else:
                    st.info("No tier drift detected — all 24 weapon platforms are 100% synchronized with live feeds.")
                st.rerun()

    if edit_w_name:
        chosen_w = w_names[edit_w_name]
        current_rec = consensus_map.get(chosen_w.weapon_id)

        tier_opts = ["S-Tier 👑", "A-Tier ⭐", "B-Tier 🔷", "C-Tier 🔶", "D-Tier 🔘"]
        
        st.markdown("##### 🎚️ Platform Tier Ratings")
        col_wzs, col_wzr, col_cod = st.columns(3)
        with col_wzs:
            cur_wzs = current_rec.wzstats_tier if current_rec else "B-Tier 🔷"
            wzs_idx = tier_opts.index(cur_wzs) if cur_wzs in tier_opts else 2
            new_wzs = st.selectbox("WZStats.gg Tier", options=tier_opts, index=wzs_idx)
        with col_wzr:
            cur_wzr = current_rec.wzranked_tier if current_rec else "B-Tier 🔷"
            wzr_idx = tier_opts.index(cur_wzr) if cur_wzr in tier_opts else 2
            new_wzr = st.selectbox("WZRanked Tier", options=tier_opts, index=wzr_idx)
        with col_cod:
            cur_cod = current_rec.codmunity_tier if current_rec else "B-Tier 🔷"
            cod_idx = tier_opts.index(cur_cod) if cur_cod in tier_opts else 2
            new_cod = st.selectbox("CODMunity Tier", options=tier_opts, index=cod_idx)

        col_d, col_c, col_dot = st.columns(3)
        with col_d:
            cur_d = current_rec.dexerto_tier if current_rec else "B-Tier 🔷"
            d_idx = tier_opts.index(cur_d) if cur_d in tier_opts else 2
            new_dex = st.selectbox("Dexerto Tier", options=tier_opts, index=d_idx)
        with col_c:
            cur_c = current_rec.charlie_tier if current_rec else "B-Tier 🔷"
            c_idx = tier_opts.index(cur_c) if cur_c in tier_opts else 2
            new_cha = st.selectbox("CharlieIntel Tier", options=tier_opts, index=c_idx)
        with col_dot:
            cur_dot = current_rec.dotesports_tier if current_rec else "B-Tier 🔷"
            dot_idx = tier_opts.index(cur_dot) if cur_dot in tier_opts else 2
            new_dot = st.selectbox("Dot Esports Tier", options=tier_opts, index=dot_idx)

        col_pr, col_kd, col_sec = st.columns([1, 1, 2])
        with col_pr:
            cur_pr = current_rec.community_pick_rate_pct if current_rec else 5.0
            new_pr = st.number_input("Community Pick Rate (%)", min_value=0.0, max_value=100.0, value=float(cur_pr), step=0.1)
        with col_kd:
            cur_kd = current_rec.community_kd_ratio if current_rec else 1.05
            new_kd = st.number_input("Average Player K/D", min_value=0.0, max_value=5.0, value=float(cur_kd), step=0.01)
        with col_sec:
            cur_sec = current_rec.recommended_secondary if current_rec else "Renetti 3-Burst"
            new_sec = st.text_input("Recommended Secondary Companion", value=cur_sec)

        col_tag, col_badge = st.columns([2, 1])
        with col_tag:
            default_tag = current_rec.consensus_tag if current_rec else "⭐ BALANCED VIABLE"
            new_tag = st.text_input("Consensus Tag / Note", value=default_tag)
        with col_badge:
            color_opts = ["#f59e0b", "#38bdf8", "#4ade80", "#a855f7", "#94a3b8"]
            cur_badge = current_rec.badge_color if current_rec else "#4ade80"
            b_idx = color_opts.index(cur_badge) if cur_badge in color_opts else 2
            new_badge = st.selectbox("Badge Color", options=color_opts, index=b_idx)

        if st.button(f"💾 Save Updated Consensus for {chosen_w.name}", type="primary"):
            updated_consensus = CommunityMetaConsensus(
                consensus_id=f"c_{chosen_w.weapon_id}_{selected_ver}",
                weapon_id=chosen_w.weapon_id,
                game_version_id=selected_ver,
                wzstats_tier=new_wzs,
                wzranked_tier=new_wzr,
                codmunity_tier=new_cod,
                dexerto_tier=new_dex,
                charlie_tier=new_cha,
                dotesports_tier=new_dot,
                consensus_tag=new_tag.strip(),
                badge_color=new_badge,
                community_pick_rate_pct=new_pr,
                community_kd_ratio=new_kd,
                recommended_secondary=new_sec.strip(),
                last_updated=datetime.now(timezone.utc).isoformat()
            )
            repo.upsert_community_consensus(updated_consensus)

            # Record evidence receipt
            evidence_entry = EvidenceLedgerEntry(
                evidence_id=f"ev_consensus_{chosen_w.weapon_id}_{int(datetime.now(timezone.utc).timestamp())}",
                target_entity_type="community_consensus",
                target_entity_id=chosen_w.weapon_id,
                field_name="multi_outlet_tier_standings",
                observed_value=f"WZStats:{new_wzs} | WZRanked:{new_wzr} | Pick:{new_pr}% | KD:{new_kd}",
                source_url="https://wzstats.gg/mw4/meta",
                source_name="Multi-Authority Consensus Sync",
                source_tier=SourceTier.TIER_4,
                test_method="Live Web Ingestion & Cross-Platform Meta Audit",
                confidence_score=0.95,
                notes=f"Updated consensus tag: {new_tag.strip()}"
            )
            repo.record_evidence(evidence_entry)

            st.success(f"Successfully saved updated consensus ratings for **{chosen_w.name}** across all 6 authorities and logged evidence receipt!")
            st.rerun()


# ---------------------------------------------------------------------------
# TAB 3: META Builds Management
# ---------------------------------------------------------------------------
with tab_metabuilds:
    st.markdown("### 🎯 Verified META Build Presets Manager")
    st.caption("Inspect, create, or update official CDL Pro, Community, and Lab Pareto class setups stored in DuckDB.")

    meta_builds_list = []
    if hasattr(repo, "get_meta_builds"):
        try:
            meta_builds_list = repo.get_meta_builds(game_version_id=selected_ver)
            if not meta_builds_list:
                meta_builds_list = repo.get_meta_builds()
        except Exception:
            meta_builds_list = []

    col_mb_hdr, col_mb_sync = st.columns([2, 1])
    with col_mb_hdr:
        st.markdown(f"#### 📋 Cataloged Builds (`{len(meta_builds_list)}` Total)")
    with col_mb_sync:
        if st.button("🔄 Sync WZStats Builds & Attachments", type="primary", use_container_width=True):
            with st.spinner("Connecting to WZStats.gg SSR transfer feeds & ingesting meta attachments..."):
                comm_scraper = CommunityMetaScraper(repo)
                sync_res = comm_scraper.sync_wzstats_loadouts_and_attachments()
                st.success(f"✅ Ingested `{sync_res['total_attachments_synced']}` authentic attachments across `{sync_res['total_wzstats_builds_scraped']}` competitive loadouts!")
                st.rerun()

    if meta_builds_list:
        b_summary_rows = []
        for mb in meta_builds_list:
            b_summary_rows.append({
                "Build ID": mb.build_id,
                "Weapon ID": mb.weapon_id,
                "Build Name": mb.build_name,
                "Archetype": mb.archetype_display,
                "Source Outlet": mb.source_outlet,
                "Secondary Companion": f"{mb.secondary_name} ({mb.secondary_role})",
                "Perk Package": f"{mb.perk_1_name} / {mb.perk_2_name} / {mb.perk_3_name}",
                "Share Code": mb.share_code
            })
        st.dataframe(pd.DataFrame(b_summary_rows), use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### ➕ Create or Override Meta Build Preset")
    with st.form("form_create_meta_build"):
        col_w_sel, col_arch_sel = st.columns(2)
        with col_w_sel:
            all_w_dict = {w.name: w for w in repo.get_weapons()}
            sel_w_name = st.selectbox("Weapon", options=list(all_w_dict.keys()))
        with col_arch_sel:
            arch_map = {
                "👑 CDL Pro Meta": "cdl_pro",
                "🔬 Lab Pareto Optimal": "lab_pareto",
                "⚡ Max Speed Rusher": "max_speed",
                "🎯 Zero-Recoil Beamer": "zero_recoil",
                "🤫 S&D Stealth Infiltrator": "stealth_snd"
            }
            sel_arch_disp = st.selectbox("Archetype", options=list(arch_map.keys()))

        col_bname, col_bsource = st.columns(2)
        with col_bname:
            custom_bname = st.text_input("Build Name", value=f"{sel_w_name} - Competitive Class")
        with col_bsource:
            custom_bsource = st.text_input("Source / Creator", value="CODMunity / Pro Consensus")

        all_atts = repo.get_attachments()
        att_options = {f"[{a.slot.value.upper()}] {a.name} ({a.attachment_id})": a.attachment_id for a in all_atts}
        sel_att_labels = st.multiselect("Select up to 5 Primary Attachments", options=list(att_options.keys()), max_selections=5)
        sel_att_ids = [att_options[label] for label in sel_att_labels]

        col_sname, col_srole = st.columns(2)
        with col_sname:
            in_sname = st.text_input("Recommended Secondary Weapon", value="Renetti 3-Burst")
        with col_srole:
            in_srole = st.text_input("Secondary Tactical Role", value="180ms Fast-Swap Pocket Pistol")

        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            in_p1 = st.text_input("Perk 1", value="Quick Fix")
        with col_p2:
            in_p2 = st.text_input("Perk 2", value="Fast Hands")
        with col_p3:
            in_p3 = st.text_input("Perk 3", value="Battle Hardened")

        col_eq1, col_eq2, col_eq3 = st.columns(3)
        with col_eq1:
            in_tac = st.text_input("Tactical", value="Shock Stick")
        with col_eq2:
            in_let = st.text_input("Lethal", value="Semtex")
        with col_eq3:
            in_fld = st.text_input("Field Upgrade", value="Trophy System")

        in_maps = st.text_input("Recommended Maps", value="Skyline, Babylon, Protocol")
        in_notes = st.text_area("Playstyle Strategy Guide", value="Tuned for high mobility and aggressive map control.")
        in_share = st.text_input("Share Code", value=f"MW4-{sel_w_name.upper().replace(' ', '')}-CUSTOM")

        if st.form_submit_button("💾 Save Meta Build Preset to Database", type="primary"):
            target_wid = all_w_dict[sel_w_name].weapon_id
            target_arch = arch_map[sel_arch_disp]
            new_preset = MetaBuildPreset(
                build_id=f"mb_{target_wid}_{target_arch}_{selected_ver}",
                weapon_id=target_wid,
                game_version_id=selected_ver,
                build_name=custom_bname.strip(),
                archetype=target_arch,
                archetype_display=sel_arch_disp,
                source_outlet=custom_bsource.strip(),
                attachment_ids=sel_att_ids,
                perk_1_name=in_p1.strip(),
                perk_2_name=in_p2.strip(),
                perk_3_name=in_p3.strip(),
                tactical_name=in_tac.strip(),
                lethal_name=in_let.strip(),
                field_upgrade_name=in_fld.strip(),
                secondary_name=in_sname.strip(),
                secondary_role=in_srole.strip(),
                secondary_attachments=[],
                best_maps=in_maps.strip(),
                playstyle_notes=in_notes.strip(),
                share_code=in_share.strip(),
                is_verified_meta=True
            )
            if hasattr(repo, "upsert_meta_build"):
                repo.upsert_meta_build(new_preset)
                st.success(f"Successfully saved **{custom_bname}** to DuckDB database!")
                st.rerun()


# ---------------------------------------------------------------------------
# TAB 4: CSV Batch Importer
# ---------------------------------------------------------------------------
with tab_csv:
    st.markdown("### 📥 Pydantic-Validated CSV Batch Importer")
    st.caption("Upload CSV files to batch import weapon physical statistics or damage falloff tables into DuckDB.")

    csv_type = st.radio("Select Ingestion Schema", options=["Weapon Physical Stats CSV", "Damage Profiles CSV"], horizontal=True)

    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

    if uploaded_file is not None:
        csv_content = uploaded_file.getvalue().decode("utf-8")
        st.write(f"**File:** `{uploaded_file.name}` ({len(csv_content)} bytes)")

        if st.button("🚀 Process & Ingest CSV", type="primary"):
            if csv_type == "Weapon Physical Stats CSV":
                count, logs, errors = import_weapon_stats_csv(
                    csv_content=csv_content,
                    game_version_id=selected_ver,
                    repo=repo,
                    source_name=f"Upload: {uploaded_file.name}"
                )
            else:
                count, logs, errors = import_damage_profiles_csv(
                    csv_content=csv_content,
                    game_version_id=selected_ver,
                    ruleset_id=selected_rs_id,
                    repo=repo
                )

            if count > 0:
                st.success(f"Successfully validated and ingested {count} records into version '{selected_ver}'!")
                for l in logs[:5]:
                    st.write(f"• {l}")
            if errors:
                st.error(f"Encountered {len(errors)} validation errors:")
                for e in errors:
                    st.write(f"⚠️ {e}")

    # CSV Templates
    st.markdown("---")
    st.markdown("#### 📄 Standard CSV Schema Templates")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**Weapon Physical Stats Template:**")
        sample_stats_csv = "weapon_id,rpm,base_ads_ms,sprint_to_fire_ms,tactical_sprint_to_fire_ms,bullet_velocity_mps,reload_empty_s,reload_tactical_s,recoil_horizontal,recoil_vertical,hipfire_spread_deg,move_speed_mps,ads_move_speed_mps,flinch_resistance\npatriot_xmr_mw4,780.0,235.0,205.0,280.0,735.0,2.35,1.80,17.8,25.2,3.8,4.88,2.95,1.0"
        st.code(sample_stats_csv, language="csv")
    with col_t2:
        st.markdown("**Damage Profiles Template:**")
        sample_dmg_csv = "weapon_id,range_start_m,range_end_m,damage_head,damage_neck,damage_chest,damage_stomach,damage_limbs\npatriot_xmr_mw4,0.0,28.0,39.2,35.0,30.8,28.0,25.2\npatriot_xmr_mw4,28.0,42.0,35.0,31.2,27.5,25.0,22.5\npatriot_xmr_mw4,42.0,100.0,30.8,27.5,24.2,22.0,19.8"
        st.code(sample_dmg_csv, language="csv")

# ---------------------------------------------------------------------------
# TAB 2: Screenshot OCR Ingestion
# ---------------------------------------------------------------------------
with tab_ocr:
    st.markdown("### 📷 In-Game Screenshot & Stat Card Ingest")
    st.caption("Extracts weapon card metrics from screenshot captures and quarantines them safely into the AI Review Queue.")

    img_file = st.file_uploader("Upload In-Game Stat Card Image", type=["png", "jpg", "jpeg", "webp"])
    weapons = repo.get_weapons()
    weapon_opts = {w.name: w.weapon_id for w in weapons}
    selected_w_ocr = st.selectbox("Select Target Weapon Platform", options=list(weapon_opts.keys()), key="ocr_w_sel")

    if img_file is not None:
        st.image(img_file, caption="Uploaded Stat Card Capture", width=450)

        if st.button("🔍 Extract & Quarantine to AI Review Queue", type="primary"):
            success, msg, extracted = parse_weapon_card_screenshot(
                image_bytes=img_file.getvalue(),
                weapon_id_hint=weapon_opts[selected_w_ocr],
                repo=repo
            )
            if success:
                st.success(msg)
                st.json(extracted)
                st.info("Navigate to 'Evidence Review' to review and promote this claim.")
            else:
                st.error(msg)

# ---------------------------------------------------------------------------
# TAB 3: Parquet Snapshots
# ---------------------------------------------------------------------------
with tab_parquet:
    st.markdown("### 📦 Parquet Offline Snapshots & High-Speed Backups")
    st.caption("Exports DuckDB relational tables to compressed column-oriented Parquet files for offline analysis and zero-lock backups.")

    export_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "snapshots"
    )

    if st.button("💾 Export All Tables to Parquet Now", type="primary"):
        with st.spinner("Exporting DuckDB tables to Parquet..."):
            results = db_manager.export_all_to_parquet(export_path)
            st.success(f"Export completed! {len(results)} tables snapshotted to `{export_path}`")
            for tbl, path in results.items():
                st.write(f"• **{tbl}**: `{os.path.basename(path)}`")

    # List existing snapshots
    if os.path.exists(export_path):
        files = [f for f in os.listdir(export_path) if f.endswith(".parquet")]
        if files:
            st.markdown("#### 📁 Existing Parquet Snapshots")
            f_rows = [
                {
                    "Filename": f,
                    "Size (KB)": f"{os.path.getsize(os.path.join(export_path, f)) / 1024:.1f} KB",
                    "Path": os.path.join(export_path, f)
                }
                for f in files
            ]
            st.dataframe(pd.DataFrame(f_rows), use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# TAB 4: APScheduler Maintenance
# ---------------------------------------------------------------------------
with tab_scheduler:
    st.markdown("### ⏱️ Background Task Scheduler (APScheduler)")
    st.caption("Controls automated background jobs for periodic Parquet backups and feed polling.")

    col_sch_stat, col_sch_btn = st.columns([2, 1])

    with col_sch_stat:
        status_text = "🟢 ACTIVE / RUNNING" if lab_scheduler.is_running else "⚪ STOPPED / IDLE"
        st.markdown(f"**Scheduler Status:** `{status_text}`")
        st.write("• **Job 1:** `auto_parquet_backup` (Interval: every 60 minutes)")

    with col_sch_btn:
        if not lab_scheduler.is_running:
            if st.button("▶️ Start Background Scheduler", type="primary"):
                lab_scheduler.start()
                st.success("Background scheduler started!")
                st.rerun()
        else:
            if st.button("⏹️ Stop Background Scheduler"):
                lab_scheduler.shutdown()
                st.info("Background scheduler stopped.")
                st.rerun()

# ---------------------------------------------------------------------------
# TAB 5: Re-Seed Database
# ---------------------------------------------------------------------------
with tab_seed:
    st.markdown("### 🔄 Database Reset & Baseline Re-Seed")
    st.warning("⚠️ This will clear all tables and restore the verified illustrative baseline for MW4 beta & launch.")

    if st.button("🚨 Clear Database & Re-Seed Default Intelligence", type="primary"):
        with st.spinner("Re-seeding database..."):
            db_manager.clear_all_tables()
            seed_database(db_manager)
            st.success("Database successfully re-seeded with clean baseline!")
            st.rerun()
