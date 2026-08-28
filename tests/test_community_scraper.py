"""
Unit tests for Multi-Platform Community Meta Scraper.
Validates weapon name normalization, tier parsing, delta detection, and evidence ledger logging.
"""

import pytest
from src.database.connection import DatabaseManager
from src.database.repository import IntelligenceRepository
from src.database.seed_data import seed_database
from src.ingestion.community_scraper import CommunityMetaScraper, TARGET_PLATFORMS


def test_community_scraper_target_platforms():
    assert len(TARGET_PLATFORMS) == 6
    assert "wzstats" in TARGET_PLATFORMS
    assert "wzranked" in TARGET_PLATFORMS
    assert "codmunity" in TARGET_PLATFORMS
    assert "dexerto" in TARGET_PLATFORMS
    assert "charlie" in TARGET_PLATFORMS
    assert "dotesports" in TARGET_PLATFORMS


def test_community_scraper_weapon_id_matching():
    db = DatabaseManager(":memory:")
    seed_database(db)
    repo = IntelligenceRepository(db)
    scraper = CommunityMetaScraper(repo)

    assert scraper.match_weapon_id("patriot xmr") == "patriot_xmr_mw4"
    assert scraper.match_weapon_id("M4") == "m4_mw4"
    assert scraper.match_weapon_id("iso nightshade") == "iso_nightshade_mw4"
    assert scraper.match_weapon_id("iso nightshade") == "iso_nightshade_mw4"
    assert scraper.match_weapon_id("Kastov 762") == "kastov762_mw4"
    assert scraper.match_weapon_id("PPSh-41") == "ppsh41_mw4"
    assert scraper.match_weapon_id("Hyeon Burst") == "hyeon_burst_mw4"


def test_community_scraper_normalize_tier():
    db = DatabaseManager(":memory:")
    repo = IntelligenceRepository(db)
    scraper = CommunityMetaScraper(repo)

    assert scraper.normalize_tier_string("S-Tier") == "S-Tier 👑"
    assert scraper.normalize_tier_string("meta") == "S-Tier 👑"
    assert scraper.normalize_tier_string("A-Tier") == "A-Tier ⭐"
    assert scraper.normalize_tier_string("B") == "B-Tier 🔷"
    assert scraper.normalize_tier_string("C-Tier") == "C-Tier 🔶"
    assert scraper.normalize_tier_string("D") == "D-Tier 🔘"


def test_community_scraper_sync_all_platforms_execution():
    db = DatabaseManager(":memory:")
    seed_database(db)
    repo = IntelligenceRepository(db)
    scraper = CommunityMetaScraper(repo)

    report = scraper.sync_all_platforms("v1.2.0-beta-weekend2")
    assert report["success"] is True
    assert len(report["platforms_scraped"]) == 6
    assert report["total_weapons_audited"] == 17
    assert "evidence_id" in report
