"""
MW4 Weapon Intelligence Lab - Seed Data Generator (Authentic 2026 MW4 Beta)
Populates DuckDB from data/snapshots/*.parquet or falls back to authentic 17-weapon definitions.
"""

import os
from typing import List
from src.database.connection import db_manager, DatabaseManager
from src.database.repository import IntelligenceRepository
from src.database.models import (
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
    """Initializes and seeds DuckDB with full baseline weapon intelligence from Parquet snapshots."""
    manager.init_database()
    repo = IntelligenceRepository(manager)
    
    # 1. Attempt to load from versioned Parquet snapshots
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    snapshots_dir = os.path.join(base_dir, "data", "snapshots")
    
    tables = [
        "game_versions",
        "rulesets",
        "weapons",
        "weapon_version_stats",
        "weapon_damage_profiles",
        "attachments",
        "attachment_modifiers",
        "evidence_ledger",
        "ai_review_queue",
        "source_snapshots",
        "custom_builds",
        "stat_delta_events",
        "community_meta_consensus",
        "meta_build_presets"
    ]
    
    loaded_any = False
    if os.path.exists(snapshots_dir):
        for table in tables:
            p_path = os.path.join(snapshots_dir, f"{table}.parquet")
            if os.path.exists(p_path):
                try:
                    manager.import_table_from_parquet(table, p_path)
                    loaded_any = True
                except Exception as e:
                    pass
                    
    if loaded_any:
        return

    # Fallback to direct Python seeding if Parquet snapshots missing
    _seed_fallback(manager, repo)


def _seed_fallback(manager: DatabaseManager, repo: IntelligenceRepository) -> None:
    """Hardcoded fallback for authentic MW4 Beta 17 weapons."""
    # 1. Game Versions
    v_w2 = GameVersion(
        version_id="v1.2.0-beta-weekend2",
        name="Beta Weekend 2 Patch",
        patch_date="2026-08-28",
        is_active=True,
        notes="Weekend 2 TTK overhaul, 5 new weapons, Blood Rush TacSprint rework."
    )
    repo.save_game_version(v_w2)
    
    # 2. Rulesets
    repo.save_ruleset(Ruleset(ruleset_id="core", name="Core 100 HP", target_health=100.0, headshot_multiplier_global=1.0, limb_multiplier_global=1.0, is_active=True))
    repo.save_ruleset(Ruleset(ruleset_id="hardcore", name="Hardcore 30 HP", target_health=30.0, headshot_multiplier_global=1.0, limb_multiplier_global=1.0, is_active=True))
    repo.save_ruleset(Ruleset(ruleset_id="warzone", name="Warzone 300 HP", target_health=300.0, headshot_multiplier_global=1.0, limb_multiplier_global=1.0, is_active=True))
