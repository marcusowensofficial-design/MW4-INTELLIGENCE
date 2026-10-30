"""
Unit tests verifying the October 28, 2026 MW4 weapon tuning patch notes ingestion (v1.3.1-patch1).
"""

import pytest
from src.database.connection import db_manager
from src.database.repository import IntelligenceRepository
from src.ingestion.diff_engine import compare_weapon_versions
from src.engines.stat_lineage_engine import reconstruct_stat_lineage, audit_weapon_patch_continuity


@pytest.fixture
def repo():
    return IntelligenceRepository(db_manager)


def test_game_version_v131_registered_and_active(repo):
    active = repo.get_active_game_version()
    assert active is not None
    assert active.version_id == "v1.3.1-patch1"
    assert active.release_date == "2026-10-28"
    assert "weapon tuning" in active.patch_name.lower() or "patch notes" in active.patch_name.lower()

    versions = [v.version_id for v in repo.get_game_versions()]
    assert "v1.3.1-patch1" in versions
    assert "v1.3.0-launch" in versions


def test_ppsh41_stat_adjustments(repo):
    stats = repo.get_weapon_stats("ppsh41_mw4", "v1.3.1-patch1")
    assert stats is not None
    assert stats.base_ads_ms == 280.0
    assert stats.move_speed_mps == 4.70
    assert stats.ads_move_speed_mps == 2.78

    diff = compare_weapon_versions("ppsh41_mw4", "v1.3.0-launch", "v1.3.1-patch1", repo)
    assert diff is not None
    assert diff.has_changes is True

    ads_delta = next((d for d in diff.deltas if d.stat_name == "base_ads_ms"), None)
    assert ads_delta is not None
    assert ads_delta.v1_value == 300.0
    assert ads_delta.v2_value == 280.0
    assert ads_delta.classification == "BUFF"


def test_damage_profile_ranges_and_multipliers(repo):
    # Han 86 range extended to 30.0m
    han_profiles = repo.get_damage_profiles("han86_mw4", "v1.3.1-patch1", "core")
    assert len(han_profiles) >= 3
    assert han_profiles[0].range_end_m == 30.0
    assert han_profiles[0].damage_neck == han_profiles[0].damage_chest

    # Kastov 762 range extended to 31.0m
    kastov_profiles = repo.get_damage_profiles("kastov762_mw4", "v1.3.1-patch1", "core")
    assert kastov_profiles[0].range_end_m == 31.0

    # M4 range extended to 26.8m
    m4_profiles = repo.get_damage_profiles("m4_mw4", "v1.3.1-patch1", "core")
    assert m4_profiles[0].range_end_m == 26.8

    # Oden damage normalization
    oden_profiles = repo.get_damage_profiles("oden_mw4", "v1.3.1-patch1", "core")
    assert oden_profiles[0].damage_stomach == oden_profiles[0].damage_chest

    # SMG limb normalization (arms and hands 1.0x)
    for smg_id in ["iso_nightshade_mw4", "vel46_mw4", "wz55_striga_mw4", "x58_nyx_mw4"]:
        profiles = repo.get_damage_profiles(smg_id, "v1.3.1-patch1", "core")
        assert profiles[0].damage_limbs == profiles[0].damage_chest

    # X-58 Nyx headshot multiplier = 1.30x
    nyx_profiles = repo.get_damage_profiles("x58_nyx_mw4", "v1.3.1-patch1", "core")
    assert round(nyx_profiles[0].damage_head / nyx_profiles[0].damage_chest, 2) == 1.30


def test_patriot_xmr_attachment_penalties(repo):
    mods = repo.get_attachment_modifiers("v1.3.1-patch1")
    haste_mods = [m for m in mods if m.attachment_id == "exp_haste_80l_14"]
    fury_mods = [m for m in mods if m.attachment_id == "fjx_fury_iv_grip"]

    for m in haste_mods:
        if m.stat_key in ("recoil_horizontal", "recoil_vertical"):
            assert m.mod_value == 6.0

    for m in fury_mods:
        if m.stat_key in ("recoil_horizontal", "recoil_vertical"):
            assert m.mod_value == 4.0


def test_stat_lineage_continuity(repo):
    for wid, stat, exp_val in [
        ("m4_mw4", "range_effective_m", 26.8),
        ("kastov762_mw4", "range_effective_m", 31.0),
        ("han86_mw4", "range_effective_m", 30.0),
        ("ppsh41_mw4", "base_ads_ms", 280.0)
    ]:
        events = repo.get_stat_delta_events(wid)
        rec = reconstruct_stat_lineage(events, wid, stat)
        assert rec.is_continuity_verified is True
        assert rec.reconstructed_value == exp_val
        assert rec.total_patches_applied >= 1
