"""
Unit tests for the Automated Database Promotion & Guardrail Engine.
"""

import pytest
from src.ingestion.auto_promotion_engine import validate_stat_guardrails, parse_and_auto_apply_patch_adjustments
from src.database.connection import db_manager
from src.database.repository import IntelligenceRepository


def test_validate_stat_guardrails_within_bounds():
    is_valid, msg = validate_stat_guardrails("bullet_velocity_mps", 700.0, 750.0)
    assert is_valid is True

    is_valid, msg = validate_stat_guardrails("base_ads_ms", 220.0, 210.0)
    assert is_valid is True

    is_valid, msg = validate_stat_guardrails("damage_chest", 30.0, 28.0)
    assert is_valid is True


def test_validate_stat_guardrails_out_of_bounds():
    # Negative damage
    is_valid, msg = validate_stat_guardrails("damage_chest", 30.0, -10.0)
    assert is_valid is False
    assert "Guardrail Violation" in msg

    # Insane RPM (e.g. 9999 RPM)
    is_valid, msg = validate_stat_guardrails("rpm", 800.0, 9999.0)
    assert is_valid is False
    assert "Guardrail Violation" in msg


def test_validate_stat_guardrails_excessive_delta():
    # 80% single-patch damage buff (should be flagged as corrupted scrape)
    is_valid, msg = validate_stat_guardrails("damage_chest", 30.0, 58.0)
    assert is_valid is False
    assert "Plausibility Guardrail" in msg


def test_parse_and_auto_apply_patch_adjustments_success():
    from src.database.connection import DatabaseManager
    from src.database.seed_data import seed_database
    db = DatabaseManager(":memory:")
    seed_database(db)
    repo = IntelligenceRepository(db)
    adjustments = [
        {"raw_text": "Patriot XMR Commando: Bullet velocity increased from 735m/s to 750m/s."}
    ]
    report = parse_and_auto_apply_patch_adjustments(
        adjustments=adjustments,
        source_url="https://callofduty.com/test",
        patch_version_id="v1.2.0-beta-weekend2",
        effective_date="2026-08-26",
        repo=repo
    )
    assert report["applied_count"] == 1
    assert report["rejected_count"] == 0

    # Verify stat was updated in DB
    stats = repo.get_weapon_stats("patriot_xmr_mw4", "v1.2.0-beta-weekend2")
    assert stats.bullet_velocity_mps > 0
