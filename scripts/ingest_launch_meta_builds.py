"""
Ingest official MW4 v1.3.0-launch meta build presets and export Parquet snapshots.
"""

import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import json
import duckdb
from src.database.connection import DatabaseManager
from src.database.repository import IntelligenceRepository
from src.database.models import MetaBuildPreset
DB_PATH = os.path.join(ROOT_DIR, "data", "mw4_intelligence.duckdb")
SNAPSHOTS_DIR = os.path.join(ROOT_DIR, "data", "snapshots")

def run_ingestion():
    db = DatabaseManager(DB_PATH)
    repo = IntelligenceRepository(db)

    # 1. Update attachments table to clear weapon_id_compat for shared multi-weapon attachments
    conn = db.get_connection()
    conn.execute("""
        UPDATE attachments
        SET weapon_id_compat = NULL
        WHERE attachment_id IN (
            SELECT a.attachment_id
            FROM attachments a
            JOIN weapon_attachments wa ON a.attachment_id = wa.attachment_id
            WHERE a.weapon_id_compat IS NOT NULL
            GROUP BY a.attachment_id
            HAVING count(wa.weapon_id) > 1
        )
    """)

    # 2. Existing presets
    beta_builds = repo.get_meta_builds(game_version_id="v1.2.0-beta-weekend2")
    
    # 3. Create v1.3.0-launch presets
    launch_builds = []
    for b in beta_builds:
        # Base launch preset
        new_id = f"{b.build_id}_launch"
        new_notes = b.playstyle_notes.replace("in Weekend 2", "at Worldwide Launch").replace("in the beta", "in Modern Warfare 4 Launch")
        
        # M4 specific launch setup from official audit report
        if b.weapon_id == "m4_mw4":
            m4_build = MetaBuildPreset(
                build_id="meta_m4_launch_meta",
                weapon_id="m4_mw4",
                game_version_id="v1.3.0-launch",
                build_name="M4 Competitive Launch Meta",
                archetype="cdl_pro",
                archetype_display="👑 CDL Pro Meta",
                source_outlet="MW4 Intelligence Lab Official Audit",
                attachment_ids=["fss-is300", "ft_cannonade_7", "fss-tac90-grip", "slimline-elite", "45_round_mag"],
                perk_1_name="Quick Fix",
                perk_2_name="Fast Hands",
                perk_3_name="Blood Rush",
                tactical_name="Stun Grenade",
                lethal_name="Semtex",
                field_upgrade_name="Trophy System",
                secondary_name="krait_p68_mw4",
                secondary_role="Buffed CQB 46-Damage Sidearm",
                secondary_attachments=["laser_point_g3p"],
                best_maps="Skyline, Lithium, Protocol, Babylon",
                playstyle_notes="Official worldwide launch meta loadout. 810 RPM flex rifle engineered for zero horizontal shake (-22% recoil) while retaining rapid aim snap and generous 45-round magazine sustain.",
                share_code="MW4-M4-L1-810PRO",
                is_verified_meta=True
            )
            launch_builds.append(m4_build)
        else:
            lb = MetaBuildPreset(
                build_id=new_id,
                weapon_id=b.weapon_id,
                game_version_id="v1.3.0-launch",
                build_name=b.build_name.replace(" w2", "").replace(" W2", " Launch"),
                archetype=b.archetype,
                archetype_display=b.archetype_display,
                source_outlet=b.source_outlet,
                attachment_ids=b.attachment_ids,
                perk_1_name=b.perk_1_name,
                perk_2_name=b.perk_2_name,
                perk_3_name=b.perk_3_name,
                tactical_name=b.tactical_name,
                lethal_name=b.lethal_name,
                field_upgrade_name=b.field_upgrade_name,
                secondary_name=b.secondary_name if b.secondary_name != "Renetti 3-Burst" else "krait_p68_mw4",
                secondary_role=b.secondary_role,
                secondary_attachments=b.secondary_attachments,
                best_maps=b.best_maps,
                playstyle_notes=new_notes,
                share_code=b.share_code.replace("W2", "L1"),
                is_verified_meta=b.is_verified_meta
            )
            launch_builds.append(lb)

    # Delete existing launch presets to avoid duplicates
    conn.execute("DELETE FROM meta_build_presets WHERE game_version_id = 'v1.3.0-launch'")
    
    # Save launch builds
    for lb in launch_builds:
        repo.upsert_meta_build(lb)
    
    print(f"Saved {len(launch_builds)} meta build presets for v1.3.0-launch.")

    # Export to snapshots
    db.export_all_to_parquet(SNAPSHOTS_DIR)
    print("Exported all tables to Parquet snapshots successfully.")

if __name__ == "__main__":
    run_ingestion()
