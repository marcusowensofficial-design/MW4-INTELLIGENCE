"""
Unit tests for Gunsmith Build Legality and Constraint Verification.
"""

import pytest
from src.database.models import Weapon, Attachment, AttachmentSlot, WeaponClass, FiringMode
from src.engines.attachment_engine import validate_build_legality


@pytest.fixture
def mock_weapon():
    return Weapon(
        weapon_id="xm4_mw4", name="XM4", weapon_class=WeaponClass.ASSAULT_RIFLE,
        firing_mode=FiringMode.FULL_AUTO, default_rpm=780.0, base_mag_size=30
    )


def test_legal_5_attachment_build(mock_weapon):
    attachments = [
        Attachment(attachment_id="m1", name="Muzzle Brake", slot=AttachmentSlot.MUZZLE),
        Attachment(attachment_id="b1", name="Long Barrel", slot=AttachmentSlot.BARREL),
        Attachment(attachment_id="o1", name="Reflex Optic", slot=AttachmentSlot.OPTIC),
        Attachment(attachment_id="u1", name="Angled Grip", slot=AttachmentSlot.UNDERBARREL),
        Attachment(attachment_id="mg1", name="40-Round Mag", slot=AttachmentSlot.MAGAZINE)
    ]
    is_legal, error = validate_build_legality(mock_weapon, attachments)
    assert is_legal is True
    assert error is None


def test_illegal_exceeds_5_slots(mock_weapon):
    attachments = [
        Attachment(attachment_id="m1", name="Muzzle Brake", slot=AttachmentSlot.MUZZLE),
        Attachment(attachment_id="b1", name="Long Barrel", slot=AttachmentSlot.BARREL),
        Attachment(attachment_id="o1", name="Reflex Optic", slot=AttachmentSlot.OPTIC),
        Attachment(attachment_id="u1", name="Angled Grip", slot=AttachmentSlot.UNDERBARREL),
        Attachment(attachment_id="mg1", name="40-Round Mag", slot=AttachmentSlot.MAGAZINE),
        Attachment(attachment_id="s1", name="Tactical Stock", slot=AttachmentSlot.STOCK) # 6th attachment
    ]
    is_legal, error = validate_build_legality(mock_weapon, attachments)
    assert is_legal is False
    assert "Exceeds maximum attachment limit" in error


def test_illegal_duplicate_slot(mock_weapon):
    # Two muzzles equipped
    attachments = [
        Attachment(attachment_id="m1", name="Muzzle Brake", slot=AttachmentSlot.MUZZLE),
        Attachment(attachment_id="m2", name="Flash Hider", slot=AttachmentSlot.MUZZLE)
    ]
    is_legal, error = validate_build_legality(mock_weapon, attachments)
    assert is_legal is False
    assert "Duplicate slot conflict" in error


def test_illegal_incompatible_weapon(mock_weapon):
    # Attachment exclusive to rival9
    incompat_att = Attachment(
        attachment_id="rival_barrel", name="Rival Exclusive Barrel",
        slot=AttachmentSlot.BARREL, is_universal=False, weapon_id_compat="rival9_mw4"
    )
    is_legal, error = validate_build_legality(mock_weapon, [incompat_att])
    assert is_legal is False
    assert "not compatible with weapon" in error
