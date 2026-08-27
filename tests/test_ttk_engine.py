"""
Unit tests for MW4 TTK and Ballistics Calculation Engine.
"""

import pytest
from src.engines.ttk_engine import (
    calculate_shots_to_kill,
    calculate_theoretical_ttk_ms,
    get_damage_at_distance,
    generate_ttk_curve
)
from src.database.models import (
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Ruleset,
    WeaponClass,
    FiringMode
)


def test_stk_calculation_core():
    # 100 HP, 30 damage per shot -> ceil(100/30) = 4 shots
    stk = calculate_shots_to_kill(target_health=100.0, damage_per_shot=30.0)
    assert stk == 4


def test_stk_calculation_exact_division():
    # 100 HP, 25 damage per shot -> 4 shots
    stk = calculate_shots_to_kill(target_health=100.0, damage_per_shot=25.0)
    assert stk == 4


def test_stk_calculation_hardcore_1shot():
    # 30 HP, 35 damage per shot -> 1 shot
    stk = calculate_shots_to_kill(target_health=30.0, damage_per_shot=35.0)
    assert stk == 1


def test_stk_calculation_hardcore_2shot():
    # 30 HP, 28 damage per shot -> 2 shots
    stk = calculate_shots_to_kill(target_health=30.0, damage_per_shot=28.0)
    assert stk == 2


def test_ttk_calculation_full_auto():
    # 4 STK at 750 RPM: (4 - 1) * 60000 / 750 = 3 * 80ms = 240.0 ms
    ttk = calculate_theoretical_ttk_ms(stk=4, rpm=750.0)
    assert pytest.approx(ttk, 0.01) == 240.0


def test_ttk_calculation_1shot_zero_ms():
    # 1 STK should yield instant 0.0 ms TTK
    ttk = calculate_theoretical_ttk_ms(stk=1, rpm=900.0)
    assert ttk == 0.0


def test_ttk_calculation_burst_weapon():
    # 3-round burst at 600 cyclic RPM with 120ms burst delay
    # If 3 STK (1 burst): (3 - 1) * (60000/600) + 0 delays = 2 * 100ms = 200.0 ms
    ttk_1burst = calculate_theoretical_ttk_ms(stk=3, rpm=600.0, burst_count=3, burst_delay_ms=120.0)
    assert pytest.approx(ttk_1burst, 0.01) == 200.0

    # If 4 STK (requires 2nd burst): 3 intra-burst shots (300ms) + 1 burst delay (120ms) = 420.0 ms
    ttk_2burst = calculate_theoretical_ttk_ms(stk=4, rpm=600.0, burst_count=3, burst_delay_ms=120.0)
    assert pytest.approx(ttk_2burst, 0.01) == 420.0


def test_damage_at_distance_brackets():
    profiles = [
        DamageRangeBracket(
            profile_id="p1", weapon_id="test", game_version_id="v1",
            ruleset_id="core", range_start_m=0.0, range_end_m=25.0,
            damage_head=40.0, damage_neck=35.0, damage_chest=30.0, damage_stomach=28.0, damage_limbs=25.0
        ),
        DamageRangeBracket(
            profile_id="p2", weapon_id="test", game_version_id="v1",
            ruleset_id="core", range_start_m=25.0, range_end_m=50.0,
            damage_head=35.0, damage_neck=30.0, damage_chest=25.0, damage_stomach=23.0, damage_limbs=20.0
        )
    ]

    # At 10m (Bracket 1)
    dmg_10m = get_damage_at_distance(10.0, profiles, hit_location="chest")
    assert dmg_10m == 30.0

    # At 35m (Bracket 2)
    dmg_35m = get_damage_at_distance(35.0, profiles, hit_location="chest")
    assert dmg_35m == 25.0

    # With +20% range multiplier, Bracket 1 extends from 25m to 30m
    dmg_28m_extended = get_damage_at_distance(28.0, profiles, hit_location="chest", range_multiplier=1.20)
    assert dmg_28m_extended == 30.0


def test_generate_ttk_curve_generation():
    weapon = Weapon(
        weapon_id="test_ar", name="Test AR", weapon_class=WeaponClass.ASSAULT_RIFLE,
        firing_mode=FiringMode.FULL_AUTO, default_rpm=800.0, base_mag_size=30
    )
    stats = WeaponVersionStats(
        stat_id="test_stat", weapon_id="test_ar", game_version_id="v1",
        rpm=800.0, base_ads_ms=220.0, sprint_to_fire_ms=190.0, bullet_velocity_mps=700.0,
        reload_empty_s=2.2, reload_tactical_s=1.8, recoil_horizontal=15.0, recoil_vertical=22.0,
        hipfire_spread_deg=3.5, move_speed_mps=4.8, ads_move_speed_mps=2.9
    )
    profiles = [
        DamageRangeBracket(
            profile_id="p1", weapon_id="test_ar", game_version_id="v1",
            ruleset_id="core", range_start_m=0.0, range_end_m=30.0,
            damage_head=42.0, damage_neck=36.0, damage_chest=34.0, damage_stomach=30.0, damage_limbs=26.0
        ),
        DamageRangeBracket(
            profile_id="p2", weapon_id="test_ar", game_version_id="v1",
            ruleset_id="core", range_start_m=30.0, range_end_m=80.0,
            damage_head=35.0, damage_neck=30.0, damage_chest=26.0, damage_stomach=24.0, damage_limbs=22.0
        )
    ]
    ruleset = Ruleset(ruleset_id="core", name="Core 100 HP", target_health=100.0)

    result = generate_ttk_curve(weapon, stats, profiles, ruleset, hit_location="chest", max_distance_m=50.0)

    assert len(result.curve_points) == 51  # 0 to 50m with 1m step
    assert result.curve_points[0].shots_to_kill == 3  # ceil(100/34) = 3
    assert pytest.approx(result.curve_points[0].ttk_ms, 0.1) == 150.0  # (3-1)*60000/800 = 150ms
    assert result.curve_points[40].shots_to_kill == 4  # ceil(100/26) = 4
    assert pytest.approx(result.curve_points[40].ttk_ms, 0.1) == 225.0  # (4-1)*60000/800 = 225ms
    # Check impact TTK has travel time added
    assert result.curve_points[40].bullet_travel_time_ms > 0
    assert result.curve_points[40].impact_ttk_ms > result.curve_points[40].ttk_ms


def test_open_bolt_delay_ttk():
    # 4 STK at 600 RPM with 50ms Open-Bolt Delay
    # Base TTK: (4 - 1) * (60000/600) = 300ms + 50ms OBD = 350ms
    ttk_obd = calculate_theoretical_ttk_ms(stk=4, rpm=600.0, open_bolt_delay_ms=50.0)
    assert pytest.approx(ttk_obd, 0.01) == 350.0


def test_headshot_stk_reduction_threshold():
    from src.engines.ttk_engine import calculate_headshots_for_stk_reduction
    # 100 HP, 30 body damage (4 STK). Head damage is 40.
    # 1 head (40) + 2 body (60) = 100 dmg in 3 shots (3 STK) -> 1 headshot reduces STK from 4 to 3!
    hs_req = calculate_headshots_for_stk_reduction(target_health=100.0, body_damage=30.0, head_damage=40.0)
    assert hs_req == 1
