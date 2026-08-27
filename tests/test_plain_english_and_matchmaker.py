"""
Unit Tests for Plain-English Intelligence, Star Ratings, and Tactical Matchmaker
"""

import pytest
from src.ui.plain_english import (
    get_weapon_plain_summary,
    get_weapon_star_ratings,
    get_attachment_plain_effects,
    get_matchmaker_recommendation,
    WEAPON_PLAIN_DOSSIERS
)
from src.database.models import WeaponClass, WeaponVersionStats


def test_get_weapon_plain_summary_known_weapons():
    """Verify curated dossiers are returned for key weapons and aliases."""
    xm4_dossier = get_weapon_plain_summary("xm4_mw4")
    assert "Laser Beam" in xm4_dossier["role_title"]
    assert len(xm4_dossier["summary"]) > 10

    rival_dossier = get_weapon_plain_summary("rival9_mw4")
    assert "SMG" in rival_dossier["role_title"]
    assert "close-quarters" in rival_dossier["summary"]


def test_get_weapon_plain_summary_dynamic_stats():
    """Verify dynamic physical recoil ease calculation from stats object."""
    laser_stats = WeaponVersionStats(
        stat_id="laser_v1", weapon_id="laser_gun", game_version_id="v1.0.0",
        rpm=800.0, base_ads_ms=200.0, sprint_to_fire_ms=150.0, bullet_velocity_mps=800.0,
        reload_tactical_s=2.0, reload_empty_s=2.5,
        recoil_horizontal=8.0, recoil_vertical=12.0, # sum = 20 <= 28
        hipfire_spread_deg=3.0, move_speed_mps=5.0, ads_move_speed_mps=3.0
    )
    doss_laser = get_weapon_plain_summary("custom_gun", stats=laser_stats)
    assert doss_laser["ease_rating"] == 5
    assert "Zero Kick" in doss_laser["ease_label"]

    kick_stats = WeaponVersionStats(
        stat_id="kick_v1", weapon_id="kick_gun", game_version_id="v1.0.0",
        rpm=600.0, base_ads_ms=280.0, sprint_to_fire_ms=240.0, bullet_velocity_mps=700.0,
        reload_tactical_s=2.5, reload_empty_s=3.0,
        recoil_horizontal=30.0, recoil_vertical=50.0, # sum = 80 > 65
        hipfire_spread_deg=4.5, move_speed_mps=4.5, ads_move_speed_mps=2.5
    )
    doss_kick = get_weapon_plain_summary("custom_heavy", stats=kick_stats)
    assert doss_kick["ease_rating"] == 1
    assert "Severe Kick" in doss_kick["ease_label"]


def test_get_weapon_plain_summary_fallback():
    """Verify uncataloged weapons get a clean, valid fallback dossier."""
    fallback = get_weapon_plain_summary("custom_prototype_x", "Prototype X", "assault_rifle")
    assert "Prototype X" in fallback["summary"]
    assert fallback["ease_rating"] >= 3
    assert "role_title" in fallback


def test_get_weapon_star_ratings():
    """Verify dynamic 1-5 star ratings calculation from physical stats."""
    fast_stats = WeaponVersionStats(
        stat_id="test_fast_v1",
        weapon_id="test_fast",
        game_version_id="v1.0.0",
        rpm=900.0,
        base_ads_ms=180.0,
        sprint_to_fire_ms=120.0,
        bullet_velocity_mps=950.0,
        reload_tactical_s=1.8,
        reload_empty_s=2.2,
        recoil_horizontal=8.0,
        recoil_vertical=16.0,
        hipfire_spread_deg=3.5,
        move_speed_mps=6.8,
        ads_move_speed_mps=3.4
    )
    stars = get_weapon_star_ratings(fast_stats, WeaponClass.SUBMACHINE_GUN)
    assert stars["kill_speed"][0] == 5
    assert stars["ease_of_control"][0] == 5
    assert stars["quick_aim_speed"][0] == 5
    assert stars["long_range_power"][0] == 5

    heavy_stats = WeaponVersionStats(
        stat_id="test_heavy_v1",
        weapon_id="test_heavy",
        game_version_id="v1.0.0",
        rpm=550.0,
        base_ads_ms=380.0,
        sprint_to_fire_ms=280.0,
        bullet_velocity_mps=500.0,
        reload_tactical_s=3.5,
        reload_empty_s=4.5,
        recoil_horizontal=30.0,
        recoil_vertical=45.0,
        hipfire_spread_deg=6.0,
        move_speed_mps=5.0,
        ads_move_speed_mps=2.0
    )
    stars_heavy = get_weapon_star_ratings(heavy_stats, WeaponClass.LIGHT_MACHINE_GUN)
    assert stars_heavy["kill_speed"][0] == 3
    assert stars_heavy["ease_of_control"][0] == 2
    assert stars_heavy["quick_aim_speed"][0] == 2
    assert stars_heavy["long_range_power"][0] == 2


def test_get_attachment_plain_effects():
    """Verify attachment strings are translated into clear gameplay benefits."""
    suppressor_effs = get_attachment_plain_effects("muzzle_vt7_spiritfire", "VT-7 Spiritfire Suppressor")
    assert any("radar" in e.lower() for e in suppressor_effs)

    grip_effs = get_attachment_plain_effects("underbarrel_bruen_heavy_grip", "Bruen Heavy Support Grip")
    assert any("recoil" in e.lower() or "shake" in e.lower() for e in grip_effs)

    mag_effs = get_attachment_plain_effects("mag_40_round", "40-Round Mag")
    assert any("bullets" in e.lower() or "ammo" in e.lower() for e in mag_effs)

    optic_effs = get_attachment_plain_effects("optic_slate_reflector", "Slate Reflector")
    assert any("red dot" in e.lower() or "track" in e.lower() for e in optic_effs)


def test_tactical_matchmaker_recommendations():
    """Verify Tactical Arsenal Matchmaker handles all playstyle variations."""
    # 1. Zero Recoil
    rec_laser = get_matchmaker_recommendation(
        playstyle_choice="🎯 Zero-Kick Laser Beam (Easy Control / Minimal Recoil)",
        distance_choice="🗺️ Standard 6v6 Multiplayer (15m - 35m Mid-Range)",
        control_pref="🟢 Maximum Stability & Forgiving Aim (Easiest to Control)"
    )
    assert rec_laser["weapon_id"] == "xm4"
    assert len(rec_laser["attachments"]) == 5
    assert len(rec_laser["why_it_works"]) > 10
    assert len(rec_laser["combat_tip"]) > 5

    # 2. Aggressive CQB Rusher
    rec_cqb = get_matchmaker_recommendation(
        playstyle_choice="⚡ Aggressive CQB Rusher (Run & Gun / Slide-Canceling)",
        distance_choice="🏃 Close Quarters / Small Maps (0m - 15m Point Blank)",
        control_pref="⚡ Super Fast Scope-In & Sprint Reaction Speed"
    )
    assert rec_cqb["weapon_id"] == "rival_9"
    assert len(rec_cqb["attachments"]) == 5

    # 3. Heavy Punch Battle Rifle
    rec_heavy = get_matchmaker_recommendation(
        playstyle_choice="💥 Heavy Punch / Max Impact (High Stopping Power)",
        distance_choice="🗺️ Standard 6v6 Multiplayer (15m - 35m Mid-Range)",
        control_pref="🟢 Maximum Stability & Forgiving Aim (Easiest to Control)"
    )
    assert rec_heavy["weapon_id"] == "bas_b"
    assert len(rec_heavy["attachments"]) == 5
