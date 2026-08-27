"""
Unit tests for Patch Notes Web Scraper and Monthly Rollover Resolution.
"""

import pytest
from src.database.connection import DatabaseManager
from src.database.repository import IntelligenceRepository
from src.ingestion.web_scraper import PatchNotesScraper


from src.database.seed_data import seed_database


@pytest.fixture
def mock_scraper_repo():
    mgr = DatabaseManager(db_path=":memory:")
    mgr.init_database()
    seed_database(mgr)
    repo = IntelligenceRepository(mgr)
    return repo



def test_candidate_url_monthly_rollover(mock_scraper_repo):
    scraper = PatchNotesScraper(mock_scraper_repo)

    # August 2026 test
    aug_urls = scraper.generate_candidate_urls(year=2026, month=8)
    assert any("/2026/08/" in u for u in aug_urls)
    assert any("/2026/09/" in u for u in aug_urls)  # Next month rollover
    assert any("/2026/07/" in u for u in aug_urls)  # Prev month

    # September 2026 test
    sep_urls = scraper.generate_candidate_urls(year=2026, month=9)
    assert any("/2026/09/" in u for u in sep_urls)
    assert any("/2026/10/" in u for u in sep_urls)


def test_parse_patch_html_bullet_extraction(mock_scraper_repo):
    scraper = PatchNotesScraper(mock_scraper_repo)

    html_sample = """
    <html>
        <head><title>MW4 Beta Patch Notes v1.1.2</title></head>
        <body>
            <h1>Call of Duty Modern Warfare 4 Beta Tuning</h1>
            <ul>
                <li>XM4 Commando: Base ADS Speed decreased from 240ms to 230ms.</li>
                <li>Rival-9: Sprint to fire time improved by 15ms.</li>
                <li>General stability improvements and bug fixes.</li>
            </ul>
        </body>
    </html>
    """

    parsed = scraper.parse_patch_html(html_sample, "https://callofduty.com/patchnotes/test")

    assert parsed["title"] == "Call of Duty Modern Warfare 4 Beta Tuning"
    assert parsed["version_id"] == "v1.1.2"
    assert parsed["adjustments_count"] >= 2
    assert any("XM4" in a["raw_text"] for a in parsed["adjustments"])


def test_scrape_and_ingest_quarantine(mock_scraper_repo):
    scraper = PatchNotesScraper(mock_scraper_repo)

    success, msg, data = scraper.scrape_and_ingest(
        target_url="https://www.callofduty.com/patchnotes/2026/08/call-of-duty-modern-warfare-4-beta-patch-notes",
        auto_promote_tier1=False
    )

    assert success is True
    # Verify snapshot recorded in DuckDB
    snapshots = mock_scraper_repo.get_source_snapshots()
    assert len(snapshots) >= 1

    # Verify item queued in AI Review Queue for human triage
    queue_items = mock_scraper_repo.get_ai_review_queue(status="pending")
    assert len(queue_items) >= 1


def test_scrape_and_ingest_auto_promote(mock_scraper_repo):
    scraper = PatchNotesScraper(mock_scraper_repo)

    success, msg, data = scraper.scrape_and_ingest(
        target_url="https://www.callofduty.com/patchnotes/2026/08/call-of-duty-modern-warfare-4-beta-patch-notes",
        auto_promote_tier1=True
    )

    assert success is True
    assert "auto-updated" in msg.lower() or "auto-applied" in msg.lower()
    assert "promotion_report" in data
    assert "applied_count" in data["promotion_report"]


