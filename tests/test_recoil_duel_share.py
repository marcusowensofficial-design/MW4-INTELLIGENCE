"""
Unit tests for 2D Recoil Simulation, 1v1 Duel Arena, and Loadout Share Codes.
"""

import pytest
from src.engines.recoil_engine import simulate_recoil_pattern
from src.engines.duel_engine import simulate_1v1_duel, DuelCombatant
from src.engines.share_code import encode_loadout_share_code, decode_loadout_share_code
from src.database.models import DamageRangeBracket, Ruleset


def test_recoil_simulation_basic():
    res = simulate_recoil_pattern(
        weapon_id="test_ar",
        weapon_name="Test AR",
        recoil_vertical=25.0,
        recoil_horizontal=15.0,
        rpm=750.0,
        magazine_size=30,
        vertical_modifier_pct=-20.0,
        horizontal_modifier_pct=-15.0,
        distance_m=10.0
    )

    assert res.total_shots == 30
    assert len(res.impacts) == 30
    assert res.max_vertical_climb_cm > 0.0
    assert res.max_horizontal_spread_cm > 0.0
    # First shot must be at center
    assert res.impacts[0].x_offset_cm == 0.0
    assert res.impacts[0].y_offset_cm == 0.0


def test_recoil_modifier_reduction():
    base_res = simulate_recoil_pattern(
        weapon_id="test_ar", weapon_name="Base",
        recoil_vertical=30.0, recoil_horizontal=20.0, rpm=750.0,
        vertical_modifier_pct=0.0, horizontal_modifier_pct=0.0
    )
    stabilized_res = simulate_recoil_pattern(
        weapon_id="test_ar", weapon_name="Tuned",
        recoil_vertical=30.0, recoil_horizontal=20.0, rpm=750.0,
        vertical_modifier_pct=-30.0, horizontal_modifier_pct=-30.0
    )

    assert stabilized_res.max_vertical_climb_cm < base_res.max_vertical_climb_cm


def test_1v1_duel_arena_simulation():
    profiles = [
        DamageRangeBracket(
            profile_id="p1", weapon_id="test_fast", game_version_id="v1", ruleset_id="core",
            range_start_m=0.0, range_end_m=50.0,
            damage_head=45.0, damage_neck=38.0, damage_chest=35.0, damage_stomach=30.0, damage_limbs=25.0
        )
    ]

    combatant_fast = DuelCombatant(
        name="Fast ADS Player",
        weapon_name="SMG",
        rpm=900.0,
        base_ads_ms=180.0,
        sprint_to_fire_ms=150.0,
        bullet_velocity_mps=650.0,
        profiles=profiles,
        reaction_ms=180.0,
        accuracy=0.85,
        is_sprinting=True
    )

    combatant_slow = DuelCombatant(
        name="Slow ADS Player",
        weapon_name="LMG",
        rpm=600.0,
        base_ads_ms=450.0,
        sprint_to_fire_ms=350.0,
        bullet_velocity_mps=800.0,
        open_bolt_delay_ms=50.0,
        profiles=profiles,
        reaction_ms=220.0,
        accuracy=0.70,
        is_sprinting=True
    )

    ruleset = Ruleset(ruleset_id="core", name="Core 100 HP", target_health=100.0)
    result = simulate_1v1_duel(combatant_fast, combatant_slow, distance_m=15.0, ruleset=ruleset)

    assert result.winner_name == "Fast ADS Player"
    assert result.winner_hp_remaining > 0
    assert result.time_to_kill_ms > 0
    assert len(result.combat_log) > 0


def test_loadout_share_code_bidirectional():
    weapon_id = "xm4_mw4"
    attachment_ids = ["att_compensator", "att_long_barrel", "att_extended_mag_45"]

    code = encode_loadout_share_code(
        weapon_id=weapon_id,
        attachment_ids=attachment_ids,
        game_version_id="v1.1.0-launch",
        ruleset_id="core",
        user_label="Meta AR Setup"
    )

    assert code.startswith("MW4-")

    success, decoded, msg = decode_loadout_share_code(code)
    assert success is True
    assert decoded is not None
    assert decoded.weapon_id == "xm4_mw4"
    assert len(decoded.attachment_ids) == 3
    assert "att_compensator" in decoded.attachment_ids
    assert decoded.user_label == "Meta AR Setup"


def test_loadout_share_code_invalid():
    success, decoded, msg = decode_loadout_share_code("INVALID-12345")
    assert success is False
    assert decoded is None
