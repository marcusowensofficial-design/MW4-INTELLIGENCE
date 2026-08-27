"""
Unit tests for Meta Build Presets and Pro Class Hub.
Validates model schemas, DuckDB persistence, archetype filtering, and Gunsmith attachment legality.
"""

import pytest
from src.database.connection import DatabaseManager
from src.database.repository import IntelligenceRepository
from src.database.seed_data import seed_database
from src.database.models import MetaBuildPreset
from src.engines.attachment_engine import validate_build_legality


def test_meta_build_preset_model_instantiation():
    preset = MetaBuildPreset(
        build_id="mb_test_xm4",
        weapon_id="xm4_mw4",
        game_version_id="v1.0.0-beta",
        build_name="Test XM4 Build",
        archetype="cdl_pro",
        archetype_display="👑 CDL Pro Meta",
        source_outlet="CODMunity Test",
        attachment_ids=["muzzle_casus_brake", "barrel_phantom_short"],
        perk_1_name="Quick Fix",
        perk_2_name="Fast Hands",
        perk_3_name="Battle Hardened",
        tactical_name="Shock Stick",
        lethal_name="Semtex",
        field_upgrade_name="Trophy System",
        secondary_name="Renetti 3-Burst",
        secondary_role="180ms Pocket Finisher",
        secondary_attachments=["barrel_phantom_short"],
        best_maps="Skyline, Babylon",
        playstyle_notes="Test playstyle notes",
        share_code="MW4-TEST-SHARE-CODE"
    )
    assert preset.build_id == "mb_test_xm4"
    assert len(preset.attachment_ids) == 2
    assert preset.secondary_name == "Renetti 3-Burst"
    assert preset.is_verified_meta is True


def test_meta_builds_repository_persistence():
    db = DatabaseManager(":memory:")
    seed_database(db)
    repo = IntelligenceRepository(db)

    # Fetch all builds
    all_builds = repo.get_meta_builds()
    assert len(all_builds) >= 15

    # Check secondary weapon companion
    for b in all_builds:
        assert b.secondary_name is not None
        assert b.secondary_role is not None

    # Filter by weapon
    xm4_builds = repo.get_meta_builds(weapon_id="xm4_mw4")
    assert len(xm4_builds) == 4
    arch_types = [b.archetype for b in xm4_builds]
    assert "cdl_pro" in arch_types
    assert "lab_pareto" in arch_types
    assert "max_speed" in arch_types
    assert "zero_recoil" in arch_types

    # Filter by archetype
    cdl_builds = repo.get_meta_builds(archetype="cdl_pro")
    assert len(cdl_builds) >= 8

    # Test consensus pick rate & KD retrieval
    consensus = repo.get_community_consensus()
    assert "xm4_mw4" in consensus
    assert consensus["xm4_mw4"].community_pick_rate_pct == 18.4
    assert consensus["xm4_mw4"].community_kd_ratio == 1.18


def test_all_seeded_meta_builds_attachment_legality():
    db = DatabaseManager(":memory:")
    seed_database(db)
    repo = IntelligenceRepository(db)

    weapons = {w.weapon_id: w for w in repo.get_weapons()}
    all_attachments = {a.attachment_id: a for a in repo.get_attachments()}
    all_builds = repo.get_meta_builds()

    for b in all_builds:
        assert b.weapon_id in weapons, f"Unknown weapon_id {b.weapon_id} in build {b.build_id}"
        w = weapons[b.weapon_id]
        
        equipped_attachments = []
        for aid in b.attachment_ids:
            assert aid in all_attachments, f"Unknown attachment_id {aid} in build {b.build_id}"
            equipped_attachments.append(all_attachments[aid])

        is_legal, err = validate_build_legality(w, equipped_attachments, max_slots=5)
        assert is_legal is True, f"Build {b.build_id} failed legality check: {err}"

