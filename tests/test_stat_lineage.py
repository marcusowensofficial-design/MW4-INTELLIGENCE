"""
Unit tests for Chronological Stat Lineage and Patch Walk Engine.
"""

import pytest
from src.engines.stat_lineage_engine import reconstruct_stat_lineage, audit_weapon_patch_continuity
from src.database.models import StatDeltaEvent


def test_stat_lineage_sequential_reconstruction():
    events = [
        StatDeltaEvent(
            event_id="e1",
            weapon_id="test_gun",
            stat_name="damage_chest",
            patch_version_id="v1.0.0",
            effective_date="2026-08-08",
            previous_value=33.0,
            delta_type="DELTA_ADD",
            delta_value=-3.0,
            new_value=30.0,
            official_patch_url="https://test.com",
            developer_notes="Reduced close damage from 33 to 30",
            captured_timestamp="2026-08-08T12:00:00Z"
        ),
        StatDeltaEvent(
            event_id="e2",
            weapon_id="test_gun",
            stat_name="damage_chest",
            patch_version_id="v1.0.1",
            effective_date="2026-08-15",
            previous_value=30.0,
            delta_type="DELTA_ADD",
            delta_value=2.0,
            new_value=32.0,
            official_patch_url="https://test.com",
            developer_notes="Raised damage back to 32",
            captured_timestamp="2026-08-15T12:00:00Z"
        )
    ]

    # Test full reconstruction to latest
    res_latest = reconstruct_stat_lineage(events, "test_gun", "damage_chest")
    assert res_latest.baseline_value == 33.0
    assert res_latest.reconstructed_value == 32.0
    assert res_latest.total_patches_applied == 2
    assert res_latest.is_continuity_verified is True

    # Test time-machine cutoff as of 2026-08-10 (only first patch applied)
    res_aug10 = reconstruct_stat_lineage(events, "test_gun", "damage_chest", target_date="2026-08-10")
    assert res_aug10.baseline_value == 33.0
    assert res_aug10.reconstructed_value == 30.0
    assert res_aug10.total_patches_applied == 1


def test_stat_lineage_gap_detection():
    # Event with an invalid previous_value (should fail continuity check)
    events_broken = [
        StatDeltaEvent(
            event_id="e1",
            weapon_id="test_gun",
            stat_name="rpm",
            patch_version_id="v1.0.0",
            effective_date="2026-08-08",
            previous_value=700.0,
            delta_type="DELTA_ADD",
            delta_value=50.0,
            new_value=750.0,
            official_patch_url="https://test.com",
            developer_notes="Buffed RPM",
            captured_timestamp="2026-08-08T12:00:00Z"
        ),
        StatDeltaEvent(
            event_id="e2",
            weapon_id="test_gun",
            stat_name="rpm",
            patch_version_id="v1.0.1",
            effective_date="2026-08-15",
            previous_value=600.0, # MISMATCH! (Expected 750.0)
            delta_type="DELTA_ADD",
            delta_value=20.0,
            new_value=620.0,
            official_patch_url="https://test.com",
            developer_notes="Conflicting baseline",
            captured_timestamp="2026-08-15T12:00:00Z"
        )
    ]

    res = reconstruct_stat_lineage(events_broken, "test_gun", "rpm")
    assert res.is_continuity_verified is False


def test_audit_weapon_patch_continuity():
    events = [
        StatDeltaEvent(
            event_id="e1", weapon_id="xm4_test", stat_name="recoil_vertical",
            patch_version_id="v1.0.0", effective_date="2026-08-08",
            previous_value=28.0, delta_type="DELTA_ADD", delta_value=-2.8, new_value=25.2,
            official_patch_url="https://test.com", developer_notes="Recoil buff", captured_timestamp="2026-08-08T12:00:00Z"
        )
    ]
    report = audit_weapon_patch_continuity(events, "xm4_test")
    assert report["all_continuous"] is True
    assert report["total_patch_events"] == 1
    assert "recoil_vertical" in report["stat_breakdown"]
