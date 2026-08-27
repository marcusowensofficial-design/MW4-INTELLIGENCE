"""
MW4 Weapon Intelligence Lab - Advanced Balance Scoring Engine
Implements Class-Relative Role Benchmarking, Empirical 6v6 Engagement Sightline Curves,
and Nonlinear Fatal Flaw Bottleneck Penalties for gold-standard competitive accuracy.
"""

from typing import Dict, List, Optional
from ..database.models import (
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Ruleset,
    BalanceScoreBreakdown,
    WeaponClass
)
from .ttk_engine import generate_ttk_curve


# Empirical 6v6 Multiplayer Sightline Weights (Reflecting realistic 12m-32m primary combat zone)
DEFAULT_EMPIRICAL_WEIGHTS = {
    "cqb_ttk": 0.25,        # 0m - 12m
    "mid_ttk": 0.35,        # 12m - 32m (Primary engagement zone)
    "long_ttk": 0.15,       # 32m - 50m
    "handling_ads_stf": 0.15, # ADS + Sprint-to-fire reaction
    "recoil_stability": 0.07, # Recoil control & visual steadiness
    "sustainability_reload_mag": 0.03 # Mag capacity & reload speed
}

# Role Archetype Class Specific Weightings (For Class-Relative Best-in-Category Evaluation)
CLASS_ARCHETYPE_WEIGHTS: Dict[WeaponClass, Dict[str, float]] = {
    WeaponClass.ASSAULT_RIFLE: {
        "cqb_ttk": 0.15, "mid_ttk": 0.35, "long_ttk": 0.20,
        "handling_ads_stf": 0.15, "recoil_stability": 0.12, "sustainability_reload_mag": 0.03
    },
    WeaponClass.SUBMACHINE_GUN: {
        "cqb_ttk": 0.40, "mid_ttk": 0.20, "long_ttk": 0.05,
        "handling_ads_stf": 0.25, "recoil_stability": 0.05, "sustainability_reload_mag": 0.05
    },
    WeaponClass.BATTLE_RIFLE: {
        "cqb_ttk": 0.10, "mid_ttk": 0.35, "long_ttk": 0.25,
        "handling_ads_stf": 0.10, "recoil_stability": 0.15, "sustainability_reload_mag": 0.05
    },
    WeaponClass.MARKSMAN_RIFLE: {
        "cqb_ttk": 0.10, "mid_ttk": 0.35, "long_ttk": 0.30,
        "handling_ads_stf": 0.15, "recoil_stability": 0.08, "sustainability_reload_mag": 0.02
    },
    WeaponClass.SNIPER_RIFLE: {
        "cqb_ttk": 0.05, "mid_ttk": 0.25, "long_ttk": 0.45,
        "handling_ads_stf": 0.20, "recoil_stability": 0.03, "sustainability_reload_mag": 0.02
    },
    WeaponClass.LIGHT_MACHINE_GUN: {
        "cqb_ttk": 0.10, "mid_ttk": 0.30, "long_ttk": 0.30,
        "handling_ads_stf": 0.05, "recoil_stability": 0.15, "sustainability_reload_mag": 0.10
    },
    WeaponClass.SHOTGUN: {
        "cqb_ttk": 0.60, "mid_ttk": 0.10, "long_ttk": 0.00,
        "handling_ads_stf": 0.25, "recoil_stability": 0.02, "sustainability_reload_mag": 0.03
    },
    WeaponClass.HANDGUN: {
        "cqb_ttk": 0.40, "mid_ttk": 0.15, "long_ttk": 0.05,
        "handling_ads_stf": 0.35, "recoil_stability": 0.03, "sustainability_reload_mag": 0.02
    }
}


def normalize_metric(val: float, best_val: float, worst_val: float) -> float:
    """
    Normalizes a value between best_val (100.0) and worst_val (0.0).
    """
    if best_val == worst_val:
        return 50.0
    if best_val < worst_val:
        # Lower is better (e.g., TTK: 120ms is best, 420ms is worst)
        score = (worst_val - val) / (worst_val - best_val) * 100.0
    else:
        # Higher is better (e.g., Mag size: 60 is best, 15 is worst)
        score = (val - worst_val) / (best_val - worst_val) * 100.0

    return max(0.0, min(100.0, round(score, 1)))


def calculate_balance_score(
    weapon: Weapon,
    stats: WeaponVersionStats,
    damage_profiles: List[DamageRangeBracket],
    ruleset: Ruleset,
    custom_weights: Optional[Dict[str, float]] = None,
    confidence_score: float = 0.92,
    use_class_relative_scoring: bool = False
) -> BalanceScoreBreakdown:
    """
    Calculates transparent composite balance score and sub-scores for a weapon.
    Supports both Class-Relative Role Benchmarking and Global Sightline Meta evaluation.
    """
    # 1. Determine active weight profile
    if custom_weights:
        weights = custom_weights
    elif use_class_relative_scoring and weapon.weapon_class in CLASS_ARCHETYPE_WEIGHTS:
        weights = CLASS_ARCHETYPE_WEIGHTS[weapon.weapon_class]
    else:
        weights = DEFAULT_EMPIRICAL_WEIGHTS

    total_w = sum(weights.values())
    norm_weights = {k: v / total_w for k, v in weights.items()} if total_w > 0 else DEFAULT_EMPIRICAL_WEIGHTS

    # 2. Calculate TTK anchor metrics
    ttk_data = generate_ttk_curve(
        weapon=weapon,
        stats=stats,
        profiles=damage_profiles,
        ruleset=ruleset,
        hit_location="chest"
    )

    close_ttk = ttk_data.close_range_ttk_ms
    mid_ttk = ttk_data.mid_range_ttk_ms
    long_ttk = ttk_data.long_range_ttk_ms

    # 3. Domain normalizations with realistic competitive thresholds
    # Shotguns & Snipers with 1-shot lethal capabilities receive true 100 CQB/Long scores
    if weapon.weapon_class == WeaponClass.SHOTGUN:
        cqb_score = 100.0 if close_ttk == 0.0 else normalize_metric(close_ttk, 0.0, 300.0)
        mid_score = normalize_metric(mid_ttk, 150.0, 600.0)
        long_score = 0.0
    elif weapon.weapon_class == WeaponClass.SNIPER_RIFLE:
        cqb_score = normalize_metric(close_ttk + stats.base_ads_ms, 300.0, 700.0)
        mid_score = 95.0 if mid_ttk == 0.0 else normalize_metric(mid_ttk, 0.0, 350.0)
        long_score = 100.0 if long_ttk == 0.0 else normalize_metric(long_ttk, 0.0, 350.0)
    else:
        cqb_score = normalize_metric(close_ttk, best_val=140.0, worst_val=360.0)
        mid_score = normalize_metric(mid_ttk, best_val=190.0, worst_val=420.0)
        long_score = normalize_metric(long_ttk, best_val=240.0, worst_val=520.0)

    # 4. Handling: Combined ADS + Sprint to Fire
    combined_handling = stats.base_ads_ms + stats.sprint_to_fire_ms
    handling_score = normalize_metric(combined_handling, best_val=220.0, worst_val=680.0)

    # 5. Recoil Stability: Horizontal + Vertical + Open Bolt Delay penalty
    combined_recoil = stats.recoil_horizontal + stats.recoil_vertical
    recoil_score = normalize_metric(combined_recoil, best_val=20.0, worst_val=75.0)

    # 6. Sustainability: Mag Size + Reload Downtime
    mag_norm = normalize_metric(float(weapon.base_mag_size), best_val=60.0, worst_val=15.0)
    reload_norm = normalize_metric(stats.reload_tactical_s, best_val=1.6, worst_val=5.2)
    sustainability_score = round((mag_norm * 0.6) + (reload_norm * 0.4), 1)

    # 7. Base Composite Weighted Score
    raw_composite = (
        cqb_score * norm_weights.get("cqb_ttk", 0.25) +
        mid_score * norm_weights.get("mid_ttk", 0.35) +
        long_score * norm_weights.get("long_ttk", 0.15) +
        handling_score * norm_weights.get("handling_ads_stf", 0.15) +
        recoil_score * norm_weights.get("recoil_stability", 0.07) +
        sustainability_score * norm_weights.get("sustainability_reload_mag", 0.03)
    )

    # 8. Nonlinear Fatal Flaw Bottleneck Penalties (Conjunctive Reality Checks)
    bottleneck_multiplier = 1.0

    # Fatal Recoil Flaw: If combined recoil > 58, human tracking consistency drops sharply
    if combined_recoil > 58.0 and weapon.weapon_class not in [WeaponClass.SNIPER_RIFLE, WeaponClass.SHOTGUN]:
        recoil_penalty = max(0.72, 1.0 - ((combined_recoil - 58.0) * 0.015))
        bottleneck_multiplier *= recoil_penalty

    # Open-Bolt Delay Latency Penalty (e.g. 40-50ms chambering delay on heavy LMGs)
    obd = getattr(stats, "open_bolt_delay_ms", 0.0) or 0.0
    if obd > 0.0:
        bottleneck_multiplier *= max(0.85, 1.0 - (obd / 250.0))

    final_score = raw_composite * bottleneck_multiplier
    final_score = max(0.0, min(100.0, round(final_score, 1)))

    # 9. Gold-Standard Calibrated Competitive Tier Classification
    if final_score >= 74.0:
        tier = "S"
    elif final_score >= 64.0:
        tier = "A"
    elif final_score >= 54.0:
        tier = "B"
    elif final_score >= 42.0:
        tier = "C"
    else:
        tier = "D"

    assumptions = [
        f"Ruleset: {ruleset.name} ({ruleset.target_health} HP)",
        f"Scoring Mode: {'Class-Relative Role Archetype' if use_class_relative_scoring else 'Empirical 6v6 Sightline Meta'}",
        f"Target Hitbox: Chest / Upper Torso",
        f"Bottleneck Multiplier: {bottleneck_multiplier:.2f}x",
        f"Evidence Confidence Rating: {round(confidence_score * 100, 1)}%"
    ]

    return BalanceScoreBreakdown(
        weapon_id=weapon.weapon_id,
        weapon_name=weapon.name,
        weapon_class=weapon.weapon_class,
        game_version_id=stats.game_version_id,
        ruleset_id=ruleset.ruleset_id,
        composite_balance_score=final_score,
        tier_rating=tier,
        cqb_ttk_score=cqb_score,
        mid_ttk_score=mid_score,
        long_ttk_score=long_score,
        handling_score=handling_score,
        recoil_score=recoil_score,
        sustainability_score=sustainability_score,
        raw_close_ttk_ms=close_ttk,
        raw_ads_ms=stats.base_ads_ms,
        raw_recoil_vertical=stats.recoil_vertical,
        raw_mag_size=weapon.base_mag_size,
        confidence_score=confidence_score,
        weights_used=norm_weights,
        assumptions_log=assumptions
    )
