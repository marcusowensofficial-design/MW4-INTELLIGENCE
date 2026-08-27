"""
MW4 Weapon Intelligence Lab - 1v1 Gunsmith Duel Arena Engine
Simulates millisecond-accurate 1v1 shootouts between two customized weapon builds.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from .ttk_engine import get_damage_at_distance, calculate_shots_to_kill
from ..database.models import DamageRangeBracket, Ruleset


class DuelCombatant(BaseModel):
    name: str
    weapon_name: str
    rpm: float
    base_ads_ms: float
    sprint_to_fire_ms: float
    bullet_velocity_mps: float
    open_bolt_delay_ms: float = 0.0
    profiles: List[DamageRangeBracket]
    reaction_ms: float = 200.0
    accuracy: float = 0.70
    is_sprinting: bool = True
    is_already_ads: bool = False
    hit_location: str = "chest"


class CombatEvent(BaseModel):
    timestamp_ms: float
    shooter_name: str
    target_name: str
    event_type: str  # 'ADS_START', 'FIRST_SHOT', 'HIT', 'MISS', 'FATAL'
    damage_dealt: float
    target_hp_remaining: float
    description: str


class DuelResult(BaseModel):
    winner_name: str
    loser_name: str
    time_to_kill_ms: float
    winner_hp_remaining: float
    total_shots_fired_winner: int
    total_shots_fired_loser: int
    distance_m: float
    target_health: float
    combat_log: List[CombatEvent]
    summary_verdict: str


def simulate_1v1_duel(
    combatant_a: DuelCombatant,
    combatant_b: DuelCombatant,
    distance_m: float = 20.0,
    ruleset: Optional[Ruleset] = None
) -> DuelResult:
    """
    Executes a high-precision, millisecond-by-millisecond 1v1 gunfight simulation.
    """
    target_health = ruleset.target_health if ruleset else 100.0
    
    # 1. Calculate time to first trigger discharge
    def get_first_shot_time(c: DuelCombatant) -> float:
        t = c.reaction_ms + c.open_bolt_delay_ms
        if not c.is_already_ads:
            if c.is_sprinting:
                t += max(c.base_ads_ms, c.sprint_to_fire_ms)
            else:
                t += c.base_ads_ms
        return t

    first_shot_a = get_first_shot_time(combatant_a)
    first_shot_b = get_first_shot_time(combatant_b)

    # 2. Damage per shot at given distance
    dmg_a = get_damage_at_distance(distance_m, combatant_a.profiles, combatant_a.hit_location)
    dmg_b = get_damage_at_distance(distance_m, combatant_b.profiles, combatant_b.hit_location)

    interval_a = 60000.0 / max(100.0, combatant_a.rpm)
    interval_b = 60000.0 / max(100.0, combatant_b.rpm)

    flight_time_a = (distance_m / max(100.0, combatant_a.bullet_velocity_mps)) * 1000.0
    flight_time_b = (distance_m / max(100.0, combatant_b.bullet_velocity_mps)) * 1000.0

    # 3. Schedule shots for both combatants up to 50 rounds
    events_queue = []

    # Combatant A shots
    for i in range(50):
        discharge_t = first_shot_a + (i * interval_a)
        impact_t = discharge_t + flight_time_a
        is_hit = ((i * 7 + 3) % 100) < (combatant_a.accuracy * 100)
        events_queue.append({
            "impact_time": impact_t,
            "discharge_time": discharge_t,
            "shooter": combatant_a,
            "target": combatant_b,
            "is_hit": is_hit,
            "damage": dmg_a if is_hit else 0.0,
            "shot_num": i + 1
        })

    # Combatant B shots
    for i in range(50):
        discharge_t = first_shot_b + (i * interval_b)
        impact_t = discharge_t + flight_time_b
        is_hit = ((i * 11 + 5) % 100) < (combatant_b.accuracy * 100)
        events_queue.append({
            "impact_time": impact_t,
            "discharge_time": discharge_t,
            "shooter": combatant_b,
            "target": combatant_a,
            "is_hit": is_hit,
            "damage": dmg_b if is_hit else 0.0,
            "shot_num": i + 1
        })

    # Sort all scheduled impacts chronologically
    events_queue.sort(key=lambda x: x["impact_time"])

    # 4. Resolve combat timeline
    hp_a = target_health
    hp_b = target_health
    combat_log: List[CombatEvent] = []

    winner = None
    loser = None
    fatal_time = 0.0
    shots_a_fired = 0
    shots_b_fired = 0

    for ev in events_queue:
        if hp_a <= 0 or hp_b <= 0:
            break

        shooter = ev["shooter"]
        target = ev["target"]
        impact_t = round(ev["impact_time"], 1)

        if shooter.name == combatant_a.name:
            shots_a_fired += 1
            if ev["is_hit"]:
                hp_b = max(0.0, hp_b - ev["damage"])
                combat_log.append(
                    CombatEvent(
                        timestamp_ms=impact_t,
                        shooter_name=shooter.name,
                        target_name=target.name,
                        event_type="HIT" if hp_b > 0 else "FATAL",
                        damage_dealt=ev["damage"],
                        target_hp_remaining=round(hp_b, 1),
                        description=f"{shooter.name} landed Shot #{ev['shot_num']} on {target.name} for {ev['damage']} DMG ({round(hp_b, 1)} HP left)"
                    )
                )
                if hp_b <= 0:
                    winner = combatant_a
                    loser = combatant_b
                    fatal_time = impact_t
                    break
            else:
                combat_log.append(
                    CombatEvent(
                        timestamp_ms=impact_t,
                        shooter_name=shooter.name,
                        target_name=target.name,
                        event_type="MISS",
                        damage_dealt=0.0,
                        target_hp_remaining=round(hp_b, 1),
                        description=f"{shooter.name} missed Shot #{ev['shot_num']}"
                    )
                )
        else:
            shots_b_fired += 1
            if ev["is_hit"]:
                hp_a = max(0.0, hp_a - ev["damage"])
                combat_log.append(
                    CombatEvent(
                        timestamp_ms=impact_t,
                        shooter_name=shooter.name,
                        target_name=target.name,
                        event_type="HIT" if hp_a > 0 else "FATAL",
                        damage_dealt=ev["damage"],
                        target_hp_remaining=round(hp_a, 1),
                        description=f"{shooter.name} landed Shot #{ev['shot_num']} on {target.name} for {ev['damage']} DMG ({round(hp_a, 1)} HP left)"
                    )
                )
                if hp_a <= 0:
                    winner = combatant_b
                    loser = combatant_a
                    fatal_time = impact_t
                    break
            else:
                combat_log.append(
                    CombatEvent(
                        timestamp_ms=impact_t,
                        shooter_name=shooter.name,
                        target_name=target.name,
                        event_type="MISS",
                        damage_dealt=0.0,
                        target_hp_remaining=round(hp_a, 1),
                        description=f"{shooter.name} missed Shot #{ev['shot_num']}"
                    )
                )

    if not winner:
        winner = combatant_a if hp_a >= hp_b else combatant_b
        loser = combatant_b if winner == combatant_a else combatant_a
        fatal_time = 2000.0

    winner_hp = round(hp_a if winner.name == combatant_a.name else hp_b, 1)
    diff_ms = abs(first_shot_a - first_shot_b)

    verdict = (
        f"🏆 {winner.name} ({winner.weapon_name}) eliminates {loser.name} in {fatal_time:.1f}ms "
        f"with {winner_hp} HP remaining at {distance_m:.0f}m."
    )

    return DuelResult(
        winner_name=winner.name,
        loser_name=loser.name,
        time_to_kill_ms=fatal_time,
        winner_hp_remaining=winner_hp,
        total_shots_fired_winner=shots_a_fired if winner == combatant_a else shots_b_fired,
        total_shots_fired_loser=shots_b_fired if winner == combatant_a else shots_a_fired,
        distance_m=distance_m,
        target_health=target_health,
        combat_log=combat_log,
        summary_verdict=verdict
    )
