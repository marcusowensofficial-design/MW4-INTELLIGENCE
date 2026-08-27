"""
Unit tests for Attachment Stacking and Modifier Calculation Engine.
"""

import pytest
from src.database.models import (
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Attachment,
    AttachmentModifier,
    AttachmentSlot,
    ModifierType,
    Ruleset,
    WeaponClass,
    FiringMode
)
from src.engines.attachment_engine import calculate_modified_stats


@pytest.fixture
def mock_setup():
    weapon = Weapon(
        weapon_id="test_m4", name="Test M4", weapon_class=WeaponClass.ASSAULT_RIFLE,
        firing_mode=FiringMode.FULL_AUTO, default_rpm=800.0, base_mag_size=30
    )
    stats = WeaponVersionStats(
        stat_id="stat_m4", weapon_id="test_m4", game_version_id="v1.0.0",
        rpm=800.0, base_ads_ms=240.0, sprint_to_fire_ms=200.0, bullet_velocity_mps=700.0,
        reload_empty_s=2.4, reload_tactical_s=1.8, recoil_horizontal=20.0, recoil_vertical=30.0,
        hipfire_spread_deg=3.5, move_speed_mps=4.8, ads_move_speed_mps=2.8
    )
    profiles = [
        DamageRangeBracket(
            profile_id="p1", weapon_id="test_m4", game_version_id="v1.0.0",
            ruleset_id="core", range_start_m=0.0, range_end_m=30.0,
            damage_head=40.0, damage_neck=35.0, damage_chest=30.0, damage_stomach=28.0, damage_limbs=25.0
        )
    ]
    ruleset = Ruleset(ruleset_id="core", name="Core 100 HP", target_health=100.0)
    return weapon, stats, profiles, ruleset


def test_delta_modifier_application(mock_setup):
    weapon, stats, profiles, ruleset = mock_setup

    suppressor = Attachment(attachment_id="suppressor_1", name="Heavy Suppressor", slot=AttachmentSlot.MUZZLE)
    mods = [
        AttachmentModifier(
            mod_id="m1", attachment_id="suppressor_1", game_version_id="v1.0.0",
            stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=15.0
        )
    ]

    evaluated = calculate_modified_stats(weapon, stats, [suppressor], mods, ruleset, profiles)
    # 240ms + 15ms = 255ms ADS
    assert evaluated.effective_ads_ms == 255.0


def test_percentage_modifier_application(mock_setup):
    weapon, stats, profiles, ruleset = mock_setup

    comp = Attachment(attachment_id="comp_1", name="Compensator", slot=AttachmentSlot.MUZZLE)
    mods = [
        AttachmentModifier(
            mod_id="m2", attachment_id="comp_1", game_version_id="v1.0.0",
            stat_key="recoil_vertical", mod_type=ModifierType.PERCENTAGE, mod_value=-0.20
        )
    ]

    evaluated = calculate_modified_stats(weapon, stats, [comp], mods, ruleset, profiles)
    # 30.0 * (1 - 0.20) = 24.0 recoil vertical
    assert pytest.approx(evaluated.effective_recoil_vertical, 0.01) == 24.0


def test_stacking_multiple_attachments(mock_setup):
    weapon, stats, profiles, ruleset = mock_setup

    barrel = Attachment(attachment_id="barrel_1", name="Long Barrel", slot=AttachmentSlot.BARREL)
    laser = Attachment(attachment_id="laser_1", name="Speed Laser", slot=AttachmentSlot.LASER)

    mods = [
        AttachmentModifier(
            mod_id="m_b1", attachment_id="barrel_1", game_version_id="v1.0.0",
            stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=20.0
        ),
        AttachmentModifier(
            mod_id="m_b2", attachment_id="barrel_1", game_version_id="v1.0.0",
            stat_key="range_multiplier", mod_type=ModifierType.PERCENTAGE, mod_value=0.15
        ),
        AttachmentModifier(
            mod_id="m_l1", attachment_id="laser_1", game_version_id="v1.0.0",
            stat_key="base_ads_ms", mod_type=ModifierType.DELTA, mod_value=-15.0
        )
    ]

    evaluated = calculate_modified_stats(weapon, stats, [barrel, laser], mods, ruleset, profiles)
    # ADS: 240 + 20 - 15 = 245ms
    assert evaluated.effective_ads_ms == 245.0
    # Range: 1.0 + 0.15 = 1.15x
    assert pytest.approx(evaluated.range_multiplier, 0.01) == 1.15
