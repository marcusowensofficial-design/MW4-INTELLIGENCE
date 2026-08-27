"""
MW4 Weapon Intelligence Lab - Chronological Stat Lineage & Patch Walk Engine
Reconstructs weapon stats historically at any date by applying sequential patch tuning deltas,
preventing stale baselines from overwriting verified updates.
"""

from typing import List, Dict, Optional, Any, Tuple
from ..database.models import StatDeltaEvent, StatLineageReconstruction


def reconstruct_stat_lineage(
    events: List[StatDeltaEvent],
    weapon_id: str,
    stat_name: str,
    target_date: Optional[str] = None
) -> StatLineageReconstruction:
    """
    Sequentially walks through chronological patch events to reconstruct a stat value as of target_date.
    Ensures mathematical continuity: current_val = prev_val + delta (or absolute set).
    """
    # Filter and sort chronologically
    matching_events = [
        e for e in events
        if e.weapon_id == weapon_id and e.stat_name == stat_name
    ]
    matching_events.sort(key=lambda x: (x.effective_date, x.captured_timestamp))

    if not matching_events:
        return StatLineageReconstruction(
            weapon_id=weapon_id,
            stat_name=stat_name,
            baseline_date="N/A",
            baseline_value=0.0,
            as_of_date=target_date or "latest",
            reconstructed_value=0.0,
            total_patches_applied=0,
            patch_trail=[],
            is_continuity_verified=True
        )

    baseline_event = matching_events[0]
    baseline_date = baseline_event.effective_date
    baseline_val = baseline_event.previous_value

    current_val = baseline_val
    applied_trail: List[StatDeltaEvent] = []
    continuity_valid = True

    for ev in matching_events:
        if target_date and ev.effective_date > target_date:
            break

        # Verify continuity: does previous_value match current accumulated state?
        if abs(ev.previous_value - current_val) > 0.001:
            continuity_valid = False

        if ev.delta_type == "SET_ABSOLUTE":
            current_val = ev.delta_value
        elif ev.delta_type == "DELTA_PERCENT":
            current_val = current_val * (1.0 + ev.delta_value / 100.0)
        else:  # DELTA_ADD
            current_val = current_val + ev.delta_value

        applied_trail.append(ev)

    return StatLineageReconstruction(
        weapon_id=weapon_id,
        stat_name=stat_name,
        baseline_date=baseline_date,
        baseline_value=round(baseline_val, 2),
        as_of_date=target_date or (applied_trail[-1].effective_date if applied_trail else baseline_date),
        reconstructed_value=round(current_val, 2),
        total_patches_applied=len(applied_trail),
        patch_trail=applied_trail,
        is_continuity_verified=continuity_valid
    )


def audit_weapon_patch_continuity(
    events: List[StatDeltaEvent],
    weapon_id: str
) -> Dict[str, Any]:
    """
    Audits the entire chronological patch lineage for a weapon across all tracked stats.
    Detects any gaps, out-of-order patches, or overwritten baselines.
    """
    weapon_events = [e for e in events if e.weapon_id == weapon_id]
    stat_keys = sorted(list({e.stat_name for e in weapon_events}))

    audit_report = {
        "weapon_id": weapon_id,
        "total_patch_events": len(weapon_events),
        "tracked_stats": len(stat_keys),
        "all_continuous": True,
        "stat_breakdown": {}
    }

    for sk in stat_keys:
        reconstructed = reconstruct_stat_lineage(weapon_events, weapon_id, sk)
        audit_report["stat_breakdown"][sk] = {
            "baseline_date": reconstructed.baseline_date,
            "baseline_value": reconstructed.baseline_value,
            "latest_value": reconstructed.reconstructed_value,
            "patches_count": reconstructed.total_patches_applied,
            "continuity_verified": reconstructed.is_continuity_verified
        }
        if not reconstructed.is_continuity_verified:
            audit_report["all_continuous"] = False

    return audit_report
