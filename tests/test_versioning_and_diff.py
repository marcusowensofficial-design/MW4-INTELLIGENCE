"""
Unit tests for Game Version Immutability, Multi-Version Queries, and Patch Diff Engine.
"""

import pytest
from src.database.connection import DatabaseManager
from src.database.repository import IntelligenceRepository
from src.database.models import (
    GameVersion,
    Weapon,
    WeaponVersionStats,
    WeaponClass,
    FiringMode
)
from src.ingestion.diff_engine import compare_weapon_versions, classify_stat_delta


@pytest.fixture
def ephemeral_repo():
    # Use in-memory DuckDB instance for clean isolated testing
    mgr = DatabaseManager(db_path=":memory:")
    mgr.init_database()
    repo = IntelligenceRepository(mgr)

    # Add 2 versions
    repo.upsert_game_version(GameVersion(version_id="v1.0.0-beta", release_date="2026-09-01", patch_name="Beta 1"))
    repo.upsert_game_version(GameVersion(version_id="v1.1.0-launch", release_date="2026-10-25", patch_name="Launch Patch"))

    # Add weapon
    repo.upsert_weapon(
        Weapon(
            weapon_id="test_smg", name="Test SMG", weapon_class=WeaponClass.SUBMACHINE_GUN,
            firing_mode=FiringMode.FULL_AUTO, default_rpm=900.0, base_mag_size=30
        )
    )

    # Stats v1.0.0 (Beta)
    repo.upsert_weapon_stats(
        WeaponVersionStats(
            stat_id="smg_v1.0.0", weapon_id="test_smg", game_version_id="v1.0.0-beta",
            rpm=900.0, base_ads_ms=200.0, sprint_to_fire_ms=180.0, bullet_velocity_mps=500.0,
            reload_empty_s=2.2, reload_tactical_s=1.7, recoil_horizontal=25.0, recoil_vertical=30.0,
            hipfire_spread_deg=3.0, move_speed_mps=5.2, ads_move_speed_mps=3.5
        )
    )

    # Stats v1.1.0 (Launch: Buffed ADS & STF, Nerfed Velocity)
    repo.upsert_weapon_stats(
        WeaponVersionStats(
            stat_id="smg_v1.1.0", weapon_id="test_smg", game_version_id="v1.1.0-launch",
            rpm=900.0, base_ads_ms=185.0, sprint_to_fire_ms=160.0, bullet_velocity_mps=480.0,
            reload_empty_s=2.2, reload_tactical_s=1.7, recoil_horizontal=25.0, recoil_vertical=30.0,
            hipfire_spread_deg=3.0, move_speed_mps=5.2, ads_move_speed_mps=3.5
        )
    )

    return repo


def test_version_immutability(ephemeral_repo):
    # Verify that v1.0.0-beta stats remain intact and are not overwritten
    v1_stats = ephemeral_repo.get_weapon_stats("test_smg", "v1.0.0-beta")
    v2_stats = ephemeral_repo.get_weapon_stats("test_smg", "v1.1.0-launch")

    assert v1_stats.base_ads_ms == 200.0
    assert v2_stats.base_ads_ms == 185.0
    assert v1_stats.stat_id != v2_stats.stat_id


def test_stat_delta_classification():
    # ADS decreased from 200 to 185 -> Faster -> BUFF
    cls_ads, is_lower = classify_stat_delta("base_ads_ms", 200.0, 185.0)
    assert cls_ads == "BUFF"
    assert is_lower is True

    # Velocity decreased from 500 to 480 -> Slower -> NERF
    cls_vel, is_lower_vel = classify_stat_delta("bullet_velocity_mps", 500.0, 480.0)
    assert cls_vel == "NERF"
    assert is_lower_vel is False


def test_weapon_version_diff_engine(ephemeral_repo):
    diff = compare_weapon_versions("test_smg", "v1.0.0-beta", "v1.1.0-launch", ephemeral_repo)

    assert diff is not None
    assert diff.has_changes is True
    ads_delta = next(d for d in diff.deltas if d.stat_name == "base_ads_ms")
    assert ads_delta.classification == "BUFF"
    assert ads_delta.delta == -15.0
