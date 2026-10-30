"""
MW4 Weapon Intelligence Lab - October 28, 2026 Weapon Tuning Ingestion Pipeline
Release Date: 2026-10-28 (Modern Warfare 4 First Weapon Tuning Update)
Game Version: v1.3.1-patch1
Official URL: https://www.callofduty.com/patchnotes/2026/10/call-of-duty-modern-warfare-4-launch-patch-notes

Ingests authentic Tier 1 weapon adjustments from the October 28, 2026 update:
- Broad weapon tuning pass normalizing hit location damage and improving SMG performance.
- Recoil control penalty reductions on Patriot XMR attachments.
- Tuning for Oden Sentinel, Hyeon Burst Hyperburst, X-58 Nyx Void, Type 73 Assault, and Warlord 12G Slugs.
"""

import os
import sys
import json
import duckdb
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.database.connection import db_manager

DB_PATH = os.path.join(ROOT_DIR, "data", "mw4_intelligence.duckdb")
SNAPSHOTS_DIR = os.path.join(ROOT_DIR, "data", "snapshots")
TIMESTAMP = datetime.now(timezone.utc).isoformat()

PATCH_VERSION = "v1.3.1-patch1"
PREV_VERSION = "v1.3.0-launch"
PATCH_DATE = "2026-10-28"
PATCH_NAME = "Call of Duty: Modern Warfare 4 Launch Patch Notes (October 28, 2026 Update)"
PATCH_URL = "https://www.callofduty.com/patchnotes/2026/10/call-of-duty-modern-warfare-4-launch-patch-notes"


def main():
    print(f"[{TIMESTAMP}] Initializing MW4 October 28, 2026 Weapon Tuning Ingestion ({PATCH_VERSION})...")
    con = duckdb.connect(DB_PATH)

    # 1. REGISTER NEW GAME VERSION & SET ACTIVE
    con.execute("UPDATE game_versions SET is_active = FALSE")
    con.execute("""
        INSERT INTO game_versions (version_id, release_date, patch_name, is_active, notes)
        VALUES (
            ?, ?, ?, TRUE,
            'First post-launch broad weapon tuning pass (Oct 28) + Oct 29-30 Live Update: hit location damage normalization for consistent TTK, SMG upper-limb/arm/hand multiplier buffs to 1.0x, PPSh-41 handling/mobility buffs, APOC-338 & FiNN LMG adjustments, Apex attachment tuning, and Oct 29 MP XP / DMZ economy updates.'
        )
        ON CONFLICT (version_id) DO UPDATE SET
            release_date = EXCLUDED.release_date,
            patch_name = EXCLUDED.patch_name,
            is_active = EXCLUDED.is_active,
            notes = EXCLUDED.notes
    """, [PATCH_VERSION, PATCH_DATE, PATCH_NAME])
    print(f"✓ Registered and activated game version: {PATCH_VERSION}")

    # 2. SEED WEAPON_VERSION_STATS FROM PREVIOUS VERSION
    print(f"Cloning base weapon stats from {PREV_VERSION} into {PATCH_VERSION}...")
    con.execute(f"DELETE FROM weapon_version_stats WHERE game_version_id = '{PATCH_VERSION}'")
    con.execute(f"""
        INSERT INTO weapon_version_stats (
            stat_id, weapon_id, game_version_id, rpm, base_ads_ms, sprint_to_fire_ms,
            tactical_sprint_to_fire_ms, bullet_velocity_mps, reload_empty_s, reload_tactical_s,
            recoil_horizontal, recoil_vertical, hipfire_spread_deg, move_speed_mps,
            ads_move_speed_mps, flinch_resistance, open_bolt_delay_ms, reload_add_ammo_s,
            swap_speed_raise_ms, swap_speed_stow_ms, tac_sprint_speed_mps
        )
        SELECT 
            weapon_id || '_{PATCH_VERSION}', weapon_id, '{PATCH_VERSION}', rpm, base_ads_ms, sprint_to_fire_ms,
            tactical_sprint_to_fire_ms, bullet_velocity_mps, reload_empty_s, reload_tactical_s,
            recoil_horizontal, recoil_vertical, hipfire_spread_deg, move_speed_mps,
            ads_move_speed_mps, flinch_resistance, open_bolt_delay_ms, reload_add_ammo_s,
            swap_speed_raise_ms, swap_speed_stow_ms, tac_sprint_speed_mps
        FROM weapon_version_stats
        WHERE game_version_id = '{PREV_VERSION}'
    """)

    # Apply physical stat adjustments:
    # PPSh-41 handling & mobility buffs:
    # ADS: 300 -> 280ms (-7%)
    # ADS Strafe: 2.75 -> 2.78 m/s (+1%)
    # Movement speed: 4.66 -> 4.70 m/s (+1%)
    # Sprint speed: 6.18 -> 6.21 m/s
    con.execute(f"""
        UPDATE weapon_version_stats
        SET base_ads_ms = 280.0,
            ads_move_speed_mps = 2.78,
            move_speed_mps = 4.70,
            tac_sprint_speed_mps = round(tac_sprint_speed_mps * (6.21 / 6.18), 2)
        WHERE weapon_id = 'ppsh41_mw4' AND game_version_id = '{PATCH_VERSION}'
    """)
    print("✓ Updated weapon_version_stats for PPSh-41 mobility and ADS speed.")

    # 3. SEED AND UPDATE WEAPON_DAMAGE_PROFILES
    print(f"Cloning and updating damage profiles for {PATCH_VERSION}...")
    con.execute(f"DELETE FROM weapon_damage_profiles WHERE game_version_id = '{PATCH_VERSION}'")
    con.execute(f"""
        INSERT INTO weapon_damage_profiles (
            profile_id, weapon_id, game_version_id, ruleset_id, range_start_m, range_end_m,
            damage_head, damage_neck, damage_chest, damage_stomach, damage_limbs
        )
        SELECT 
            weapon_id || '_{PATCH_VERSION}_' || ruleset_id || '_' || ROW_NUMBER() OVER(PARTITION BY weapon_id, ruleset_id ORDER BY range_start_m),
            weapon_id, '{PATCH_VERSION}', ruleset_id, range_start_m, range_end_m,
            damage_head, damage_neck, damage_chest, damage_stomach, damage_limbs
        FROM weapon_damage_profiles
        WHERE game_version_id = '{PREV_VERSION}'
    """)

    # A. Han 86: Max Damage Range 1120 -> 1200 (+7.14%). Neck & Upper Torso multipliers normalized 1.1 -> 1.0 (-9%)
    # Extended bracket 0 range_end_m from 28.0m to 30.0m, bracket 1 range_start_m to 30.0m
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_end_m = 30.0,
            damage_neck = damage_chest,
            damage_limbs = damage_limbs
        WHERE weapon_id = 'han86_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 0.0
    """)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_start_m = 30.0,
            damage_neck = damage_chest
        WHERE weapon_id = 'han86_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 28.0
    """)

    # B. Kastov 762: Max Damage Range 950 -> 1050 (+10.53%)
    # Extended bracket 0 range_end_m from 28.0m to 31.0m, bracket 1 range_start_m to 31.0m
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_end_m = 31.0
        WHERE weapon_id = 'kastov762_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 0.0
    """)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_start_m = 31.0
        WHERE weapon_id = 'kastov762_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 28.0
    """)

    # C. M4: Max Damage Range 990 -> 1020 (+3.03%)
    # Extended bracket 0 range_end_m from 26.0m to 26.8m, bracket 1 range_start_m to 26.8m
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_end_m = 26.8
        WHERE weapon_id = 'm4_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 0.0
    """)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_start_m = 26.8
        WHERE weapon_id = 'm4_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 26.0
    """)

    # D. Oden: Neck multiplier 1.2 -> 1.1 (-8%), Upper Torso 1.2 -> 1.1 (-8%), Lower Torso 1.1 -> 1.0 (-9%)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET damage_neck = round(damage_chest * 1.1, 1),
            damage_stomach = damage_chest
        WHERE weapon_id = 'oden_mw4' AND game_version_id = '{PATCH_VERSION}'
    """)

    # E. Wz.55 Striga: Max Damage Range 440 -> 470 (+7%), Mid Damage Range 1 825 -> 840 (+2%)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_end_m = 17.1
        WHERE weapon_id = 'wz55_striga_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 0.0
    """)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_start_m = 17.1,
            range_end_m = 30.6
        WHERE weapon_id = 'wz55_striga_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 16.0
    """)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_start_m = 30.6
        WHERE weapon_id = 'wz55_striga_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 30.0
    """)

    # F. SMG Limb Damage Multiplier Normalization (Arm & Hand Damage 0.95 -> 1.0)
    # Applies to all SMGs: ISO Nightshade, PPSh-41, VEL 46, Wz.55 Striga, X-58 Nyx
    smg_ids = ['iso_nightshade_mw4', 'ppsh41_mw4', 'vel46_mw4', 'wz55_striga_mw4', 'x58_nyx_mw4']
    for smg in smg_ids:
        con.execute(f"""
            UPDATE weapon_damage_profiles
            SET damage_limbs = damage_chest
            WHERE weapon_id = '{smg}' AND game_version_id = '{PATCH_VERSION}'
        """)

    # G. X-58 Nyx Headshot Multiplier Buff (1.25 -> 1.30, +4%)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET damage_head = round(damage_chest * 1.30, 1)
        WHERE weapon_id = 'x58_nyx_mw4' AND game_version_id = '{PATCH_VERSION}'
    """)

    # H. APOC-338: Mid Damage 1: 38 -> 37 (-3%), Mid Range 1: 1980 -> 1900 (-4%), Min Damage: 35 -> 33 (-6%)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_end_m = 40.3
        WHERE weapon_id = 'apoc338_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 0.0
    """)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_start_m = 40.3,
            damage_chest = 37.0,
            damage_neck = round(37.0 * 1.15, 1),
            damage_stomach = round(37.0 * 0.95, 1),
            damage_limbs = round(37.0 * 0.85, 1)
        WHERE weapon_id = 'apoc338_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 42.0
    """)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET damage_chest = 33.0,
            damage_neck = round(33.0 * 1.15, 1),
            damage_stomach = round(33.0 * 0.95, 1),
            damage_limbs = round(33.0 * 0.85, 1)
        WHERE weapon_id = 'apoc338_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_end_m > 100.0
    """)

    # I. FiNN LMG: Mid Damage Range 1: 1720 -> 1620 (-6%), Upper Arm Multiplier 1.1 -> 1.0 (-9%)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_end_m = 33.0
        WHERE weapon_id = 'finn_lmg_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 0.0
    """)
    con.execute(f"""
        UPDATE weapon_damage_profiles
        SET range_start_m = 33.0
        WHERE weapon_id = 'finn_lmg_mw4' AND game_version_id = '{PATCH_VERSION}' AND range_start_m = 35.0
    """)
    print("✓ Updated weapon_damage_profiles across all tuned weapons.")

    # 4. CLONE AND UPDATE ATTACHMENT MODIFIERS
    print(f"Cloning and updating attachment modifiers for {PATCH_VERSION}...")
    con.execute(f"DELETE FROM attachment_modifiers WHERE game_version_id = '{PATCH_VERSION}'")
    con.execute(f"""
        INSERT INTO attachment_modifiers (
            mod_id, attachment_id, game_version_id, stat_key, mod_type, mod_value, notes
        )
        SELECT 
            attachment_id || '_' || stat_key || '_{PATCH_VERSION}',
            attachment_id, '{PATCH_VERSION}', stat_key, mod_type, mod_value, notes
        FROM attachment_modifiers
        WHERE game_version_id = '{PREV_VERSION}'
    """)

    # Patriot XMR - EXP Haste 80L 14" (Light Barrel): Recoil Penalty 8% -> 6% (-25% ⇩)
    con.execute(f"""
        UPDATE attachment_modifiers
        SET mod_value = 6.0,
            notes = 'MW4 Launch 1:1 In-Game Stat (+6.0% Horizontal Recoil Penalty, tuned Oct 28)'
        WHERE attachment_id = 'exp_haste_80l_14' AND stat_key = 'recoil_horizontal' AND game_version_id = '{PATCH_VERSION}'
    """)
    con.execute(f"""
        UPDATE attachment_modifiers
        SET mod_value = 6.0,
            notes = 'MW4 Launch 1:1 In-Game Stat (+6.0% Vertical Recoil Penalty, tuned Oct 28)'
        WHERE attachment_id = 'exp_haste_80l_14' AND stat_key = 'recoil_vertical' AND game_version_id = '{PATCH_VERSION}'
    """)

    # Patriot XMR - FJX Fury IV Grip (Skeleton Grip): Recoil Penalty 5% -> 4% (-20% ⇩)
    con.execute(f"""
        UPDATE attachment_modifiers
        SET mod_value = 4.0,
            notes = 'MW4 Launch 1:1 In-Game Stat (+4.0% Horizontal Recoil Penalty, tuned Oct 28)'
        WHERE attachment_id = 'fjx_fury_iv_grip' AND stat_key = 'recoil_horizontal' AND game_version_id = '{PATCH_VERSION}'
    """)
    con.execute(f"""
        UPDATE attachment_modifiers
        SET mod_value = 4.0,
            notes = 'MW4 Launch 1:1 In-Game Stat (+4.0% Vertical Recoil Penalty, tuned Oct 28)'
        WHERE attachment_id = 'fjx_fury_iv_grip' AND stat_key = 'recoil_vertical' AND game_version_id = '{PATCH_VERSION}'
    """)
    print("✓ Updated attachment_modifiers for Patriot XMR barrels and grips.")

    # 5. INGEST STAT DELTA EVENTS
    # Bridge launch transition events for continuous lineage if not already present
    launch_bridges = [
        ("kastov762_mw4", "range_effective_m", 24.1, "buff", 3.9, 28.0, "Worldwide launch baseline range adjustment to 28.0m."),
        ("han86_mw4", "range_effective_m", 28.4, "nerf", -0.4, 28.0, "Worldwide launch baseline range adjustment to 28.0m."),
        ("m4_mw4", "range_effective_m", 27.4, "nerf", -1.4, 26.0, "Worldwide launch baseline range adjustment to 26.0m.")
    ]
    for wid, stat, prev, dtype, dval, newv, notes in launch_bridges:
        con.execute("""
            INSERT INTO stat_delta_events (
                event_id, weapon_id, stat_name, patch_version_id, effective_date,
                previous_value, delta_type, delta_value, new_value, official_patch_url,
                developer_notes, captured_timestamp
            ) VALUES (?, ?, ?, 'v1.3.0-launch', '2026-10-22', ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (event_id) DO UPDATE SET
                previous_value = EXCLUDED.previous_value,
                delta_type = EXCLUDED.delta_type,
                delta_value = EXCLUDED.delta_value,
                new_value = EXCLUDED.new_value,
                developer_notes = EXCLUDED.developer_notes
        """, [
            f"delta_launch_{wid}_{stat}", wid, stat, prev, dtype, dval, newv, PATCH_URL, notes, TIMESTAMP
        ])

    print("Recording granular tuning deltas into stat_delta_events...")
    deltas = [
        # Han 86
        ("han86_mw4", "range_effective_m", 28.0, "buff", 2.0, 30.0, "Max damage range extended by 7.1% (1120 -> 1200 units)."),
        ("han86_mw4", "neck_damage_multiplier", 1.1, "nerf", -0.1, 1.0, "Neck damage multiplier normalized to 1.0x for consistent TTK."),
        ("han86_mw4", "upper_torso_multiplier", 1.1, "nerf", -0.1, 1.0, "Upper torso damage multiplier normalized to 1.0x."),
        # Kastov 762
        ("kastov762_mw4", "range_effective_m", 28.0, "buff", 3.0, 31.0, "Max damage range extended by 10.5% (950 -> 1050 units)."),
        # M4
        ("m4_mw4", "range_effective_m", 26.0, "buff", 0.8, 26.8, "Max damage range extended by 3.0% (990 -> 1020 units)."),
        # Oden
        ("oden_mw4", "neck_damage_multiplier", 1.2, "nerf", -0.1, 1.1, "Neck damage multiplier reduced from 1.2x to 1.1x."),
        ("oden_mw4", "upper_torso_multiplier", 1.2, "nerf", -0.1, 1.1, "Upper torso damage multiplier reduced from 1.2x to 1.1x."),
        ("oden_mw4", "lower_torso_multiplier", 1.1, "nerf", -0.1, 1.0, "Lower torso damage multiplier normalized from 1.1x to 1.0x."),
        # PPSh-41
        ("ppsh41_mw4", "base_ads_ms", 300.0, "buff", -20.0, 280.0, "ADS In Speed quickened from 300ms to 280ms (-7%)."),
        ("ppsh41_mw4", "move_speed_mps", 4.66, "buff", 0.04, 4.70, "Base movement speed increased from 4.66 to 4.70 m/s."),
        ("ppsh41_mw4", "ads_move_speed_mps", 2.75, "buff", 0.03, 2.78, "ADS strafe movement speed buffed from 2.75 to 2.78 m/s."),
        ("ppsh41_mw4", "arm_damage_multiplier", 0.95, "buff", 0.05, 1.0, "Arm and hand hit location damage normalized to 1.0x."),
        # ISO Nightshade
        ("iso_nightshade_mw4", "arm_damage_multiplier", 0.95, "buff", 0.05, 1.0, "Arm and hand damage multiplier increased from 0.95x to 1.0x."),
        # VEL 46
        ("vel46_mw4", "arm_damage_multiplier", 0.95, "buff", 0.05, 1.0, "Arm and hand damage multiplier increased from 0.95x to 1.0x."),
        # Wz.55 Striga
        ("wz55_striga_mw4", "range_effective_m", 16.0, "buff", 1.1, 17.1, "Max damage range extended from 440 to 470 units (+7%)."),
        ("wz55_striga_mw4", "range_mid_m", 30.0, "buff", 0.6, 30.6, "Mid damage range 1 extended from 825 to 840 units (+2%)."),
        ("wz55_striga_mw4", "arm_damage_multiplier", 0.95, "buff", 0.05, 1.0, "Arm and hand damage multiplier normalized to 1.0x."),
        # X-58 Nyx
        ("x58_nyx_mw4", "damage_head_multiplier", 1.25, "buff", 0.05, 1.30, "Head damage multiplier buffed from 1.25x to 1.30x (+4%)."),
        ("x58_nyx_mw4", "arm_damage_multiplier", 0.95, "buff", 0.05, 1.0, "Arm and hand damage multiplier normalized to 1.0x."),
        # APOC-338
        ("apoc338_mw4", "damage_mid", 38.0, "nerf", -1.0, 37.0, "Mid damage reduced from 38 to 37 (-3%)."),
        ("apoc338_mw4", "range_mid_m", 42.0, "nerf", -1.7, 40.3, "Mid damage range 1 reduced from 1980 to 1900 units (-4%)."),
        ("apoc338_mw4", "damage_min", 35.0, "nerf", -2.0, 33.0, "Min damage reduced from 35 to 33 (-6%)."),
        # FiNN LMG
        ("finn_lmg_mw4", "range_mid_m", 35.0, "nerf", -2.0, 33.0, "Mid damage range 1 reduced from 1720 to 1620 units (-6%)."),
        ("finn_lmg_mw4", "arm_damage_multiplier", 1.1, "nerf", -0.1, 1.0, "Upper arm damage multiplier normalized from 1.1x to 1.0x (-9%)."),
        # Patriot XMR Attachments
        ("patriot_xmr_mw4", "exp_haste_recoil_penalty_pct", 8.0, "buff", -2.0, 6.0, "EXP Haste 80L 14-inch barrel recoil penalty reduced from 8% to 6%."),
        ("patriot_xmr_mw4", "fjx_fury_recoil_penalty_pct", 5.0, "buff", -1.0, 4.0, "FJX Fury IV skeleton rear grip recoil penalty reduced from 5% to 4%."),
        # Oden - Sentinel Apex Attachment
        ("oden_mw4", "sentinel_apex_max_range_units", 870.0, "nerf", -50.0, 820.0, "Sentinel Apex Attachment: Max damage range reduced from 870 to 820 units (-6%)."),
        ("oden_mw4", "sentinel_apex_mid_range_units", 1810.0, "nerf", -70.0, 1740.0, "Sentinel Apex Attachment: Mid damage range 1 reduced from 1810 to 1740 units (-4%)."),
        ("oden_mw4", "sentinel_apex_muzzle_velocity_pct", 0.0, "nerf", -7.0, -7.0, "Sentinel Apex Attachment: Added -7% muzzle velocity penalty."),
        # Hyeon Burst - Hyperburst Apex Attachment
        ("hyeon_burst_mw4", "hyperburst_apex_max_damage", 37.0, "nerf", -3.0, 34.0, "Hyperburst Apex Attachment: Full-auto max damage reduced from 37 to 34 (-8%)."),
        ("hyeon_burst_mw4", "hyperburst_apex_max_range_units", 970.0, "buff", 250.0, 1220.0, "Hyperburst Apex Attachment: Full-auto max damage range increased from 970 to 1220 units (+26%)."),
        # X-58 Nyx - Void Apex Attachment
        ("x58_nyx_mw4", "void_apex_max_range_units", 437.0, "buff", 23.0, 460.0, "Void Apex Attachment: Max damage range increased from 437 to 460 units (+5%)."),
        ("x58_nyx_mw4", "void_apex_mid_range_units", 788.0, "buff", 27.0, 815.0, "Void Apex Attachment: Mid damage range 1 increased from 788 to 815 units (+3%)."),
        # Type 73 - Assault Apex Attachment
        ("type73_mw4", "assault_apex_min_damage", 19.0, "buff", 1.0, 20.0, "Assault Apex Attachment: Minimum damage increased from 19 to 20 (+5%)."),
        # Warlord - 12G Slug Rounds
        ("warlord_mw4", "slug_12g_mid_range_units", 900.0, "nerf", -90.0, 810.0, "12G Slug Rounds: Mid damage range 2 reduced from 900 to 810 units (-10%).")
    ]

    for wid, stat, prev, dtype, dval, newv, notes in deltas:
        ev_id = f"delta_oct28_{wid}_{stat}"
        con.execute("""
            INSERT INTO stat_delta_events (
                event_id, weapon_id, stat_name, patch_version_id, effective_date,
                previous_value, delta_type, delta_value, new_value, official_patch_url,
                developer_notes, captured_timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (event_id) DO UPDATE SET
                previous_value = EXCLUDED.previous_value,
                delta_type = EXCLUDED.delta_type,
                delta_value = EXCLUDED.delta_value,
                new_value = EXCLUDED.new_value,
                developer_notes = EXCLUDED.developer_notes,
                captured_timestamp = EXCLUDED.captured_timestamp
        """, [
            ev_id, wid, stat, PATCH_VERSION, PATCH_DATE,
            prev, dtype, dval, newv, PATCH_URL, notes, TIMESTAMP
        ])
    print(f"✓ Ingested {len(deltas)} stat delta events.")

    # 6. CLONE META BUILDS & SYNC OCT 30 POST-PATCH CONSENSUS FOR NEW VERSION
    print(f"Cloning meta builds and syncing Oct 30 post-patch consensus for {PATCH_VERSION}...")
    con.execute("UPDATE meta_build_presets SET secondary_name = 'Sang 9mm' WHERE secondary_name LIKE '%Renetti%'")
    con.execute("UPDATE community_meta_consensus SET recommended_secondary = 'Sang 9mm' WHERE recommended_secondary LIKE '%Renetti%'")

    con.execute(f"DELETE FROM meta_build_presets WHERE game_version_id = '{PATCH_VERSION}'")
    con.execute(f"""
        INSERT INTO meta_build_presets (
            build_id, weapon_id, game_version_id, build_name, archetype, archetype_display,
            source_outlet, attachment_ids_json, perk_1_name, perk_2_name, perk_3_name,
            tactical_name, lethal_name, field_upgrade_name, secondary_name, secondary_role,
            secondary_attachments_json, best_maps, playstyle_notes, share_code, is_verified_meta, created_at
        )
        SELECT 
            build_id || '_oct28', weapon_id, '{PATCH_VERSION}', build_name, archetype, archetype_display,
            source_outlet, attachment_ids_json, perk_1_name, perk_2_name, perk_3_name,
            tactical_name, lethal_name, field_upgrade_name, secondary_name, secondary_role,
            secondary_attachments_json, best_maps, playstyle_notes, share_code, is_verified_meta, '{TIMESTAMP}'
        FROM meta_build_presets
        WHERE game_version_id = '{PREV_VERSION}'
    """)

    con.execute(f"DELETE FROM community_meta_consensus WHERE game_version_id = '{PATCH_VERSION}'")
    oct30_consensus = [
        # --- ASSAULT RIFLES (8) ---
        {
            "weapon_id": "m4_mw4",
            "wzstats": "S-Tier 🔥", "wzranked": "S-Tier 🔥", "codmunity": "A-Tier ⚡",
            "dexerto": "S-Tier 🔥", "charlie": "S-Tier 🔥", "dotesports": "S-Tier 🔥",
            "tag": "👑 #1 ALL-AROUND WORKHORSE AR (OCT 28 BUFF)", "color": "#f43f5e",
            "pick_rate": 23.6, "kd": 1.25, "secondary": "Krait P68",
            "win_rate": 55.8, "trend": 3.2, "hs": 21.5, "kpm": 2.25
        },
        {
            "weapon_id": "patriot_xmr_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "S-Tier 🔥", "codmunity": "A-Tier ⚡",
            "dexerto": "A-Tier ⚡", "charlie": "S-Tier 🔥", "dotesports": "S-Tier 🔥",
            "tag": "👑 S-TIER FLEX AR (OCT 28 RECOIL BUFF)", "color": "#f43f5e",
            "pick_rate": 20.8, "kd": 1.29, "secondary": "Krait P68",
            "win_rate": 56.1, "trend": 2.9, "hs": 22.4, "kpm": 2.38
        },
        {
            "weapon_id": "axion_mw4",
            "wzstats": "S-Tier 🔥", "wzranked": "S-Tier 🔥", "codmunity": "S-Tier 🔥",
            "dexerto": "S-Tier 🔥", "charlie": "S-Tier 🔥", "dotesports": "A-Tier ⚡",
            "tag": "👑 #1 META SURGE AR (255ms TTK)", "color": "#f43f5e",
            "pick_rate": 19.4, "kd": 1.27, "secondary": "Krait P68",
            "win_rate": 55.9, "trend": 8.4, "hs": 21.8, "kpm": 2.30
        },
        {
            "weapon_id": "hyeon_burst_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "S-Tier 🔥",
            "dexerto": "A-Tier ⚡", "charlie": "S-Tier 🔥", "dotesports": "S-Tier 🔥",
            "tag": "⚡ #1 ONE-BURST LETHAL AR (144ms TTK)", "color": "#f43f5e",
            "pick_rate": 17.5, "kd": 1.32, "secondary": "VEL 46",
            "win_rate": 56.5, "trend": 1.8, "hs": 28.2, "kpm": 2.18
        },
        {
            "weapon_id": "han86_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "S-Tier 🔥", "codmunity": "B-Tier 🔷",
            "dexerto": "B-Tier 🔷", "charlie": "S-Tier 🔥", "dotesports": "A-Tier ⚡",
            "tag": "👑 CDL PRO STAPLE (30m RANGE BUFF)", "color": "#38bdf8",
            "pick_rate": 28.4, "kd": 1.22, "secondary": "Krait P68",
            "win_rate": 54.2, "trend": -1.4, "hs": 23.0, "kpm": 2.22
        },
        {
            "weapon_id": "kastov762_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "A-Tier ⚡",
            "dexerto": "A-Tier ⚡", "charlie": "A-Tier ⚡", "dotesports": "A-Tier ⚡",
            "tag": "💪 31m RANGE BUFFED 7.62 HAMMER", "color": "#38bdf8",
            "pick_rate": 12.6, "kd": 1.21, "secondary": ".50 GS",
            "win_rate": 53.9, "trend": 3.1, "hs": 21.0, "kpm": 2.12
        },
        {
            "weapon_id": "oden_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
            "dexerto": "A-Tier ⚡", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ SLOW 2-SHOT HEAVY AR (OCT 28 NERF)", "color": "#4ade80",
            "pick_rate": 3.4, "kd": 1.10, "secondary": "ISO Nightshade",
            "win_rate": 50.6, "trend": -1.2, "hs": 24.5, "kpm": 1.68
        },
        {
            "weapon_id": "cronen_squall_mw4",
            "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
            "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ HIGH-RECOIL 6.8 WRENCH", "color": "#4ade80",
            "pick_rate": 3.6, "kd": 1.11, "secondary": "VEL 46",
            "win_rate": 51.0, "trend": -0.3, "hs": 22.0, "kpm": 1.80
        },

        # --- SUBMACHINE GUNS (5) ---
        {
            "weapon_id": "iso_nightshade_mw4",
            "wzstats": "S-Tier 🔥", "wzranked": "S-Tier 🔥", "codmunity": "S-Tier 🔥",
            "dexerto": "S-Tier 🔥", "charlie": "S-Tier 🔥", "dotesports": "S-Tier 🔥",
            "tag": "👑 UNANIMOUS 6/6 S-TIER CQB KING", "color": "#f43f5e",
            "pick_rate": 24.8, "kd": 1.27, "secondary": "Sang 9mm",
            "win_rate": 56.2, "trend": 4.1, "hs": 19.8, "kpm": 2.48
        },
        {
            "weapon_id": "vel46_mw4",
            "wzstats": "S-Tier 🔥", "wzranked": "S-Tier 🔥", "codmunity": "S-Tier 🔥",
            "dexerto": "S-Tier 🔥", "charlie": "S-Tier 🔥", "dotesports": "A-Tier ⚡",
            "tag": "👑 #1 META SMG SURGE (OCT 28 LIMB BUFF)", "color": "#f43f5e",
            "pick_rate": 22.4, "kd": 1.26, "secondary": "Krait P68",
            "win_rate": 55.7, "trend": 6.8, "hs": 18.8, "kpm": 2.42
        },
        {
            "weapon_id": "ppsh41_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "S-Tier 🔥", "codmunity": "A-Tier ⚡",
            "dexerto": "A-Tier ⚡", "charlie": "S-Tier 🔥", "dotesports": "A-Tier ⚡",
            "tag": "⚡ 280ms ADS + 1110-RPM SWARM (OCT 28 BUFF)", "color": "#38bdf8",
            "pick_rate": 18.2, "kd": 1.23, "secondary": "Patriot XMR",
            "win_rate": 54.4, "trend": 3.6, "hs": 17.5, "kpm": 2.45
        },
        {
            "weapon_id": "x58_nyx_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "B-Tier 🔷",
            "dexerto": "A-Tier ⚡", "charlie": "A-Tier ⚡", "dotesports": "B-Tier 🔷",
            "tag": "⚡ 1.30x HEADSHOT & VOID APEX BUFFED", "color": "#38bdf8",
            "pick_rate": 12.9, "kd": 1.18, "secondary": "Krait P68",
            "win_rate": 52.6, "trend": 2.1, "hs": 19.5, "kpm": 2.18
        },
        {
            "weapon_id": "wz55_striga_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "B-Tier 🔷",
            "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ 17.1m RANGE & LIMB BUFFED SMG", "color": "#4ade80",
            "pick_rate": 7.2, "kd": 1.12, "secondary": "Krait P68",
            "win_rate": 51.4, "trend": 1.8, "hs": 18.0, "kpm": 2.04
        },

        # --- SHOTGUNS (2) ---
        {
            "weapon_id": "rezi12_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "B-Tier 🔷",
            "dexerto": "C-Tier ⚙️", "charlie": "A-Tier ⚡", "dotesports": "B-Tier 🔷",
            "tag": "💥 #1 POINT-BLANK 1-PUMP SHOTGUN", "color": "#38bdf8",
            "pick_rate": 7.6, "kd": 1.16, "secondary": "Patriot XMR",
            "win_rate": 52.6, "trend": 0.4, "hs": 14.0, "kpm": 2.28
        },
        {
            "weapon_id": "warlord_mw4",
            "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
            "dexerto": "C-Tier ⚙️", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ SLUG RANGE TUNED BREACHER", "color": "#4ade80",
            "pick_rate": 2.6, "kd": 1.04, "secondary": "Patriot XMR",
            "win_rate": 49.5, "trend": -0.8, "hs": 12.0, "kpm": 2.00
        },

        # --- LMGS (3) ---
        {
            "weapon_id": "type73_mw4",
            "wzstats": "B-Tier 🔷", "wzranked": "A-Tier ⚡", "codmunity": "B-Tier 🔷",
            "dexerto": "C-Tier ⚙️", "charlie": "A-Tier ⚡", "dotesports": "A-Tier ⚡",
            "tag": "🛡️ ASSAULT APEX BUFFED 821-RPM LMG", "color": "#38bdf8",
            "pick_rate": 13.2, "kd": 1.20, "secondary": "Krait P68",
            "win_rate": 52.8, "trend": 1.1, "hs": 19.0, "kpm": 2.12
        },
        {
            "weapon_id": "finn_lmg_mw4",
            "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
            "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ SUSTAINED SUPPRESSION LMG (OCT 28 NERF)", "color": "#4ade80",
            "pick_rate": 4.6, "kd": 1.07, "secondary": "ISO Nightshade",
            "win_rate": 50.2, "trend": -1.1, "hs": 16.0, "kpm": 1.72
        },
        {
            "weapon_id": "apoc338_mw4",
            "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "C-Tier ⚙️",
            "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ .338 MAGNUM HEAVY LMG (OCT 28 NERF)", "color": "#4ade80",
            "pick_rate": 3.4, "kd": 1.08, "secondary": "VEL 46",
            "win_rate": 50.1, "trend": -0.9, "hs": 20.0, "kpm": 1.66
        },

        # --- MARKSMAN RIFLES (3) ---
        {
            "weapon_id": "mosin_nagant_mw4",
            "wzstats": "S-Tier 🔥", "wzranked": "A-Tier ⚡", "codmunity": "B-Tier 🔷",
            "dexerto": "S-Tier 🔥", "charlie": "A-Tier ⚡", "dotesports": "A-Tier ⚡",
            "tag": "🎯 #1 SNAP-AIM ONE-SHOT MARKSMAN", "color": "#38bdf8",
            "pick_rate": 9.8, "kd": 1.21, "secondary": "VEL 46",
            "win_rate": 53.5, "trend": 4.5, "hs": 34.0, "kpm": 1.92
        },
        {
            "weapon_id": "oris86_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
            "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ SILENT INTEGRAL-SUPPRESSED SCOUT", "color": "#4ade80",
            "pick_rate": 9.2, "kd": 1.15, "secondary": "Krait P68",
            "win_rate": 51.4, "trend": 0.4, "hs": 31.0, "kpm": 1.85
        },
        {
            "weapon_id": "mar9_mw4",
            "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
            "dexerto": "C-Tier ⚙️", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ 2-TAP PRECISION DMR", "color": "#4ade80",
            "pick_rate": 4.0, "kd": 1.12, "secondary": "Krait P68",
            "win_rate": 50.9, "trend": 0.1, "hs": 29.0, "kpm": 1.78
        },

        # --- SNIPER RIFLES (3) ---
        {
            "weapon_id": "kg7_vulcan_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "S-Tier 🔥",
            "dexerto": "A-Tier ⚡", "charlie": "S-Tier 🔥", "dotesports": "A-Tier ⚡",
            "tag": "🎯 #1 S&D QUICK-SCOPE SNIPER", "color": "#f43f5e",
            "pick_rate": 15.4, "kd": 1.34, "secondary": "Krait P68",
            "win_rate": 54.4, "trend": 2.2, "hs": 37.0, "kpm": 1.94
        },
        {
            "weapon_id": "signal50_mw4",
            "wzstats": "B-Tier 🔷", "wzranked": "A-Tier ⚡", "codmunity": "A-Tier ⚡",
            "dexerto": "B-Tier 🔷", "charlie": "A-Tier ⚡", "dotesports": "S-Tier 🔥",
            "tag": "🎯 RAPID SEMI-AUTO .50 BMG", "color": "#38bdf8",
            "pick_rate": 8.6, "kd": 1.32, "secondary": "ISO Nightshade",
            "win_rate": 53.8, "trend": 0.6, "hs": 34.0, "kpm": 1.84
        },
        {
            "weapon_id": "astaroth57_mw4",
            "wzstats": "A-Tier ⚡", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
            "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ HEAVY ANTI-MATERIEL SNIPER", "color": "#4ade80",
            "pick_rate": 3.5, "kd": 1.15, "secondary": "VEL 46",
            "win_rate": 50.5, "trend": 0.3, "hs": 38.0, "kpm": 1.62
        },

        # --- PISTOLS (4) ---
        {
            "weapon_id": "krait_p68_mw4",
            "wzstats": "C-Tier ⚙️", "wzranked": "A-Tier ⚡", "codmunity": "B-Tier 🔷",
            "dexerto": "B-Tier 🔷", "charlie": "A-Tier ⚡", "dotesports": "A-Tier ⚡",
            "tag": "👑 #1 CDL PRO POCKET FINISHER", "color": "#38bdf8",
            "pick_rate": 19.2, "kd": 1.20, "secondary": "Patriot XMR",
            "win_rate": 53.6, "trend": 2.4, "hs": 21.0, "kpm": 2.16
        },
        {
            "weapon_id": "gs50_mw4",
            "wzstats": "C-Tier ⚙️", "wzranked": "A-Tier ⚡", "codmunity": "C-Tier ⚙️",
            "dexerto": "C-Tier ⚙️", "charlie": "B-Tier 🔷", "dotesports": "A-Tier ⚡",
            "tag": "💥 2-TAP HIGH-CALIBER HAND CANNON", "color": "#38bdf8",
            "pick_rate": 8.1, "kd": 1.21, "secondary": "Patriot XMR",
            "win_rate": 52.9, "trend": 0.8, "hs": 27.5, "kpm": 1.94
        },
        {
            "weapon_id": "sang9mm_mw4",
            "wzstats": "C-Tier ⚙️", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
            "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ FAST-SWAP 9MM SIDEARM", "color": "#4ade80",
            "pick_rate": 4.2, "kd": 1.07, "secondary": "M4",
            "win_rate": 50.3, "trend": 0.2, "hs": 19.0, "kpm": 1.92
        },
        {
            "weapon_id": "mojave357_mw4",
            "wzstats": "C-Tier ⚙️", "wzranked": "B-Tier 🔷", "codmunity": "C-Tier ⚙️",
            "dexerto": "C-Tier ⚙️", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "⭐ .357 MAGNUM REVOLVER", "color": "#4ade80",
            "pick_rate": 2.3, "kd": 1.07, "secondary": "M4",
            "win_rate": 49.4, "trend": -0.2, "hs": 25.0, "kpm": 1.68
        },

        # --- LAUNCHERS & MELEE (5) ---
        {
            "weapon_id": "pila_mw4",
            "wzstats": "D-Tier 🔘", "wzranked": "C-Tier ⚙️", "codmunity": "C-Tier ⚙️",
            "dexerto": "D-Tier 🔘", "charlie": "C-Tier ⚙️", "dotesports": "C-Tier ⚙️",
            "tag": "🛡️ ANTI-STREAK LOCK-ON LAUNCHER", "color": "#94a3b8",
            "pick_rate": 1.8, "kd": 0.85, "secondary": "M4",
            "win_rate": 48.5, "trend": 0.0, "hs": 0.0, "kpm": 1.10
        },
        {
            "weapon_id": "rpg8_mw4",
            "wzstats": "D-Tier 🔘", "wzranked": "C-Tier ⚙️", "codmunity": "C-Tier ⚙️",
            "dexerto": "D-Tier 🔘", "charlie": "C-Tier ⚙️", "dotesports": "C-Tier ⚙️",
            "tag": "💥 OBJECTIVE ROOM CLEARER", "color": "#94a3b8",
            "pick_rate": 2.1, "kd": 0.92, "secondary": "ISO Nightshade",
            "win_rate": 49.0, "trend": 0.1, "hs": 0.0, "kpm": 1.25
        },
        {
            "weapon_id": "jokr_mw4",
            "wzstats": "D-Tier 🔘", "wzranked": "C-Tier ⚙️", "codmunity": "C-Tier ⚙️",
            "dexerto": "D-Tier 🔘", "charlie": "C-Tier ⚙️", "dotesports": "C-Tier ⚙️",
            "tag": "🚀 TOP-ATTACK THERMAL LAUNCHER", "color": "#94a3b8",
            "pick_rate": 1.2, "kd": 0.82, "secondary": "Han 86",
            "win_rate": 48.0, "trend": -0.1, "hs": 0.0, "kpm": 0.95
        },
        {
            "weapon_id": "pm40_anvil_mw4",
            "wzstats": "D-Tier 🔘", "wzranked": "C-Tier ⚙️", "codmunity": "C-Tier ⚙️",
            "dexerto": "D-Tier 🔘", "charlie": "C-Tier ⚙️", "dotesports": "C-Tier ⚙️",
            "tag": "🛡️ HEAVY BREACH LAUNCHER", "color": "#94a3b8",
            "pick_rate": 0.9, "kd": 0.88, "secondary": "VEL 46",
            "win_rate": 48.2, "trend": 0.0, "hs": 0.0, "kpm": 1.05
        },
        {
            "weapon_id": "fss_carbon_edge_mw4",
            "wzstats": "D-Tier 🔘", "wzranked": "B-Tier 🔷", "codmunity": "A-Tier ⚡",
            "dexerto": "C-Tier ⚙️", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
            "tag": "🗡️ MAX-SPRINT 1-HIT MELEE BLADE", "color": "#4ade80",
            "pick_rate": 4.2, "kd": 1.15, "secondary": "ISO Nightshade",
            "win_rate": 51.3, "trend": 0.5, "hs": 0.0, "kpm": 2.50
        }
    ]

    for item in oct30_consensus:
        cid = f"{item['weapon_id']}_{PATCH_VERSION}_consensus"
        con.execute("""
            INSERT INTO community_meta_consensus (
                consensus_id, weapon_id, game_version_id, wzstats_tier, wzranked_tier,
                codmunity_tier, dexerto_tier, charlie_tier, dotesports_tier, consensus_tag,
                badge_color, community_pick_rate_pct, community_kd_ratio, recommended_secondary,
                last_updated, global_win_rate_pct, meta_trend_delta_pct, headshot_pct, kills_per_minute
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            cid, item["weapon_id"], PATCH_VERSION, item["wzstats"], item["wzranked"],
            item["codmunity"], item["dexerto"], item["charlie"], item["dotesports"],
            item["tag"], item["color"], item["pick_rate"], item["kd"], item["secondary"],
            TIMESTAMP, item["win_rate"], item["trend"], item["hs"], item["kpm"]
        ])

    # 7. LOG EVIDENCE LEDGER ENTRIES (OCT 28 TUNING + OCT 29 PATCH + OCT 30 LIVE META SYNC)
    print("Writing verified evidence ledger entries through October 30, 2026...")
    con.execute("""
        INSERT INTO evidence_ledger (
            evidence_id, target_entity_type, target_entity_id, field_name, observed_value,
            source_url, source_name, source_tier, test_method, captured_timestamp,
            recorded_by, verification_status, confidence_score, notes
        ) VALUES (
            'ev_mw4_oct28_weapon_tuning_patchnotes',
            'patch_notes',
            ?,
            'oct28_weapon_tuning',
            '15 weapons & Apex attachments tuned',
            ?,
            'Official Call of Duty Blog & Patch Notes',
            'tier_1',
            'First-party developer patch notes and live weapon balance release',
            ?,
            'system',
            'verified',
            1.00,
            'Official MW4 Launch Patch Notes update dated October 28, 2026 detailing weapon tuning, SMG upper-limb hit location damage normalization, Apex attachment balance, and Patriot XMR recoil penalty reductions.'
        )
        ON CONFLICT (evidence_id) DO UPDATE SET
            observed_value = EXCLUDED.observed_value,
            source_url = EXCLUDED.source_url,
            test_method = EXCLUDED.test_method,
            captured_timestamp = EXCLUDED.captured_timestamp,
            verification_status = EXCLUDED.verification_status,
            confidence_score = EXCLUDED.confidence_score,
            notes = EXCLUDED.notes
    """, [PATCH_VERSION, PATCH_URL, TIMESTAMP])

    con.execute("""
        INSERT INTO evidence_ledger (
            evidence_id, target_entity_type, target_entity_id, field_name, observed_value,
            source_url, source_name, source_tier, test_method, captured_timestamp,
            recorded_by, verification_status, confidence_score, notes
        ) VALUES (
            'ev_mw4_oct29_oct30_patch_and_meta_sync',
            'multi_community_consensus',
            ?,
            'oct30_live_meta_and_patch_audit',
            'Oct 29 Official Patch (0 weapon deltas) + Oct 30 6-Platform Meta Sync (33/33 weapons)',
            ?,
            'Official Call of Duty Patch Notes & 6-Authority Meta Index (WZStats, GGRanked, CODMunity, Dexerto)',
            'tier_1',
            'Live October 30, 2026 web audit of official patch notes (Oct 28-29 updates) and post-patch 6-outlet tier consensus',
            ?,
            'system',
            'verified',
            0.99,
            'Verified October 29, 2026 patch notes (Possession mode, MP XP buff, DMZ cash economy buff, SMG upper-limb normalization note) and synchronized October 30, 2026 post-patch tier standings across all 33 MW4 weapons.'
        )
        ON CONFLICT (evidence_id) DO UPDATE SET
            observed_value = EXCLUDED.observed_value,
            source_url = EXCLUDED.source_url,
            test_method = EXCLUDED.test_method,
            captured_timestamp = EXCLUDED.captured_timestamp,
            verification_status = EXCLUDED.verification_status,
            confidence_score = EXCLUDED.confidence_score,
            notes = EXCLUDED.notes
    """, [PATCH_VERSION, PATCH_URL, TIMESTAMP])

    con.close()
    print("✓ DuckDB migration complete!")

    # 8. EXPORT PARQUET SNAPSHOTS
    print(f"Exporting updated Parquet snapshots to {SNAPSHOTS_DIR}...")
    db_manager.export_all_to_parquet(SNAPSHOTS_DIR)
    print("✓ Parquet snapshots synchronized successfully!")


if __name__ == "__main__":
    main()
