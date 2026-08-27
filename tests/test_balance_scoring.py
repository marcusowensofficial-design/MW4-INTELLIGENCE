"""
Unit tests for Transparent Weapon Balance Scoring Engine.
"""

import pytest
from src.database.models import (
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Ruleset,
    WeaponClass,
    FiringMode
)
from src.engines.balance_scorer import calculate_balance_score, normalize_metric


@pytest.fixture
def mock_scoring_data():
    weapon = Weapon(
        weapon_id="mcw_test", name="MCW Test", weapon_class=WeaponClass.ASSAULT_RIFLE,
        firing_mode=FiringMode.FULL_AUTO, default_rpm=715.0, base_mag_size=30
    )
    stats = WeaponVersionStats(
        stat_id="mcw_stat", weapon_id="mcw_test", game_version_id="v1",
        rpm=715.0, base_ads_ms=230.0, sprint_to_fire_ms=200.0, bullet_velocity_mps=760.0,
        reload_empty_s=2.3, reload_tactical_s=1.75, recoil_horizontal=12.0, recoil_vertical=18.0,
        hipfire_spread_deg=3.5, move_speed_mps=4.9, ads_move_speed_mps=3.0
    )
    profiles = [
        DamageRangeBracket(
            profile_id="p1", weapon_id="mcw_test", game_version_id="v1",
            ruleset_id="core", range_start_m=0.0, range_end_m=35.0,
            damage_head=38.0, damage_neck=34.0, damage_chest=30.0, damage_stomach=27.0, damage_limbs=24.0
        ),
        DamageRangeBracket(
            profile_id="p2", weapon_id="mcw_test", game_version_id="v1",
            ruleset_id="core", range_start_m=35.0, range_end_m=80.0,
            damage_head=34.0, damage_neck=30.0, damage_chest=26.0, damage_stomach=24.0, damage_limbs=21.0
        )
    ]
    ruleset = Ruleset(ruleset_id="core", name="Core 100 HP", target_health=100.0)
    return weapon, stats, profiles, ruleset


def test_normalization_lower_is_better():
    # Best=100ms (100.0), Worst=300ms (0.0)
    # Val=200ms -> 50.0
    score = normalize_metric(val=200.0, best_val=100.0, worst_val=300.0)
    assert score == 50.0

    # Val=100ms -> 100.0
    assert normalize_metric(val=100.0, best_val=100.0, worst_val=300.0) == 100.0

    # Val=300ms -> 0.0
    assert normalize_metric(val=300.0, best_val=100.0, worst_val=300.0) == 0.0


def test_normalization_higher_is_better():
    # Best=60 (100.0), Worst=20 (0.0)
    # Val=40 -> 50.0
    score = normalize_metric(val=40.0, best_val=60.0, worst_val=20.0)
    assert score == 50.0


def test_balance_score_generation(mock_scoring_data):
    weapon, stats, profiles, ruleset = mock_scoring_data

    result = calculate_balance_score(weapon, stats, profiles, ruleset, confidence_score=0.95)

    assert 0.0 <= result.composite_balance_score <= 100.0
    assert result.tier_rating in ["S", "A", "B", "C", "D"]
    assert len(result.assumptions_log) >= 3
    assert result.confidence_score == 0.95
    assert "cqb_ttk" in result.weights_used
