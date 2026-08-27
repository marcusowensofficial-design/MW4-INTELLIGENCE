"""
MW4 Weapon Intelligence Lab - Seed Data Generator
Populates the database with realistic illustrative data across game versions, rulesets,
weapons, attachments, damage profiles, and evidence records.
"""

from typing import List
from .connection import db_manager, DatabaseManager
from .repository import IntelligenceRepository
from .models import (
    GameVersion,
    Ruleset,
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Attachment,
    AttachmentModifier,
    EvidenceLedgerEntry,
    AIReviewItem,
    CustomBuild,
    StatDeltaEvent,
    CommunityMetaConsensus,
    MetaBuildPreset,
    WeaponClass,
    FiringMode,
    AttachmentSlot,
    ModifierType,
    SourceTier,
    VerificationStatus
)


def seed_database(manager: DatabaseManager = db_manager) -> None:
    """Initializes and seeds DuckDB with full baseline weapon intelligence."""
    manager.init_database()
    repo = IntelligenceRepository(manager)

    # 1. Game Versions
    versions = [
        GameVersion(
            version_id="v1.0.0-beta",
            release_date="2026-09-01",
            patch_name="MW4 Public Beta Phase 1",
            is_active=False,
            notes="Initial public beta weapon tuning baseline."
        ),
        GameVersion(
            version_id="v1.1.0-launch",
            release_date="2026-10-25",
            patch_name="MW4 Global Launch Day 1 Patch",
            is_active=True,
            notes="Launch balancing: XM4 range adjusted, Rival-9 sprint-to-fire buffed, BAS-B recoil adjusted."
        )
    ]
    for v in versions:
        repo.upsert_game_version(v)

    # 2. Rulesets
    rulesets = [
        Ruleset(
            ruleset_id="core",
            name="Core 100 HP",
            description="Standard multiplayer ruleset with 100 HP, health regen, and hit-location multipliers.",
            target_health=100.0,
            regen_delay_ms=5000.0,
            regen_rate_hp_per_sec=25.0,
            friendly_fire=False,
            min_stk_cap=1,
            body_multipliers={
                "head": 1.40,
                "neck": 1.25,
                "upper_torso": 1.10,
                "lower_torso": 1.00,
                "limbs": 0.90
            }
        ),
        Ruleset(
            ruleset_id="hardcore",
            name="Hardcore 30 HP",
            description="Tactical high-lethality ruleset with 30 HP, zero health regen, and flat lethal damage.",
            target_health=30.0,
            regen_delay_ms=0.0,
            regen_rate_hp_per_sec=0.0,
            friendly_fire=True,
            min_stk_cap=1,
            body_multipliers={
                "head": 1.00,
                "neck": 1.00,
                "upper_torso": 1.00,
                "lower_torso": 1.00,
                "limbs": 1.00
            }
        ),
        Ruleset(
            ruleset_id="custom_wz_armor",
            name="Warzone 3-Plate (300 HP)",
            description="Simulated Battle Royale armored health pool (150 HP base + 150 armor).",
            target_health=300.0,
            regen_delay_ms=6000.0,
            regen_rate_hp_per_sec=20.0,
            friendly_fire=False,
            min_stk_cap=1,
            body_multipliers={
                "head": 1.35,
                "neck": 1.15,
                "upper_torso": 1.00,
                "lower_torso": 1.00,
                "limbs": 0.85
            }
        )
    ]
    for r in rulesets:
        repo.upsert_ruleset(r)

    # 3. Weapons Catalog
    weapons = [
        # Assault Rifles
        Weapon(
            weapon_id="xm4_mw4",
            name="XM4 Commando",
            weapon_class=WeaponClass.ASSAULT_RIFLE,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=780.0,
            base_mag_size=30,
            description="Versatile all-around assault rifle with balanced fire rate and predictable recoil."
        ),
        Weapon(
            weapon_id="mcw_mw4",
            name="MCW Precision",
            weapon_class=WeaponClass.ASSAULT_RIFLE,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=715.0,
            base_mag_size=30,
            description="Low-recoil tactical assault rifle engineered for precision at mid-to-long ranges."
        ),
        Weapon(
            weapon_id="ak74m_mw4",
            name="Kastov 74-M",
            weapon_class=WeaponClass.ASSAULT_RIFLE,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=650.0,
            base_mag_size=30,
            description="Heavy-caliber assault rifle delivering high per-shot damage at the cost of vertical climb."
        ),

        # Submachine Guns
        Weapon(
            weapon_id="rival9_mw4",
            name="Rival-9 SpecOps",
            weapon_class=WeaponClass.SUBMACHINE_GUN,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=900.0,
            base_mag_size=30,
            description="Rapid-fire submachine gun designed for elite close-quarters agility and room clearing."
        ),
        Weapon(
            weapon_id="striker45_mw4",
            name="Striker 45",
            weapon_class=WeaponClass.SUBMACHINE_GUN,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=645.0,
            base_mag_size=25,
            description="Hard-hitting .45 ACP submachine gun with class-leading effective damage range."
        ),
        Weapon(
            weapon_id="amr9_mw4",
            name="AMR-9 PDW",
            weapon_class=WeaponClass.SUBMACHINE_GUN,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=833.0,
            base_mag_size=30,
            description="High-velocity 9mm platform bridging the gap between SMG mobility and AR range."
        ),

        # Battle Rifles
        Weapon(
            weapon_id="basb_mw4",
            name="BAS-B Battle Rifle",
            weapon_class=WeaponClass.BATTLE_RIFLE,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=600.0,
            base_mag_size=20,
            description=".277 Fury chambered battle rifle offering punishing damage with steep recoil."
        ),

        # Marksman Rifles
        Weapon(
            weapon_id="kvd_enforcer_mw4",
            name="KVD Enforcer",
            weapon_class=WeaponClass.MARKSMAN_RIFLE,
            firing_mode=FiringMode.SEMI_AUTO,
            default_rpm=315.0,
            base_mag_size=20,
            description="Semi-automatic designated marksman rifle offering consistent 2-shot lethality."
        ),

        # Sniper Rifles
        Weapon(
            weapon_id="longbow_mw4",
            name="Longbow Tactical Sniper",
            weapon_class=WeaponClass.SNIPER_RIFLE,
            firing_mode=FiringMode.BOLT_ACTION,
            default_rpm=110.0,
            base_mag_size=10,
            description="High-mobility quick-chamber bolt-action sniper rifle lethal to the upper chest and head."
        ),

        # Light Machine Guns
        Weapon(
            weapon_id="pulemyot762_mw4",
            name="Pulemyot 762",
            weapon_class=WeaponClass.LIGHT_MACHINE_GUN,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=575.0,
            base_mag_size=100,
            description="Heavy sustained-fire machine gun offering immense suppression and 100-round capacity."
        ),

        # Additional Weapons
        Weapon(
            weapon_id="holger556_mw4",
            name="Holger 556",
            weapon_class=WeaponClass.ASSAULT_RIFLE,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=660.0,
            base_mag_size=30,
            description="5.56 NATO assault rifle engineered for superior range retention and low horizontal bounce."
        ),
        Weapon(
            weapon_id="wsp_swarm_mw4",
            name="WSP Swarm",
            weapon_class=WeaponClass.SUBMACHINE_GUN,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=1090.0,
            base_mag_size=32,
            description="Ultra-high fire rate 9mm micro-SMG offering devastating close-range TTK."
        ),
        Weapon(
            weapon_id="sidewinder_mw4",
            name="Sidewinder .450",
            weapon_class=WeaponClass.BATTLE_RIFLE,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=375.0,
            base_mag_size=20,
            description=".450 Bushmaster heavy battle rifle delivering punishing per-shot kinetic trauma."
        ),
        Weapon(
            weapon_id="bruen_mk9_mw4",
            name="Bruen Mk9",
            weapon_class=WeaponClass.LIGHT_MACHINE_GUN,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=750.0,
            base_mag_size=60,
            description="Air-cooled 5.56 squad automatic weapon with 60-round drum and steady sustained recoil."
        ),
        Weapon(
            weapon_id="katt_amr_mw4",
            name="KATT-AMR .50",
            weapon_class=WeaponClass.SNIPER_RIFLE,
            firing_mode=FiringMode.BOLT_ACTION,
            default_rpm=42.0,
            base_mag_size=5,
            description="Anti-materiel .50 BMG bolt-action sniper rifle delivering lethal 1-shot kills across all distances."
        ),

        # Shotguns
        Weapon(
            weapon_id="lockwood680_mw4",
            name="Lockwood 680",
            weapon_class=WeaponClass.SHOTGUN,
            firing_mode=FiringMode.PUMP_ACTION,
            default_rpm=75.0,
            base_mag_size=6,
            description="12-gauge pump shotgun providing devastating 1-shot lethality in close quarters."
        ),

        # Handguns
        Weapon(
            weapon_id="renetti_mw4",
            name="Renetti Tactical",
            weapon_class=WeaponClass.HANDGUN,
            firing_mode=FiringMode.BURST_3,
            default_rpm=480.0,
            base_mag_size=15,
            burst_count=3,
            burst_delay_ms=120.0,
            description="3-round burst sidearm with rapid cycle rate and excellent backup sprint speed."
        ),
        Weapon(
            weapon_id="cor45_mw4",
            name="COR-45",
            weapon_class=WeaponClass.HANDGUN,
            firing_mode=FiringMode.SEMI_AUTO,
            default_rpm=400.0,
            base_mag_size=13,
            description="Semi-automatic .45 ACP tactical sidearm with crisp trigger response."
        ),

        # 2026 Beta Roster Expansions
        Weapon(
            weapon_id="han86_mw4",
            name="Han 86",
            weapon_class=WeaponClass.ASSAULT_RIFLE,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=720.0,
            base_mag_size=30,
            description="High-stability bullpup assault rifle with exceptional mid-range beam consistency."
        ),
        Weapon(
            weapon_id="hyeon_burst_mw4",
            name="Hyeon Burst",
            weapon_class=WeaponClass.ASSAULT_RIFLE,
            firing_mode=FiringMode.BURST_3,
            default_rpm=850.0,
            base_mag_size=30,
            burst_count=3,
            burst_delay_ms=110.0,
            description="Tactical 3-round burst assault rifle lethal in a single concentrated upper-chest burst."
        ),
        Weapon(
            weapon_id="iso_nightshade_mw4",
            name="ISO Nightshade",
            weapon_class=WeaponClass.SUBMACHINE_GUN,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=950.0,
            base_mag_size=30,
            description="Rapid-cycling close-quarters SMG with hyper-fast sprint-to-fire speed."
        ),
        Weapon(
            weapon_id="ppsh41_mw4",
            name="PPSh-41",
            weapon_class=WeaponClass.SUBMACHINE_GUN,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=1000.0,
            base_mag_size=35,
            description="Legendary high-capacity open-bolt SMG with blistering room-clearing fire rate."
        ),
        Weapon(
            weapon_id="signal50_mw4",
            name="Signal .50",
            weapon_class=WeaponClass.SNIPER_RIFLE,
            firing_mode=FiringMode.SEMI_AUTO,
            default_rpm=120.0,
            base_mag_size=5,
            description="Semi-automatic .50 BMG anti-materiel sniper with devastating follow-up shot capability."
        ),
        Weapon(
            weapon_id="rezi12_mw4",
            name="Rezi 12",
            weapon_class=WeaponClass.SHOTGUN,
            firing_mode=FiringMode.FULL_AUTO,
            default_rpm=280.0,
            base_mag_size=10,
            description="Full-auto drum-fed combat shotgun engineered for extreme room-breaching dominance."
        )
    ]
    for w in weapons:
        repo.upsert_weapon(w)

    # 4. Weapon Version Stats (v1.0.0-beta and v1.1.0-launch)
    # Allows version diffing and patch tracking immediately
    version_stats = [
        # XM4
        WeaponVersionStats(
            stat_id="xm4_v1.0.0-beta",
            weapon_id="xm4_mw4",
            game_version_id="v1.0.0-beta",
            rpm=780.0,
            base_ads_ms=240.0,
            sprint_to_fire_ms=210.0,
            tactical_sprint_to_fire_ms=290.0,
            bullet_velocity_mps=720.0,
            reload_empty_s=2.40,
            reload_tactical_s=1.85,
            recoil_horizontal=18.5,
            recoil_vertical=26.0,
            hipfire_spread_deg=3.8,
            move_speed_mps=4.85,
            ads_move_speed_mps=2.90,
            flinch_resistance=1.0
        ),
        WeaponVersionStats(
            stat_id="xm4_v1.1.0-launch",
            weapon_id="xm4_mw4",
            game_version_id="v1.1.0-launch",
            rpm=780.0,
            base_ads_ms=235.0,  # Buff: 5ms faster ADS
            sprint_to_fire_ms=205.0, # Buff: 5ms faster STF
            tactical_sprint_to_fire_ms=280.0,
            bullet_velocity_mps=735.0, # Buff: velocity increase
            reload_empty_s=2.35,
            reload_tactical_s=1.80,
            recoil_horizontal=17.8, # Buff: slightly lower recoil
            recoil_vertical=25.2,
            hipfire_spread_deg=3.8,
            move_speed_mps=4.88,
            ads_move_speed_mps=2.95,
            flinch_resistance=1.0
        ),

        # MCW
        WeaponVersionStats(
            stat_id="mcw_v1.0.0-beta",
            weapon_id="mcw_mw4",
            game_version_id="v1.0.0-beta",
            rpm=715.0,
            base_ads_ms=230.0,
            sprint_to_fire_ms=200.0,
            tactical_sprint_to_fire_ms=275.0,
            bullet_velocity_mps=760.0,
            reload_empty_s=2.30,
            reload_tactical_s=1.75,
            recoil_horizontal=12.0,
            recoil_vertical=18.0,
            hipfire_spread_deg=3.5,
            move_speed_mps=4.90,
            ads_move_speed_mps=3.00,
            flinch_resistance=1.1
        ),
        WeaponVersionStats(
            stat_id="mcw_v1.1.0-launch",
            weapon_id="mcw_mw4",
            game_version_id="v1.1.0-launch",
            rpm=715.0,
            base_ads_ms=230.0,
            sprint_to_fire_ms=200.0,
            tactical_sprint_to_fire_ms=275.0,
            bullet_velocity_mps=760.0,
            reload_empty_s=2.30,
            reload_tactical_s=1.75,
            recoil_horizontal=13.2, # Slight nerf: slightly more recoil
            recoil_vertical=19.5,
            hipfire_spread_deg=3.5,
            move_speed_mps=4.90,
            ads_move_speed_mps=3.00,
            flinch_resistance=1.05
        ),

        # Kastov 74-M
        WeaponVersionStats(
            stat_id="ak74m_v1.1.0-launch",
            weapon_id="ak74m_mw4",
            game_version_id="v1.1.0-launch",
            rpm=650.0,
            base_ads_ms=260.0,
            sprint_to_fire_ms=225.0,
            tactical_sprint_to_fire_ms=310.0,
            bullet_velocity_mps=690.0,
            reload_empty_s=2.60,
            reload_tactical_s=2.00,
            recoil_horizontal=22.0,
            recoil_vertical=34.0,
            hipfire_spread_deg=4.2,
            move_speed_mps=4.75,
            ads_move_speed_mps=2.70,
            flinch_resistance=0.9
        ),

        # Rival-9
        WeaponVersionStats(
            stat_id="rival9_v1.0.0-beta",
            weapon_id="rival9_mw4",
            game_version_id="v1.0.0-beta",
            rpm=900.0,
            base_ads_ms=190.0,
            sprint_to_fire_ms=175.0,
            tactical_sprint_to_fire_ms=240.0,
            bullet_velocity_mps=540.0,
            reload_empty_s=2.10,
            reload_tactical_s=1.60,
            recoil_horizontal=24.0,
            recoil_vertical=28.0,
            hipfire_spread_deg=2.9,
            move_speed_mps=5.20,
            ads_move_speed_mps=3.60,
            flinch_resistance=1.2
        ),
        WeaponVersionStats(
            stat_id="rival9_v1.1.0-launch",
            weapon_id="rival9_mw4",
            game_version_id="v1.1.0-launch",
            rpm=900.0,
            base_ads_ms=180.0, # Buff: 10ms faster ADS
            sprint_to_fire_ms=160.0, # Buff: 15ms faster STF
            tactical_sprint_to_fire_ms=220.0,
            bullet_velocity_mps=550.0,
            reload_empty_s=2.05,
            reload_tactical_s=1.55,
            recoil_horizontal=23.0,
            recoil_vertical=27.0,
            hipfire_spread_deg=2.8,
            move_speed_mps=5.25,
            ads_move_speed_mps=3.70,
            flinch_resistance=1.2
        ),

        # Striker 45
        WeaponVersionStats(
            stat_id="striker45_v1.1.0-launch",
            weapon_id="striker45_mw4",
            game_version_id="v1.1.0-launch",
            rpm=645.0,
            base_ads_ms=205.0,
            sprint_to_fire_ms=185.0,
            tactical_sprint_to_fire_ms=250.0,
            bullet_velocity_mps=590.0,
            reload_empty_s=2.20,
            reload_tactical_s=1.70,
            recoil_horizontal=16.0,
            recoil_vertical=22.0,
            hipfire_spread_deg=3.1,
            move_speed_mps=5.10,
            ads_move_speed_mps=3.40,
            flinch_resistance=1.1
        ),

        # AMR-9
        WeaponVersionStats(
            stat_id="amr9_v1.1.0-launch",
            weapon_id="amr9_mw4",
            game_version_id="v1.1.0-launch",
            rpm=833.0,
            base_ads_ms=195.0,
            sprint_to_fire_ms=170.0,
            tactical_sprint_to_fire_ms=230.0,
            bullet_velocity_mps=580.0,
            reload_empty_s=2.15,
            reload_tactical_s=1.65,
            recoil_horizontal=20.0,
            recoil_vertical=25.0,
            hipfire_spread_deg=3.0,
            move_speed_mps=5.15,
            ads_move_speed_mps=3.50,
            flinch_resistance=1.15
        ),

        # BAS-B
        WeaponVersionStats(
            stat_id="basb_v1.0.0-beta",
            weapon_id="basb_mw4",
            game_version_id="v1.0.0-beta",
            rpm=600.0,
            base_ads_ms=270.0,
            sprint_to_fire_ms=235.0,
            tactical_sprint_to_fire_ms=320.0,
            bullet_velocity_mps=750.0,
            reload_empty_s=2.80,
            reload_tactical_s=2.10,
            recoil_horizontal=26.0,
            recoil_vertical=38.0,
            hipfire_spread_deg=4.5,
            move_speed_mps=4.65,
            ads_move_speed_mps=2.50,
            flinch_resistance=0.8
        ),
        WeaponVersionStats(
            stat_id="basb_v1.1.0-launch",
            weapon_id="basb_mw4",
            game_version_id="v1.1.0-launch",
            rpm=600.0,
            base_ads_ms=275.0, # Slight nerf: +5ms ADS
            sprint_to_fire_ms=240.0, # Slight nerf: +5ms STF
            tactical_sprint_to_fire_ms=330.0,
            bullet_velocity_mps=750.0,
            reload_empty_s=2.80,
            reload_tactical_s=2.10,
            recoil_horizontal=28.5, # Nerf: higher recoil
            recoil_vertical=41.0,
            hipfire_spread_deg=4.6,
            move_speed_mps=4.60,
            ads_move_speed_mps=2.45,
            flinch_resistance=0.8
        ),

        # KVD Enforcer
        WeaponVersionStats(
            stat_id="kvd_v1.1.0-launch",
            weapon_id="kvd_enforcer_mw4",
            game_version_id="v1.1.0-launch",
            rpm=315.0,
            base_ads_ms=280.0,
            sprint_to_fire_ms=250.0,
            tactical_sprint_to_fire_ms=340.0,
            bullet_velocity_mps=820.0,
            reload_empty_s=2.90,
            reload_tactical_s=2.20,
            recoil_horizontal=15.0,
            recoil_vertical=45.0,
            hipfire_spread_deg=5.0,
            move_speed_mps=4.55,
            ads_move_speed_mps=2.30,
            flinch_resistance=0.7
        ),

        # Longbow Sniper
        WeaponVersionStats(
            stat_id="longbow_v1.1.0-launch",
            weapon_id="longbow_mw4",
            game_version_id="v1.1.0-launch",
            rpm=110.0,
            base_ads_ms=440.0,
            sprint_to_fire_ms=320.0,
            tactical_sprint_to_fire_ms=420.0,
            bullet_velocity_mps=880.0,
            reload_empty_s=3.40,
            reload_tactical_s=2.70,
            recoil_horizontal=10.0,
            recoil_vertical=60.0,
            hipfire_spread_deg=7.5,
            move_speed_mps=4.40,
            ads_move_speed_mps=1.80,
            flinch_resistance=0.5
        ),

        # Pulemyot 762 LMG
        WeaponVersionStats(
            stat_id="pulemyot_v1.1.0-launch",
            weapon_id="pulemyot762_mw4",
            game_version_id="v1.1.0-launch",
            rpm=575.0,
            base_ads_ms=460.0,
            sprint_to_fire_ms=350.0,
            tactical_sprint_to_fire_ms=460.0,
            bullet_velocity_mps=790.0,
            reload_empty_s=6.80,
            reload_tactical_s=5.40,
            recoil_horizontal=25.0,
            recoil_vertical=35.0,
            hipfire_spread_deg=6.0,
            move_speed_mps=4.20,
            ads_move_speed_mps=1.90,
            flinch_resistance=0.8,
            open_bolt_delay_ms=50.0  # Open bolt delay characteristic of heavy GPMG
        ),

        # Lockwood 680 Shotgun
        WeaponVersionStats(
            stat_id="lockwood_v1.1.0-launch",
            weapon_id="lockwood680_mw4",
            game_version_id="v1.1.0-launch",
            rpm=75.0,
            base_ads_ms=260.0,
            sprint_to_fire_ms=210.0,
            tactical_sprint_to_fire_ms=280.0,
            bullet_velocity_mps=360.0,
            reload_empty_s=4.50,
            reload_tactical_s=0.75, # Per shell
            recoil_horizontal=30.0,
            recoil_vertical=70.0,
            hipfire_spread_deg=4.0,
            move_speed_mps=4.95,
            ads_move_speed_mps=3.10,
            flinch_resistance=1.0
        ),

        # Renetti Handgun
        WeaponVersionStats(
            stat_id="renetti_v1.1.0-launch",
            weapon_id="renetti_mw4",
            game_version_id="v1.1.0-launch",
            rpm=480.0,
            base_ads_ms=140.0,
            sprint_to_fire_ms=120.0,
            tactical_sprint_to_fire_ms=160.0,
            bullet_velocity_mps=420.0,
            reload_empty_s=1.80,
            reload_tactical_s=1.35,
            recoil_horizontal=15.0,
            recoil_vertical=22.0,
            hipfire_spread_deg=2.2,
            move_speed_mps=5.40,
            ads_move_speed_mps=4.10,
            flinch_resistance=1.3
        ),

        # Holger 556
        WeaponVersionStats(
            stat_id="holger556_v1.1.0-launch",
            weapon_id="holger556_mw4",
            game_version_id="v1.1.0-launch",
            rpm=660.0,
            base_ads_ms=250.0,
            sprint_to_fire_ms=215.0,
            tactical_sprint_to_fire_ms=295.0,
            bullet_velocity_mps=780.0,
            reload_empty_s=2.50,
            reload_tactical_s=1.90,
            recoil_horizontal=14.0,
            recoil_vertical=24.0,
            hipfire_spread_deg=3.7,
            move_speed_mps=4.82,
            ads_move_speed_mps=2.85,
            flinch_resistance=1.05
        ),

        # WSP Swarm
        WeaponVersionStats(
            stat_id="wsp_swarm_v1.1.0-launch",
            weapon_id="wsp_swarm_mw4",
            game_version_id="v1.1.0-launch",
            rpm=1090.0,
            base_ads_ms=175.0,
            sprint_to_fire_ms=155.0,
            tactical_sprint_to_fire_ms=220.0,
            bullet_velocity_mps=580.0,
            reload_empty_s=2.10,
            reload_tactical_s=1.60,
            recoil_horizontal=26.0,
            recoil_vertical=36.0,
            hipfire_spread_deg=2.8,
            move_speed_mps=5.15,
            ads_move_speed_mps=3.60,
            flinch_resistance=1.2
        ),

        # Sidewinder
        WeaponVersionStats(
            stat_id="sidewinder_v1.1.0-launch",
            weapon_id="sidewinder_mw4",
            game_version_id="v1.1.0-launch",
            rpm=375.0,
            base_ads_ms=290.0,
            sprint_to_fire_ms=245.0,
            tactical_sprint_to_fire_ms=330.0,
            bullet_velocity_mps=720.0,
            reload_empty_s=2.90,
            reload_tactical_s=2.20,
            recoil_horizontal=22.0,
            recoil_vertical=48.0,
            hipfire_spread_deg=4.8,
            move_speed_mps=4.60,
            ads_move_speed_mps=2.40,
            flinch_resistance=0.75
        ),

        # Bruen Mk9 LMG
        WeaponVersionStats(
            stat_id="bruen_mk9_v1.1.0-launch",
            weapon_id="bruen_mk9_mw4",
            game_version_id="v1.1.0-launch",
            rpm=750.0,
            base_ads_ms=410.0,
            sprint_to_fire_ms=320.0,
            tactical_sprint_to_fire_ms=430.0,
            bullet_velocity_mps=810.0,
            reload_empty_s=5.20,
            reload_tactical_s=4.10,
            recoil_horizontal=19.0,
            recoil_vertical=28.0,
            hipfire_spread_deg=5.2,
            move_speed_mps=4.35,
            ads_move_speed_mps=2.10,
            flinch_resistance=0.85,
            open_bolt_delay_ms=40.0
        ),

        # KATT-AMR .50 Sniper
        WeaponVersionStats(
            stat_id="katt_amr_v1.1.0-launch",
            weapon_id="katt_amr_mw4",
            game_version_id="v1.1.0-launch",
            rpm=42.0,
            base_ads_ms=580.0,
            sprint_to_fire_ms=380.0,
            tactical_sprint_to_fire_ms=490.0,
            bullet_velocity_mps=960.0,
            reload_empty_s=4.80,
            reload_tactical_s=3.80,
            recoil_horizontal=40.0,
            recoil_vertical=95.0,
            hipfire_spread_deg=7.5,
            move_speed_mps=3.95,
            ads_move_speed_mps=1.60,
            flinch_resistance=0.5
        ),

        # COR-45 Handgun
        WeaponVersionStats(
            stat_id="cor45_v1.1.0-launch",
            weapon_id="cor45_mw4",
            game_version_id="v1.1.0-launch",
            rpm=400.0,
            base_ads_ms=130.0,
            sprint_to_fire_ms=115.0,
            tactical_sprint_to_fire_ms=150.0,
            bullet_velocity_mps=450.0,
            reload_empty_s=1.70,
            reload_tactical_s=1.25,
            recoil_horizontal=12.0,
            recoil_vertical=20.0,
            hipfire_spread_deg=2.0,
            move_speed_mps=5.45,
            ads_move_speed_mps=4.20,
            flinch_resistance=1.35
        ),

        # Han 86
        WeaponVersionStats(
            stat_id="han86_v1.0.0-beta",
            weapon_id="han86_mw4",
            game_version_id="v1.0.0-beta",
            rpm=720.0,
            base_ads_ms=235.0,
            sprint_to_fire_ms=205.0,
            tactical_sprint_to_fire_ms=285.0,
            bullet_velocity_mps=740.0,
            reload_empty_s=2.35,
            reload_tactical_s=1.80,
            recoil_horizontal=16.5,
            recoil_vertical=24.0,
            hipfire_spread_deg=3.7,
            move_speed_mps=4.90,
            ads_move_speed_mps=2.95,
            flinch_resistance=1.0
        ),
        WeaponVersionStats(
            stat_id="han86_v1.1.0-launch",
            weapon_id="han86_mw4",
            game_version_id="v1.1.0-launch",
            rpm=720.0,
            base_ads_ms=230.0,
            sprint_to_fire_ms=200.0,
            tactical_sprint_to_fire_ms=280.0,
            bullet_velocity_mps=745.0,
            reload_empty_s=2.30,
            reload_tactical_s=1.75,
            recoil_horizontal=16.0,
            recoil_vertical=23.5,
            hipfire_spread_deg=3.6,
            move_speed_mps=4.92,
            ads_move_speed_mps=2.98,
            flinch_resistance=1.0
        ),

        # Hyeon Burst
        WeaponVersionStats(
            stat_id="hyeon_burst_v1.0.0-beta",
            weapon_id="hyeon_burst_mw4",
            game_version_id="v1.0.0-beta",
            rpm=850.0,
            base_ads_ms=240.0,
            sprint_to_fire_ms=210.0,
            tactical_sprint_to_fire_ms=290.0,
            bullet_velocity_mps=750.0,
            reload_empty_s=2.40,
            reload_tactical_s=1.85,
            recoil_horizontal=14.0,
            recoil_vertical=22.0,
            hipfire_spread_deg=3.9,
            move_speed_mps=4.85,
            ads_move_speed_mps=2.85,
            flinch_resistance=1.0
        ),
        WeaponVersionStats(
            stat_id="hyeon_burst_v1.1.0-launch",
            weapon_id="hyeon_burst_mw4",
            game_version_id="v1.1.0-launch",
            rpm=850.0,
            base_ads_ms=235.0,
            sprint_to_fire_ms=205.0,
            tactical_sprint_to_fire_ms=285.0,
            bullet_velocity_mps=760.0,
            reload_empty_s=2.35,
            reload_tactical_s=1.80,
            recoil_horizontal=13.5,
            recoil_vertical=21.5,
            hipfire_spread_deg=3.8,
            move_speed_mps=4.88,
            ads_move_speed_mps=2.90,
            flinch_resistance=1.0
        ),

        # ISO Nightshade
        WeaponVersionStats(
            stat_id="iso_nightshade_v1.0.0-beta",
            weapon_id="iso_nightshade_mw4",
            game_version_id="v1.0.0-beta",
            rpm=950.0,
            base_ads_ms=180.0,
            sprint_to_fire_ms=150.0,
            tactical_sprint_to_fire_ms=215.0,
            bullet_velocity_mps=580.0,
            reload_empty_s=2.15,
            reload_tactical_s=1.60,
            recoil_horizontal=22.0,
            recoil_vertical=28.0,
            hipfire_spread_deg=3.0,
            move_speed_mps=5.15,
            ads_move_speed_mps=3.40,
            flinch_resistance=1.1
        ),
        WeaponVersionStats(
            stat_id="iso_nightshade_v1.1.0-launch",
            weapon_id="iso_nightshade_mw4",
            game_version_id="v1.1.0-launch",
            rpm=950.0,
            base_ads_ms=175.0,
            sprint_to_fire_ms=145.0,
            tactical_sprint_to_fire_ms=210.0,
            bullet_velocity_mps=590.0,
            reload_empty_s=2.10,
            reload_tactical_s=1.55,
            recoil_horizontal=21.5,
            recoil_vertical=27.5,
            hipfire_spread_deg=2.9,
            move_speed_mps=5.18,
            ads_move_speed_mps=3.45,
            flinch_resistance=1.1
        ),

        # PPSh-41
        WeaponVersionStats(
            stat_id="ppsh41_v1.0.0-beta",
            weapon_id="ppsh41_mw4",
            game_version_id="v1.0.0-beta",
            rpm=1000.0,
            base_ads_ms=185.0,
            sprint_to_fire_ms=155.0,
            tactical_sprint_to_fire_ms=220.0,
            bullet_velocity_mps=520.0,
            reload_empty_s=2.35,
            reload_tactical_s=1.70,
            recoil_horizontal=26.0,
            recoil_vertical=32.0,
            hipfire_spread_deg=3.2,
            move_speed_mps=5.10,
            ads_move_speed_mps=3.35,
            flinch_resistance=1.0,
            open_bolt_delay_ms=30.0
        ),
        WeaponVersionStats(
            stat_id="ppsh41_v1.1.0-launch",
            weapon_id="ppsh41_mw4",
            game_version_id="v1.1.0-launch",
            rpm=1000.0,
            base_ads_ms=180.0,
            sprint_to_fire_ms=150.0,
            tactical_sprint_to_fire_ms=215.0,
            bullet_velocity_mps=530.0,
            reload_empty_s=2.30,
            reload_tactical_s=1.65,
            recoil_horizontal=25.0,
            recoil_vertical=31.0,
            hipfire_spread_deg=3.1,
            move_speed_mps=5.12,
            ads_move_speed_mps=3.38,
            flinch_resistance=1.0,
            open_bolt_delay_ms=30.0
        ),

        # Signal .50
        WeaponVersionStats(
            stat_id="signal50_v1.0.0-beta",
            weapon_id="signal50_mw4",
            game_version_id="v1.0.0-beta",
            rpm=120.0,
            base_ads_ms=490.0,
            sprint_to_fire_ms=300.0,
            tactical_sprint_to_fire_ms=410.0,
            bullet_velocity_mps=850.0,
            reload_empty_s=3.45,
            reload_tactical_s=2.65,
            recoil_horizontal=18.0,
            recoil_vertical=65.0,
            hipfire_spread_deg=6.5,
            move_speed_mps=4.20,
            ads_move_speed_mps=1.80,
            flinch_resistance=0.65
        ),
        WeaponVersionStats(
            stat_id="signal50_v1.1.0-launch",
            weapon_id="signal50_mw4",
            game_version_id="v1.1.0-launch",
            rpm=120.0,
            base_ads_ms=480.0,
            sprint_to_fire_ms=290.0,
            tactical_sprint_to_fire_ms=400.0,
            bullet_velocity_mps=860.0,
            reload_empty_s=3.40,
            reload_tactical_s=2.60,
            recoil_horizontal=17.5,
            recoil_vertical=63.0,
            hipfire_spread_deg=6.4,
            move_speed_mps=4.22,
            ads_move_speed_mps=1.85,
            flinch_resistance=0.65
        ),

        # Rezi 12
        WeaponVersionStats(
            stat_id="rezi12_v1.0.0-beta",
            weapon_id="rezi12_mw4",
            game_version_id="v1.0.0-beta",
            rpm=280.0,
            base_ads_ms=265.0,
            sprint_to_fire_ms=225.0,
            tactical_sprint_to_fire_ms=310.0,
            bullet_velocity_mps=320.0,
            reload_empty_s=3.15,
            reload_tactical_s=2.45,
            recoil_horizontal=30.0,
            recoil_vertical=45.0,
            hipfire_spread_deg=4.5,
            move_speed_mps=4.60,
            ads_move_speed_mps=2.50,
            flinch_resistance=1.1
        ),
        WeaponVersionStats(
            stat_id="rezi12_v1.1.0-launch",
            weapon_id="rezi12_mw4",
            game_version_id="v1.1.0-launch",
            rpm=280.0,
            base_ads_ms=260.0,
            sprint_to_fire_ms=220.0,
            tactical_sprint_to_fire_ms=305.0,
            bullet_velocity_mps=330.0,
            reload_empty_s=3.10,
            reload_tactical_s=2.40,
            recoil_horizontal=29.0,
            recoil_vertical=44.0,
            hipfire_spread_deg=4.4,
            move_speed_mps=4.62,
            ads_move_speed_mps=2.55,
            flinch_resistance=1.1
        )
    ]
    for vs in version_stats:
        repo.upsert_weapon_stats(vs)

    # 5. Damage Profiles (Core and Hardcore)
    damage_profiles = [
        # XM4 - Launch - Core
        DamageRangeBracket(
            profile_id="xm4_core_p1_v1.1.0",
            weapon_id="xm4_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=28.0,
            damage_head=39.2,
            damage_neck=35.0,
            damage_chest=30.8,
            damage_stomach=28.0,
            damage_limbs=25.2
        ),
        DamageRangeBracket(
            profile_id="xm4_core_p2_v1.1.0",
            weapon_id="xm4_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=28.0,
            range_end_m=42.0,
            damage_head=35.0,
            damage_neck=31.2,
            damage_chest=27.5,
            damage_stomach=25.0,
            damage_limbs=22.5
        ),
        DamageRangeBracket(
            profile_id="xm4_core_p3_v1.1.0",
            weapon_id="xm4_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=42.0,
            range_end_m=100.0,
            damage_head=30.8,
            damage_neck=27.5,
            damage_chest=24.2,
            damage_stomach=22.0,
            damage_limbs=19.8
        ),

        # XM4 - Launch - Hardcore (30 HP)
        DamageRangeBracket(
            profile_id="xm4_hc_p1_v1.1.0",
            weapon_id="xm4_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="hardcore",
            range_start_m=0.0,
            range_end_m=35.0,
            damage_head=38.0,
            damage_neck=35.0,
            damage_chest=32.0, # 1-shot lethal <= 35m
            damage_stomach=30.0,
            damage_limbs=28.0
        ),
        DamageRangeBracket(
            profile_id="xm4_hc_p2_v1.1.0",
            weapon_id="xm4_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="hardcore",
            range_start_m=35.0,
            range_end_m=100.0,
            damage_head=34.0,
            damage_neck=30.0,
            damage_chest=27.0, # 2-shot lethal > 35m
            damage_stomach=25.0,
            damage_limbs=24.0
        ),

        # MCW - Launch - Core
        DamageRangeBracket(
            profile_id="mcw_core_p1_v1.1.0",
            weapon_id="mcw_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=32.0,
            damage_head=37.8,
            damage_neck=33.7,
            damage_chest=29.7,
            damage_stomach=27.0,
            damage_limbs=24.3
        ),
        DamageRangeBracket(
            profile_id="mcw_core_p2_v1.1.0",
            weapon_id="mcw_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=32.0,
            range_end_m=48.0,
            damage_head=33.6,
            damage_neck=30.0,
            damage_chest=26.4,
            damage_stomach=24.0,
            damage_limbs=21.6
        ),
        DamageRangeBracket(
            profile_id="mcw_core_p3_v1.1.0",
            weapon_id="mcw_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=48.0,
            range_end_m=100.0,
            damage_head=29.4,
            damage_neck=26.2,
            damage_chest=23.1,
            damage_stomach=21.0,
            damage_limbs=18.9
        ),

        # Kastov 74-M - Launch - Core (Heavy 3-shot AR)
        DamageRangeBracket(
            profile_id="ak74m_core_p1_v1.1.0",
            weapon_id="ak74m_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=25.0,
            damage_head=48.0,
            damage_neck=42.0,
            damage_chest=35.0, # 3-shot kill in Core (184.6ms TTK)
            damage_stomach=30.0,
            damage_limbs=27.0
        ),
        DamageRangeBracket(
            profile_id="ak74m_core_p2_v1.1.0",
            weapon_id="ak74m_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=25.0,
            range_end_m=45.0,
            damage_head=40.0,
            damage_neck=36.0,
            damage_chest=28.0, # 4-shot kill
            damage_stomach=25.0,
            damage_limbs=22.0
        ),
        DamageRangeBracket(
            profile_id="ak74m_core_p3_v1.1.0",
            weapon_id="ak74m_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=45.0,
            range_end_m=100.0,
            damage_head=32.0,
            damage_neck=28.0,
            damage_chest=23.0,
            damage_stomach=20.0,
            damage_limbs=18.0
        ),

        # AMR-9 - Launch - Core (Fast 4-shot SMG)
        DamageRangeBracket(
            profile_id="amr9_core_p1_v1.1.0",
            weapon_id="amr9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=18.0,
            damage_head=38.0,
            damage_neck=34.0,
            damage_chest=28.0, # 4-shot kill (216.1ms TTK)
            damage_stomach=25.0,
            damage_limbs=22.0
        ),
        DamageRangeBracket(
            profile_id="amr9_core_p2_v1.1.0",
            weapon_id="amr9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=18.0,
            range_end_m=32.0,
            damage_head=32.0,
            damage_neck=28.0,
            damage_chest=24.0, # 5-shot kill
            damage_stomach=21.0,
            damage_limbs=19.0
        ),
        DamageRangeBracket(
            profile_id="amr9_core_p3_v1.1.0",
            weapon_id="amr9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=32.0,
            range_end_m=100.0,
            damage_head=26.0,
            damage_neck=22.0,
            damage_chest=18.0,
            damage_stomach=16.0,
            damage_limbs=14.0
        ),

        # Striker 45 - Launch - Core (.45 ACP 3-shot CQB)
        DamageRangeBracket(
            profile_id="striker45_core_p1_v1.1.0",
            weapon_id="striker45_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=16.0,
            damage_head=45.0,
            damage_neck=38.0,
            damage_chest=34.0, # 3-shot kill (186.0ms TTK)
            damage_stomach=28.0,
            damage_limbs=25.0
        ),
        DamageRangeBracket(
            profile_id="striker45_core_p2_v1.1.0",
            weapon_id="striker45_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=16.0,
            range_end_m=30.0,
            damage_head=36.0,
            damage_neck=30.0,
            damage_chest=26.0, # 4-shot kill
            damage_stomach=22.0,
            damage_limbs=20.0
        ),
        DamageRangeBracket(
            profile_id="striker45_core_p3_v1.1.0",
            weapon_id="striker45_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=30.0,
            range_end_m=100.0,
            damage_head=28.0,
            damage_neck=24.0,
            damage_chest=20.0,
            damage_stomach=18.0,
            damage_limbs=16.0
        ),

        # Rival-9 - Launch - Core
        DamageRangeBracket(
            profile_id="rival9_core_p1_v1.1.0",
            weapon_id="rival9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=12.5,
            damage_head=35.0,
            damage_neck=31.2,
            damage_chest=28.0,
            damage_stomach=26.0,
            damage_limbs=23.4
        ),
        DamageRangeBracket(
            profile_id="rival9_core_p2_v1.1.0",
            weapon_id="rival9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=12.5,
            range_end_m=22.0,
            damage_head=29.4,
            damage_neck=26.2,
            damage_chest=23.5,
            damage_stomach=21.8,
            damage_limbs=19.6
        ),
        DamageRangeBracket(
            profile_id="rival9_core_p3_v1.1.0",
            weapon_id="rival9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=22.0,
            range_end_m=100.0,
            damage_head=22.4,
            damage_neck=20.0,
            damage_chest=17.9,
            damage_stomach=16.6,
            damage_limbs=15.0
        ),

        # Rival-9 - Launch - Hardcore (30 HP)
        DamageRangeBracket(
            profile_id="rival9_hc_p1_v1.1.0",
            weapon_id="rival9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="hardcore",
            range_start_m=0.0,
            range_end_m=14.0,
            damage_head=35.0,
            damage_neck=32.0,
            damage_chest=30.5, # 1-shot lethal in close range
            damage_stomach=28.0,
            damage_limbs=26.0
        ),
        DamageRangeBracket(
            profile_id="rival9_hc_p2_v1.1.0",
            weapon_id="rival9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="hardcore",
            range_start_m=14.0,
            range_end_m=100.0,
            damage_head=28.0,
            damage_neck=25.0,
            damage_chest=22.0,
            damage_stomach=20.0,
            damage_limbs=18.0
        ),

        # BAS-B - Launch - Core
        DamageRangeBracket(
            profile_id="basb_core_p1_v1.1.0",
            weapon_id="basb_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=35.0,
            damage_head=54.6,
            damage_neck=48.7,
            damage_chest=42.9, # 3-shot kill in core!
            damage_stomach=39.0,
            damage_limbs=35.1
        ),
        DamageRangeBracket(
            profile_id="basb_core_p2_v1.1.0",
            weapon_id="basb_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=35.0,
            range_end_m=100.0,
            damage_head=46.2,
            damage_neck=41.2,
            damage_chest=36.3,
            damage_stomach=33.0,
            damage_limbs=29.7
        ),

        # KVD Enforcer - Launch - Core (DMR 2-shot)
        DamageRangeBracket(
            profile_id="kvd_core_p1_v1.1.0",
            weapon_id="kvd_enforcer_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=45.0,
            damage_head=98.0,
            damage_neck=87.5,
            damage_chest=68.0, # 2-shot kill
            damage_stomach=60.0,
            damage_limbs=52.0
        ),
        DamageRangeBracket(
            profile_id="kvd_core_p2_v1.1.0",
            weapon_id="kvd_enforcer_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=45.0,
            range_end_m=100.0,
            damage_head=84.0,
            damage_neck=75.0,
            damage_chest=58.0,
            damage_stomach=50.0,
            damage_limbs=44.0
        ),

        # Longbow - Launch - Core (Sniper 1-shot upper torso)
        DamageRangeBracket(
            profile_id="longbow_core_p1_v1.1.0",
            weapon_id="longbow_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=30.0,
            damage_head=240.0,
            damage_neck=180.0,
            damage_chest=120.0, # 1-shot kill upper torso <= 30m
            damage_stomach=95.0,
            damage_limbs=80.0
        ),
        DamageRangeBracket(
            profile_id="longbow_core_p2_v1.1.0",
            weapon_id="longbow_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=30.0,
            range_end_m=100.0,
            damage_head=210.0,
            damage_neck=150.0,
            damage_chest=95.0, # 2-shot kill to chest > 30m
            damage_stomach=80.0,
            damage_limbs=70.0
        ),

        # Holger 556 - Core (4-shot kill)
        DamageRangeBracket(
            profile_id="holger556_core_p1_v1.1.0",
            weapon_id="holger556_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=36.0,
            damage_head=42.0,
            damage_neck=36.0,
            damage_chest=29.0,
            damage_stomach=26.0,
            damage_limbs=24.0
        ),
        DamageRangeBracket(
            profile_id="holger556_core_p2_v1.1.0",
            weapon_id="holger556_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=36.0,
            range_end_m=100.0,
            damage_head=35.0,
            damage_neck=30.0,
            damage_chest=24.0,
            damage_stomach=22.0,
            damage_limbs=20.0
        ),

        # WSP Swarm - Core (Fast CQB 5-shot)
        DamageRangeBracket(
            profile_id="wsp_core_p1_v1.1.0",
            weapon_id="wsp_swarm_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=12.0,
            damage_head=32.0,
            damage_neck=28.0,
            damage_chest=22.0,
            damage_stomach=20.0,
            damage_limbs=18.0
        ),
        DamageRangeBracket(
            profile_id="wsp_core_p2_v1.1.0",
            weapon_id="wsp_swarm_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=12.0,
            range_end_m=100.0,
            damage_head=24.0,
            damage_neck=20.0,
            damage_chest=16.0,
            damage_stomach=14.0,
            damage_limbs=13.0
        ),

        # Sidewinder - Core (Heavy 3-shot Battle Rifle)
        DamageRangeBracket(
            profile_id="sidewinder_core_p1_v1.1.0",
            weapon_id="sidewinder_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=40.0,
            damage_head=60.0,
            damage_neck=54.0,
            damage_chest=46.0,
            damage_stomach=40.0,
            damage_limbs=36.0
        ),
        DamageRangeBracket(
            profile_id="sidewinder_core_p2_v1.1.0",
            weapon_id="sidewinder_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=40.0,
            range_end_m=100.0,
            damage_head=50.0,
            damage_neck=45.0,
            damage_chest=38.0,
            damage_stomach=34.0,
            damage_limbs=30.0
        ),

        # Bruen Mk9 - Core (4-shot sustained LMG)
        DamageRangeBracket(
            profile_id="bruen_core_p1_v1.1.0",
            weapon_id="bruen_mk9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=42.0,
            damage_head=40.0,
            damage_neck=35.0,
            damage_chest=28.0,
            damage_stomach=25.0,
            damage_limbs=23.0
        ),
        DamageRangeBracket(
            profile_id="bruen_core_p2_v1.1.0",
            weapon_id="bruen_mk9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=42.0,
            range_end_m=100.0,
            damage_head=33.0,
            damage_neck=29.0,
            damage_chest=23.0,
            damage_stomach=21.0,
            damage_limbs=19.0
        ),

        # KATT-AMR .50 - Core (1-shot lethal all ranges)
        DamageRangeBracket(
            profile_id="katt_core_p1_v1.1.0",
            weapon_id="katt_amr_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=100.0,
            damage_head=350.0,
            damage_neck=280.0,
            damage_chest=160.0, # Guaranteed 1-shot upper body
            damage_stomach=140.0,
            damage_limbs=105.0
        ),

        # COR-45 - Core (3-shot close pistol)
        DamageRangeBracket(
            profile_id="cor45_core_p1_v1.1.0",
            weapon_id="cor45_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=10.0,
            damage_head=52.0,
            damage_neck=44.0,
            damage_chest=35.0,
            damage_stomach=30.0,
            damage_limbs=26.0
        ),
        DamageRangeBracket(
            profile_id="cor45_core_p2_v1.1.0",
            weapon_id="cor45_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=10.0,
            range_end_m=100.0,
            damage_head=36.0,
            damage_neck=30.0,
            damage_chest=24.0,
            damage_stomach=20.0,
            damage_limbs=18.0
        ),

        # Lockwood 680 - Core (1-shot lethal pump shotgun)
        DamageRangeBracket(
            profile_id="lockwood_core_p1_v1.1.0",
            weapon_id="lockwood680_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=10.0,
            damage_head=220.0,
            damage_neck=180.0,
            damage_chest=150.0, # 1-shot lethal point blank
            damage_stomach=130.0,
            damage_limbs=105.0
        ),
        DamageRangeBracket(
            profile_id="lockwood_core_p2_v1.1.0",
            weapon_id="lockwood680_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=10.0,
            range_end_m=18.0,
            damage_head=110.0,
            damage_neck=90.0,
            damage_chest=75.0, # 2-shot kill
            damage_stomach=65.0,
            damage_limbs=50.0
        ),
        DamageRangeBracket(
            profile_id="lockwood_core_p3_v1.1.0",
            weapon_id="lockwood680_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=18.0,
            range_end_m=100.0,
            damage_head=55.0,
            damage_neck=45.0,
            damage_chest=35.0,
            damage_stomach=30.0,
            damage_limbs=25.0
        ),

        # Pulemyot 762 - Core (Heavy 3-shot LMG)
        DamageRangeBracket(
            profile_id="pulemyot_core_p1_v1.1.0",
            weapon_id="pulemyot762_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=38.0,
            damage_head=52.0,
            damage_neck=46.0,
            damage_chest=38.0, # 3-shot kill
            damage_stomach=34.0,
            damage_limbs=30.0
        ),
        DamageRangeBracket(
            profile_id="pulemyot_core_p2_v1.1.0",
            weapon_id="pulemyot762_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=38.0,
            range_end_m=100.0,
            damage_head=42.0,
            damage_neck=38.0,
            damage_chest=31.0, # 4-shot kill
            damage_stomach=28.0,
            damage_limbs=25.0
        ),

        # Renetti - Core (3-round burst pistol)
        DamageRangeBracket(
            profile_id="renetti_core_p1_v1.1.0",
            weapon_id="renetti_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=0.0,
            range_end_m=12.0,
            damage_head=48.0,
            damage_neck=40.0,
            damage_chest=34.0, # 1 burst kill in close range!
            damage_stomach=28.0,
            damage_limbs=24.0
        ),
        DamageRangeBracket(
            profile_id="renetti_core_p2_v1.1.0",
            weapon_id="renetti_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            range_start_m=12.0,
            range_end_m=100.0,
            damage_head=32.0,
            damage_neck=26.0,
            damage_chest=22.0,
            damage_stomach=18.0,
            damage_limbs=16.0
        ),

        # Han 86 - Core
        DamageRangeBracket(profile_id="han86_core_p1_v1.1.0", weapon_id="han86_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=0.0, range_end_m=30.0, damage_head=40.0, damage_neck=35.0, damage_chest=31.0, damage_stomach=28.0, damage_limbs=25.0),
        DamageRangeBracket(profile_id="han86_core_p2_v1.1.0", weapon_id="han86_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=30.0, range_end_m=48.0, damage_head=34.0, damage_neck=30.0, damage_chest=26.0, damage_stomach=24.0, damage_limbs=22.0),
        DamageRangeBracket(profile_id="han86_core_p3_v1.1.0", weapon_id="han86_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=48.0, range_end_m=100.0, damage_head=28.0, damage_neck=25.0, damage_chest=22.0, damage_stomach=20.0, damage_limbs=18.0),

        # Hyeon Burst - Core
        DamageRangeBracket(profile_id="hyeon_core_p1_v1.1.0", weapon_id="hyeon_burst_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=0.0, range_end_m=32.0, damage_head=48.0, damage_neck=42.0, damage_chest=36.0, damage_stomach=30.0, damage_limbs=26.0),
        DamageRangeBracket(profile_id="hyeon_core_p2_v1.1.0", weapon_id="hyeon_burst_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=32.0, range_end_m=50.0, damage_head=38.0, damage_neck=34.0, damage_chest=28.0, damage_stomach=25.0, damage_limbs=22.0),
        DamageRangeBracket(profile_id="hyeon_core_p3_v1.1.0", weapon_id="hyeon_burst_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=50.0, range_end_m=100.0, damage_head=30.0, damage_neck=26.0, damage_chest=22.0, damage_stomach=19.0, damage_limbs=16.0),

        # ISO Nightshade - Core
        DamageRangeBracket(profile_id="iso_core_p1_v1.1.0", weapon_id="iso_nightshade_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=0.0, range_end_m=14.0, damage_head=35.0, damage_neck=30.0, damage_chest=26.0, damage_stomach=23.0, damage_limbs=20.0),
        DamageRangeBracket(profile_id="iso_core_p2_v1.1.0", weapon_id="iso_nightshade_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=14.0, range_end_m=25.0, damage_head=28.0, damage_neck=25.0, damage_chest=21.0, damage_stomach=19.0, damage_limbs=17.0),
        DamageRangeBracket(profile_id="iso_core_p3_v1.1.0", weapon_id="iso_nightshade_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=25.0, range_end_m=100.0, damage_head=22.0, damage_neck=19.0, damage_chest=16.0, damage_stomach=14.0, damage_limbs=12.0),

        # PPSh-41 - Core
        DamageRangeBracket(profile_id="ppsh_core_p1_v1.1.0", weapon_id="ppsh41_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=0.0, range_end_m=12.0, damage_head=32.0, damage_neck=28.0, damage_chest=23.0, damage_stomach=20.0, damage_limbs=18.0),
        DamageRangeBracket(profile_id="ppsh_core_p2_v1.1.0", weapon_id="ppsh41_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=12.0, range_end_m=22.0, damage_head=26.0, damage_neck=22.0, damage_chest=18.0, damage_stomach=16.0, damage_limbs=14.0),
        DamageRangeBracket(profile_id="ppsh_core_p3_v1.1.0", weapon_id="ppsh41_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=22.0, range_end_m=100.0, damage_head=20.0, damage_neck=17.0, damage_chest=14.0, damage_stomach=12.0, damage_limbs=10.0),

        # Signal .50 - Core
        DamageRangeBracket(profile_id="signal_core_p1_v1.1.0", weapon_id="signal50_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=0.0, range_end_m=60.0, damage_head=220.0, damage_neck=170.0, damage_chest=145.0, damage_stomach=110.0, damage_limbs=85.0),
        DamageRangeBracket(profile_id="signal_core_p2_v1.1.0", weapon_id="signal50_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=60.0, range_end_m=100.0, damage_head=180.0, damage_neck=140.0, damage_chest=115.0, damage_stomach=95.0, damage_limbs=75.0),

        # Rezi 12 - Core
        DamageRangeBracket(profile_id="rezi_core_p1_v1.1.0", weapon_id="rezi12_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=0.0, range_end_m=8.0, damage_head=140.0, damage_neck=115.0, damage_chest=95.0, damage_stomach=80.0, damage_limbs=60.0),
        DamageRangeBracket(profile_id="rezi_core_p2_v1.1.0", weapon_id="rezi12_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=8.0, range_end_m=15.0, damage_head=75.0, damage_neck=60.0, damage_chest=50.0, damage_stomach=42.0, damage_limbs=30.0),
        DamageRangeBracket(profile_id="rezi_core_p3_v1.1.0", weapon_id="rezi12_mw4", game_version_id="v1.1.0-launch", ruleset_id="core", range_start_m=15.0, range_end_m=100.0, damage_head=35.0, damage_neck=28.0, damage_chest=22.0, damage_stomach=18.0, damage_limbs=14.0)
    ]
    for dp in damage_profiles:
        repo.upsert_damage_profile(dp)

    # 6. Comprehensive Attachments Catalog across all 9 slots (56 attachments)
    attachments = [
        # Muzzles (8)
        Attachment(attachment_id="muzzle_shadowstrike_suppressor", name="Shadowstrike Suppressor", slot=AttachmentSlot.MUZZLE, is_universal=True, unlock_level=2, description="Undetectable on radar with zero ADS or range penalties."),
        Attachment(attachment_id="muzzle_vt7_spiritfire", name="VT-7 Spiritfire Suppressor", slot=AttachmentSlot.MUZZLE, is_universal=True, unlock_level=14, description="Heavy suppressor providing recoil control, bullet velocity, and range extension."),
        Attachment(attachment_id="muzzle_casus_brake", name="Casus Brake Compensator", slot=AttachmentSlot.MUZZLE, is_universal=True, unlock_level=8, description="Horizontal recoil mitigation brake for pinpoint spray control."),
        Attachment(attachment_id="muzzle_ported_comp", name="Ported Tactical Compensator", slot=AttachmentSlot.MUZZLE, is_universal=True, unlock_level=5, description="Vertical recoil mitigation compensator for tight upward grouping."),
        Attachment(attachment_id="muzzle_l4r_flash", name="L4R Flash Hider", slot=AttachmentSlot.MUZZLE, is_universal=True, unlock_level=3, description="Conceals muzzle flash with slight recoil kick reduction."),
        Attachment(attachment_id="muzzle_colossus_heavy", name="Colossus Heavy Silencer", slot=AttachmentSlot.MUZZLE, is_universal=True, unlock_level=17, description="Ultra-heavy sound suppressor maximizing muzzle velocity and bullet reach."),
        Attachment(attachment_id="muzzle_crown50_brake", name="Crown-50 Muzzle Brake", slot=AttachmentSlot.MUZZLE, is_universal=True, unlock_level=11, description="Aggressive gas redirector eliminating first-shot vertical climb."),
        Attachment(attachment_id="muzzle_purifier_brake", name="Purifier Horizontal Brake", slot=AttachmentSlot.MUZZLE, is_universal=True, unlock_level=19, description="Side-venting brake eliminating horizontal weapon sway during full-auto fire."),

        # Barrels (7)
        Attachment(attachment_id="barrel_cyclone_long", name="Cyclone Heavy Long Barrel", slot=AttachmentSlot.BARREL, is_universal=True, unlock_level=12, description="Extended match-grade barrel for maximum damage range and velocity."),
        Attachment(attachment_id="barrel_phantom_short", name="Phantom CQB Short Barrel", slot=AttachmentSlot.BARREL, is_universal=True, unlock_level=6, description="Ultra-light short barrel maximizing ADS and sprint speed."),
        Attachment(attachment_id="barrel_reinforced_match", name="Reinforced Match Barrel", slot=AttachmentSlot.BARREL, is_universal=True, unlock_level=16, description="Precision rifled barrel boosting damage range with minimal weight penalty."),
        Attachment(attachment_id="barrel_ultralight_fluted", name="Ultralight Fluted Barrel", slot=AttachmentSlot.BARREL, is_universal=True, unlock_level=9, description="Fluted steel barrel engineered for fast weapon maneuvering and strafe speed."),
        Attachment(attachment_id="barrel_chf_heavy", name="CHF Heavy Cold-Forged Barrel", slot=AttachmentSlot.BARREL, is_universal=True, unlock_level=20, description="Cold hammer-forged heavy barrel designed for maximum ballistic stability."),
        Attachment(attachment_id="barrel_suppressed_integral", name="Triton Integrally Suppressed Barrel", slot=AttachmentSlot.BARREL, is_universal=True, unlock_level=18, description="Integrated suppressor barrel combining sound suppression with zero muzzle attachment requirement."),
        Attachment(attachment_id="barrel_short_carbine", name="Short Carbine Speed Barrel", slot=AttachmentSlot.BARREL, is_universal=True, unlock_level=4, description="Compact carbine barrel prioritizing fast ADS transition in close-quarters."),

        # Lasers (6)
        Attachment(attachment_id="laser_ftac_grimline", name="FTAC Grimline Tac Laser", slot=AttachmentSlot.LASER, is_universal=True, unlock_level=5, description="High-output visible laser dramatically boosting sprint-to-fire speed."),
        Attachment(attachment_id="laser_corio_laz44", name="Corio LAZ-44 Precision Laser", slot=AttachmentSlot.LASER, is_universal=True, unlock_level=10, description="Non-visible laser improving aiming idle stability and ADS speed."),
        Attachment(attachment_id="laser_schlager_peq", name="Schlager PEQ Box IV", slot=AttachmentSlot.LASER, is_universal=True, unlock_level=8, description="Tactical targeting module providing smooth target acquisition with no visible beam."),
        Attachment(attachment_id="laser_fss_olev", name="FSS OLE-V Laser", slot=AttachmentSlot.LASER, is_universal=True, unlock_level=14, description="High-performance tri-beam laser for lightning-fast snap aiming."),
        Attachment(attachment_id="laser_point_g3p", name="Point-G3P 1mW Tactical Laser", slot=AttachmentSlot.LASER, is_universal=True, unlock_level=3, description="Underbarrel 1mW laser tightening hipfire spread pattern."),
        Attachment(attachment_id="laser_dxs_flash", name="DXS Flash 90 Tac-Stance Laser", slot=AttachmentSlot.LASER, is_universal=True, unlock_level=11, description="Specialized canted tactical stance laser module."),

        # Optics (8)
        Attachment(attachment_id="optic_slate_reflector", name="Slate Reflector", slot=AttachmentSlot.OPTIC, is_universal=True, unlock_level=3, description="Clean 1.25x unmagnified glass with minimal visual obstruction."),
        Attachment(attachment_id="optic_mk3_reflector", name="Mk.3 Reflector", slot=AttachmentSlot.OPTIC, is_universal=True, unlock_level=2, description="Ultra-thin bezel reflex sight providing an unobstructed target picture."),
        Attachment(attachment_id="optic_corio_eagleseye", name="Corio Eagleseye 2.5x Scope", slot=AttachmentSlot.OPTIC, is_universal=True, unlock_level=16, description="Mid-range precision optic with crystal-clear reticle and negligible ADS penalty."),
        Attachment(attachment_id="optic_cronen_mini", name="Cronen Mini Pro (Blue Dot)", slot=AttachmentSlot.OPTIC, is_universal=True, unlock_level=7, description="Compact micro reflex optic with vibrant blue-dot reticle."),
        Attachment(attachment_id="optic_sz_sro7", name="SZ SRO-7 Holographic", slot=AttachmentSlot.OPTIC, is_universal=True, unlock_level=11, description="Wide-window holographic sight for rapid target acquisition."),
        Attachment(attachment_id="optic_acog_4x", name="ACOG 4.0x Tactical Scope", slot=AttachmentSlot.OPTIC, is_universal=True, unlock_level=19, description="4.0x combat optic ideal for locking down long power sightlines."),
        Attachment(attachment_id="optic_thermo_x9", name="Thermo-Optic x9 Thermal", slot=AttachmentSlot.OPTIC, is_universal=True, unlock_level=21, description="Thermal imaging scope highlighting enemy heat signatures through smoke."),
        Attachment(attachment_id="optic_iron_elite", name="Elite Match Iron Sights", slot=AttachmentSlot.OPTIC, is_universal=True, unlock_level=1, description="Precision-machined open iron sights providing a 10ms ADS speed advantage."),

        # Stocks (6)
        Attachment(attachment_id="stock_skeletonized_cqb", name="Skeletonized CQB Stock", slot=AttachmentSlot.STOCK, is_universal=True, unlock_level=9, description="Lightweight frame stock boosting aim walking speed and sprint-to-fire."),
        Attachment(attachment_id="stock_heavy_precision", name="Heavy Precision Buffer Stock", slot=AttachmentSlot.STOCK, is_universal=True, unlock_level=18, description="Weighted stock that eliminates idle sway and minimizes vertical recoil kick."),
        Attachment(attachment_id="stock_no_stock_mod", name="No Stock Mod", slot=AttachmentSlot.STOCK, is_universal=True, unlock_level=15, description="Removes rear stock for extreme CQB sprint speed and lightning ADS."),
        Attachment(attachment_id="stock_heavy_tac", name="Heavy Tactical Anchor Stock", slot=AttachmentSlot.STOCK, is_universal=True, unlock_level=12, description="Reinforced polymer stock maximizing weapon stability during sustained fire."),
        Attachment(attachment_id="stock_commando_light", name="Commando Lightweight Stock", slot=AttachmentSlot.STOCK, is_universal=True, unlock_level=4, description="Sleek tactical stock improving strafe agility."),
        Attachment(attachment_id="stock_buffer_tube", name="Buffer Tube Ultralight Stock", slot=AttachmentSlot.STOCK, is_universal=True, unlock_level=7, description="Minimalist buffer tube reducing weapon weight for faster target snap."),

        # Underbarrels (7)
        Attachment(attachment_id="underbarrel_dr6_handstop", name="DR-6 Handstop", slot=AttachmentSlot.UNDERBARREL, is_universal=True, unlock_level=7, description="Ergonomic handstop boosting ADS speed, sprint-to-fire, and aim walking speed."),
        Attachment(attachment_id="underbarrel_bruen_heavy_grip", name="Bruen Heavy Support Grip", slot=AttachmentSlot.UNDERBARREL, is_universal=True, unlock_level=15, description="Heavy angled grip providing elite horizontal recoil stabilization."),
        Attachment(attachment_id="underbarrel_ftac_ripper", name="FTAC Ripper 56 Stabilizer", slot=AttachmentSlot.UNDERBARREL, is_universal=True, unlock_level=10, description="Heavy stabilizing foregrip eliminating idle sway and gun kick."),
        Attachment(attachment_id="underbarrel_xten_phantom5", name="XTEN Phantom-5 Handstop", slot=AttachmentSlot.UNDERBARREL, is_universal=True, unlock_level=6, description="Hybrid handstop improving sprint-to-fire speed and vertical control."),
        Attachment(attachment_id="underbarrel_merc_foregrip", name="Merc Foregrip", slot=AttachmentSlot.UNDERBARREL, is_universal=True, unlock_level=4, description="Vertical foregrip tightening hipfire spread while taming vertical recoil."),
        Attachment(attachment_id="underbarrel_operator_grip", name="Operator Vertical Foregrip", slot=AttachmentSlot.UNDERBARREL, is_universal=True, unlock_level=13, description="Tactical vertical grip dedicated strictly to vertical recoil reduction."),
        Attachment(attachment_id="underbarrel_chemerov_angled", name="Chemerov Heavy Angled Grip", slot=AttachmentSlot.UNDERBARREL, is_universal=True, unlock_level=17, description="Heavy ergonomic wedge grip providing rock-solid aiming stability."),

        # Magazines (5)
        Attachment(attachment_id="mag_40_round", name="40-Round Extended Magazine", slot=AttachmentSlot.MAGAZINE, is_universal=True, unlock_level=4, description="High-capacity magazine for sustained multi-target gunfights."),
        Attachment(attachment_id="mag_50_round_drum", name="50-Round Heavy Drum", slot=AttachmentSlot.MAGAZINE, is_universal=True, unlock_level=14, description="Heavy drum magazine with extended capacity for quad-wipe potential."),
        Attachment(attachment_id="mag_60_round_drum", name="60-Round Super Drum", slot=AttachmentSlot.MAGAZINE, is_universal=True, unlock_level=22, description="Maximum ammo reserve at the cost of handling and mobility."),
        Attachment(attachment_id="mag_20_fast_mag", name="20-Round Fast Speed Mag", slot=AttachmentSlot.MAGAZINE, is_universal=True, unlock_level=8, description="Lightweight speed magazine offering lightning-fast reload and faster ADS."),
        Attachment(attachment_id="mag_100_round_belt", name="100-Round Ammo Belt Box", slot=AttachmentSlot.MAGAZINE, is_universal=True, unlock_level=24, description="Heavy squad support ammo box for continuous suppression fire."),

        # Ammunition (8)
        Attachment(attachment_id="ammo_high_grain", name="High Grain Match Ammunition", slot=AttachmentSlot.AMMUNITION, is_universal=True, unlock_level=11, description="Overpressured match rounds extending damage range and muzzle velocity."),
        Attachment(attachment_id="ammo_overpressured", name="Overpressured +P Match Ammo", slot=AttachmentSlot.AMMUNITION, is_universal=True, unlock_level=7, description="High kinetic energy rounds that inflict severe flinch on enemy targets."),
        Attachment(attachment_id="ammo_armor_piercing", name="Armor Piercing Tungsten Rounds", slot=AttachmentSlot.AMMUNITION, is_universal=True, unlock_level=13, description="Hardened core rounds maximizing bullet penetration through walls and cover."),
        Attachment(attachment_id="ammo_subsonic_low", name="Low Grain Subsonic Rounds", slot=AttachmentSlot.AMMUNITION, is_universal=True, unlock_level=5, description="Subsonic velocity rounds that hide enemy death markers with quiet acoustic signature."),
        Attachment(attachment_id="ammo_hollow_point", name="Hollow Point Frangible Ammo", slot=AttachmentSlot.AMMUNITION, is_universal=True, unlock_level=9, description="Expanding bullets that temporarily disable enemy tactical sprint upon leg hits."),
        Attachment(attachment_id="ammo_dragons_breath", name="Dragon's Breath Incendiary Rounds", slot=AttachmentSlot.AMMUNITION, is_universal=True, unlock_level=18, description="Magnesium incendiary ammunition inflicting residual burning damage over time."),
        Attachment(attachment_id="ammo_explosive_slug", name="Explosive Heavy Slug Rounds", slot=AttachmentSlot.AMMUNITION, is_universal=True, unlock_level=21, description="High-explosive payload slugs delivering massive kinetic concussive blast on impact."),
        Attachment(attachment_id="ammo_frangible_disabling", name="Frangible Disabling Rounds", slot=AttachmentSlot.AMMUNITION, is_universal=True, unlock_level=15, description="Shattering lead-composite rounds that suppress target healing and sprint recovery."),

        # Rear Grips (4)
        Attachment(attachment_id="grip_phantom_tac", name="Phantom Tactical Grip", slot=AttachmentSlot.REAR_GRIP, is_universal=True, unlock_level=6, description="Stippled rubber grip delivering faster ADS transition."),
        Attachment(attachment_id="grip_heavy_ergo", name="Heavy Ergonomic Tac Grip", slot=AttachmentSlot.REAR_GRIP, is_universal=True, unlock_level=14, description="Rubberized combat grip reducing recoil vibration and flinch."),
        Attachment(attachment_id="grip_stippled_rubber", name="Stippled Rubberized Grip", slot=AttachmentSlot.REAR_GRIP, is_universal=True, unlock_level=10, description="Textured grip enhancing sprint-to-fire speed."),
        Attachment(attachment_id="grip_granulated_match", name="Granulated Match Grip", slot=AttachmentSlot.REAR_GRIP, is_universal=True, unlock_level=3, description="High-friction grip improving aiming idle stability.")
    ]
    for a in attachments:
        repo.upsert_attachment(a)

    # 7. Comprehensive Versioned Attachment Modifiers across Beta & Launch
    modifiers = [
        # VT-7 Spiritfire Suppressor
        AttachmentModifier(mod_id="mod_vt7_ads", attachment_id="muzzle_vt7_spiritfire", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=12.0),
        AttachmentModifier(mod_id="mod_vt7_vel", attachment_id="muzzle_vt7_spiritfire", game_version_id="v1.1.0-launch", stat_key="bullet_velocity_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.08),
        AttachmentModifier(mod_id="mod_vt7_range", attachment_id="muzzle_vt7_spiritfire", game_version_id="v1.1.0-launch", stat_key="range_multiplier", mod_type=ModifierType.PERCENTAGE, mod_value=0.07),
        AttachmentModifier(mod_id="mod_vt7_recoil", attachment_id="muzzle_vt7_spiritfire", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.05),

        # Casus Brake
        AttachmentModifier(mod_id="mod_casus_recoil_h", attachment_id="muzzle_casus_brake", game_version_id="v1.1.0-launch", stat_key="recoil_horizontal", mod_type=ModifierType.PERCENTAGE, mod_value=-0.16),
        AttachmentModifier(mod_id="mod_casus_ads", attachment_id="muzzle_casus_brake", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=6.0),

        # Ported Compensator
        AttachmentModifier(mod_id="mod_ported_recoil_v", attachment_id="muzzle_ported_comp", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.18),
        AttachmentModifier(mod_id="mod_ported_ads", attachment_id="muzzle_ported_comp", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=8.0),

        # Crown-50 Brake
        AttachmentModifier(mod_id="mod_crown_recoil_v", attachment_id="muzzle_crown50_brake", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.22),
        AttachmentModifier(mod_id="mod_crown_ads", attachment_id="muzzle_crown50_brake", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=10.0),

        # Purifier Brake
        AttachmentModifier(mod_id="mod_purifier_recoil_h", attachment_id="muzzle_purifier_brake", game_version_id="v1.1.0-launch", stat_key="recoil_horizontal", mod_type=ModifierType.PERCENTAGE, mod_value=-0.20),
        AttachmentModifier(mod_id="mod_purifier_ads", attachment_id="muzzle_purifier_brake", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=8.0),

        # Colossus Silencer
        AttachmentModifier(mod_id="mod_colossus_vel", attachment_id="muzzle_colossus_heavy", game_version_id="v1.1.0-launch", stat_key="bullet_velocity_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.14),
        AttachmentModifier(mod_id="mod_colossus_range", attachment_id="muzzle_colossus_heavy", game_version_id="v1.1.0-launch", stat_key="range_multiplier", mod_type=ModifierType.PERCENTAGE, mod_value=0.10),
        AttachmentModifier(mod_id="mod_colossus_ads", attachment_id="muzzle_colossus_heavy", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=16.0),

        # Cyclone Long Barrel
        AttachmentModifier(mod_id="mod_cyclone_range", attachment_id="barrel_cyclone_long", game_version_id="v1.1.0-launch", stat_key="range_multiplier", mod_type=ModifierType.PERCENTAGE, mod_value=0.18),
        AttachmentModifier(mod_id="mod_cyclone_vel", attachment_id="barrel_cyclone_long", game_version_id="v1.1.0-launch", stat_key="bullet_velocity_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.15),
        AttachmentModifier(mod_id="mod_cyclone_ads", attachment_id="barrel_cyclone_long", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=22.0),
        AttachmentModifier(mod_id="mod_cyclone_move", attachment_id="barrel_cyclone_long", game_version_id="v1.1.0-launch", stat_key="move_speed_mps", mod_type=ModifierType.PERCENTAGE, mod_value=-0.03),

        # Phantom Short Barrel
        AttachmentModifier(mod_id="mod_phantom_ads", attachment_id="barrel_phantom_short", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-18.0),
        AttachmentModifier(mod_id="mod_phantom_stf", attachment_id="barrel_phantom_short", game_version_id="v1.1.0-launch", stat_key="sprint_to_fire_ms", mod_type=ModifierType.DELTA, mod_value=-15.0),
        AttachmentModifier(mod_id="mod_phantom_range", attachment_id="barrel_phantom_short", game_version_id="v1.1.0-launch", stat_key="range_multiplier", mod_type=ModifierType.PERCENTAGE, mod_value=-0.12),

        # Reinforced Match Barrel
        AttachmentModifier(mod_id="mod_reinf_range", attachment_id="barrel_reinforced_match", game_version_id="v1.1.0-launch", stat_key="range_multiplier", mod_type=ModifierType.PERCENTAGE, mod_value=0.12),
        AttachmentModifier(mod_id="mod_reinf_vel", attachment_id="barrel_reinforced_match", game_version_id="v1.1.0-launch", stat_key="bullet_velocity_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.10),
        AttachmentModifier(mod_id="mod_reinf_ads", attachment_id="barrel_reinforced_match", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=12.0),

        # Ultralight Fluted Barrel
        AttachmentModifier(mod_id="mod_fluted_ads", attachment_id="barrel_ultralight_fluted", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-14.0),
        AttachmentModifier(mod_id="mod_fluted_strafe", attachment_id="barrel_ultralight_fluted", game_version_id="v1.1.0-launch", stat_key="ads_move_speed_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.08),

        # CHF Heavy Barrel
        AttachmentModifier(mod_id="mod_chf_recoil", attachment_id="barrel_chf_heavy", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.15),
        AttachmentModifier(mod_id="mod_chf_vel", attachment_id="barrel_chf_heavy", game_version_id="v1.1.0-launch", stat_key="bullet_velocity_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.18),
        AttachmentModifier(mod_id="mod_chf_ads", attachment_id="barrel_chf_heavy", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=25.0),

        # FTAC Grimline Laser
        AttachmentModifier(mod_id="mod_ftac_stf", attachment_id="laser_ftac_grimline", game_version_id="v1.1.0-launch", stat_key="sprint_to_fire_ms", mod_type=ModifierType.DELTA, mod_value=-22.0),
        AttachmentModifier(mod_id="mod_ftac_ads", attachment_id="laser_ftac_grimline", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-10.0),

        # Corio LAZ-44 Laser
        AttachmentModifier(mod_id="mod_laz44_ads", attachment_id="laser_corio_laz44", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-14.0),

        # FSS OLE-V Laser
        AttachmentModifier(mod_id="mod_olev_ads", attachment_id="laser_fss_olev", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-20.0),
        AttachmentModifier(mod_id="mod_olev_stf", attachment_id="laser_fss_olev", game_version_id="v1.1.0-launch", stat_key="sprint_to_fire_ms", mod_type=ModifierType.DELTA, mod_value=-16.0),

        # Point-G3P Laser
        AttachmentModifier(mod_id="mod_g3p_hip", attachment_id="laser_point_g3p", game_version_id="v1.1.0-launch", stat_key="hipfire_spread_deg", mod_type=ModifierType.PERCENTAGE, mod_value=-0.22),

        # Elite Iron Sights
        AttachmentModifier(mod_id="mod_iron_ads", attachment_id="optic_iron_elite", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-10.0),

        # Slate & Mk.3 Reflector
        AttachmentModifier(mod_id="mod_mk3_ads", attachment_id="optic_mk3_reflector", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=0.0),

        # Corio Eagleseye 2.5x
        AttachmentModifier(mod_id="mod_eagleseye_ads", attachment_id="optic_corio_eagleseye", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=15.0),

        # Skeletonized CQB Stock
        AttachmentModifier(mod_id="mod_skel_ads", attachment_id="stock_skeletonized_cqb", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-20.0),
        AttachmentModifier(mod_id="mod_skel_stf", attachment_id="stock_skeletonized_cqb", game_version_id="v1.1.0-launch", stat_key="sprint_to_fire_ms", mod_type=ModifierType.DELTA, mod_value=-15.0),
        AttachmentModifier(mod_id="mod_skel_strafe", attachment_id="stock_skeletonized_cqb", game_version_id="v1.1.0-launch", stat_key="ads_move_speed_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.09),
        AttachmentModifier(mod_id="mod_skel_recoil", attachment_id="stock_skeletonized_cqb", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=0.08),

        # Heavy Precision Stock
        AttachmentModifier(mod_id="mod_prec_recoil_v", attachment_id="stock_heavy_precision", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.16),
        AttachmentModifier(mod_id="mod_prec_recoil_h", attachment_id="stock_heavy_precision", game_version_id="v1.1.0-launch", stat_key="recoil_horizontal", mod_type=ModifierType.PERCENTAGE, mod_value=-0.12),
        AttachmentModifier(mod_id="mod_prec_ads", attachment_id="stock_heavy_precision", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=18.0),

        # No Stock Mod
        AttachmentModifier(mod_id="mod_nostock_ads", attachment_id="stock_no_stock_mod", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-35.0),
        AttachmentModifier(mod_id="mod_nostock_stf", attachment_id="stock_no_stock_mod", game_version_id="v1.1.0-launch", stat_key="sprint_to_fire_ms", mod_type=ModifierType.DELTA, mod_value=-28.0),
        AttachmentModifier(mod_id="mod_nostock_move", attachment_id="stock_no_stock_mod", game_version_id="v1.1.0-launch", stat_key="move_speed_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.06),
        AttachmentModifier(mod_id="mod_nostock_recoil", attachment_id="stock_no_stock_mod", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=0.25),

        # Heavy Tac Anchor Stock
        AttachmentModifier(mod_id="mod_heavytac_recoil", attachment_id="stock_heavy_tac", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.14),
        AttachmentModifier(mod_id="mod_heavytac_ads", attachment_id="stock_heavy_tac", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=12.0),

        # DR-6 Handstop
        AttachmentModifier(mod_id="mod_dr6_ads", attachment_id="underbarrel_dr6_handstop", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-12.0),
        AttachmentModifier(mod_id="mod_dr6_stf", attachment_id="underbarrel_dr6_handstop", game_version_id="v1.1.0-launch", stat_key="sprint_to_fire_ms", mod_type=ModifierType.DELTA, mod_value=-10.0),
        AttachmentModifier(mod_id="mod_dr6_strafe", attachment_id="underbarrel_dr6_handstop", game_version_id="v1.1.0-launch", stat_key="ads_move_speed_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.06),

        # Bruen Heavy Support Grip
        AttachmentModifier(mod_id="mod_bruen_recoil_h", attachment_id="underbarrel_bruen_heavy_grip", game_version_id="v1.1.0-launch", stat_key="recoil_horizontal", mod_type=ModifierType.PERCENTAGE, mod_value=-0.16),
        AttachmentModifier(mod_id="mod_bruen_recoil_v", attachment_id="underbarrel_bruen_heavy_grip", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.08),
        AttachmentModifier(mod_id="mod_bruen_ads", attachment_id="underbarrel_bruen_heavy_grip", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=14.0),

        # FTAC Ripper
        AttachmentModifier(mod_id="mod_ripper_recoil_v", attachment_id="underbarrel_ftac_ripper", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.12),
        AttachmentModifier(mod_id="mod_ripper_recoil_h", attachment_id="underbarrel_ftac_ripper", game_version_id="v1.1.0-launch", stat_key="recoil_horizontal", mod_type=ModifierType.PERCENTAGE, mod_value=-0.10),
        AttachmentModifier(mod_id="mod_ripper_ads", attachment_id="underbarrel_ftac_ripper", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=12.0),

        # XTEN Phantom-5
        AttachmentModifier(mod_id="mod_xten_ads", attachment_id="underbarrel_xten_phantom5", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-10.0),
        AttachmentModifier(mod_id="mod_xten_stf", attachment_id="underbarrel_xten_phantom5", game_version_id="v1.1.0-launch", stat_key="sprint_to_fire_ms", mod_type=ModifierType.DELTA, mod_value=-12.0),

        # Merc Foregrip
        AttachmentModifier(mod_id="mod_merc_hip", attachment_id="underbarrel_merc_foregrip", game_version_id="v1.1.0-launch", stat_key="hipfire_spread_deg", mod_type=ModifierType.PERCENTAGE, mod_value=-0.18),
        AttachmentModifier(mod_id="mod_merc_recoil_v", attachment_id="underbarrel_merc_foregrip", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.10),

        # Operator Foregrip
        AttachmentModifier(mod_id="mod_operator_recoil_v", attachment_id="underbarrel_operator_grip", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.16),
        AttachmentModifier(mod_id="mod_operator_ads", attachment_id="underbarrel_operator_grip", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=10.0),

        # 40-Round Mag
        AttachmentModifier(mod_id="mod_40mag_cap", attachment_id="mag_40_round", game_version_id="v1.1.0-launch", stat_key="base_mag_size", mod_type=ModifierType.DELTA, mod_value=10.0),
        AttachmentModifier(mod_id="mod_40mag_ads", attachment_id="mag_40_round", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=8.0),
        AttachmentModifier(mod_id="mod_40mag_reload", attachment_id="mag_40_round", game_version_id="v1.1.0-launch", stat_key="reload_empty_s", mod_type=ModifierType.PERCENTAGE, mod_value=0.08),

        # 50-Round Drum
        AttachmentModifier(mod_id="mod_50mag_cap", attachment_id="mag_50_round_drum", game_version_id="v1.1.0-launch", stat_key="base_mag_size", mod_type=ModifierType.DELTA, mod_value=20.0),
        AttachmentModifier(mod_id="mod_50mag_ads", attachment_id="mag_50_round_drum", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=16.0),
        AttachmentModifier(mod_id="mod_50mag_move", attachment_id="mag_50_round_drum", game_version_id="v1.1.0-launch", stat_key="move_speed_mps", mod_type=ModifierType.PERCENTAGE, mod_value=-0.03),

        # 60-Round Drum
        AttachmentModifier(mod_id="mod_60mag_cap", attachment_id="mag_60_round_drum", game_version_id="v1.1.0-launch", stat_key="base_mag_size", mod_type=ModifierType.DELTA, mod_value=30.0),
        AttachmentModifier(mod_id="mod_60mag_ads", attachment_id="mag_60_round_drum", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=24.0),
        AttachmentModifier(mod_id="mod_60mag_reload", attachment_id="mag_60_round_drum", game_version_id="v1.1.0-launch", stat_key="reload_empty_s", mod_type=ModifierType.PERCENTAGE, mod_value=0.18),

        # 20-Round Fast Mag
        AttachmentModifier(mod_id="mod_20fast_cap", attachment_id="mag_20_fast_mag", game_version_id="v1.1.0-launch", stat_key="base_mag_size", mod_type=ModifierType.DELTA, mod_value=-10.0),
        AttachmentModifier(mod_id="mod_20fast_reload", attachment_id="mag_20_fast_mag", game_version_id="v1.1.0-launch", stat_key="reload_empty_s", mod_type=ModifierType.PERCENTAGE, mod_value=-0.25),
        AttachmentModifier(mod_id="mod_20fast_ads", attachment_id="mag_20_fast_mag", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-14.0),

        # High Grain Ammo
        AttachmentModifier(mod_id="mod_highgrain_range", attachment_id="ammo_high_grain", game_version_id="v1.1.0-launch", stat_key="range_multiplier", mod_type=ModifierType.PERCENTAGE, mod_value=0.10),
        AttachmentModifier(mod_id="mod_highgrain_vel", attachment_id="ammo_high_grain", game_version_id="v1.1.0-launch", stat_key="bullet_velocity_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.12),
        AttachmentModifier(mod_id="mod_highgrain_recoil", attachment_id="ammo_high_grain", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=0.06),

        # Overpressured Ammo
        AttachmentModifier(mod_id="mod_overpressure_flinch", attachment_id="ammo_overpressured", game_version_id="v1.1.0-launch", stat_key="flinch_resistance", mod_type=ModifierType.PERCENTAGE, mod_value=-0.20),

        # Armor Piercing Ammo
        AttachmentModifier(mod_id="mod_ap_vel", attachment_id="ammo_armor_piercing", game_version_id="v1.1.0-launch", stat_key="bullet_velocity_mps", mod_type=ModifierType.PERCENTAGE, mod_value=0.05),

        # Dragon's Breath Incendiary Ammo
        AttachmentModifier(mod_id="mod_dragons_vel", attachment_id="ammo_dragons_breath", game_version_id="v1.1.0-launch", stat_key="bullet_velocity_mps", mod_type=ModifierType.PERCENTAGE, mod_value=-0.12),
        AttachmentModifier(mod_id="mod_dragons_range", attachment_id="ammo_dragons_breath", game_version_id="v1.1.0-launch", stat_key="range_multiplier", mod_type=ModifierType.PERCENTAGE, mod_value=-0.08),

        # Explosive Heavy Slug Rounds
        AttachmentModifier(mod_id="mod_slug_vel", attachment_id="ammo_explosive_slug", game_version_id="v1.1.0-launch", stat_key="bullet_velocity_mps", mod_type=ModifierType.PERCENTAGE, mod_value=-0.15),
        AttachmentModifier(mod_id="mod_slug_recoil", attachment_id="ammo_explosive_slug", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=0.12),

        # Frangible Disabling Rounds
        AttachmentModifier(mod_id="mod_frangible_flinch", attachment_id="ammo_frangible_disabling", game_version_id="v1.1.0-launch", stat_key="flinch_resistance", mod_type=ModifierType.PERCENTAGE, mod_value=-0.15),

        # Phantom Rear Grip
        AttachmentModifier(mod_id="mod_phantomgrip_ads", attachment_id="grip_phantom_tac", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-22.0),
        AttachmentModifier(mod_id="mod_phantomgrip_stf", attachment_id="grip_phantom_tac", game_version_id="v1.1.0-launch", stat_key="sprint_to_fire_ms", mod_type=ModifierType.DELTA, mod_value=-18.0),
        AttachmentModifier(mod_id="mod_phantomgrip_recoil", attachment_id="grip_phantom_tac", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=0.06),

        # Heavy Ergonomic Grip
        AttachmentModifier(mod_id="mod_heavyergo_recoil", attachment_id="grip_heavy_ergo", game_version_id="v1.1.0-launch", stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.12),
        AttachmentModifier(mod_id="mod_heavyergo_ads", attachment_id="grip_heavy_ergo", game_version_id="v1.1.0-launch", stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=8.0),

        # Stippled Rubber Grip
        AttachmentModifier(mod_id="mod_stippled_stf", attachment_id="grip_stippled_rubber", game_version_id="v1.1.0-launch", stat_key="sprint_to_fire_ms", mod_type=ModifierType.DELTA, mod_value=-16.0)
    ]
    for m in modifiers:
        repo.upsert_attachment_modifier(m)

    # 8. Evidence Ledger Entries (Audit trail for data provenance)
    evidence_entries = [
        EvidenceLedgerEntry(
            evidence_id="ev_xm4_rpm_launch",
            target_entity_type="weapon_stats",
            target_entity_id="xm4_mw4",
            field_name="rpm",
            observed_value=780.0,
            source_url="https://www.callofduty.com/patchnotes/mw4-launch",
            source_name="Official Call of Duty Blog & Patch Notes",
            source_tier=SourceTier.TIER_1,
            test_method="Official Patch Documentation [ILLUSTRATIVE_BETA_DATA]",
            verification_status=VerificationStatus.VERIFIED,
            confidence_score=0.98,
            notes="Verified against official Day 1 patch notes documentation."
        ),
        EvidenceLedgerEntry(
            evidence_id="ev_xm4_ads_launch",
            target_entity_type="weapon_stats",
            target_entity_id="xm4_mw4",
            field_name="base_ads_ms",
            observed_value=235.0,
            source_url="https://mw4-intel-lab.local/tests/xm4-frame-audit",
            source_name="MW4 Intelligence Lab 240fps Frame Audit",
            source_tier=SourceTier.TIER_2,
            test_method="240fps video capture, first-frame trigger pull to full sight picture [ILLUSTRATIVE_BETA_DATA]",
            verification_status=VerificationStatus.VERIFIED,
            confidence_score=0.94,
            notes="5-sample average measured in private match environment."
        ),
        EvidenceLedgerEntry(
            evidence_id="ev_rival9_stf_launch",
            target_entity_type="weapon_stats",
            target_entity_id="rival9_mw4",
            field_name="sprint_to_fire_ms",
            observed_value=160.0,
            source_url="https://truegamedata.com/mw4/rival-9",
            source_name="Sym.gg / TrueGameData Verified Public Archive",
            source_tier=SourceTier.TIER_3,
            test_method="Frame timing analysis cross-referenced across 3 independent testers [ILLUSTRATIVE_BETA_DATA]",
            verification_status=VerificationStatus.VERIFIED,
            confidence_score=0.88,
            notes="Buff confirmed following October 25 launch update."
        )
    ]
    for e in evidence_entries:
        repo.upsert_evidence_entry(e)

    # 9. AI Review Queue Sample (Demonstrating Quarantine & Approval workflow)
    ai_items = [
        AIReviewItem(
            queue_id="ai_queue_001",
            proposed_payload={
                "weapon_id": "striker45_mw4",
                "field_name": "base_ads_ms",
                "proposed_value": 195.0,
                "current_value": 205.0,
                "confidence": 0.65,
                "source_context": "Community Discord OCR clip claiming stealth 10ms ADS buff in hotfix v1.1.1"
            },
            ai_model="Claude-3.5-Sonnet / OCR-Pipeline-v2",
            confidence_claim=0.65,
            rationale="OCR card extracted from 1080p twitch stream shows 195ms ADS on Striker 45. Requires 240fps frame verification before promoting to verified ledger.",
            status="pending"
        )
    ]
    for ai in ai_items:
        repo.upsert_ai_review_item(ai)

    # 10. Sample Custom Builds
    sample_builds = [
        CustomBuild(
            build_id="build_xm4_meta_laser",
            user_label="XM4 Zero-Recoil Laser",
            weapon_id="xm4_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            attachment_ids=[
                "muzzle_vt7_spiritfire",
                "barrel_cyclone_long",
                "underbarrel_bruen_heavy_grip",
                "optic_slate_reflector",
                "mag_40_round"
            ],
            notes="Ideal mid-range build with extended damage range and negligible recoil kick."
        ),
        CustomBuild(
            build_id="build_rival9_speed_rusher",
            user_label="Rival-9 Hyperspeed CQB",
            weapon_id="rival9_mw4",
            game_version_id="v1.1.0-launch",
            ruleset_id="core",
            attachment_ids=[
                "muzzle_shadowstrike_suppressor",
                "barrel_phantom_short",
                "laser_ftac_grimline",
                "underbarrel_dr6_handstop",
                "stock_skeletonized_cqb"
            ],
            notes="Ultra-fast practical engagement time and lightning sprint-to-fire speed."
        )
    ]
    for b in sample_builds:
        repo.upsert_custom_build(b)

    # 11. Chronological Stat Delta Events (Patch Tuning Lineage)
    sample_patch_deltas = [
        # XM4 Vertical Recoil Tuning
        StatDeltaEvent(
            event_id="delta_xm4_rec_aug08",
            weapon_id="xm4_mw4",
            stat_name="recoil_vertical",
            patch_version_id="v1.0.0-beta-aug08",
            effective_date="2026-08-08",
            previous_value=28.0,
            delta_type="DELTA_ADD",
            delta_value=-2.8,
            new_value=25.2,
            official_patch_url="https://www.callofduty.com/patchnotes/2026/08/call-of-duty-modern-warfare-4-beta-patch-notes",
            developer_notes="Reduced initial vertical kick to improve burst accuracy at mid range.",
            captured_timestamp="2026-08-08T18:00:00Z"
        ),
        StatDeltaEvent(
            event_id="delta_xm4_range_aug15",
            weapon_id="xm4_mw4",
            stat_name="damage_chest",
            patch_version_id="v1.0.1-beta-aug15",
            effective_date="2026-08-15",
            previous_value=30.0,
            delta_type="DELTA_ADD",
            delta_value=-2.0,
            new_value=28.0,
            official_patch_url="https://www.callofduty.com/patchnotes/2026/08/call-of-duty-modern-warfare-4-beta-patch-notes",
            developer_notes="Adjusted close-range chest damage from 30.0 to 28.0 to maintain 4-shot kill baseline.",
            captured_timestamp="2026-08-15T18:00:00Z"
        ),
        StatDeltaEvent(
            event_id="delta_xm4_range_aug22",
            weapon_id="xm4_mw4",
            stat_name="damage_chest",
            patch_version_id="v1.0.2-beta-aug22",
            effective_date="2026-08-22",
            previous_value=28.0,
            delta_type="DELTA_ADD",
            delta_value=0.0,
            new_value=28.0,
            official_patch_url="https://www.callofduty.com/patchnotes/2026/08/call-of-duty-modern-warfare-4-beta-patch-notes",
            developer_notes="Verified 28.0 chest damage with 1-headshot drop threshold maintained into launch.",
            captured_timestamp="2026-08-22T18:00:00Z"
        ),

        # Rival-9 Chest Damage Tuning
        StatDeltaEvent(
            event_id="delta_rival9_dmg_aug08",
            weapon_id="rival9_mw4",
            stat_name="damage_chest",
            patch_version_id="v1.0.0-beta-aug08",
            effective_date="2026-08-08",
            previous_value=30.0,
            delta_type="DELTA_ADD",
            delta_value=-2.0,
            new_value=28.0,
            official_patch_url="https://www.callofduty.com/patchnotes/2026/08/call-of-duty-modern-warfare-4-beta-patch-notes",
            developer_notes="Normalized close-range burst damage to align with 200ms TTK target.",
            captured_timestamp="2026-08-08T18:00:00Z"
        ),

        # BAS-B Recoil Tuning
        StatDeltaEvent(
            event_id="delta_basb_rec_aug15",
            weapon_id="basb_mw4",
            stat_name="recoil_vertical",
            patch_version_id="v1.0.1-beta-aug15",
            effective_date="2026-08-15",
            previous_value=36.0,
            delta_type="DELTA_ADD",
            delta_value=5.0,
            new_value=41.0,
            official_patch_url="https://www.callofduty.com/patchnotes/2026/08/call-of-duty-modern-warfare-4-beta-patch-notes",
            developer_notes="Increased vertical recoil kick to balance high 3-shot kinetic power.",
            captured_timestamp="2026-08-15T18:00:00Z"
        ),

        # AMR-9 ADS Speed Buff
        StatDeltaEvent(
            event_id="delta_amr9_ads_aug22",
            weapon_id="amr9_mw4",
            stat_name="base_ads_ms",
            patch_version_id="v1.0.2-beta-aug22",
            effective_date="2026-08-22",
            previous_value=210.0,
            delta_type="DELTA_ADD",
            delta_value=-15.0,
            new_value=195.0,
            official_patch_url="https://www.callofduty.com/patchnotes/2026/08/call-of-duty-modern-warfare-4-beta-patch-notes",
            developer_notes="Enhanced ADS transition speed by 15ms to reinforce SMG rush agility.",
            captured_timestamp="2026-08-22T18:00:00Z"
        )
    ]
    for d in sample_patch_deltas:
        repo.upsert_stat_delta_event(d)

    # 10. Community Meta Consensus Seed Data (WZStats, WZRanked, CODMunity, Dexerto, CharlieIntel, Dot Esports)
    initial_consensus = [
        CommunityMetaConsensus(consensus_id="c_xm4_beta", weapon_id="xm4_mw4", game_version_id="v1.0.0-beta", wzstats_tier="S-Tier 👑", wzranked_tier="S-Tier 👑", codmunity_tier="S-Tier 👑", dexerto_tier="S-Tier 👑", charlie_tier="S-Tier 👑", dotesports_tier="S-Tier 👑", consensus_tag="🔥 UNANIMOUS S-TIER META", badge_color="#f59e0b", community_pick_rate_pct=18.4, community_kd_ratio=1.18, recommended_secondary="ISO Nightshade CQB"),
        CommunityMetaConsensus(consensus_id="c_iso_beta", weapon_id="iso_nightshade_mw4", game_version_id="v1.0.0-beta", wzstats_tier="S-Tier 👑", wzranked_tier="S-Tier 👑", codmunity_tier="S-Tier 👑", dexerto_tier="S-Tier 👑", charlie_tier="S-Tier 👑", dotesports_tier="S-Tier 👑", consensus_tag="🔥 UNANIMOUS S-TIER SMG", badge_color="#f59e0b", community_pick_rate_pct=14.2, community_kd_ratio=1.15, recommended_secondary="Renetti 3-Burst"),
        CommunityMetaConsensus(consensus_id="c_hyeon_beta", weapon_id="hyeon_burst_mw4", game_version_id="v1.0.0-beta", wzstats_tier="A-Tier ⭐", wzranked_tier="A-Tier ⭐", codmunity_tier="S-Tier 👑", dexerto_tier="A-Tier ⭐", charlie_tier="A-Tier ⭐", dotesports_tier="A-Tier ⭐", consensus_tag="⚡ 1-BURST TTK CEILING", badge_color="#38bdf8", community_pick_rate_pct=8.5, community_kd_ratio=1.28, recommended_secondary="Rival-9 SpecOps"),
        CommunityMetaConsensus(consensus_id="c_rival9_beta", weapon_id="rival9_mw4", game_version_id="v1.0.0-beta", wzstats_tier="A-Tier ⭐", wzranked_tier="S-Tier 👑", codmunity_tier="A-Tier ⭐", dexerto_tier="S-Tier 👑", charlie_tier="A-Tier ⭐", dotesports_tier="A-Tier ⭐", consensus_tag="⚡ TOP PRO CQB RUSH SMG", badge_color="#38bdf8", community_pick_rate_pct=9.8, community_kd_ratio=1.12, recommended_secondary="Renetti 3-Burst"),
        CommunityMetaConsensus(consensus_id="c_ak74m_beta", weapon_id="ak74m_mw4", game_version_id="v1.0.0-beta", wzstats_tier="S-Tier 👑", wzranked_tier="A-Tier ⭐", codmunity_tier="A-Tier ⭐", dexerto_tier="A-Tier ⭐", charlie_tier="S-Tier 👑", dotesports_tier="A-Tier ⭐", consensus_tag="💪 HEAVY 7.62 PUNCH", badge_color="#38bdf8", community_pick_rate_pct=7.9, community_kd_ratio=1.16, recommended_secondary="PPSh-41 Hipfire"),
        CommunityMetaConsensus(consensus_id="c_striker_beta", weapon_id="striker45_mw4", game_version_id="v1.0.0-beta", wzstats_tier="A-Tier ⭐", wzranked_tier="A-Tier ⭐", codmunity_tier="A-Tier ⭐", dexerto_tier="A-Tier ⭐", charlie_tier="A-Tier ⭐", dotesports_tier="A-Tier ⭐", consensus_tag="🎯 LONGEST RANGE SMG", badge_color="#38bdf8", community_pick_rate_pct=5.8, community_kd_ratio=1.09, recommended_secondary="COR-45 Fast-Draw"),
        CommunityMetaConsensus(consensus_id="c_ppsh_beta", weapon_id="ppsh41_mw4", game_version_id="v1.0.0-beta", wzstats_tier="S-Tier 👑", wzranked_tier="A-Tier ⭐", codmunity_tier="A-Tier ⭐", dexerto_tier="A-Tier ⭐", charlie_tier="A-Tier ⭐", dotesports_tier="S-Tier 👑", consensus_tag="⚡ 1000 RPM ROOM CLEARER", badge_color="#38bdf8", community_pick_rate_pct=6.2, community_kd_ratio=1.07, recommended_secondary="XM4 Long-Range"),
        CommunityMetaConsensus(consensus_id="c_kvd_beta", weapon_id="kvd_enforcer_mw4", game_version_id="v1.0.0-beta", wzstats_tier="B-Tier 🔷", wzranked_tier="A-Tier ⭐", codmunity_tier="A-Tier ⭐", dexerto_tier="B-Tier 🔷", charlie_tier="A-Tier ⭐", dotesports_tier="A-Tier ⭐", consensus_tag="🎯 2-TAP PRECISION DMR", badge_color="#4ade80", community_pick_rate_pct=4.3, community_kd_ratio=1.22, recommended_secondary="ISO Nightshade CQB"),
        CommunityMetaConsensus(consensus_id="c_mcw_beta", weapon_id="mcw_mw4", game_version_id="v1.0.0-beta", wzstats_tier="B-Tier 🔷", wzranked_tier="A-Tier ⭐", codmunity_tier="B-Tier 🔷", dexerto_tier="B-Tier 🔷", charlie_tier="A-Tier ⭐", dotesports_tier="B-Tier 🔷", consensus_tag="🎯 ZERO-RECOIL LASER BEAM", badge_color="#4ade80", community_pick_rate_pct=5.1, community_kd_ratio=1.10, recommended_secondary="Striker 45 Hybrid"),
        CommunityMetaConsensus(consensus_id="c_han86_beta", weapon_id="han86_mw4", game_version_id="v1.0.0-beta", wzstats_tier="A-Tier ⭐", wzranked_tier="B-Tier 🔷", codmunity_tier="B-Tier 🔷", dexerto_tier="B-Tier 🔷", charlie_tier="B-Tier 🔷", dotesports_tier="B-Tier 🔷", consensus_tag="🛡️ HIGH STABILITY BULLPUP", badge_color="#4ade80", community_pick_rate_pct=3.6, community_kd_ratio=1.06, recommended_secondary="Renetti 3-Burst"),
        CommunityMetaConsensus(consensus_id="c_signal50_beta", weapon_id="signal50_mw4", game_version_id="v1.0.0-beta", wzstats_tier="A-Tier ⭐", wzranked_tier="B-Tier 🔷", codmunity_tier="A-Tier ⭐", dexerto_tier="A-Tier ⭐", charlie_tier="A-Tier ⭐", dotesports_tier="B-Tier 🔷", consensus_tag="🎯 1-SHOT SEMI-AUTO SNIPER", badge_color="#38bdf8", community_pick_rate_pct=4.8, community_kd_ratio=1.16, recommended_secondary="ISO Nightshade CQB"),
        CommunityMetaConsensus(consensus_id="c_basb_beta", weapon_id="basb_mw4", game_version_id="v1.0.0-beta", wzstats_tier="B-Tier 🔷", wzranked_tier="B-Tier 🔷", codmunity_tier="B-Tier 🔷", dexerto_tier="B-Tier 🔷", charlie_tier="B-Tier 🔷", dotesports_tier="B-Tier 🔷", consensus_tag="💥 PUNISHING 3-SHOT POWER", badge_color="#4ade80", community_pick_rate_pct=2.4, community_kd_ratio=1.04, recommended_secondary="Rival-9 SpecOps"),
        CommunityMetaConsensus(consensus_id="c_amr9_beta", weapon_id="amr9_mw4", game_version_id="v1.0.0-beta", wzstats_tier="B-Tier 🔷", wzranked_tier="B-Tier 🔷", codmunity_tier="B-Tier 🔷", dexerto_tier="B-Tier 🔷", charlie_tier="B-Tier 🔷", dotesports_tier="B-Tier 🔷", consensus_tag="⚡ BALANCED 833 RPM SMG", badge_color="#4ade80", community_pick_rate_pct=2.1, community_kd_ratio=1.02, recommended_secondary="COR-45 Fast-Draw"),
        CommunityMetaConsensus(consensus_id="c_katt_beta", weapon_id="katt_amr_mw4", game_version_id="v1.0.0-beta", wzstats_tier="B-Tier 🔷", wzranked_tier="B-Tier 🔷", codmunity_tier="B-Tier 🔷", dexerto_tier="A-Tier ⭐", charlie_tier="B-Tier 🔷", dotesports_tier="B-Tier 🔷", consensus_tag="🎯 .50 BMG 1-SHOT ANCHOR", badge_color="#4ade80", community_pick_rate_pct=2.9, community_kd_ratio=1.14, recommended_secondary="ISO Nightshade CQB"),
        CommunityMetaConsensus(consensus_id="c_holger_beta", weapon_id="holger556_mw4", game_version_id="v1.0.0-beta", wzstats_tier="B-Tier 🔷", wzranked_tier="B-Tier 🔷", codmunity_tier="B-Tier 🔷", dexerto_tier="B-Tier 🔷", charlie_tier="B-Tier 🔷", dotesports_tier="B-Tier 🔷", consensus_tag="🛡️ ACCURATE MID-AR", badge_color="#4ade80", community_pick_rate_pct=1.8, community_kd_ratio=1.01, recommended_secondary="Renetti 3-Burst"),
        CommunityMetaConsensus(consensus_id="c_wsp_beta", weapon_id="wsp_swarm_mw4", game_version_id="v1.0.0-beta", wzstats_tier="B-Tier 🔷", wzranked_tier="B-Tier 🔷", codmunity_tier="B-Tier 🔷", dexerto_tier="B-Tier 🔷", charlie_tier="B-Tier 🔷", dotesports_tier="B-Tier 🔷", consensus_tag="⚡ 1090 RPM MICRO-SMG", badge_color="#4ade80", community_pick_rate_pct=1.7, community_kd_ratio=0.98, recommended_secondary="XM4 Commando"),
        CommunityMetaConsensus(consensus_id="c_longbow_beta", weapon_id="longbow_mw4", game_version_id="v1.0.0-beta", wzstats_tier="B-Tier 🔷", wzranked_tier="B-Tier 🔷", codmunity_tier="B-Tier 🔷", dexerto_tier="B-Tier 🔷", charlie_tier="B-Tier 🔷", dotesports_tier="B-Tier 🔷", consensus_tag="⚡ FAST-CHAMBER SNIPER", badge_color="#4ade80", community_pick_rate_pct=1.6, community_kd_ratio=1.03, recommended_secondary="Rival-9 SpecOps"),
        CommunityMetaConsensus(consensus_id="c_rezi_beta", weapon_id="rezi12_mw4", game_version_id="v1.0.0-beta", wzstats_tier="A-Tier ⭐", wzranked_tier="C-Tier 🔶", codmunity_tier="C-Tier 🔶", dexerto_tier="C-Tier 🔶", charlie_tier="C-Tier 🔶", dotesports_tier="S-Tier 👑", consensus_tag="🚪 FULL-AUTO ROOM BREACHER", badge_color="#a855f7", community_pick_rate_pct=2.2, community_kd_ratio=1.05, recommended_secondary="XM4 Commando"),
        CommunityMetaConsensus(consensus_id="c_lockwood_beta", weapon_id="lockwood680_mw4", game_version_id="v1.0.0-beta", wzstats_tier="C-Tier 🔶", wzranked_tier="C-Tier 🔶", codmunity_tier="C-Tier 🔶", dexerto_tier="C-Tier 🔶", charlie_tier="C-Tier 🔶", dotesports_tier="C-Tier 🔶", consensus_tag="💥 1-SHOT PUMP SHOTGUN", badge_color="#a855f7", community_pick_rate_pct=1.1, community_kd_ratio=0.99, recommended_secondary="Renetti 3-Burst"),
        CommunityMetaConsensus(consensus_id="c_pulemyot_beta", weapon_id="pulemyot762_mw4", game_version_id="v1.0.0-beta", wzstats_tier="C-Tier 🔶", wzranked_tier="C-Tier 🔶", codmunity_tier="C-Tier 🔶", dexerto_tier="C-Tier 🔶", charlie_tier="C-Tier 🔶", dotesports_tier="C-Tier 🔶", consensus_tag="🛡️ 100-RND SUSTAINED FIRE", badge_color="#a855f7", community_pick_rate_pct=0.9, community_kd_ratio=0.95, recommended_secondary="ISO Nightshade CQB"),
        CommunityMetaConsensus(consensus_id="c_bruen_beta", weapon_id="bruen_mk9_mw4", game_version_id="v1.0.0-beta", wzstats_tier="C-Tier 🔶", wzranked_tier="C-Tier 🔶", codmunity_tier="C-Tier 🔶", dexerto_tier="C-Tier 🔶", charlie_tier="C-Tier 🔶", dotesports_tier="C-Tier 🔶", consensus_tag="🛡️ 60-RND SQUAD LMG", badge_color="#a855f7", community_pick_rate_pct=0.8, community_kd_ratio=0.96, recommended_secondary="ISO Nightshade CQB"),
        CommunityMetaConsensus(consensus_id="c_sidewinder_beta", weapon_id="sidewinder_mw4", game_version_id="v1.0.0-beta", wzstats_tier="D-Tier 🔘", wzranked_tier="D-Tier 🔘", codmunity_tier="D-Tier 🔘", dexerto_tier="D-Tier 🔘", charlie_tier="D-Tier 🔘", dotesports_tier="D-Tier 🔘", consensus_tag="⚠️ HIGH RECOIL / LOW RPM", badge_color="#94a3b8", community_pick_rate_pct=0.4, community_kd_ratio=0.88, recommended_secondary="Renetti 3-Burst"),
        CommunityMetaConsensus(consensus_id="c_renetti_beta", weapon_id="renetti_mw4", game_version_id="v1.0.0-beta", wzstats_tier="D-Tier 🔘", wzranked_tier="D-Tier 🔘", codmunity_tier="D-Tier 🔘", dexerto_tier="D-Tier 🔘", charlie_tier="D-Tier 🔘", dotesports_tier="D-Tier 🔘", consensus_tag="🔫 3-ROUND BURST SIDEARM", badge_color="#94a3b8", community_pick_rate_pct=0.6, community_kd_ratio=0.92, recommended_secondary="XM4 Commando"),
        CommunityMetaConsensus(consensus_id="c_cor45_beta", weapon_id="cor45_mw4", game_version_id="v1.0.0-beta", wzstats_tier="D-Tier 🔘", wzranked_tier="D-Tier 🔘", codmunity_tier="D-Tier 🔘", dexerto_tier="D-Tier 🔘", charlie_tier="D-Tier 🔘", dotesports_tier="D-Tier 🔘", consensus_tag="🔫 SEMI-AUTO BACKUP SIDEARM", badge_color="#94a3b8", community_pick_rate_pct=0.5, community_kd_ratio=0.90, recommended_secondary="XM4 Commando")
    ]
    for c in initial_consensus:
        repo.upsert_community_consensus(c)

    # 11. Verified Meta Build Presets (CDL Pro, Lab Pareto, Max Speed, Zero Recoil, S&D Stealth)
    initial_meta_builds = [
        # XM4 Commando
        MetaBuildPreset(
            build_id="mb_xm4_cdl_pro", weapon_id="xm4_mw4", game_version_id="v1.0.0-beta",
            build_name="XM4 Commando - CDL Pro Tournament Meta", archetype="cdl_pro", archetype_display="👑 CDL Pro Meta",
            source_outlet="CODMunity / OpTic Dashy (Ranked Meta)",
            attachment_ids=["muzzle_casus_brake", "barrel_phantom_short", "underbarrel_dr6_handstop", "mag_40_round", "stock_skeletonized_cqb"],
            perk_1_name="Quick Fix", perk_2_name="Fast Hands", perk_3_name="Battle Hardened",
            tactical_name="Shock Stick", lethal_name="Semtex", field_upgrade_name="Trophy System",
            secondary_name="Renetti 3-Burst", secondary_role="180ms Fast-Swap Pocket Finisher",
            secondary_attachments=["barrel_phantom_short", "stock_skeletonized_cqb"],
            best_maps="Skyline, Babylon, Protocol",
            playstyle_notes="The definitive tournament standard. Cuts ADS down to 195ms while retaining a lethal 4-shot TTK across all mid-range lanes.",
            share_code="MW4-XM4-PRO-CAS-PH-DR6-40R-SK"
        ),
        MetaBuildPreset(
            build_id="mb_xm4_pareto", weapon_id="xm4_mw4", game_version_id="v1.0.0-beta",
            build_name="XM4 Commando - Laboratory Pareto-Optimal", archetype="lab_pareto", archetype_display="🔬 Lab Pareto Optimal",
            source_outlet="Lab Multi-Objective Optimization Engine",
            attachment_ids=["muzzle_crown50_brake", "barrel_reinforced_match", "underbarrel_bruen_heavy_grip", "mag_40_round", "stock_heavy_precision"],
            perk_1_name="Overkill", perk_2_name="Fast Hands", perk_3_name="Battle Hardened",
            tactical_name="Flashbang", lethal_name="Frag Grenade", field_upgrade_name="Trophy System",
            secondary_name="ISO Nightshade CQB", secondary_role="Overkill CQB Shredder (188ms TTK)",
            secondary_attachments=["muzzle_casus_brake", "barrel_ultralight_fluted", "underbarrel_dr6_handstop"],
            best_maps="Scud, Protocol, Derelict",
            playstyle_notes="Mathematically superior 5-axis balance. -38% horizontal recoil reduction and +12% effective damage range with only 12ms ADS penalty.",
            share_code="MW4-XM4-PAR-CR-RF-BRU-40R-HP"
        ),
        MetaBuildPreset(
            build_id="mb_xm4_speed", weapon_id="xm4_mw4", game_version_id="v1.0.0-beta",
            build_name="XM4 Commando - Hyper-Omnimovement Rusher", archetype="max_speed", archetype_display="⚡ Max Speed Rusher",
            source_outlet="WZRanked / 42% Aggro Pick",
            attachment_ids=["barrel_phantom_short", "laser_fss_olev", "underbarrel_dr6_handstop", "stock_no_stock_mod", "mag_20_fast_mag"],
            perk_1_name="Quick Fix", perk_2_name="Fast Hands", perk_3_name="Blood Rush",
            tactical_name="Stim", lethal_name="Semtex", field_upgrade_name="Dead Silence",
            secondary_name="COR-45 Quick-Draw", secondary_role="Instantaneous Slide-Draw Pistol",
            secondary_attachments=["laser_point_g3p", "grip_phantom_tac"],
            best_maps="Skyline, Babylon, Gala",
            playstyle_notes="Engineered for slide-canceling and aggressive corner peeking. 155ms ADS and 130ms Sprint-to-Fire with maximum strafe mobility.",
            share_code="MW4-XM4-SPD-PH-OLE-DR6-NST-20F"
        ),
        MetaBuildPreset(
            build_id="mb_xm4_laser", weapon_id="xm4_mw4", game_version_id="v1.0.0-beta",
            build_name="XM4 Commando - Zero-Recoil Long-Range Beamer", archetype="zero_recoil", archetype_display="🎯 Zero-Recoil Beamer",
            source_outlet="WZStats.gg / Long Range Tier 1",
            attachment_ids=["muzzle_purifier_brake", "barrel_cyclone_long", "underbarrel_bruen_heavy_grip", "mag_40_round", "stock_heavy_precision"],
            perk_1_name="High Alert", perk_2_name="Hardline", perk_3_name="Cold-Blooded",
            tactical_name="Smoke Grenade", lethal_name="Claymore", field_upgrade_name="Smoke Wall",
            secondary_name="ISO Nightshade CQB", secondary_role="Overkill CQB Defense",
            secondary_attachments=["muzzle_casus_brake", "stock_skeletonized_cqb"],
            best_maps="Scud, Protocol, Redacted",
            playstyle_notes="Zero muzzle drift. Pinpoint laser precision at 45m+ sightlines with +18% bullet velocity.",
            share_code="MW4-XM4-LSR-PUR-CYC-BRU-40R-HP"
        ),

        # ISO Nightshade
        MetaBuildPreset(
            build_id="mb_iso_cdl_pro", weapon_id="iso_nightshade_mw4", game_version_id="v1.0.0-beta",
            build_name="ISO Nightshade - CDL Pro CQB Shredder", archetype="cdl_pro", archetype_display="👑 CDL Pro Meta",
            source_outlet="CODMunity / FaZe Simp Pro Setup",
            attachment_ids=["muzzle_casus_brake", "barrel_ultralight_fluted", "underbarrel_dr6_handstop", "stock_skeletonized_cqb", "mag_40_round"],
            perk_1_name="Quick Fix", perk_2_name="Fast Hands", perk_3_name="Battle Hardened",
            tactical_name="Shock Stick", lethal_name="Semtex", field_upgrade_name="Trophy System",
            secondary_name="Renetti 3-Burst", secondary_role="180ms Pocket Clean-Up",
            secondary_attachments=["optic_cronen_mini"],
            best_maps="Skyline, Babylon, Gala",
            playstyle_notes="The #1 close-range weapon in MW4 Beta. 188ms TTK with blazing 160ms ADS and instantaneous hipfire sprint recovery.",
            share_code="MW4-ISO-PRO-CAS-FL-DR6-SK-40R"
        ),
        MetaBuildPreset(
            build_id="mb_iso_stealth", weapon_id="iso_nightshade_mw4", game_version_id="v1.0.0-beta",
            build_name="ISO Nightshade - S&D Silent Infiltrator", archetype="stealth_snd", archetype_display="🤫 S&D Stealth Infiltrator",
            source_outlet="CharlieIntel / Competitive S&D Guide",
            attachment_ids=["muzzle_colossus_heavy", "barrel_ultralight_fluted", "laser_corio_laz44", "stock_skeletonized_cqb", "mag_40_round"],
            perk_1_name="Ghost", perk_2_name="Bomb Squad", perk_3_name="Ninja",
            tactical_name="Heartbeat Sensor", lethal_name="Semtex", field_upgrade_name="Smoke Wall",
            secondary_name="COR-45 Subsonic", secondary_role="Suppressed Stealth Sidearm",
            secondary_attachments=["ammo_subsonic_low"],
            best_maps="Skyline, Scud, Protocol",
            playstyle_notes="Completely suppressed sound signature + total UAV and footstep audio masking for flank-lane multi-kills.",
            share_code="MW4-ISO-SND-COL-FL-LAZ-SK-40R"
        ),

        # Hyeon Burst
        MetaBuildPreset(
            build_id="mb_hyeon_cdl_pro", weapon_id="hyeon_burst_mw4", game_version_id="v1.0.0-beta",
            build_name="Hyeon Burst - 1-Burst Lethal Anchor", archetype="cdl_pro", archetype_display="👑 CDL Pro Meta",
            source_outlet="CODMunity / CDL Anchor Meta",
            attachment_ids=["muzzle_crown50_brake", "barrel_reinforced_match", "underbarrel_bruen_heavy_grip", "mag_40_round", "stock_heavy_precision"],
            perk_1_name="High Alert", perk_2_name="Fast Hands", perk_3_name="Battle Hardened",
            tactical_name="Shock Stick", lethal_name="Semtex", field_upgrade_name="Trophy System",
            secondary_name="Rival-9 SpecOps", secondary_role="Overkill CQB Rush Entry",
            secondary_attachments=["muzzle_casus_brake", "barrel_phantom_short", "underbarrel_dr6_handstop"],
            best_maps="Scud, Protocol, Skyline",
            playstyle_notes="Groups all 3 burst rounds into the upper chest for an unbelievable 125ms 1-burst kill ceiling.",
            share_code="MW4-HYN-PRO-CR-RF-BRU-40R-HP"
        ),

        # Rival-9 SpecOps
        MetaBuildPreset(
            build_id="mb_rival9_cdl_pro", weapon_id="rival9_mw4", game_version_id="v1.0.0-beta",
            build_name="Rival-9 SpecOps - OpTic Shotzzy Rush Build", archetype="cdl_pro", archetype_display="👑 CDL Pro Meta",
            source_outlet="CODMunity / OpTic Shotzzy Class",
            attachment_ids=["muzzle_casus_brake", "barrel_phantom_short", "underbarrel_dr6_handstop", "stock_skeletonized_cqb", "mag_40_round"],
            perk_1_name="Quick Fix", perk_2_name="Fast Hands", perk_3_name="Blood Rush",
            tactical_name="Stim", lethal_name="Semtex", field_upgrade_name="Dead Silence",
            secondary_name="Renetti 3-Burst", secondary_role="180ms Pocket Burst Sidearm",
            secondary_attachments=["laser_point_g3p"],
            best_maps="Skyline, Babylon, Gala, Pit",
            playstyle_notes="Maximum slide-peek velocity and 900 RPM bullet hose for high-octane 6v6 Hardpoint entry fragging.",
            share_code="MW4-RIV-PRO-CAS-PH-DR6-SK-40R"
        ),

        # Kastov 74-M
        MetaBuildPreset(
            build_id="mb_ak74m_cdl_pro", weapon_id="ak74m_mw4", game_version_id="v1.0.0-beta",
            build_name="Kastov 74-M - Heavy 7.62 Punch Meta", archetype="cdl_pro", archetype_display="👑 CDL Pro Meta",
            source_outlet="CharlieIntel / Ranked 7.62 Meta",
            attachment_ids=["muzzle_casus_brake", "barrel_chf_heavy", "underbarrel_bruen_heavy_grip", "mag_40_round", "stock_heavy_precision"],
            perk_1_name="Quick Fix", perk_2_name="Fast Hands", perk_3_name="Battle Hardened",
            tactical_name="Shock Stick", lethal_name="Semtex", field_upgrade_name="Trophy System",
            secondary_name="PPSh-41 Hipfire", secondary_role="Overkill CQB Room Clearer",
            secondary_attachments=["laser_point_g3p", "stock_no_stock_mod"],
            best_maps="Protocol, Scud, Skyline",
            playstyle_notes="Delivers punishing 38 damage upper-torso hits that guarantee a flat 3-shot kill out to 28 meters.",
            share_code="MW4-KAS-PRO-CAS-CHF-BRU-40R-HP"
        ),

        # Striker 45
        MetaBuildPreset(
            build_id="mb_striker_cdl_pro", weapon_id="striker45_mw4", game_version_id="v1.0.0-beta",
            build_name="Striker 45 - Long-Range SMG Hybrid", archetype="cdl_pro", archetype_display="👑 CDL Pro Meta",
            source_outlet="WZRanked / Longest Range SMG",
            attachment_ids=["muzzle_colossus_heavy", "barrel_cyclone_long", "underbarrel_dr6_handstop", "mag_40_round", "stock_skeletonized_cqb"],
            perk_1_name="Quick Fix", perk_2_name="Fast Hands", perk_3_name="Battle Hardened",
            tactical_name="Shock Stick", lethal_name="Semtex", field_upgrade_name="Trophy System",
            secondary_name="COR-45 Quick-Draw", secondary_role="Instant Draw Pistol",
            secondary_attachments=["grip_phantom_tac"],
            best_maps="Protocol, Skyline, Scud",
            playstyle_notes="Combines AR-like damage range with snappy SMG handling. Dominates hybrid mid-range engagements.",
            share_code="MW4-STR-PRO-COL-CYC-DR6-40R-SK"
        ),

        # PPSh-41
        MetaBuildPreset(
            build_id="mb_ppsh_room_clear", weapon_id="ppsh41_mw4", game_version_id="v1.0.0-beta",
            build_name="PPSh-41 - 1000 RPM Hipfire Shredder", archetype="max_speed", archetype_display="⚡ Max Speed Rusher",
            source_outlet="Dot Esports / Weekend 1 Meta",
            attachment_ids=["muzzle_casus_brake", "laser_point_g3p", "underbarrel_merc_foregrip", "mag_50_round_drum", "stock_no_stock_mod"],
            perk_1_name="Quick Fix", perk_2_name="Fast Hands", perk_3_name="Blood Rush",
            tactical_name="Stim", lethal_name="Molotov Cocktail", field_upgrade_name="Dead Silence",
            secondary_name="XM4 Commando", secondary_role="Overkill Long-Range Anchor",
            secondary_attachments=["muzzle_purifier_brake", "barrel_cyclone_long"],
            best_maps="Skyline, Babylon, Gala",
            playstyle_notes="Zero-bloom hipfire laser. Blazes at 1000 RPM to instantly clear hardpoint hills without aiming down sights.",
            share_code="MW4-PPS-HIP-CAS-G3P-MRC-50D-NST"
        ),

        # KVD Enforcer
        MetaBuildPreset(
            build_id="mb_kvd_2tap", weapon_id="kvd_enforcer_mw4", game_version_id="v1.0.0-beta",
            build_name="KVD Enforcer - 2-Tap Precision DMR", archetype="cdl_pro", archetype_display="👑 CDL Pro Meta",
            source_outlet="CODMunity / Precision DMR Meta",
            attachment_ids=["muzzle_crown50_brake", "barrel_cyclone_long", "optic_corio_eagleseye", "underbarrel_bruen_heavy_grip", "mag_40_round"],
            perk_1_name="High Alert", perk_2_name="Hardline", perk_3_name="Cold-Blooded",
            tactical_name="Smoke Grenade", lethal_name="Trip Wire", field_upgrade_name="Smoke Wall",
            secondary_name="ISO Nightshade CQB", secondary_role="Overkill CQB Shredder",
            secondary_attachments=["muzzle_casus_brake", "barrel_phantom_short"],
            best_maps="Scud, Protocol, Redacted",
            playstyle_notes="Flat 2-shot kill to the chest at any distance with crisp 2.5x magnification and negligible muzzle climb.",
            share_code="MW4-KVD-DMR-CR-CYC-EE-BRU-40R"
        ),

        # Signal .50
        MetaBuildPreset(
            build_id="mb_signal50_quick", weapon_id="signal50_mw4", game_version_id="v1.0.0-beta",
            build_name="Signal .50 - Semi-Auto Quickscope Anchor", archetype="cdl_pro", archetype_display="👑 CDL Pro Meta",
            source_outlet="WZStats.gg / Sniper Tier 1",
            attachment_ids=["barrel_phantom_short", "laser_fss_olev", "stock_skeletonized_cqb", "grip_phantom_tac", "underbarrel_dr6_handstop"],
            perk_1_name="High Alert", perk_2_name="Fast Hands", perk_3_name="Battle Hardened",
            tactical_name="Shock Stick", lethal_name="Claymore", field_upgrade_name="Trophy System",
            secondary_name="ISO Nightshade CQB", secondary_role="Overkill CQB Defense",
            secondary_attachments=["muzzle_casus_brake", "stock_skeletonized_cqb"],
            best_maps="Scud, Protocol, Redacted",
            playstyle_notes="Semi-automatic 1-shot sniper rifle tuned for rapid follow-up shots and lightning-fast quickscoping.",
            share_code="MW4-SIG-SNIP-PH-OLE-SK-RGP-DR6"
        ),

        # MCW Precision
        MetaBuildPreset(
            build_id="mb_mcw_laser", weapon_id="mcw_mw4", game_version_id="v1.0.0-beta",
            build_name="MCW Precision - Zero-Recoil Laser", archetype="zero_recoil", archetype_display="🎯 Zero-Recoil Beamer",
            source_outlet="CODMunity / Laser AR Class",
            attachment_ids=["muzzle_purifier_brake", "barrel_reinforced_match", "underbarrel_bruen_heavy_grip", "optic_mk3_reflector", "stock_heavy_precision"],
            perk_1_name="Quick Fix", perk_2_name="Fast Hands", perk_3_name="Battle Hardened",
            tactical_name="Shock Stick", lethal_name="Semtex", field_upgrade_name="Trophy System",
            secondary_name="Striker 45 Hybrid", secondary_role="Overkill Hybrid Mobility SMG",
            secondary_attachments=["barrel_phantom_short", "stock_skeletonized_cqb"],
            best_maps="Protocol, Scud, Skyline",
            playstyle_notes="The easiest gun to control in MW4. Zero horizontal recoil variance allows cross-map beaming with 100% accuracy.",
            share_code="MW4-MCW-LSR-PUR-RF-BRU-MK3-HP"
        ),

        # Rezi 12
        MetaBuildPreset(
            build_id="mb_rezi12_breacher", weapon_id="rezi12_mw4", game_version_id="v1.0.0-beta",
            build_name="Rezi 12 - Full-Auto Room Breacher", archetype="max_speed", archetype_display="⚡ Max Speed Rusher",
            source_outlet="Dot Esports / CQB Room Breacher",
            attachment_ids=["muzzle_crown50_brake", "barrel_phantom_short", "laser_point_g3p", "mag_50_round_drum", "stock_no_stock_mod"],
            perk_1_name="Quick Fix", perk_2_name="Fast Hands", perk_3_name="Blood Rush",
            tactical_name="Stim", lethal_name="Molotov Cocktail", field_upgrade_name="Trophy System",
            secondary_name="XM4 Commando", secondary_role="Overkill Mid-Range Anchor",
            secondary_attachments=["muzzle_casus_brake", "barrel_cyclone_long"],
            best_maps="Skyline, Babylon, Gala, Pit",
            playstyle_notes="Full-auto 12-gauge shotgun that tears through interior hardpoints and doorway chokepoints in under 150ms.",
            share_code="MW4-REZ-CQB-CR-PH-G3P-50D-NST"
        )
    ]
    for b in initial_meta_builds:
        repo.upsert_meta_build(b)




