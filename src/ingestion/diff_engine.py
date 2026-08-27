"""
MW4 Weapon Intelligence Lab - Version Diff & Stealth Balance Detector
Compares weapon physical stats and damage profiles across game versions to detect buffs, nerfs, and stealth changes.
"""

from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel
from src.database.models import WeaponVersionStats, DamageRangeBracket
from src.database.repository import IntelligenceRepository


class StatDelta(BaseModel):
    stat_name: str
    display_name: str
    v1_value: float
    v2_value: float
    delta: float
    pct_change: float
    classification: str  # "BUFF", "NERF", "NEUTRAL"
    is_lower_better: bool = False


class WeaponVersionDiff(BaseModel):
    weapon_id: str
    weapon_name: str
    v1_version_id: str
    v2_version_id: str
    deltas: List[StatDelta]
    has_changes: bool
    summary: str


def classify_stat_delta(
    stat_key: str,
    v1: float,
    v2: float
) -> Tuple[str, bool]:
    """
    Classifies whether a change is a BUFF, NERF, or NEUTRAL.
    Returns (classification, is_lower_better).
    """
    delta = v2 - v1
    if abs(delta) < 0.001:
        return "NEUTRAL", False

    # Lower is better stats (faster/smaller is a buff)
    lower_better_keys = {
        "base_ads_ms",
        "sprint_to_fire_ms",
        "tactical_sprint_to_fire_ms",
        "reload_empty_s",
        "reload_tactical_s",
        "recoil_horizontal",
        "recoil_vertical",
        "hipfire_spread_deg"
    }

    if stat_key in lower_better_keys:
        return ("BUFF" if delta < 0 else "NERF"), True
    else:
        # Higher is better (RPM, velocity, move speed, damage)
        return ("BUFF" if delta > 0 else "NERF"), False


def compare_weapon_versions(
    weapon_id: str,
    v1_version_id: str,
    v2_version_id: str,
    repo: IntelligenceRepository
) -> Optional[WeaponVersionDiff]:
    """
    Computes delta between two versions for a specific weapon.
    """
    weapon = repo.get_weapon(weapon_id)
    if not weapon:
        return None

    stats_v1 = repo.get_weapon_stats(weapon_id, v1_version_id)
    stats_v2 = repo.get_weapon_stats(weapon_id, v2_version_id)

    if not stats_v1 or not stats_v2:
        return None

    stat_fields = [
        ("rpm", "Fire Rate (RPM)"),
        ("base_ads_ms", "ADS Speed (ms)"),
        ("sprint_to_fire_ms", "Sprint to Fire (ms)"),
        ("bullet_velocity_mps", "Bullet Velocity (m/s)"),
        ("reload_tactical_s", "Tactical Reload (s)"),
        ("reload_empty_s", "Empty Reload (s)"),
        ("recoil_horizontal", "Horizontal Recoil Index"),
        ("recoil_vertical", "Vertical Recoil Index"),
        ("hipfire_spread_deg", "Hipfire Spread (deg)"),
        ("move_speed_mps", "Move Speed (m/s)"),
        ("ads_move_speed_mps", "ADS Strafe Speed (m/s)")
    ]

    deltas: List[StatDelta] = []
    buff_count = 0
    nerf_count = 0

    for key, display_name in stat_fields:
        v1_val = getattr(stats_v1, key)
        v2_val = getattr(stats_v2, key)
        delta = round(v2_val - v1_val, 2)
        pct = round((delta / v1_val) * 100.0, 1) if v1_val != 0 else 0.0

        classification, is_lower = classify_stat_delta(key, v1_val, v2_val)
        if classification == "BUFF":
            buff_count += 1
        elif classification == "NERF":
            nerf_count += 1

        deltas.append(
            StatDelta(
                stat_name=key,
                display_name=display_name,
                v1_value=v1_val,
                v2_value=v2_val,
                delta=delta,
                pct_change=pct,
                classification=classification,
                is_lower_better=is_lower
            )
        )

    has_changes = (buff_count > 0 or nerf_count > 0)
    summary = f"{buff_count} Buffs, {nerf_count} Nerfs between {v1_version_id} and {v2_version_id}"

    return WeaponVersionDiff(
        weapon_id=weapon_id,
        weapon_name=weapon.name,
        v1_version_id=v1_version_id,
        v2_version_id=v2_version_id,
        deltas=deltas,
        has_changes=has_changes,
        summary=summary
    )


def compare_all_weapons_across_versions(
    v1_version_id: str,
    v2_version_id: str,
    repo: IntelligenceRepository
) -> List[WeaponVersionDiff]:
    """
    Computes changes for all weapons between two game versions.
    """
    weapons = repo.get_weapons()
    results: List[WeaponVersionDiff] = []
    for w in weapons:
        diff = compare_weapon_versions(w.weapon_id, v1_version_id, v2_version_id, repo)
        if diff and diff.has_changes:
            results.append(diff)
    return results
