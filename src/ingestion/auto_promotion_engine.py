"""
MW4 Weapon Intelligence Lab - Automated Database Promotion & Guardrail Engine
Validates incoming patch notes against strict physical, biological, and mathematical guardrails
to apply direct verified database updates without manual review friction.
"""

import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from src.database.models import (
    WeaponVersionStats,
    DamageRangeBracket,
    EvidenceLedgerEntry,
    StatDeltaEvent,
    SourceTier,
    VerificationStatus
)
from src.database.repository import IntelligenceRepository


# Strict physical and anatomical bounding guardrails
STAT_BOUNDS = {
    "bullet_velocity_mps": (150.0, 2000.0, "Muzzle velocity must be between 150m/s and 2000m/s"),
    "base_ads_ms": (60.0, 750.0, "ADS speed must be between 60ms and 750ms"),
    "sprint_to_fire_ms": (40.0, 600.0, "Sprint-to-fire must be between 40ms and 600ms"),
    "recoil_vertical": (1.0, 95.0, "Recoil vertical index must be between 1.0 and 95.0"),
    "recoil_horizontal": (1.0, 95.0, "Recoil horizontal index must be between 1.0 and 95.0"),
    "rpm": (150.0, 1800.0, "Fire rate must be between 150 RPM and 1800 RPM"),
    "damage_head": (5.0, 300.0, "Head damage must be between 5.0 and 300.0 HP"),
    "damage_chest": (5.0, 250.0, "Chest damage must be between 5.0 and 250.0 HP"),
    "damage_neck": (5.0, 260.0, "Neck damage must be between 5.0 and 260.0 HP"),
    "damage_stomach": (5.0, 220.0, "Stomach damage must be between 5.0 and 220.0 HP"),
    "damage_limbs": (5.0, 200.0, "Limb damage must be between 5.0 and 200.0 HP"),
    "range_end_m": (2.0, 150.0, "Range falloff bracket must be between 2m and 150m")
}

# Maximum plausible single-patch delta percentage (50% max swing to catch parsing corruptions)
MAX_PLAUSIBLE_DELTA_PCT = 50.0


def validate_stat_guardrails(
    stat_key: str,
    old_value: float,
    new_value: float
) -> Tuple[bool, str]:
    """
    Validates a proposed stat modification against physical bounds and plausibility limits.
    """
    if stat_key in STAT_BOUNDS:
        min_v, max_v, err_msg = STAT_BOUNDS[stat_key]
        if not (min_v <= new_value <= max_v):
            return False, f"Guardrail Violation: {err_msg} (Proposed: {new_value:g})"

    if old_value > 0:
        pct_change = abs(new_value - old_value) / old_value * 100.0
        if pct_change > MAX_PLAUSIBLE_DELTA_PCT:
            return False, f"Plausibility Guardrail: Single-patch delta of {pct_change:.1f}% exceeds max {MAX_PLAUSIBLE_DELTA_PCT}% cap."

    return True, "Passed all mathematical and physical guardrails"


def parse_and_auto_apply_patch_adjustments(
    adjustments: List[Dict[str, Any]],
    source_url: str,
    patch_version_id: str,
    effective_date: str,
    repo: IntelligenceRepository
) -> Dict[str, Any]:
    """
    Directly parses, validates, and promotes official patch adjustments into the database.
    Updates weapon_version_stats, generates chronological stat_delta_events, and creates evidence entries.
    """
    weapons = repo.get_weapons()
    weapon_id_by_name = {}
    for w in weapons:
        weapon_id_by_name[w.name.lower()] = w.weapon_id
        # Also map short names e.g. "xm4" -> "xm4_mw4"
        clean_alias = re.sub(r"[^a-zA-Z0-9]", "", w.name.lower())
        weapon_id_by_name[clean_alias] = w.weapon_id

    applied_count = 0
    rejected_count = 0
    audit_trail: List[Dict[str, Any]] = []

    for adj in adjustments:
        raw_text = adj.get("raw_text", "")
        clean_raw_text = re.sub(r"[^a-zA-Z0-9]", "", raw_text.lower())
        # Look for weapon target
        matched_w_id = None
        for alias, w_id in weapon_id_by_name.items():
            if alias in raw_text.lower() or alias in clean_raw_text or w_id.split("_")[0] in clean_raw_text:
                matched_w_id = w_id
                break

        if not matched_w_id:
            continue

        # Pattern detection: "Bullet velocity increased from 735m/s to 750m/s"
        # Or "Sprint to fire time improved by 10ms (160ms -> 150ms)"
        # Or "damage increased from X to Y"
        stat_key = None
        old_val = 0.0
        new_val = 0.0
        delta_val = 0.0

        if "velocity" in raw_text.lower():
            stat_key = "bullet_velocity_mps"
        elif "sprint to fire" in raw_text.lower() or "sprint-to-fire" in raw_text.lower():
            stat_key = "sprint_to_fire_ms"
        elif "ads" in raw_text.lower():
            stat_key = "base_ads_ms"
        elif "recoil" in raw_text.lower():
            stat_key = "recoil_vertical"
        elif "damage" in raw_text.lower():
            stat_key = "damage_chest"
        elif "range" in raw_text.lower():
            stat_key = "range_end_m"
        elif "fire rate" in raw_text.lower() or "rpm" in raw_text.lower():
            stat_key = "rpm"

        if not stat_key:
            continue

        payload_text = raw_text.split(":", 1)[1] if ":" in raw_text else raw_text

        # 1. Look for explicit "from X to Y" or "(X -> Y)" or "reduced from X to Y"
        m_from_to = re.search(r"from\s+(\d+(?:\.\d+)?)\s*(?:m/s|ms|m|rpm)?\s*to\s+(\d+(?:\.\d+)?)", payload_text, re.IGNORECASE)
        m_arrow = re.search(r"(\d+(?:\.\d+)?)\s*(?:m/s|ms|m|rpm)?\s*(?:->|–>|➔)\s*(\d+(?:\.\d+)?)", payload_text)

        if m_from_to:
            old_val = float(m_from_to.group(1))
            new_val = float(m_from_to.group(2))
            delta_val = new_val - old_val
        elif m_arrow:
            old_val = float(m_arrow.group(1))
            new_val = float(m_arrow.group(2))
            delta_val = new_val - old_val
        else:
            numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", payload_text)]
            if len(numbers) >= 2:
                old_val = numbers[-2]
                new_val = numbers[-1]
                delta_val = new_val - old_val
            elif len(numbers) == 1:
                cur_stats = repo.get_weapon_stats(matched_w_id, "v1.1.0-launch")
                if cur_stats and hasattr(cur_stats, stat_key):
                    old_val = float(getattr(cur_stats, stat_key, 0.0) or 0.0)
                    new_val = numbers[0]
                    delta_val = new_val - old_val
                else:
                    continue
            else:
                continue

        # Run guardrail check
        is_valid, reason = validate_stat_guardrails(stat_key, old_val, new_val)

        if not is_valid:
            rejected_count += 1
            audit_trail.append({
                "status": "REJECTED",
                "weapon_id": matched_w_id,
                "stat_key": stat_key,
                "raw_text": raw_text,
                "reason": reason
            })
            continue

        # 1. Update weapon_version_stats directly
        cur_stats = repo.get_weapon_stats(matched_w_id, "v1.1.0-launch")
        if cur_stats and hasattr(cur_stats, stat_key):
            setattr(cur_stats, stat_key, new_val)
            repo.upsert_weapon_stats(cur_stats)

        # 2. Record StatDeltaEvent in chronological lineage
        event_id = f"auto_delta_{matched_w_id}_{stat_key}_{int(datetime.now(timezone.utc).timestamp())}"
        delta_event = StatDeltaEvent(
            event_id=event_id,
            weapon_id=matched_w_id,
            stat_name=stat_key,
            patch_version_id=patch_version_id,
            effective_date=effective_date,
            previous_value=old_val,
            delta_type="DELTA_ADD",
            delta_value=round(delta_val, 2),
            new_value=round(new_val, 2),
            official_patch_url=source_url,
            developer_notes=f"Auto-Promoted: {raw_text}",
            captured_timestamp=datetime.now(timezone.utc).isoformat()
        )
        repo.upsert_stat_delta_event(delta_event)

        # 3. Create Evidence Ledger entry
        evidence = EvidenceLedgerEntry(
            evidence_id=f"ev_auto_{event_id}",
            target_entity_type="weapon_stats",
            target_entity_id=matched_w_id,
            field_name=stat_key,
            observed_value=str(new_val),
            source_url=source_url,
            source_name="Official Activision Patch Notes",
            source_tier=SourceTier.TIER_1,
            test_method="Official Developer Ingestion",
            captured_timestamp=datetime.now(timezone.utc).isoformat(),
            recorded_by="auto_promotion_guardrail_engine",
            verification_status=VerificationStatus.VERIFIED,
            confidence_score=0.99,
            notes=f"Auto-verified via guardrails: {raw_text}"
        )
        repo.upsert_evidence_entry(evidence)

        applied_count += 1
        audit_trail.append({
            "status": "APPLIED",
            "weapon_id": matched_w_id,
            "stat_key": stat_key,
            "old_value": old_val,
            "new_value": new_val,
            "delta": delta_val,
            "raw_text": raw_text
        })

    return {
        "applied_count": applied_count,
        "rejected_count": rejected_count,
        "total_evaluated": len(adjustments),
        "audit_trail": audit_trail
    }
