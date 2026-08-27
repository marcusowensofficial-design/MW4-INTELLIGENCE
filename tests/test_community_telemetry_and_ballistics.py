"""
MW4 Weapon Intelligence Lab - Telemetry & Advanced Ballistics Unit Tests
Validates attachment pick rates, weapon win rates, 7-day momentum, tactical add-ammo calculations, and auto-equip functionality.
"""

import pytest
from src.database.connection import DatabaseManager
from src.database.repository import IntelligenceRepository
from src.database.seed_data import seed_database
from src.database.models import Attachment, AttachmentSlot, WeaponClass, FiringMode
from src.engines.attachment_engine import calculate_modified_stats
from src.ingestion.community_scraper import CommunityMetaScraper


@pytest.fixture
def test_repo():
    mgr = DatabaseManager(":memory:")
    seed_database(mgr)
    return IntelligenceRepository(mgr)


def test_attachment_pick_rate_fields(test_repo):
    """Verifies that attachments contain pick rate percentage and meta favorite flags."""
    attachments = test_repo.get_attachments()
    assert len(attachments) > 0
    
    # Check that at least some attachments have positive pick rates
    scraper = CommunityMetaScraper(test_repo)
    scraper._seed_attachment_pick_rates()
    
    updated_atts = test_repo.get_attachments()
    popular_atts = [a for a in updated_atts if a.pick_rate_pct > 50.0]
    assert len(popular_atts) > 0
    assert any(a.is_meta_favorite for a in popular_atts)


def test_get_most_popular_attachments(test_repo):
    """Verifies that get_most_popular_attachments returns top picked items for distinct slots."""
    scraper = CommunityMetaScraper(test_repo)
    scraper._seed_attachment_pick_rates()
    
    top_atts = test_repo.get_most_popular_attachments("xm4_mw4", max_slots=5)
    assert len(top_atts) <= 5
    # Ensure all slots are distinct
    slots_used = [a.slot for a in top_atts]
    assert len(slots_used) == len(set(slots_used))


def test_community_consensus_telemetry_fields(test_repo):
    """Verifies that CommunityMetaConsensus stores win rates, 7D momentum, and headshot %."""
    consensus = test_repo.get_community_consensus("v1.0.0-beta")
    assert len(consensus) > 0
    
    xm4_c = consensus.get("xm4_mw4")
    assert xm4_c is not None
    assert xm4_c.global_win_rate_pct >= 0.0
    assert isinstance(xm4_c.meta_trend_delta_pct, float)
    assert xm4_c.headshot_pct > 0.0
    assert xm4_c.kills_per_minute > 0.0


def test_tactical_ballistics_add_ammo_and_capacity_calculation(test_repo):
    """Verifies that EvaluatedBuildStats computes add-ammo, swap speed, and mag capacity."""
    weapon = test_repo.get_weapon("xm4_mw4")
    stats = test_repo.get_weapon_stats("xm4_mw4", "v1.1.0-launch")
    profiles = test_repo.get_damage_profiles("xm4_mw4", "v1.1.0-launch", "core")
    ruleset = test_repo.get_ruleset("core")
    all_mods = test_repo.get_attachment_modifiers("v1.1.0-launch")
    
    eval_stats = calculate_modified_stats(
        weapon=weapon,
        base_stats=stats,
        attachments=[],
        all_modifiers=all_mods,
        ruleset=ruleset,
        damage_profiles=profiles
    )
    
    assert eval_stats.effective_reload_add_ammo_s > 0.0
    assert eval_stats.effective_reload_add_ammo_s < eval_stats.effective_reload_tactical_s
    assert eval_stats.effective_swap_speed_raise_ms > 0.0
    assert eval_stats.damage_per_mag > 0.0
    assert eval_stats.kills_per_mag >= 1.0
