"""
MW4 Weapon Intelligence Lab - Multi-Objective Pareto-Frontier Optimizer
Finds non-dominated Gunsmith attachment builds across Practical Engagement Time,
Recoil Stability, Mobility, and Effective Range.
"""

import itertools
from typing import List, Dict, Optional, Tuple
from src.database.models import (
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Attachment,
    AttachmentModifier,
    AttachmentSlot,
    Ruleset,
    ParetoBuildPoint,
    EvaluatedBuildStats
)
from src.engines.attachment_engine import calculate_modified_stats, validate_build_legality


def is_dominated(
    candidate: EvaluatedBuildStats,
    other: EvaluatedBuildStats
) -> bool:
    """
    Checks if 'candidate' is dominated by 'other'.
    'other' dominates 'candidate' iff:
      1. other is at least as good as candidate in all 4 objectives:
         - PET: other <= candidate (lower is better)
         - Recoil: other <= candidate (lower is better)
         - Mobility: other >= candidate (higher is better)
         - Range: other >= candidate (higher is better)
      2. other is strictly better in at least one objective.
    """
    other_pet = other.mid_pet_ms
    cand_pet = candidate.mid_pet_ms

    other_recoil = other.recoil_index
    cand_recoil = candidate.recoil_index

    other_mob = other.mobility_index
    cand_mob = candidate.mobility_index

    other_range = other.range_multiplier
    cand_range = candidate.range_multiplier

    # Condition 1: other is at least as good in all objectives
    at_least_as_good = (
        other_pet <= cand_pet and
        other_recoil <= cand_recoil and
        other_mob >= cand_mob and
        other_range >= cand_range
    )

    if not at_least_as_good:
        return False

    # Condition 2: other is strictly better in at least one objective
    strictly_better = (
        other_pet < cand_pet or
        other_recoil < cand_recoil or
        other_mob > cand_mob or
        other_range > cand_range
    )

    return strictly_better


def generate_candidate_builds(
    weapon: Weapon,
    base_stats: WeaponVersionStats,
    available_attachments: List[Attachment],
    all_modifiers: List[AttachmentModifier],
    ruleset: Ruleset,
    damage_profiles: List[DamageRangeBracket],
    max_combinations: int = 400
) -> List[EvaluatedBuildStats]:
    """
    Generates a diverse candidate population of legal Gunsmith builds.
    Includes naked baseline, single-attachment builds, and 2-to-5 attachment combinations.
    """
    candidates: List[EvaluatedBuildStats] = []

    # 1. Naked weapon baseline (0 attachments)
    try:
        baseline = calculate_modified_stats(
            weapon=weapon,
            base_stats=base_stats,
            attachments=[],
            all_modifiers=all_modifiers,
            ruleset=ruleset,
            damage_profiles=damage_profiles,
            build_label="Naked Baseline"
        )
        candidates.append(baseline)
    except Exception:
        pass

    # Group attachments by slot
    by_slot: Dict[AttachmentSlot, List[Attachment]] = {}
    for a in available_attachments:
        if a.is_universal or a.weapon_id_compat == weapon.weapon_id:
            by_slot.setdefault(a.slot, []).append(a)

    # 2. Single-attachment builds
    for a in available_attachments:
        if a.is_universal or a.weapon_id_compat == weapon.weapon_id:
            try:
                b = calculate_modified_stats(
                    weapon=weapon,
                    base_stats=base_stats,
                    attachments=[a],
                    all_modifiers=all_modifiers,
                    ruleset=ruleset,
                    damage_profiles=damage_profiles,
                    build_label=f"Solo: {a.name}"
                )
                candidates.append(b)
            except Exception:
                continue

    # 3. Multi-slot combinations (sample up to max_combinations)
    active_slots = list(by_slot.keys())
    sampled_count = 0

    # Test 2, 3, 4, 5-attachment combinations across different slots
    for k in [2, 3, 4, 5]:
        if len(active_slots) < k:
            continue
        for slot_comb in itertools.combinations(active_slots, k):
            # Take first 1-2 attachments per chosen slot
            slot_options = [by_slot[s][:2] for s in slot_comb]
            for att_combo in itertools.product(*slot_options):
                if sampled_count >= max_combinations:
                    break
                att_list = list(att_combo)
                label_names = " + ".join([a.name.split()[0] for a in att_list])
                try:
                    b = calculate_modified_stats(
                        weapon=weapon,
                        base_stats=base_stats,
                        attachments=att_list,
                        all_modifiers=all_modifiers,
                        ruleset=ruleset,
                        damage_profiles=damage_profiles,
                        build_label=f"Config ({k} att): {label_names}"
                    )
                    candidates.append(b)
                    sampled_count += 1
                except Exception:
                    continue
            if sampled_count >= max_combinations:
                break

    return candidates


def compute_pareto_frontier(
    candidates: List[EvaluatedBuildStats]
) -> Tuple[List[ParetoBuildPoint], List[ParetoBuildPoint]]:
    """
    Computes the non-dominated Pareto frontier from candidate builds.
    Returns (pareto_optimal_builds, all_evaluated_points).
    """
    if not candidates:
        return [], []

    pareto_optimal_builds: List[ParetoBuildPoint] = []
    all_points: List[ParetoBuildPoint] = []

    for i, candidate in enumerate(candidates):
        dominated = False
        for j, other in enumerate(candidates):
            if i != j and is_dominated(candidate, other):
                dominated = True
                break

        point = ParetoBuildPoint(
            build_label=candidate.build_label,
            attachment_ids=candidate.attachment_ids,
            attachment_names=[a.name for a in candidate.attachments_applied],
            practical_engagement_ms=candidate.mid_pet_ms,
            recoil_index=candidate.recoil_index,
            mobility_index=candidate.mobility_index,
            effective_ads_ms=candidate.effective_ads_ms,
            effective_range_multiplier=candidate.range_multiplier,
            is_pareto_optimal=not dominated,
            dominance_rank=1 if not dominated else 2
        )
        all_points.append(point)
        if not dominated:
            pareto_optimal_builds.append(point)

    # Sort pareto frontier by practical engagement time ascending
    pareto_optimal_builds.sort(key=lambda p: p.practical_engagement_ms)

    return pareto_optimal_builds, all_points
