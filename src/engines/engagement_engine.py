"""
MW4 Weapon Intelligence Lab - Practical Engagement Time (PET) Engine
Calculates realistic human-performance engagement latency incorporating
reaction time, ADS transition, sprint-to-fire delay, theoretical TTK, and accuracy degradation.
"""

from typing import Optional
from ..database.models import PracticalEngagementResult


def calculate_expected_miss_penalty_ms(
    stk: int,
    rpm: float,
    accuracy: float = 0.70
) -> float:
    """
    Calculates the expected time penalty from missed shots based on accuracy probability.
    Expected missed shots = STK * ((1 - Accuracy) / Accuracy)
    Penalty (ms) = Expected Missed Shots * (60,000 / RPM)
    """
    if accuracy >= 1.0 or accuracy <= 0.0:
        return 0.0
    if rpm <= 0:
        return 0.0

    expected_misses = stk * ((1.0 - accuracy) / accuracy)
    shot_interval_ms = 60000.0 / rpm
    return expected_misses * shot_interval_ms


def calculate_practical_engagement_time(
    reaction_ms: float = 200.0,
    ads_ms: float = 240.0,
    sprint_to_fire_ms: float = 200.0,
    theoretical_ttk_ms: float = 230.0,
    stk: int = 4,
    rpm: float = 780.0,
    accuracy: float = 0.70,
    is_sprinting: bool = True,
    is_already_ads: bool = False,
    is_tactical_sprint: bool = False,
    tactical_sprint_to_fire_ms: float = 280.0,
    weapon_id: str = "weapon",
    weapon_name: str = "Weapon",
    distance_m: float = 15.0
) -> PracticalEngagementResult:
    """
    Calculates total Practical Engagement Time (PET) in milliseconds.
    
    Formula:
    PET = reaction_ms + ads_ms_effective + sprint_penalty_effective + theoretical_ttk_ms + expected_miss_penalty_ms
    """
    # ADS handling
    ads_effective = 0.0 if is_already_ads else ads_ms

    # Sprint-to-fire handling
    if is_already_ads or not is_sprinting:
        stf_effective = 0.0
    else:
        stf_effective = tactical_sprint_to_fire_ms if is_tactical_sprint else sprint_to_fire_ms

    # Miss penalty
    miss_penalty_ms = calculate_expected_miss_penalty_ms(stk=stk, rpm=rpm, accuracy=accuracy)

    total_pet_ms = reaction_ms + ads_effective + stf_effective + theoretical_ttk_ms + miss_penalty_ms

    return PracticalEngagementResult(
        weapon_id=weapon_id,
        weapon_name=weapon_name,
        distance_m=round(distance_m, 1),
        reaction_ms=round(reaction_ms, 1),
        ads_ms=round(ads_effective, 1),
        sprint_to_fire_ms=round(stf_effective, 1),
        theoretical_ttk_ms=round(theoretical_ttk_ms, 1),
        expected_miss_penalty_ms=round(miss_penalty_ms, 1),
        practical_engagement_time_ms=round(total_pet_ms, 1),
        accuracy_used=accuracy,
        is_sprinting=is_sprinting,
        stk=stk
    )
