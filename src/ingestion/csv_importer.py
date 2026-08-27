"""
MW4 Weapon Intelligence Lab - CSV Ingestion Engine
Strict Pydantic-validated batch importer for weapon statistics, damage profiles, and attachments.
"""

import io
import pandas as pd
from typing import Tuple, List, Dict, Any
from src.database.models import (
    WeaponVersionStats,
    DamageRangeBracket,
    Attachment,
    AttachmentModifier,
    EvidenceLedgerEntry,
    SourceTier,
    VerificationStatus
)
from src.database.repository import IntelligenceRepository


def import_weapon_stats_csv(
    csv_content: str,
    game_version_id: str,
    repo: IntelligenceRepository,
    source_name: str = "Manual CSV Import",
    source_tier: SourceTier = SourceTier.TIER_3
) -> Tuple[int, List[str], List[str]]:
    """
    Imports weapon physical stats from CSV.
    Expected headers: weapon_id,rpm,base_ads_ms,sprint_to_fire_ms,tactical_sprint_to_fire_ms,bullet_velocity_mps,reload_empty_s,reload_tactical_s,recoil_horizontal,recoil_vertical,hipfire_spread_deg,move_speed_mps,ads_move_speed_mps,flinch_resistance
    """
    df = pd.read_csv(io.StringIO(csv_content))
    success_count = 0
    errors: List[str] = []
    logs: List[str] = []

    for idx, row in df.iterrows():
        try:
            weapon_id = str(row["weapon_id"]).strip()
            stat_id = f"{weapon_id}_{game_version_id}"

            stat_model = WeaponVersionStats(
                stat_id=stat_id,
                weapon_id=weapon_id,
                game_version_id=game_version_id,
                rpm=float(row["rpm"]),
                base_ads_ms=float(row["base_ads_ms"]),
                sprint_to_fire_ms=float(row["sprint_to_fire_ms"]),
                tactical_sprint_to_fire_ms=float(row.get("tactical_sprint_to_fire_ms", 0.0)),
                bullet_velocity_mps=float(row["bullet_velocity_mps"]),
                reload_empty_s=float(row["reload_empty_s"]),
                reload_tactical_s=float(row["reload_tactical_s"]),
                recoil_horizontal=float(row["recoil_horizontal"]),
                recoil_vertical=float(row["recoil_vertical"]),
                hipfire_spread_deg=float(row["hipfire_spread_deg"]),
                move_speed_mps=float(row["move_speed_mps"]),
                ads_move_speed_mps=float(row["ads_move_speed_mps"]),
                flinch_resistance=float(row.get("flinch_resistance", 1.0))
            )

            repo.upsert_weapon_stats(stat_model)

            # Record evidence
            evidence = EvidenceLedgerEntry(
                evidence_id=f"ev_csv_{stat_id}",
                target_entity_type="weapon_stats",
                target_entity_id=weapon_id,
                field_name="batch_csv_stats",
                observed_value=f"Imported {stat_id}",
                source_url="local://manual_csv_import",
                source_name=source_name,
                source_tier=source_tier,
                test_method="Validated Batch CSV Ingestion",
                verification_status=VerificationStatus.VERIFIED,
                confidence_score=0.85 if source_tier == SourceTier.TIER_3 else 0.95
            )
            repo.upsert_evidence_entry(evidence)

            success_count += 1
            logs.append(f"Successfully imported stats for {weapon_id}")

        except Exception as e:
            errors.append(f"Row {idx + 1} error: {str(e)}")

    return success_count, logs, errors


def import_damage_profiles_csv(
    csv_content: str,
    game_version_id: str,
    ruleset_id: str,
    repo: IntelligenceRepository
) -> Tuple[int, List[str], List[str]]:
    """
    Imports damage range profiles from CSV.
    Expected headers: weapon_id,range_start_m,range_end_m,damage_head,damage_neck,damage_chest,damage_stomach,damage_limbs
    """
    df = pd.read_csv(io.StringIO(csv_content))
    success_count = 0
    errors: List[str] = []
    logs: List[str] = []

    for idx, row in df.iterrows():
        try:
            weapon_id = str(row["weapon_id"]).strip()
            r_start = float(row["range_start_m"])
            r_end = float(row["range_end_m"])
            profile_id = f"{weapon_id}_{ruleset_id}_{int(r_start)}_{int(r_end)}_{game_version_id}"

            profile = DamageRangeBracket(
                profile_id=profile_id,
                weapon_id=weapon_id,
                game_version_id=game_version_id,
                ruleset_id=ruleset_id,
                range_start_m=r_start,
                range_end_m=r_end,
                damage_head=float(row["damage_head"]),
                damage_neck=float(row["damage_neck"]),
                damage_chest=float(row["damage_chest"]),
                damage_stomach=float(row["damage_stomach"]),
                damage_limbs=float(row["damage_limbs"])
            )

            repo.upsert_damage_profile(profile)
            success_count += 1
            logs.append(f"Imported bracket {r_start}-{r_end}m for {weapon_id}")

        except Exception as e:
            errors.append(f"Row {idx + 1} error: {str(e)}")

    return success_count, logs, errors
