"""
MW4 Weapon Intelligence Lab - Recoil Pattern Simulation Engine
Simulates 2D bullet-by-bullet recoil trajectories on a Cartesian target canvas (X = Horizontal, Y = Vertical).
"""

import math
import random
from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel


class BulletImpact(BaseModel):
    shot_number: int
    x_offset_cm: float  # Horizontal offset in cm from center (+ right, - left)
    y_offset_cm: float  # Vertical offset in cm from center (+ up)
    time_ms: float


class RecoilSimulationResult(BaseModel):
    weapon_id: str
    weapon_name: str
    total_shots: int
    impacts: List[BulletImpact]
    max_vertical_climb_cm: float
    max_horizontal_spread_cm: float
    recoil_area_sq_cm: float
    vertical_reduction_pct: float = 0.0
    horizontal_reduction_pct: float = 0.0


def simulate_recoil_pattern(
    weapon_id: str,
    weapon_name: str,
    recoil_vertical: float,
    recoil_horizontal: float,
    rpm: float,
    magazine_size: int = 30,
    vertical_modifier_pct: float = 0.0,
    horizontal_modifier_pct: float = 0.0,
    distance_m: float = 10.0,
    seed: int = 42
) -> RecoilSimulationResult:
    """
    Simulates a 2D bullet spray pattern against a flat wall at distance_m.
    - Factors in initial shot kick, continuous climb, horizontal sway, and attachment modifiers.
    """
    rng = random.Random(seed)
    effective_vert = max(1.0, recoil_vertical * (1.0 + vertical_modifier_pct / 100.0))
    effective_horiz = max(1.0, recoil_horizontal * (1.0 + horizontal_modifier_pct / 100.0))

    shot_interval_ms = 60000.0 / max(100.0, rpm)
    num_shots = min(magazine_size, 30)

    # Angular spread scaling per meter of distance
    # 1 recoil unit ~ 0.25 degrees of angular deflection
    dist_scale = distance_m * math.tan(math.radians(0.22)) * 100.0  # cm conversion

    impacts: List[BulletImpact] = []
    curr_x = 0.0
    curr_y = 0.0

    # Progressive recoil pattern drift (typical S-curve or upward-right bias)
    drift_direction = 1.0 if (hash(weapon_id) % 2 == 0) else -0.7

    for shot_idx in range(num_shots):
        shot_num = shot_idx + 1
        time_ms = shot_idx * shot_interval_ms

        if shot_idx == 0:
            # First shot is centered on point of aim
            curr_x = 0.0
            curr_y = 0.0
        else:
            # Center-return reticle settling between shots based on weapon cycle rate
            settle_fraction = min(0.25, (shot_interval_ms / 600.0) * 0.15)
            curr_x *= (1.0 - settle_fraction)
            curr_y *= (1.0 - (settle_fraction * 0.5))

            # First 3-5 shots have sharp vertical kick
            if shot_idx <= 4:
                vert_step = (effective_vert * 0.18) * (1.0 + rng.uniform(-0.08, 0.08))
                horiz_step = (effective_horiz * 0.06 * drift_direction) + rng.uniform(-0.05, 0.05)
            # Mid-spray stabilization
            elif shot_idx <= 15:
                vert_step = (effective_vert * 0.12) * (1.0 + rng.uniform(-0.12, 0.12))
                horiz_step = (effective_horiz * 0.10 * drift_direction) + rng.uniform(-0.12, 0.12)
            # Late-spray saturation / horizontal wobble
            else:
                vert_step = (effective_vert * 0.06) * (1.0 + rng.uniform(-0.15, 0.15))
                horiz_step = (effective_horiz * 0.15 * math.sin(shot_idx * 0.8)) + rng.uniform(-0.15, 0.15)

            curr_y += vert_step * (dist_scale * 0.08)
            curr_x += horiz_step * (dist_scale * 0.08)

        impacts.append(
            BulletImpact(
                shot_number=shot_num,
                x_offset_cm=round(curr_x, 2),
                y_offset_cm=round(curr_y, 2),
                time_ms=round(time_ms, 1)
            )
        )

    all_y = [imp.y_offset_cm for imp in impacts]
    all_x = [imp.x_offset_cm for imp in impacts]

    max_vert = max(all_y) - min(all_y)
    max_horiz = max(all_x) - min(all_x)
    area = round(max_vert * max_horiz, 2)

    return RecoilSimulationResult(
        weapon_id=weapon_id,
        weapon_name=weapon_name,
        total_shots=num_shots,
        impacts=impacts,
        max_vertical_climb_cm=round(max_vert, 2),
        max_horizontal_spread_cm=round(max_horiz, 2),
        recoil_area_sq_cm=area,
        vertical_reduction_pct=round(vertical_modifier_pct, 1),
        horizontal_reduction_pct=round(horizontal_modifier_pct, 1)
    )
