"""
MW4 Weapon Intelligence Lab - TTK & Damage Engine
Provides mathematically rigorous Shots-To-Kill, theoretical TTK, burst-fire logic,
and continuous damage distance curves for Core and Hardcore rulesets.
"""

import math
from typing import List, Dict, Optional, Tuple, Union
from src.database.models import (
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Ruleset,
    TTKPoint,
    TTKCalculationResult,
    HitLocation
)


def calculate_shots_to_kill(
    target_health: float,
    damage_per_shot: float,
    min_stk_cap: int = 1
) -> int:
    """
    Calculates Shots To Kill (STK) given health and per-shot damage.
    Formula: STK = ceil(target_health / damage_per_shot)
    """
    if damage_per_shot <= 0:
        return 999
    raw_stk = math.ceil(target_health / damage_per_shot)
    return max(min_stk_cap, raw_stk)


def calculate_theoretical_ttk_ms(
    stk: int,
    rpm: float,
    burst_count: int = 1,
    burst_delay_ms: float = 0.0,
    open_bolt_delay_ms: float = 0.0
) -> float:
    """
    Calculates theoretical Time-To-Kill (TTK) in milliseconds.
    - If STK <= 1: TTK = open_bolt_delay_ms (0.0ms for closed bolt)
    - Full-Auto: TTK = (STK - 1) * 60000 / RPM + open_bolt_delay_ms
    - Burst-Fire: Intra-burst shot time + inter-burst delays + open_bolt_delay_ms
    """
    if stk <= 1:
        return max(0.0, open_bolt_delay_ms)
    if rpm <= 0:
        return 9999.0

    shot_interval_ms = 60000.0 / rpm

    if burst_count <= 1:
        # Standard continuous automatic / semi-automatic fire
        base_ttk = (stk - 1) * shot_interval_ms
    else:
        # Burst weapon mechanics
        intra_burst_shots = stk - 1
        num_burst_delays = (stk - 1) // burst_count
        base_ttk = (intra_burst_shots * shot_interval_ms) + (num_burst_delays * burst_delay_ms)

    return base_ttk + open_bolt_delay_ms


def calculate_headshots_for_stk_reduction(
    target_health: float,
    body_damage: float,
    head_damage: float
) -> Optional[int]:
    """
    Calculates the minimum number of headshots required to reduce baseline body STK by 1 shot.
    Returns None if headshots cannot reduce STK.
    """
    if body_damage <= 0 or head_damage <= body_damage:
        return None

    base_stk = calculate_shots_to_kill(target_health, body_damage)
    if base_stk <= 1:
        return None

    target_stk = base_stk - 1
    # We want: H * head_damage + (target_stk - H) * body_damage >= target_health
    # H * (head_damage - body_damage) >= target_health - (target_stk * body_damage)
    damage_needed = target_health - (target_stk * body_damage)
    damage_bonus_per_head = head_damage - body_damage

    if damage_needed <= 0:
        return 0

    h_req = math.ceil(damage_needed / damage_bonus_per_head)
    return h_req if h_req <= target_stk else None


def get_damage_at_distance(
    distance_m: float,
    profiles: List[DamageRangeBracket],
    hit_location: str = "chest",
    body_multipliers: Optional[Dict[str, float]] = None,
    range_multiplier: float = 1.0
) -> float:
    """
    Resolves the effective per-shot damage at a given distance in meters,
    accounting for damage falloff brackets, attachment range multipliers,
    and hit location multipliers.
    """
    if not profiles:
        return 25.0  # Fallback default

    # Sort profiles ascending by range_start_m
    sorted_profiles = sorted(profiles, key=lambda p: p.range_start_m)

    # Locate the active range bracket
    active_profile = sorted_profiles[-1]  # Default to max range bracket
    for p in sorted_profiles:
        effective_start = p.range_start_m * range_multiplier if p.range_start_m > 0 else 0.0
        effective_end = p.range_end_m * range_multiplier
        if effective_start <= distance_m < effective_end:
            active_profile = p
            break

    # Determine base damage for hit location
    if hit_location == "head":
        base_dmg = active_profile.damage_head
    elif hit_location == "neck":
        base_dmg = active_profile.damage_neck
    elif hit_location == "chest" or hit_location == "upper_torso":
        base_dmg = active_profile.damage_chest
    elif hit_location == "stomach" or hit_location == "lower_torso":
        base_dmg = active_profile.damage_stomach
    elif hit_location == "limbs":
        base_dmg = active_profile.damage_limbs
    elif hit_location == "composite":
        # Realistic competitive hit distribution: 50% chest, 25% stomach, 15% limbs, 10% head
        base_dmg = (
            active_profile.damage_chest * 0.50 +
            active_profile.damage_stomach * 0.25 +
            active_profile.damage_limbs * 0.15 +
            active_profile.damage_head * 0.10
        )
    else:
        base_dmg = active_profile.damage_chest

    return max(1.0, base_dmg)


def generate_ttk_curve(
    weapon: Weapon,
    stats: WeaponVersionStats,
    profiles: List[DamageRangeBracket],
    ruleset: Ruleset,
    hit_location: str = "chest",
    max_distance_m: float = 75.0,
    step_m: float = 1.0,
    range_multiplier: float = 1.0
) -> TTKCalculationResult:
    """
    Generates a continuous sequence of TTK curve points from 0 to max_distance_m,
    including bullet travel time, Open-Bolt Delay, and Headshot STK reduction threshold.
    """
    curve_points: List[TTKPoint] = []
    current_dist = 0.0

    max_1shot_range: Optional[float] = None
    obd = getattr(stats, "open_bolt_delay_ms", 0.0) or 0.0

    while current_dist <= max_distance_m + 0.001:
        dmg = get_damage_at_distance(
            distance_m=current_dist,
            profiles=profiles,
            hit_location=hit_location,
            body_multipliers=ruleset.body_multipliers,
            range_multiplier=range_multiplier
        )

        stk = calculate_shots_to_kill(
            target_health=ruleset.target_health,
            damage_per_shot=dmg,
            min_stk_cap=ruleset.min_stk_cap
        )

        ttk = calculate_theoretical_ttk_ms(
            stk=stk,
            rpm=stats.rpm,
            burst_count=weapon.burst_count,
            burst_delay_ms=weapon.burst_delay_ms,
            open_bolt_delay_ms=obd
        )

        # Calculate bullet travel time (Distance / Bullet Velocity)
        vel = max(100.0, stats.bullet_velocity_mps)
        travel_time_ms = (current_dist / vel) * 1000.0
        impact_ttk = ttk + travel_time_ms

        is_1shot = (stk == 1)
        if is_1shot:
            max_1shot_range = current_dist

        curve_points.append(
            TTKPoint(
                distance_m=round(current_dist, 1),
                damage_per_shot=round(dmg, 2),
                shots_to_kill=stk,
                ttk_ms=round(ttk, 1),
                bullet_travel_time_ms=round(travel_time_ms, 1),
                impact_ttk_ms=round(impact_ttk, 1),
                hit_location=hit_location,
                is_lethal_1shot=is_1shot
            )
        )
        current_dist += step_m

    # Extract sample anchor TTKs
    close_dmg = get_damage_at_distance(5.0, profiles, hit_location, ruleset.body_multipliers, range_multiplier)
    mid_dmg = get_damage_at_distance(25.0, profiles, hit_location, ruleset.body_multipliers, range_multiplier)
    long_dmg = get_damage_at_distance(50.0, profiles, hit_location, ruleset.body_multipliers, range_multiplier)

    close_stk = calculate_shots_to_kill(ruleset.target_health, close_dmg, ruleset.min_stk_cap)
    mid_stk = calculate_shots_to_kill(ruleset.target_health, mid_dmg, ruleset.min_stk_cap)
    long_stk = calculate_shots_to_kill(ruleset.target_health, long_dmg, ruleset.min_stk_cap)

    close_ttk = calculate_theoretical_ttk_ms(close_stk, stats.rpm, weapon.burst_count, weapon.burst_delay_ms, obd)
    mid_ttk = calculate_theoretical_ttk_ms(mid_stk, stats.rpm, weapon.burst_count, weapon.burst_delay_ms, obd)
    long_ttk = calculate_theoretical_ttk_ms(long_stk, stats.rpm, weapon.burst_count, weapon.burst_delay_ms, obd)

    # Headshot reduction threshold at close range
    head_dmg_close = get_damage_at_distance(5.0, profiles, "head", ruleset.body_multipliers, range_multiplier)
    hs_drop = calculate_headshots_for_stk_reduction(ruleset.target_health, close_dmg, head_dmg_close)

    return TTKCalculationResult(
        weapon_id=weapon.weapon_id,
        weapon_name=weapon.name,
        game_version_id=stats.game_version_id,
        ruleset_id=ruleset.ruleset_id,
        target_health=ruleset.target_health,
        rpm=stats.rpm,
        hit_location=hit_location,
        open_bolt_delay_ms=obd,
        curve_points=curve_points,
        close_range_ttk_ms=round(close_ttk, 1),
        mid_range_ttk_ms=round(mid_ttk, 1),
        long_range_ttk_ms=round(long_ttk, 1),
        max_1shot_kill_range_m=round(max_1shot_range, 1) if max_1shot_range is not None else None,
        headshots_for_stk_drop=hs_drop
    )
