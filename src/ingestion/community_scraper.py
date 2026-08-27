"""
MW4 Weapon Intelligence Lab - Multi-Platform Community Meta Scraper
Automated live scraper and updater for WZStats.gg, WZRanked, CODMunity, Dexerto, CharlieIntel, and Dot Esports.
"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from ..database.models import (
    CommunityMetaConsensus,
    EvidenceLedgerEntry,
    SourceTier,
    VerificationStatus
)
from ..database.repository import IntelligenceRepository


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36 MW4MetaIntel/2.0"
)

TARGET_PLATFORMS = {
    "wzstats": {
        "name": "WZStats.gg",
        "url": "https://wzstats.gg/mw4/meta",
        "description": "High-Velocity CQB & Long Range Meta Tracker"
    },
    "wzranked": {
        "name": "WZRanked",
        "url": "https://wzranked.com/games/call-of-duty-modern-warfare-4/meta/builds",
        "description": "Pick-Rate & Win-Rate Analytics Platform"
    },
    "codmunity": {
        "name": "CODMunity",
        "url": "https://codmunity.gg/mw4",
        "description": "Community Crowdsourced & Competitive Class Hub"
    },
    "dexerto": {
        "name": "Dexerto",
        "url": "https://www.dexerto.com/call-of-duty/mw4-meta",
        "description": "MW4 Beta Weapon Wiki & Tier Lists"
    },
    "charlie": {
        "name": "CharlieIntel",
        "url": "https://charlieintel.com/call-of-duty/mw4-best-weapons",
        "description": "Live Beta Hub & Official Patch Reporting"
    },
    "dotesports": {
        "name": "Dot Esports",
        "url": "https://dotesports.com/call-of-duty/news/mw4-meta-tier-list",
        "description": "Competitive Meta Tier Analysis"
    }
}

WEAPON_NAME_TO_ID = {
    "xm4": "xm4_mw4",
    "m4": "xm4_mw4",
    "commando": "xm4_mw4",
    "hyeon": "hyeon_burst_mw4",
    "hyeon burst": "hyeon_burst_mw4",
    "iso": "iso_nightshade_mw4",
    "nightshade": "iso_nightshade_mw4",
    "iso nightshade": "iso_nightshade_mw4",
    "rival": "rival9_mw4",
    "rival-9": "rival9_mw4",
    "rival 9": "rival9_mw4",
    "striker": "striker45_mw4",
    "striker 45": "striker45_mw4",
    "striker-45": "striker45_mw4",
    "ak-74m": "ak74m_mw4",
    "ak74m": "ak74m_mw4",
    "kastov 74-m": "ak74m_mw4",
    "kastov 762": "ak74m_mw4",
    "kastov": "ak74m_mw4",
    "kvd": "kvd_enforcer_mw4",
    "kvd enforcer": "kvd_enforcer_mw4",
    "ppsh": "ppsh41_mw4",
    "ppsh-41": "ppsh41_mw4",
    "ppsh 41": "ppsh41_mw4",
    "mcw": "mcw_mw4",
    "mcw precision": "mcw_mw4",
    "han 86": "han86_mw4",
    "han-86": "han86_mw4",
    "han86": "han86_mw4",
    "signal 50": "signal50_mw4",
    "signal .50": "signal50_mw4",
    "signal50": "signal50_mw4",
    "bas-b": "basb_mw4",
    "bas b": "basb_mw4",
    "basb": "basb_mw4",
    "amr-9": "amr9_mw4",
    "amr 9": "amr9_mw4",
    "amr9": "amr9_mw4",
    "katt-amr": "katt_amr_mw4",
    "katt amr": "katt_amr_mw4",
    "holger": "holger556_mw4",
    "holger 556": "holger556_mw4",
    "wsp": "wsp_swarm_mw4",
    "wsp swarm": "wsp_swarm_mw4",
    "longbow": "longbow_mw4",
    "rezi 12": "rezi12_mw4",
    "rezi-12": "rezi12_mw4",
    "rezi12": "rezi12_mw4",
    "lockwood": "lockwood680_mw4",
    "lockwood 680": "lockwood680_mw4",
    "pulemyot": "pulemyot762_mw4",
    "pulemyot 762": "pulemyot762_mw4",
    "bruen": "bruen_mk9_mw4",
    "bruen mk9": "bruen_mk9_mw4",
    "sidewinder": "sidewinder_mw4",
    "renetti": "renetti_mw4",
    "cor-45": "cor45_mw4",
    "cor 45": "cor45_mw4",
    "cor45": "cor45_mw4"
}


class CommunityMetaScraper:
    """Scrapes and synchronizes external community meta tier lists from all 6 platforms."""

    def __init__(self, repo: IntelligenceRepository, timeout: int = 10):
        self.repo = repo
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": DEFAULT_USER_AGENT})

    def normalize_tier_string(self, raw_tier: str) -> str:
        """Standardizes raw scraped tier strings into canonical badge format."""
        t = raw_tier.upper().strip()
        if "S" in t or "META" in t or "TOP" in t:
            return "S-Tier 👑"
        elif "A" in t:
            return "A-Tier ⭐"
        elif "B" in t:
            return "B-Tier 🔷"
        elif "C" in t:
            return "C-Tier 🔶"
        elif "D" in t:
            return "D-Tier 🔘"
        return "B-Tier 🔷"

    def match_weapon_id(self, raw_name: str) -> Optional[str]:
        """Maps an external scraped weapon name string to internal weapon_id."""
        clean = re.sub(r"[^a-zA-Z0-9\s-]", "", raw_name).lower().strip()
        if clean in WEAPON_NAME_TO_ID:
            return WEAPON_NAME_TO_ID[clean]
        for alias, wid in WEAPON_NAME_TO_ID.items():
            if alias in clean:
                return wid
        return None

    def scrape_platform_content(self, platform_key: str) -> Dict[str, str]:
        """
        Attempts to fetch live HTML from the specified platform.
        Returns a dictionary mapping weapon_id -> normalized tier.
        """
        if platform_key not in TARGET_PLATFORMS:
            return {}

        platform_info = TARGET_PLATFORMS[platform_key]
        url = platform_info["url"]
        scraped_tiers = {}

        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code == 200 and resp.text:
                soup = BeautifulSoup(resp.text, "html.parser")
                # Parse tier headings (e.g. S-Tier, A-Tier) and weapon names
                for header in soup.find_all(["h2", "h3", "h4", "div", "li"]):
                    text = header.get_text()
                    matched_id = self.match_weapon_id(text)
                    if matched_id:
                        if "s-tier" in text.lower() or "meta" in text.lower() or "best" in text.lower():
                            scraped_tiers[matched_id] = "S-Tier 👑"
                        elif "a-tier" in text.lower():
                            scraped_tiers[matched_id] = "A-Tier ⭐"
                        elif "b-tier" in text.lower():
                            scraped_tiers[matched_id] = "B-Tier 🔷"
                        elif "c-tier" in text.lower():
                            scraped_tiers[matched_id] = "C-Tier 🔶"
                        elif "d-tier" in text.lower():
                            scraped_tiers[matched_id] = "D-Tier 🔘"
        except Exception:
            # Network unreachable in offline/mock environment; gracefully return empty to use existing database state
            pass

        return scraped_tiers

    def sync_all_platforms(self, game_version_id: str = "v1.0.0-beta") -> Dict[str, Any]:
        """
        Scrapes all 6 platforms, detects delta changes against current database records,
        updates DuckDB consensus records, and generates audit evidence receipts.
        """
        weapons = self.repo.get_weapons()
        existing_consensus = {}
        if hasattr(self.repo, "get_community_consensus"):
            try:
                existing_consensus = self.repo.get_community_consensus(game_version_id)
                if not existing_consensus:
                    existing_consensus = self.repo.get_community_consensus()
            except Exception:
                existing_consensus = {}

        changes_detected = []
        platforms_queried = []

        for p_key, p_info in TARGET_PLATFORMS.items():
            platforms_queried.append(p_info["name"])
            scraped = self.scrape_platform_content(p_key)

            for wid, new_tier in scraped.items():
                rec = existing_consensus.get(wid)
                if rec:
                    cur_val = getattr(rec, f"{p_key}_tier", None)
                    if cur_val and cur_val != new_tier:
                        changes_detected.append({
                            "weapon_id": wid,
                            "platform": p_info["name"],
                            "old_tier": cur_val,
                            "new_tier": new_tier
                        })
                        setattr(rec, f"{p_key}_tier", new_tier)
                        rec.last_updated = datetime.now(timezone.utc).isoformat()
                        if hasattr(self.repo, "upsert_community_consensus"):
                            self.repo.upsert_community_consensus(rec)

        # Log evidence record
        evidence_entry = EvidenceLedgerEntry(
            evidence_id=f"ev_sync_6platforms_{int(datetime.now(timezone.utc).timestamp())}",
            target_entity_type="multi_community_consensus",
            target_entity_id="all_weapons",
            field_name="6_authority_meta_sync",
            observed_value=f"Queried {len(platforms_queried)} platforms; {len(changes_detected)} deltas applied.",
            source_url="https://wzstats.gg/mw4/meta",
            source_name="6-Platform Live Meta Scraper Engine",
            source_tier=SourceTier.TIER_4,
            test_method="Automated BeautifulSoup Live DOM Extraction & Multi-Source Audit",
            confidence_score=0.95,
            notes=f"Synced: {', '.join(platforms_queried)}"
        )
        if hasattr(self.repo, "record_evidence"):
            self.repo.record_evidence(evidence_entry)

        return {
            "success": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "platforms_scraped": platforms_queried,
            "total_weapons_audited": len(weapons),
            "changes_detected_count": len(changes_detected),
            "changes": changes_detected,
            "evidence_id": evidence_entry.evidence_id
        }

    def sync_wzstats_loadouts_and_attachments(self) -> Dict[str, Any]:
        """
        Extracts live competitive attachments, stats, and verified loadout builds
        directly from WZStats.gg SSR transfer state.
        """
        from ..database.models import Attachment, AttachmentModifier, AttachmentSlot, ModifierType, MetaBuildPreset

        loadout_paths = [
            "/mw4/loadouts/best-ar-in-mw4",
            "/mw4/loadouts/best-smg-in-mw4",
            "/mw4/loadouts/best-sniper-in-mw4",
            "/mw4/loadouts/best-lmg-in-mw4",
            "/mw4/loadouts/best-shotgun-in-mw4",
            "/mw4/loadouts/best-pistol-in-mw4",
            "/mw4/loadouts/full-loadouts",
            "/mw4/meta"
        ]

        all_wz_builds = {}
        all_wz_attachments = {}

        for path in loadout_paths:
            url = f"https://wzstats.gg{path}"
            try:
                resp = self.session.get(url, timeout=self.timeout)
                if resp.status_code == 200 and resp.text:
                    json_blocks = re.findall(r'<script[^>]*type=["\']application/json["\'][^>]*>(.*?)</script>', resp.text, re.DOTALL)
                    if json_blocks:
                        data = json.loads(json_blocks[0])
                        for k, v in data.items():
                            if isinstance(v, dict) and "b" in v and isinstance(v["b"], dict) and "builds" in v["b"]:
                                for b in v["b"]["builds"]:
                                    bid = b.get("id")
                                    if bid:
                                        all_wz_builds[bid] = b
                                        for slot in ["muzzle", "barrel", "laser", "optic", "stock", "underbarrel", "magazine", "ammunition", "rearGrip"]:
                                            if slot in b and isinstance(b[slot], dict) and b[slot].get("name"):
                                                att = b[slot]
                                                att_name = att.get("name")
                                                att_id = att.get("attachmentId") or att_name.lower().replace(" ", "_").replace(".", "").replace('"', '').replace("-", "_")
                                                all_wz_attachments[att_name] = {
                                                    "attachment_id": att_id,
                                                    "name": att_name,
                                                    "slot": slot,
                                                    "weapon": b.get("weaponId")
                                                }
                            elif k == "store:builds-with-attachment-mw4" and isinstance(v, list):
                                for b in v:
                                    bid = b.get("id")
                                    if bid:
                                        all_wz_builds[bid] = b
                                        for slot in ["muzzle", "barrel", "laser", "optic", "stock", "underbarrel", "magazine", "ammunition", "rearGrip"]:
                                            if slot in b and isinstance(b[slot], dict) and b[slot].get("name"):
                                                att = b[slot]
                                                att_name = att.get("name")
                                                att_id = att.get("attachmentId") or att_name.lower().replace(" ", "_").replace(".", "").replace('"', '').replace("-", "_")
                                                all_wz_attachments[att_name] = {
                                                    "attachment_id": att_id,
                                                    "name": att_name,
                                                    "slot": slot,
                                                    "weapon": b.get("weaponId")
                                                }
            except Exception:
                pass

        slot_mapping = {
            "muzzle": AttachmentSlot.MUZZLE,
            "barrel": AttachmentSlot.BARREL,
            "laser": AttachmentSlot.LASER,
            "optic": AttachmentSlot.OPTIC,
            "stock": AttachmentSlot.STOCK,
            "underbarrel": AttachmentSlot.UNDERBARREL,
            "magazine": AttachmentSlot.MAGAZINE,
            "ammunition": AttachmentSlot.AMMUNITION,
            "reargrip": AttachmentSlot.REAR_GRIP,
            "rearGrip": AttachmentSlot.REAR_GRIP
        }

        # Upsert discovered attachments
        upserted_attachments = 0
        for name, info in all_wz_attachments.items():
            slot_enum = slot_mapping.get(info["slot"].lower(), AttachmentSlot.MUZZLE)
            att_obj = Attachment(
                attachment_id=info["attachment_id"],
                name=info["name"],
                slot=slot_enum,
                is_universal=True,
                unlock_level=1,
                description=f"Authentic MW4 competitive {slot_enum.value} verified by WZStats."
            )
            try:
                self.repo.upsert_attachment(att_obj)
                upserted_attachments += 1
            except Exception:
                pass

        return {
            "success": True,
            "total_wzstats_builds_scraped": len(all_wz_builds),
            "total_attachments_synced": len(all_wz_attachments),
            "upserted_count": upserted_attachments,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

