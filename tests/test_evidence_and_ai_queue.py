"""
Unit tests for Evidence Provenance, AI Review Queue Quarantine, and Promotion Workflows.
"""

import pytest
from src.database.connection import DatabaseManager
from src.database.repository import IntelligenceRepository
from src.database.models import (
    Weapon,
    WeaponVersionStats,
    WeaponClass,
    FiringMode,
    EvidenceLedgerEntry,
    SourceTier,
    VerificationStatus
)
from src.ingestion.ai_gatekeeper import (
    submit_ai_claim_to_review_queue,
    promote_ai_claim_to_verified,
    reject_ai_claim
)
from src.engines.confidence_scorer import calculate_evidence_confidence


@pytest.fixture
def ephemeral_gatekeeper_repo():
    mgr = DatabaseManager(db_path=":memory:")
    mgr.init_database()
    repo = IntelligenceRepository(mgr)

    repo.upsert_weapon(
        Weapon(
            weapon_id="test_sniper", name="Test Sniper", weapon_class=WeaponClass.SNIPER_RIFLE,
            firing_mode=FiringMode.BOLT_ACTION, default_rpm=60.0, base_mag_size=5
        )
    )
    repo.upsert_weapon_stats(
        WeaponVersionStats(
            stat_id="sniper_v1", weapon_id="test_sniper", game_version_id="v1.0.0",
            rpm=60.0, base_ads_ms=480.0, sprint_to_fire_ms=350.0, bullet_velocity_mps=900.0,
            reload_empty_s=3.5, reload_tactical_s=2.8, recoil_horizontal=10.0, recoil_vertical=50.0,
            hipfire_spread_deg=6.0, move_speed_mps=4.3, ads_move_speed_mps=1.8
        )
    )
    return repo


def test_ai_claim_quarantine_isolation(ephemeral_gatekeeper_repo):
    repo = ephemeral_gatekeeper_repo

    # Submit an unverified AI claim proposing 440ms ADS
    payload = {"weapon_id": "test_sniper", "base_ads_ms": 440.0}
    queue_id = submit_ai_claim_to_review_queue(
        proposed_payload=payload,
        ai_model="Claude-Vision-OCR",
        confidence_claim=0.70,
        rationale="Extracted from livestream clip",
        repo=repo
    )

    # 1. Verify item is in review queue as pending
    pending = repo.get_ai_review_queue(status="pending")
    assert len(pending) == 1
    assert pending[0].queue_id == queue_id

    # 2. Strict check: Verified database table MUST NOT be modified!
    verified_stats = repo.get_weapon_stats("test_sniper", "v1.0.0")
    assert verified_stats.base_ads_ms == 480.0  # Still original 480ms


def test_ai_claim_promotion_workflow(ephemeral_gatekeeper_repo):
    repo = ephemeral_gatekeeper_repo

    payload = {"weapon_id": "test_sniper", "base_ads_ms": 440.0}
    queue_id = submit_ai_claim_to_review_queue(
        proposed_payload=payload,
        ai_model="Claude-Vision-OCR",
        confidence_claim=0.90,
        rationale="Frame timing audited by human",
        repo=repo
    )

    # Human analyst promotes claim
    success, msg = promote_ai_claim_to_verified(
        queue_id=queue_id,
        reviewer_name="Lead_Analyst_Alex",
        target_version_id="v1.0.0",
        repo=repo
    )
    assert success is True

    # 1. Verified stats should now reflect updated value
    updated_stats = repo.get_weapon_stats("test_sniper", "v1.0.0")
    assert updated_stats.base_ads_ms == 440.0

    # 2. Verified evidence ledger entry must be recorded
    ev_entries = repo.get_evidence_ledger(target_entity_id="test_sniper")
    assert len(ev_entries) >= 1
    assert "Lead_Analyst_Alex" in ev_entries[0].test_method

    # 3. Queue item status updated to approved
    approved = repo.get_ai_review_queue(status="approved")
    assert len(approved) == 1


def test_ai_claim_rejection(ephemeral_gatekeeper_repo):
    repo = ephemeral_gatekeeper_repo

    payload = {"weapon_id": "test_sniper", "base_ads_ms": 300.0}
    queue_id = submit_ai_claim_to_review_queue(
        proposed_payload=payload,
        ai_model="Unverified-Community-Scraper",
        confidence_claim=0.30,
        rationale="Claimed massive buff",
        repo=repo
    )

    success, msg = reject_ai_claim(
        queue_id=queue_id,
        reviewer_name="Analyst_Bob",
        rejection_reason="Contradicts frame tests",
        repo=repo
    )
    assert success is True

    rejected = repo.get_ai_review_queue(status="rejected")
    assert len(rejected) == 1
    assert rejected[0].rejection_reason == "Contradicts frame tests"


def test_confidence_scoring_weights():
    # Tier 1 entry (98%) vs Tier 4 entry (40%)
    entry_t1 = EvidenceLedgerEntry(
        evidence_id="e1", target_entity_type="weapon", target_entity_id="w1",
        field_name="rpm", observed_value=800.0, source_url="https://callofduty.com",
        source_name="Official Patch", source_tier=SourceTier.TIER_1,
        test_method="Official Notes", verification_status=VerificationStatus.VERIFIED,
        confidence_score=0.99
    )
    entry_t4 = EvidenceLedgerEntry(
        evidence_id="e2", target_entity_type="weapon", target_entity_id="w1",
        field_name="rpm", observed_value=800.0, source_url="local://ai",
        source_name="AI Draft", source_tier=SourceTier.TIER_4,
        test_method="OCR", verification_status=VerificationStatus.PENDING_REVIEW,
        confidence_score=0.50
    )

    conf_t1 = calculate_evidence_confidence([entry_t1])
    conf_t4 = calculate_evidence_confidence([entry_t4])

    assert conf_t1 > 0.90
    assert conf_t4 < 0.30
