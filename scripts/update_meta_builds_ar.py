import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.database.connection import DatabaseManager
from src.database.repository import IntelligenceRepository
from src.database.models import MetaBuildPreset, WeaponClass

def run_update():
    db = DatabaseManager(os.path.join(ROOT_DIR, "data", "mw4_intelligence.duckdb"))
    repo = IntelligenceRepository(db)
    conn = db.get_connection()

    # Find all Assault Rifle weapon IDs
    weapons = repo.get_weapons()
    ar_ids = [w.weapon_id for w in weapons if w.weapon_class == WeaponClass.ASSAULT_RIFLE]
    print(f"Assault Rifle IDs to clear from meta builds: {ar_ids}")

    # Remove all AR meta builds
    placeholders = ",".join(["?"] * len(ar_ids))
    conn.execute(f"DELETE FROM meta_build_presets WHERE weapon_id IN ({placeholders})", ar_ids)
    print("Deleted all existing Assault Rifle meta builds.")

    # Define user's Horizontal Beam M4 build
    # Attachments:
    # 1. Barrel: 16" Highmark Barrel (16_highmark_barrel)
    # 2. Muzzle: Corvus LVL-40 (corvus_lvl_40)
    # 3. Stock: Demo Dozer Stock (demo_dozer_stock)
    # 4. Optic: Slimline Elite (slimline_elite)
    # 5. Laser: SZ Gen.6 PEQ (sz_gen_6_peq)
    hbeam_atts = ["16_highmark_barrel", "corvus_lvl_40", "demo_dozer_stock", "slimline_elite", "sz_gen_6_peq"]

    # Insert for v1.3.0-launch
    m4_launch = MetaBuildPreset(
        build_id="meta_m4_horizontal_beam_launch",
        weapon_id="m4_mw4",
        game_version_id="v1.3.0-launch",
        build_name="Horizontal Beam M4 @ Level 70",
        archetype="cdl_pro",
        archetype_display="👑 Horizontal Beam Laser",
        source_outlet="SAIL6 Competitive Meta Lab",
        attachment_ids=hbeam_atts,
        perk_1_name="Quick Fix",
        perk_2_name="Fast Hands",
        perk_3_name="Blood Rush",
        tactical_name="Stun Grenade",
        lethal_name="Semtex",
        field_upgrade_name="Trophy System",
        secondary_name="krait_p68_mw4",
        secondary_role="Buffed CQB 46-Damage Sidearm",
        secondary_attachments=["laser_point_g3p"],
        best_maps="Skyline, Protocol, Lithium, Babylon",
        playstyle_notes="Engineered at Weapon Level 70 for absolute horizontal laser stability. The Corvus LVL-40 muzzle brake and Demo Dozer Stock eliminate horizontal weapon shake, the 16\" Highmark Barrel extends effective 5-shot kill range with +18% bullet velocity, Slimline Optic gives an ultra-clean tournament sight picture, and SZ Gen.6 PEQ recovers aim-down-sights agility.",
        share_code="MW4-M4-HBEAM-LVL70",
        is_verified_meta=True
    )
    repo.upsert_meta_build(m4_launch)

    # Insert for v1.2.0-beta-weekend2 for backwards-compatibility
    m4_beta = MetaBuildPreset(
        build_id="meta_m4_horizontal_beam_w2",
        weapon_id="m4_mw4",
        game_version_id="v1.2.0-beta-weekend2",
        build_name="Horizontal Beam M4 @ Level 70",
        archetype="cdl_pro",
        archetype_display="👑 Horizontal Beam Laser",
        source_outlet="SAIL6 Competitive Meta Lab",
        attachment_ids=hbeam_atts,
        perk_1_name="Quick Fix",
        perk_2_name="Fast Hands",
        perk_3_name="Blood Rush",
        tactical_name="Stun Grenade",
        lethal_name="Semtex",
        field_upgrade_name="Trophy System",
        secondary_name="krait_p68_mw4",
        secondary_role="Buffed CQB 46-Damage Sidearm",
        secondary_attachments=["laser_point_g3p"],
        best_maps="Skyline, Protocol, Lithium, Babylon",
        playstyle_notes="Engineered at Weapon Level 70 for absolute horizontal laser stability. The Corvus LVL-40 muzzle brake and Demo Dozer Stock eliminate horizontal weapon shake, the 16\" Highmark Barrel extends effective 5-shot kill range with +18% bullet velocity, Slimline Optic gives an ultra-clean tournament sight picture, and SZ Gen.6 PEQ recovers aim-down-sights agility.",
        share_code="MW4-M4-HBEAM-LVL70",
        is_verified_meta=True
    )
    repo.upsert_meta_build(m4_beta)

    print("Inserted new Horizontal Beam M4 build into DuckDB.")

    # Export to snapshots
    snapshots_dir = os.path.join(ROOT_DIR, "data", "snapshots")
    db.export_all_to_parquet(snapshots_dir)
    print("Exported all tables to Parquet snapshots successfully.")

if __name__ == "__main__":
    run_update()
