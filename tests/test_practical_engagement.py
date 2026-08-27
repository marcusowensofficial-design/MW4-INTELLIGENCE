"""
Unit tests for Practical Engagement Time (PET) Engine.
"""

import pytest
from src.engines.engagement_engine import (
    calculate_expected_miss_penalty_ms,
    calculate_practical_engagement_time
)


def test_miss_penalty_100_percent_accuracy():
    # 100% accuracy -> 0 miss penalty
    penalty = calculate_expected_miss_penalty_ms(stk=4, rpm=750.0, accuracy=1.0)
    assert penalty == 0.0


def test_miss_penalty_50_percent_accuracy():
    # 4 STK at 600 RPM (100ms per shot) with 50% accuracy:
    # expected misses = 4 * ((1 - 0.5) / 0.5) = 4 missed shots
    # penalty = 4 * 100ms = 400.0 ms
    penalty = calculate_expected_miss_penalty_ms(stk=4, rpm=600.0, accuracy=0.50)
    assert pytest.approx(penalty, 0.01) == 400.0


def test_practical_engagement_sprint_encounter():
    # reaction=200, ads=240, stf=200, ttk=240, stk=4, rpm=750 (80ms/shot), acc=1.0 (0 miss)
    # PET = 200 + 240 + 200 + 240 + 0 = 880.0 ms
    res = calculate_practical_engagement_time(
        reaction_ms=200.0,
        ads_ms=240.0,
        sprint_to_fire_ms=200.0,
        theoretical_ttk_ms=240.0,
        stk=4,
        rpm=750.0,
        accuracy=1.0,
        is_sprinting=True,
        is_already_ads=False
    )
    assert res.practical_engagement_time_ms == 880.0
    assert res.ads_ms == 240.0
    assert res.sprint_to_fire_ms == 200.0


def test_practical_engagement_already_ads():
    # Already ADS -> ADS=0, STF=0
    # PET = 200 + 0 + 0 + 240 + 0 = 440.0 ms
    res = calculate_practical_engagement_time(
        reaction_ms=200.0,
        ads_ms=240.0,
        sprint_to_fire_ms=200.0,
        theoretical_ttk_ms=240.0,
        stk=4,
        rpm=750.0,
        accuracy=1.0,
        is_sprinting=False,
        is_already_ads=True
    )
    assert res.practical_engagement_time_ms == 440.0
    assert res.ads_ms == 0.0
    assert res.sprint_to_fire_ms == 0.0
