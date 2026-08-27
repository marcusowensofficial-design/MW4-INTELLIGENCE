"""
MW4 Weapon Intelligence Lab - Attachment Engine
Handles Gunsmith build legality, slot exclusivity, modifier stacking, and stat delta calculations.
"""

from typing import List, Dict, Optional, Tuple, Set
from src.database.models import (
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Attachment,
    AttachmentModifier,
    AttachmentSlot,
    ModifierType,
    Ruleset,
    EvaluatedBuildStats
)
from src.engines.ttk_engine import generate_ttk_curve
from src.engines.engagement_engine import calculate_practical_engagement_time


MAX_ATTACHMENTS_STANDARD = 5


class BuildLegalityError(ValueError):
    """Raised when a weapon build violates Gunsmith configuration rules."""
    pass


def validate_build_legality(
    weapon: Weapon,
    attachments: List[Attachment],
    max_slots: int = MAX_ATTACHMENTS_STANDARD
) -> Tuple[bool, Optional[str]]:
    """
    Validates whether an attachment configuration is legal under Gunsmith rules.
    - Max 5 attachments
    - Exactly 0 or 1 attachment per slot
    - All attachments must be universal or match weapon_id_compat
    """
    if len(attachments) > max_slots:
        return False, f"Exceeds maximum attachment limit of {max_slots} (equipped: {len(attachments)})"

    seen_slots: Set[AttachmentSlot] = set()
    for att in attachments:
        if att.slot in seen_slots:
            return False, f"Duplicate slot conflict: multiple attachments equipped in slot '{att.slot.value}'"
        seen_slots.add(att.slot)

        if not att.is_universal and att.weapon_id_compat and att.weapon_id_compat != weapon.weapon_id:
            return False, f"Attachment '{att.name}' is not compatible with weapon '{weapon.name}'"

    return True, None


def calculate_modified_stats(
    weapon: Weapon,
    base_stats: WeaponVersionStats,
    attachments: List[Attachment],
    all_modifiers: List[AttachmentModifier],
    ruleset: Ruleset,
    damage_profiles: List[DamageRangeBracket],
    build_label: str = "Custom Build",
    build_id: Optional[str] = None
) -> EvaluatedBuildStats:
    """
    Calculates the combined physical and practical stats for a weapon build after applying
    all equipped attachment modifiers.
    """
    is_legal, reason = validate_build_legality(weapon, attachments)
    if not is_legal:
        raise BuildLegalityError(reason)

    # Filter modifiers relevant to equipped attachments and game version
    equipped_ids = {a.attachment_id for a in attachments}
    active_modifiers = [
        m for m in all_modifiers
        if m.attachment_id in equipped_ids and m.game_version_id == base_stats.game_version_id
    ]

    # Initialize stat accumulators
    pct_mods: Dict[str, List[float]] = {}
    delta_mods: Dict[str, float] = {}

    for mod in active_modifiers:
        key = mod.stat_key
        if mod.mod_type == ModifierType.PERCENTAGE:
            pct_mods.setdefault(key, []).append(mod.mod_value)
        elif mod.mod_type == ModifierType.DELTA:
            delta_mods[key] = delta_mods.get(key, 0.0) + mod.mod_value

    def apply_mod(base_val: float, key: str, min_bound: float = 0.0, is_int: bool = False) -> float:
        # Multiplicative compound scaling for percentage modifiers (IW9 / MW4 Gunsmith engine)
        mult = 1.0
        for m in pct_mods.get(key, []):
            mult *= (1.0 + m)
        delta = delta_mods.get(key, 0.0)
        val = (base_val * mult) + delta
        val = max(min_bound, val)
        return int(round(val)) if is_int else val

    # Apply modifiers to physical stats
    eff_rpm = apply_mod(base_stats.rpm, "rpm", min_bound=50.0)
    eff_ads = apply_mod(base_stats.base_ads_ms, "base_ads_ms", min_bound=60.0)
    eff_stf = apply_mod(base_stats.sprint_to_fire_ms, "sprint_to_fire_ms", min_bound=50.0)
    eff_vel = apply_mod(base_stats.bullet_velocity_mps, "bullet_velocity_mps", min_bound=100.0)
    eff_reload_empty = apply_mod(base_stats.reload_empty_s, "reload_empty_s", min_bound=0.5)
    eff_reload_tac = apply_mod(base_stats.reload_tactical_s, "reload_tactical_s", min_bound=0.4)
    eff_recoil_h = apply_mod(base_stats.recoil_horizontal, "recoil_horizontal", min_bound=1.0)
    eff_recoil_v = apply_mod(base_stats.recoil_vertical, "recoil_vertical", min_bound=1.0)
    eff_hipfire = apply_mod(base_stats.hipfire_spread_deg, "hipfire_spread_deg", min_bound=0.5)
    eff_move = apply_mod(base_stats.move_speed_mps, "move_speed_mps", min_bound=2.0)
    eff_ads_move = apply_mod(base_stats.ads_move_speed_mps, "ads_move_speed_mps", min_bound=1.0)
    eff_mag = int(apply_mod(float(weapon.base_mag_size), "base_mag_size", min_bound=5.0, is_int=True))
    
    range_mult = 1.0
    for m in pct_mods.get("range_multiplier", []):
        range_mult *= (1.0 + m)
    range_mult += delta_mods.get("range_multiplier", 0.0)
    range_mult = max(0.20, range_mult)

    # Temporary modified stats object for TTK curves
    modified_stats_obj = WeaponVersionStats(
        stat_id=f"{base_stats.stat_id}_eval",
        weapon_id=weapon.weapon_id,
        game_version_id=base_stats.game_version_id,
        rpm=eff_rpm,
        base_ads_ms=eff_ads,
        sprint_to_fire_ms=eff_stf,
        tactical_sprint_to_fire_ms=base_stats.tactical_sprint_to_fire_ms,
        bullet_velocity_mps=eff_vel,
        reload_empty_s=eff_reload_empty,
        reload_tactical_s=eff_reload_tac,
        recoil_horizontal=eff_recoil_h,
        recoil_vertical=eff_recoil_v,
        hipfire_spread_deg=eff_hipfire,
        move_speed_mps=eff_move,
        ads_move_speed_mps=eff_ads_move,
        flinch_resistance=base_stats.flinch_resistance
    )

    # Calculate TTK curve with modified range
    ttk_result = generate_ttk_curve(
        weapon=weapon,
        stats=modified_stats_obj,
        profiles=damage_profiles,
        ruleset=ruleset,
        hit_location="chest",
        range_multiplier=range_mult
    )

    # Calculate Practical Engagement Time (15m close-mid sprint encounter)
    close_stk = ttk_result.curve_points[5].shots_to_kill if len(ttk_result.curve_points) > 5 else 4
    mid_stk = ttk_result.curve_points[25].shots_to_kill if len(ttk_result.curve_points) > 25 else 5

    close_pet = calculate_practical_engagement_time(
        reaction_ms=200.0,
        ads_ms=eff_ads,
        sprint_to_fire_ms=eff_stf,
        theoretical_ttk_ms=ttk_result.close_range_ttk_ms,
        stk=close_stk,
        rpm=eff_rpm,
        accuracy=0.75,
        is_sprinting=True
    )

    mid_pet = calculate_practical_engagement_time(
        reaction_ms=200.0,
        ads_ms=eff_ads,
        sprint_to_fire_ms=eff_stf,
        theoretical_ttk_ms=ttk_result.mid_range_ttk_ms,
        stk=mid_stk,
        rpm=eff_rpm,
        accuracy=0.65,
        is_sprinting=False,
        is_already_ads=False
    )

    # Derived Indices
    recoil_index = round((eff_recoil_h * 0.45) + (eff_recoil_v * 0.55), 2)
    mobility_index = round((eff_move * 15.0) + (eff_ads_move * 10.0) + max(0.0, (400.0 - eff_ads) * 0.1), 2)

    # Tactical Timings and Magazine Capacity
    base_add_ammo = base_stats.reload_add_ammo_s if getattr(base_stats, "reload_add_ammo_s", 0.0) > 0 else round(base_stats.reload_tactical_s * 0.68, 2)
    reload_ratio = base_add_ammo / max(0.5, base_stats.reload_tactical_s)
    eff_add_ammo = round(eff_reload_tac * reload_ratio, 2)
    
    base_swap = getattr(base_stats, "swap_speed_raise_ms", 350.0) or 350.0
    eff_swap = round(apply_mod(base_swap, "swap_speed_raise_ms", min_bound=100.0), 1)

    base_damage = damage_profiles[0].damage_chest if damage_profiles else 30.0
    damage_per_mag = round(eff_mag * base_damage, 1)
    kills_per_mag = round(eff_mag / max(1, close_stk), 1)

    # Normalized balance score placeholder (detailed in balance_scorer.py)
    balance_score = round(
        max(10.0, min(99.0, 100.0 - (mid_pet.practical_engagement_time_ms * 0.08) - (recoil_index * 0.8) + (range_mult * 10.0))),
        1
    )

    return EvaluatedBuildStats(
        weapon_id=weapon.weapon_id,
        weapon_name=weapon.name,
        build_id=build_id,
        build_label=build_label,
        game_version_id=base_stats.game_version_id,
        ruleset_id=ruleset.ruleset_id,
        attachment_ids=[a.attachment_id for a in attachments],
        attachments_applied=attachments,
        effective_rpm=round(eff_rpm, 1),
        effective_ads_ms=round(eff_ads, 1),
        effective_sprint_to_fire_ms=round(eff_stf, 1),
        effective_bullet_velocity_mps=round(eff_vel, 1),
        effective_reload_empty_s=round(eff_reload_empty, 2),
        effective_reload_tactical_s=round(eff_reload_tac, 2),
        effective_recoil_horizontal=round(eff_recoil_h, 2),
        effective_recoil_vertical=round(eff_recoil_v, 2),
        effective_hipfire_spread_deg=round(eff_hipfire, 2),
        effective_move_speed_mps=round(eff_move, 2),
        effective_ads_move_speed_mps=round(eff_ads_move, 2),
        effective_mag_size=eff_mag,
        range_multiplier=round(range_mult, 3),
        close_ttk_ms=ttk_result.close_range_ttk_ms,
        mid_ttk_ms=ttk_result.mid_range_ttk_ms,
        long_ttk_ms=ttk_result.long_range_ttk_ms,
        close_pet_ms=close_pet.practical_engagement_time_ms,
        mid_pet_ms=mid_pet.practical_engagement_time_ms,
        balance_score=balance_score,
        recoil_index=recoil_index,
        mobility_index=mobility_index,
        effective_reload_add_ammo_s=eff_add_ammo,
        effective_swap_speed_raise_ms=eff_swap,
        damage_per_mag=damage_per_mag,
        kills_per_mag=kills_per_mag
    )
