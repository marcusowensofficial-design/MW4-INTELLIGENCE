"""
Unit and Integration Tests for MW4 Gunsmith Attachment Isolation & Real-Time Performance Fidelity.
Ensures 1:1 in-game weapon attachment restrictions, slot coverage (Ammunition, Rear Grip, Magazine, etc.),
and accurate stat delta calculations against baseline.
"""

import pytest
from src.database.connection import db_manager
from src.database.repository import IntelligenceRepository
from src.engines.attachment_engine import calculate_modified_stats, validate_build_legality
from src.database.models import AttachmentSlot


@pytest.fixture
def repo():
    return IntelligenceRepository(db_manager)


def test_m4_attachment_isolation_and_slot_coverage(repo):
    """Verify that M4 only displays M4-compatible attachments across all 9 primary slots."""
    m4_atts = repo.get_attachments(weapon_id="m4_mw4")
    assert len(m4_atts) == 69, f"Expected 69 attachments for M4, got {len(m4_atts)}"

    # Check slot presence
    slots_present = {a.slot for a in m4_atts}
    assert AttachmentSlot.MUZZLE in slots_present
    assert AttachmentSlot.BARREL in slots_present
    assert AttachmentSlot.LASER in slots_present
    assert AttachmentSlot.OPTIC in slots_present
    assert AttachmentSlot.STOCK in slots_present
    assert AttachmentSlot.UNDERBARREL in slots_present
    assert AttachmentSlot.MAGAZINE in slots_present
    assert AttachmentSlot.AMMUNITION in slots_present
    assert AttachmentSlot.REAR_GRIP in slots_present

    # Verify magazines
    magazines = [a.name for a in m4_atts if a.slot == AttachmentSlot.MAGAZINE]
    assert "45 Round Mag" in magazines
    assert "60 Round Drum" in magazines

    # Verify rear grips
    rear_grips = [a.name for a in m4_atts if a.slot == AttachmentSlot.REAR_GRIP]
    assert "Schlager STB Grip" in rear_grips
    assert "Brace DX Grip" in rear_grips
    assert "ZLR Phase Grip" in rear_grips

    # Verify ammunition
    ammo = [a.name for a in m4_atts if a.slot == AttachmentSlot.AMMUNITION]
    assert any("5.56" in name for name in ammo)


def test_handgun_isolation(repo):
    """Verify .50 GS only displays handgun attachments and does NOT contain rifle stocks."""
    gs50_atts = repo.get_attachments(weapon_id="gs50_mw4")
    assert len(gs50_atts) > 0

    slots_present = {a.slot for a in gs50_atts}
    # .50 GS does not have rifle stocks
    assert AttachmentSlot.STOCK not in slots_present

    # Handgun has magazines and rear grips
    mags = [a.name for a in gs50_atts if a.slot == AttachmentSlot.MAGAZINE]
    assert len(mags) > 0
    assert any("14 Round" in m or "Drum" in m for m in mags)

    grips = [a.name for a in gs50_atts if a.slot == AttachmentSlot.REAR_GRIP]
    assert len(grips) > 0


def test_cross_weapon_isolation_no_leakage(repo):
    """Verify M4 exclusive barrel does not leak into .50 GS or Sniper rifles."""
    m4_atts = repo.get_attachments(weapon_id="m4_mw4")
    gs50_atts = repo.get_attachments(weapon_id="gs50_mw4")
    sig50_atts = repo.get_attachments(weapon_id="signal50_mw4")

    m4_att_ids = {a.attachment_id for a in m4_atts}
    gs50_att_ids = {a.attachment_id for a in gs50_atts}
    sig50_att_ids = {a.attachment_id for a in sig50_atts}

    # 18" LE Crosswind is an M4 barrel
    assert "18_le_crosswind" in m4_att_ids
    assert "18_le_crosswind" not in gs50_att_ids
    assert "18_le_crosswind" not in sig50_att_ids


def test_modified_build_performance_delta_updating(repo):
    """Verify that equipping attachments modifies performance stats with real deltas."""
    weapon = repo.get_weapon("m4_mw4")
    base_stats = repo.get_weapon_stats("m4_mw4", "v1.3.0-launch")
    profiles = repo.get_damage_profiles("m4_mw4", "v1.3.0-launch", "core")
    ruleset = repo.get_ruleset("core")
    all_mods = repo.get_attachment_modifiers("v1.3.0-launch")

    m4_atts_map = {a.name: a for a in repo.get_attachments("m4_mw4")}
    mag45 = m4_atts_map["45 Round Mag"]
    barrel18 = m4_atts_map["18\" LE Crosswind"]
    reverb = m4_atts_map["ZLR Reverb90"]

    baseline = calculate_modified_stats(weapon, base_stats, [], all_mods, ruleset, profiles)
    modified = calculate_modified_stats(weapon, base_stats, [mag45, barrel18, reverb], all_mods, ruleset, profiles)

    # Magazine capacity delta
    assert baseline.effective_mag_size == 30
    assert modified.effective_mag_size == 45

    # ADS delta (barrel and mag add aim latency)
    assert modified.effective_ads_ms > baseline.effective_ads_ms

    # Bullet velocity delta (18" Crosswind increases velocity)
    assert modified.effective_bullet_velocity_mps > baseline.effective_bullet_velocity_mps

    # Recoil index delta (ZLR Reverb90 and 18" Crosswind reduce recoil)
    assert modified.recoil_index < baseline.recoil_index

    # Effective range delta (+24% range)
    assert modified.range_multiplier > 1.20
