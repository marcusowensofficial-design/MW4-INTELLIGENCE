"""
MW4 Weapon Intelligence Lab - Official Patch Note Ingestion Engine
Parses structured patch notes, stores raw snapshots, registers new game versions,
updates versioned weapon stats, and logs Tier 1 evidence ledger entries.
"""

import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from src.database.models import (
    GameVersion,
    WeaponVersionStats,
    DamageRangeBracket,
    EvidenceLedgerEntry,
    SourceSnapshot,
    SourceTier,
    VerificationStatus
)
from src.database.repository import IntelligenceRepository


def ingest_patch_note_payload(
    payload: Dict[str, Any],
    repo: IntelligenceRepository,
    source_url: str = "https://www.callofduty.com/patchnotes"
) -> Tuple[bool, str, List[str]]:
    """
    Ingests and applies an official patch note payload.
    """
    logs: List[str] = []
    try:
        version_id = payload["version_id"]
        release_date = payload.get("release_date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
        patch_name = payload.get("patch_name", f"Patch {version_id}")
        notes = payload.get("notes", "")

        # 1. Snapshot raw payload
        raw_json = json.dumps(payload, indent=2)
        content_hash = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
        snapshot = SourceSnapshot(
            snapshot_id=f"snap_{version_id}_{int(datetime.now(timezone.utc).timestamp())}",
            source_id="official_callofduty_blog",
            fetch_timestamp=datetime.now(timezone.utc).isoformat(),
            content_hash=content_hash,
            raw_payload_path=f"data/snapshots/patch_{version_id}.json",
            diff_summary=f"Ingested {len(payload.get('weapon_stat_updates', []))} weapon stat updates."
        )
        repo.upsert_source_snapshot(snapshot)
        logs.append(f"Recorded raw source snapshot {snapshot.snapshot_id}")

        # 2. Register Game Version
        game_version = GameVersion(
            version_id=version_id,
            release_date=release_date,
            patch_name=patch_name,
            is_active=True,
            notes=notes
        )
        repo.upsert_game_version(game_version)
        logs.append(f"Registered game version: {version_id}")

        # 3. Apply versioned weapon stats & link Tier 1 evidence
        for update in payload.get("weapon_stat_updates", []):
            weapon_id = update["weapon_id"]
            stat_id = f"{weapon_id}_{version_id}"

            w_stat = WeaponVersionStats(
                stat_id=stat_id,
                weapon_id=weapon_id,
                game_version_id=version_id,
                rpm=update["rpm"],
                base_ads_ms=update["base_ads_ms"],
                sprint_to_fire_ms=update["sprint_to_fire_ms"],
                tactical_sprint_to_fire_ms=update.get("tactical_sprint_to_fire_ms", 0.0),
                bullet_velocity_mps=update["bullet_velocity_mps"],
                reload_empty_s=update["reload_empty_s"],
                reload_tactical_s=update["reload_tactical_s"],
                recoil_horizontal=update["recoil_horizontal"],
                recoil_vertical=update["recoil_vertical"],
                hipfire_spread_deg=update["hipfire_spread_deg"],
                move_speed_mps=update["move_speed_mps"],
                ads_move_speed_mps=update["ads_move_speed_mps"],
                flinch_resistance=update.get("flinch_resistance", 1.0)
            )
            repo.upsert_weapon_stats(w_stat)

            # Link Tier 1 Evidence
            evidence = EvidenceLedgerEntry(
                evidence_id=f"ev_{stat_id}_{int(datetime.now(timezone.utc).timestamp())}",
                target_entity_type="weapon_stats",
                target_entity_id=weapon_id,
                field_name="patch_stat_update",
                observed_value=f"Patch {version_id} stats applied",
                source_url=source_url,
                source_name="Official Call of Duty Blog & Patch Notes",
                source_tier=SourceTier.TIER_1,
                test_method="First-party official patch notes release",
                verification_status=VerificationStatus.VERIFIED,
                confidence_score=0.99,
                notes=f"Applied official stats from {patch_name}"
            )
            repo.upsert_evidence_entry(evidence)
            logs.append(f"Applied stats and Tier 1 evidence for {weapon_id} under {version_id}")

        return True, f"Successfully processed patch {version_id}", logs

    except Exception as e:
        return False, f"Failed to ingest patch notes: {str(e)}", logs
