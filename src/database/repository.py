"""
MW4 Weapon Intelligence Lab - Repository Layer
Parameterized DuckDB queries ensuring strict data integrity and type conversions.
"""

import json
from typing import List, Optional, Dict, Any
from src.database.connection import db_manager, DatabaseManager
from src.database.models import (
    GameVersion,
    Ruleset,
    Weapon,
    WeaponVersionStats,
    DamageRangeBracket,
    Attachment,
    AttachmentModifier,
    EvidenceLedgerEntry,
    AIReviewItem,
    SourceSnapshot,
    CustomBuild,
    StatDeltaEvent,
    CommunityMetaConsensus,
    MetaBuildPreset,
    WeaponClass,
    FiringMode,
    AttachmentSlot,
    ModifierType,
    SourceTier,
    VerificationStatus
)


class IntelligenceRepository:
    """Repository layer for weapon stats, attachments, versions, rulesets, and evidence."""

    def __init__(self, manager: DatabaseManager = db_manager):
        self.manager = manager

    # -----------------------------------------------------------------------
    # Game Versions
    # -----------------------------------------------------------------------
    def get_game_versions(self) -> List[GameVersion]:
        conn = self.manager.get_connection()
        try:
            rows = conn.execute(
                "SELECT version_id, release_date, patch_name, is_active, notes FROM game_versions ORDER BY release_date DESC"
            ).fetchall()
            return [
                GameVersion(
                    version_id=r[0],
                    release_date=r[1],
                    patch_name=r[2],
                    is_active=bool(r[3]),
                    notes=r[4]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def get_active_game_version(self) -> Optional[GameVersion]:
        versions = self.get_game_versions()
        for v in versions:
            if v.is_active:
                return v
        return versions[0] if versions else None

    def upsert_game_version(self, version: GameVersion) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO game_versions (version_id, release_date, patch_name, is_active, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                [version.version_id, version.release_date, version.patch_name, version.is_active, version.notes]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Rulesets
    # -----------------------------------------------------------------------
    def get_rulesets(self) -> List[Ruleset]:
        conn = self.manager.get_connection()
        try:
            rows = conn.execute(
                """
                SELECT ruleset_id, name, description, target_health, regen_delay_ms, 
                       regen_rate_hp_per_sec, friendly_fire, min_stk_cap, body_multipliers_json 
                FROM rulesets
                """
            ).fetchall()
            return [
                Ruleset(
                    ruleset_id=r[0],
                    name=r[1],
                    description=r[2] or "",
                    target_health=r[3],
                    regen_delay_ms=r[4],
                    regen_rate_hp_per_sec=r[5],
                    friendly_fire=bool(r[6]),
                    min_stk_cap=r[7],
                    body_multipliers=json.loads(r[8]) if r[8] else {}
                )
                for r in rows
            ]
        finally:
            conn.close()

    def get_ruleset(self, ruleset_id: str) -> Optional[Ruleset]:
        rulesets = self.get_rulesets()
        for r in rulesets:
            if r.ruleset_id == ruleset_id:
                return r
        return None

    def upsert_ruleset(self, ruleset: Ruleset) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO rulesets 
                (ruleset_id, name, description, target_health, regen_delay_ms, regen_rate_hp_per_sec, 
                 friendly_fire, min_stk_cap, body_multipliers_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    ruleset.ruleset_id,
                    ruleset.name,
                    ruleset.description,
                    ruleset.target_health,
                    ruleset.regen_delay_ms,
                    ruleset.regen_rate_hp_per_sec,
                    ruleset.friendly_fire,
                    ruleset.min_stk_cap,
                    json.dumps(ruleset.body_multipliers)
                ]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Weapons
    # -----------------------------------------------------------------------
    def get_weapons(self, weapon_class: Optional[str] = None) -> List[Weapon]:
        conn = self.manager.get_connection()
        try:
            if weapon_class:
                rows = conn.execute(
                    """
                    SELECT weapon_id, name, weapon_class, firing_mode, default_rpm, base_mag_size,
                           burst_count, burst_delay_ms, is_dlc, is_active, description
                    FROM weapons WHERE weapon_class = ? AND is_active = TRUE ORDER BY name ASC
                    """,
                    [weapon_class]
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT weapon_id, name, weapon_class, firing_mode, default_rpm, base_mag_size,
                           burst_count, burst_delay_ms, is_dlc, is_active, description
                    FROM weapons WHERE is_active = TRUE ORDER BY weapon_class ASC, name ASC
                    """
                ).fetchall()

            return [
                Weapon(
                    weapon_id=r[0],
                    name=r[1],
                    weapon_class=WeaponClass(r[2]),
                    firing_mode=FiringMode(r[3]),
                    default_rpm=r[4],
                    base_mag_size=r[5],
                    burst_count=r[6],
                    burst_delay_ms=r[7],
                    is_dlc=bool(r[8]),
                    is_active=bool(r[9]),
                    description=r[10]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def get_weapon(self, weapon_id: str) -> Optional[Weapon]:
        conn = self.manager.get_connection()
        try:
            r = conn.execute(
                """
                SELECT weapon_id, name, weapon_class, firing_mode, default_rpm, base_mag_size,
                       burst_count, burst_delay_ms, is_dlc, is_active, description
                FROM weapons WHERE weapon_id = ?
                """,
                [weapon_id]
            ).fetchone()
            if not r:
                return None
            return Weapon(
                weapon_id=r[0],
                name=r[1],
                weapon_class=WeaponClass(r[2]),
                firing_mode=FiringMode(r[3]),
                default_rpm=r[4],
                base_mag_size=r[5],
                burst_count=r[6],
                burst_delay_ms=r[7],
                is_dlc=bool(r[8]),
                is_active=bool(r[9]),
                description=r[10]
            )
        finally:
            conn.close()

    def upsert_weapon(self, weapon: Weapon) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO weapons
                (weapon_id, name, weapon_class, firing_mode, default_rpm, base_mag_size,
                 burst_count, burst_delay_ms, is_dlc, is_active, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    weapon.weapon_id,
                    weapon.name,
                    weapon.weapon_class.value,
                    weapon.firing_mode.value,
                    weapon.default_rpm,
                    weapon.base_mag_size,
                    weapon.burst_count,
                    weapon.burst_delay_ms,
                    weapon.is_dlc,
                    weapon.is_active,
                    weapon.description
                ]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Weapon Version Stats
    # -----------------------------------------------------------------------
    def get_weapon_stats(self, weapon_id: str, version_id: str) -> Optional[WeaponVersionStats]:
        conn = self.manager.get_connection()
        try:
            r = conn.execute(
                """
                SELECT stat_id, weapon_id, game_version_id, rpm, base_ads_ms, sprint_to_fire_ms,
                       tactical_sprint_to_fire_ms, bullet_velocity_mps, reload_empty_s, reload_tactical_s,
                       recoil_horizontal, recoil_vertical, hipfire_spread_deg, move_speed_mps,
                       ads_move_speed_mps, flinch_resistance, open_bolt_delay_ms,
                       reload_add_ammo_s, swap_speed_raise_ms, swap_speed_stow_ms, tac_sprint_speed_mps
                FROM weapon_version_stats
                WHERE weapon_id = ? AND game_version_id = ?
                """,
                [weapon_id, version_id]
            ).fetchone()
            if not r:
                return None
            return WeaponVersionStats(
                stat_id=r[0],
                weapon_id=r[1],
                game_version_id=r[2],
                rpm=r[3],
                base_ads_ms=r[4],
                sprint_to_fire_ms=r[5],
                tactical_sprint_to_fire_ms=r[6],
                bullet_velocity_mps=r[7],
                reload_empty_s=r[8],
                reload_tactical_s=r[9],
                recoil_horizontal=r[10],
                recoil_vertical=r[11],
                hipfire_spread_deg=r[12],
                move_speed_mps=r[13],
                ads_move_speed_mps=r[14],
                flinch_resistance=r[15],
                open_bolt_delay_ms=r[16] if len(r) > 16 and r[16] is not None else 0.0,
                reload_add_ammo_s=float(r[17]) if len(r) > 17 and r[17] is not None else round(float(r[9]) * 0.68, 2),
                swap_speed_raise_ms=float(r[18]) if len(r) > 18 and r[18] is not None else 350.0,
                swap_speed_stow_ms=float(r[19]) if len(r) > 19 and r[19] is not None else 250.0,
                tac_sprint_speed_mps=float(r[20]) if len(r) > 20 and r[20] is not None else round(float(r[13]) * 1.32, 2)
            )
        finally:
            conn.close()

    def upsert_weapon_stats(self, stats: WeaponVersionStats) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO weapon_version_stats
                (stat_id, weapon_id, game_version_id, rpm, base_ads_ms, sprint_to_fire_ms,
                 tactical_sprint_to_fire_ms, bullet_velocity_mps, reload_empty_s, reload_tactical_s,
                 recoil_horizontal, recoil_vertical, hipfire_spread_deg, move_speed_mps,
                 ads_move_speed_mps, flinch_resistance, open_bolt_delay_ms,
                 reload_add_ammo_s, swap_speed_raise_ms, swap_speed_stow_ms, tac_sprint_speed_mps)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    stats.stat_id,
                    stats.weapon_id,
                    stats.game_version_id,
                    stats.rpm,
                    stats.base_ads_ms,
                    stats.sprint_to_fire_ms,
                    stats.tactical_sprint_to_fire_ms,
                    stats.bullet_velocity_mps,
                    stats.reload_empty_s,
                    stats.reload_tactical_s,
                    stats.recoil_horizontal,
                    stats.recoil_vertical,
                    stats.hipfire_spread_deg,
                    stats.move_speed_mps,
                    stats.ads_move_speed_mps,
                    stats.flinch_resistance,
                    stats.open_bolt_delay_ms,
                    stats.reload_add_ammo_s,
                    stats.swap_speed_raise_ms,
                    stats.swap_speed_stow_ms,
                    stats.tac_sprint_speed_mps
                ]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Damage Profiles
    # -----------------------------------------------------------------------
    def get_damage_profiles(self, weapon_id: str, version_id: str, ruleset_id: str = "core") -> List[DamageRangeBracket]:
        conn = self.manager.get_connection()
        try:
            rows = conn.execute(
                """
                SELECT profile_id, weapon_id, game_version_id, ruleset_id, range_start_m, range_end_m,
                       damage_head, damage_neck, damage_chest, damage_stomach, damage_limbs
                FROM weapon_damage_profiles
                WHERE weapon_id = ? AND game_version_id = ? AND ruleset_id = ?
                ORDER BY range_start_m ASC
                """,
                [weapon_id, version_id, ruleset_id]
            ).fetchall()
            return [
                DamageRangeBracket(
                    profile_id=r[0],
                    weapon_id=r[1],
                    game_version_id=r[2],
                    ruleset_id=r[3],
                    range_start_m=r[4],
                    range_end_m=r[5],
                    damage_head=r[6],
                    damage_neck=r[7],
                    damage_chest=r[8],
                    damage_stomach=r[9],
                    damage_limbs=r[10]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def upsert_damage_profile(self, profile: DamageRangeBracket) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO weapon_damage_profiles
                (profile_id, weapon_id, game_version_id, ruleset_id, range_start_m, range_end_m,
                 damage_head, damage_neck, damage_chest, damage_stomach, damage_limbs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    profile.profile_id,
                    profile.weapon_id,
                    profile.game_version_id,
                    profile.ruleset_id,
                    profile.range_start_m,
                    profile.range_end_m,
                    profile.damage_head,
                    profile.damage_neck,
                    profile.damage_chest,
                    profile.damage_stomach,
                    profile.damage_limbs
                ]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Attachments & Modifiers
    # -----------------------------------------------------------------------
    def get_attachments(self, weapon_id: Optional[str] = None, slot: Optional[str] = None) -> List[Attachment]:
        conn = self.manager.get_connection()
        try:
            query = "SELECT attachment_id, name, slot, weapon_id_compat, is_universal, unlock_level, description, pick_rate_pct, is_meta_favorite FROM attachments WHERE 1=1"
            params: List[Any] = []
            if weapon_id:
                query += " AND (is_universal = TRUE OR weapon_id_compat = ?)"
                params.append(weapon_id)
            if slot:
                query += " AND slot = ?"
                params.append(slot)
            query += " ORDER BY slot ASC, pick_rate_pct DESC, unlock_level ASC, name ASC"

            rows = conn.execute(query, params).fetchall()
            return [
                Attachment(
                    attachment_id=r[0],
                    name=r[1],
                    slot=AttachmentSlot(r[2]),
                    weapon_id_compat=r[3],
                    is_universal=bool(r[4]),
                    unlock_level=r[5],
                    description=r[6],
                    pick_rate_pct=float(r[7]) if len(r) > 7 and r[7] is not None else 0.0,
                    is_meta_favorite=bool(r[8]) if len(r) > 8 and r[8] is not None else False
                )
                for r in rows
            ]
        finally:
            conn.close()

    def get_attachment(self, attachment_id: str) -> Optional[Attachment]:
        conn = self.manager.get_connection()
        try:
            r = conn.execute(
                "SELECT attachment_id, name, slot, weapon_id_compat, is_universal, unlock_level, description, pick_rate_pct, is_meta_favorite FROM attachments WHERE attachment_id = ?",
                [attachment_id]
            ).fetchone()
            if not r:
                return None
            return Attachment(
                attachment_id=r[0],
                name=r[1],
                slot=AttachmentSlot(r[2]),
                weapon_id_compat=r[3],
                is_universal=bool(r[4]),
                unlock_level=r[5],
                description=r[6],
                pick_rate_pct=float(r[7]) if len(r) > 7 and r[7] is not None else 0.0,
                is_meta_favorite=bool(r[8]) if len(r) > 8 and r[8] is not None else False
            )
        finally:
            conn.close()

    def upsert_attachment(self, att: Attachment) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO attachments
                (attachment_id, name, slot, weapon_id_compat, is_universal, unlock_level, description, pick_rate_pct, is_meta_favorite)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    att.attachment_id,
                    att.name,
                    att.slot.value,
                    att.weapon_id_compat,
                    att.is_universal,
                    att.unlock_level,
                    att.description,
                    att.pick_rate_pct,
                    att.is_meta_favorite
                ]
            )
        finally:
            conn.close()

    def get_most_popular_attachments(self, weapon_id: str, max_slots: int = 5) -> List[Attachment]:
        """
        Retrieves the top community meta attachment for up to max_slots distinct slots
        based on real scraped pick rate percentages.
        """
        all_atts = self.get_attachments(weapon_id=weapon_id)
        # Group by slot and pick the one with highest pick_rate_pct
        slot_bests: Dict[str, Attachment] = {}
        for a in all_atts:
            s_val = a.slot.value
            if s_val not in slot_bests or a.pick_rate_pct > slot_bests[s_val].pick_rate_pct:
                slot_bests[s_val] = a
        
        # Sort by pick_rate_pct descending and pick top 5
        sorted_bests = sorted(slot_bests.values(), key=lambda x: x.pick_rate_pct, reverse=True)
        return sorted_bests[:max_slots]

    def get_attachment_modifiers(
        self,
        attachment_id: Optional[str] = None,
        version_id: Optional[str] = None
    ) -> List[AttachmentModifier]:
        conn = self.manager.get_connection()
        try:
            actual_att_id = attachment_id
            actual_ver_id = version_id

            # If only a single positional argument was passed, check if it represents a version_id
            if actual_att_id is not None and actual_ver_id is None:
                if actual_att_id.startswith("v") and ("." in actual_att_id or "-" in actual_att_id):
                    actual_ver_id = actual_att_id
                    actual_att_id = None

            query = """
            SELECT mod_id, attachment_id, game_version_id, stat_key, mod_type, mod_value, notes
            FROM attachment_modifiers
            WHERE 1=1
            """
            params: List[Any] = []
            if actual_att_id:
                query += " AND attachment_id = ?"
                params.append(actual_att_id)
            if actual_ver_id:
                query += " AND game_version_id = ?"
                params.append(actual_ver_id)

            rows = conn.execute(query, params).fetchall()
            return [
                AttachmentModifier(
                    mod_id=r[0],
                    attachment_id=r[1],
                    game_version_id=r[2],
                    stat_key=r[3],
                    mod_type=ModifierType(r[4]),
                    mod_value=r[5],
                    notes=r[6]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def upsert_attachment_modifier(self, mod: AttachmentModifier) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO attachment_modifiers
                (mod_id, attachment_id, game_version_id, stat_key, mod_type, mod_value, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    mod.mod_id,
                    mod.attachment_id,
                    mod.game_version_id,
                    mod.stat_key,
                    mod.mod_type.value,
                    mod.mod_value,
                    mod.notes
                ]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Evidence Ledger
    # -----------------------------------------------------------------------
    def get_evidence_ledger(
        self,
        target_entity_type: Optional[str] = None,
        target_entity_id: Optional[str] = None
    ) -> List[EvidenceLedgerEntry]:
        conn = self.manager.get_connection()
        try:
            query = """
            SELECT evidence_id, target_entity_type, target_entity_id, field_name, observed_value,
                   source_url, source_name, source_tier, test_method, captured_timestamp,
                   recorded_by, verification_status, confidence_score, notes
            FROM evidence_ledger WHERE 1=1
            """
            params: List[Any] = []
            if target_entity_type:
                query += " AND target_entity_type = ?"
                params.append(target_entity_type)
            if target_entity_id:
                query += " AND target_entity_id = ?"
                params.append(target_entity_id)
            query += " ORDER BY captured_timestamp DESC"

            rows = conn.execute(query, params).fetchall()
            return [
                EvidenceLedgerEntry(
                    evidence_id=r[0],
                    target_entity_type=r[1],
                    target_entity_id=r[2],
                    field_name=r[3],
                    observed_value=r[4],
                    source_url=r[5],
                    source_name=r[6],
                    source_tier=SourceTier(r[7]),
                    test_method=r[8],
                    captured_timestamp=r[9],
                    recorded_by=r[10],
                    verification_status=VerificationStatus(r[11]),
                    confidence_score=r[12],
                    notes=r[13]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def upsert_evidence_entry(self, entry: EvidenceLedgerEntry) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO evidence_ledger
                (evidence_id, target_entity_type, target_entity_id, field_name, observed_value,
                 source_url, source_name, source_tier, test_method, captured_timestamp,
                 recorded_by, verification_status, confidence_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    entry.evidence_id,
                    entry.target_entity_type,
                    entry.target_entity_id,
                    entry.field_name,
                    str(entry.observed_value),
                    entry.source_url,
                    entry.source_name,
                    entry.source_tier.value,
                    entry.test_method,
                    entry.captured_timestamp,
                    entry.recorded_by,
                    entry.verification_status.value,
                    entry.confidence_score,
                    entry.notes
                ]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # AI Review Queue
    # -----------------------------------------------------------------------
    def get_ai_review_queue(self, status: Optional[str] = None) -> List[AIReviewItem]:
        conn = self.manager.get_connection()
        try:
            if status:
                rows = conn.execute(
                    """
                    SELECT queue_id, proposed_payload_json, ai_model, confidence_claim, rationale,
                           status, created_at, reviewed_by, reviewed_at, rejection_reason
                    FROM ai_review_queue WHERE status = ? ORDER BY created_at DESC
                    """,
                    [status]
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT queue_id, proposed_payload_json, ai_model, confidence_claim, rationale,
                           status, created_at, reviewed_by, reviewed_at, rejection_reason
                    FROM ai_review_queue ORDER BY created_at DESC
                    """
                ).fetchall()

            return [
                AIReviewItem(
                    queue_id=r[0],
                    proposed_payload=json.loads(r[1]),
                    ai_model=r[2],
                    confidence_claim=r[3],
                    rationale=r[4],
                    status=r[5],
                    created_at=r[6],
                    reviewed_by=r[7],
                    reviewed_at=r[8],
                    rejection_reason=r[9]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def upsert_ai_review_item(self, item: AIReviewItem) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO ai_review_queue
                (queue_id, proposed_payload_json, ai_model, confidence_claim, rationale,
                 status, created_at, reviewed_by, reviewed_at, rejection_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    item.queue_id,
                    json.dumps(item.proposed_payload),
                    item.ai_model,
                    item.confidence_claim,
                    item.rationale,
                    item.status,
                    item.created_at,
                    item.reviewed_by,
                    item.reviewed_at,
                    item.rejection_reason
                ]
            )
        finally:
            conn.close()

    def update_ai_review_status(
        self,
        queue_id: str,
        status: str,
        reviewed_by: str,
        rejection_reason: Optional[str] = None
    ) -> None:
        from datetime import datetime, timezone
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                UPDATE ai_review_queue
                SET status = ?, reviewed_by = ?, reviewed_at = ?, rejection_reason = ?
                WHERE queue_id = ?
                """,
                [status, reviewed_by, datetime.now(timezone.utc).isoformat(), rejection_reason, queue_id]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Custom User Builds
    # -----------------------------------------------------------------------
    def get_custom_builds(self, weapon_id: Optional[str] = None) -> List[CustomBuild]:
        conn = self.manager.get_connection()
        try:
            if weapon_id:
                rows = conn.execute(
                    "SELECT build_id, user_label, weapon_id, game_version_id, ruleset_id, attachment_ids_json, notes, created_at FROM custom_builds WHERE weapon_id = ? ORDER BY created_at DESC",
                    [weapon_id]
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT build_id, user_label, weapon_id, game_version_id, ruleset_id, attachment_ids_json, notes, created_at FROM custom_builds ORDER BY created_at DESC"
                ).fetchall()

            return [
                CustomBuild(
                    build_id=r[0],
                    user_label=r[1],
                    weapon_id=r[2],
                    game_version_id=r[3],
                    ruleset_id=r[4],
                    attachment_ids=json.loads(r[5]) if r[5] else [],
                    notes=r[6],
                    created_at=r[7]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def upsert_custom_build(self, build: CustomBuild) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO custom_builds
                (build_id, user_label, weapon_id, game_version_id, ruleset_id, attachment_ids_json, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    build.build_id,
                    build.user_label,
                    build.weapon_id,
                    build.game_version_id,
                    build.ruleset_id,
                    json.dumps(build.attachment_ids),
                    build.notes,
                    build.created_at
                ]
            )
        finally:
            conn.close()

    def delete_custom_build(self, build_id: str) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute("DELETE FROM custom_builds WHERE build_id = ?", [build_id])
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Source Snapshots
    # -----------------------------------------------------------------------
    def get_source_snapshots(self) -> List[SourceSnapshot]:
        conn = self.manager.get_connection()
        try:
            rows = conn.execute(
                "SELECT snapshot_id, source_id, fetch_timestamp, content_hash, raw_payload_path, diff_summary FROM source_snapshots ORDER BY fetch_timestamp DESC"
            ).fetchall()
            return [
                SourceSnapshot(
                    snapshot_id=r[0],
                    source_id=r[1],
                    fetch_timestamp=r[2],
                    content_hash=r[3],
                    raw_payload_path=r[4],
                    diff_summary=r[5]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def upsert_source_snapshot(self, snapshot: SourceSnapshot) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO source_snapshots
                (snapshot_id, source_id, fetch_timestamp, content_hash, raw_payload_path, diff_summary)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                [
                    snapshot.snapshot_id,
                    snapshot.source_id,
                    snapshot.fetch_timestamp,
                    snapshot.content_hash,
                    snapshot.raw_payload_path,
                    snapshot.diff_summary
                ]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Chronological Stat Delta Events (Patch Lineage)
    # -----------------------------------------------------------------------
    def get_stat_delta_events(
        self,
        weapon_id: Optional[str] = None,
        stat_name: Optional[str] = None,
        patch_version_id: Optional[str] = None
    ) -> List[StatDeltaEvent]:
        conn = self.manager.get_connection()
        try:
            query = """
            SELECT event_id, weapon_id, stat_name, patch_version_id, effective_date,
                   previous_value, delta_type, delta_value, new_value,
                   official_patch_url, developer_notes, captured_timestamp
            FROM stat_delta_events WHERE 1=1
            """
            params: List[Any] = []
            if weapon_id:
                query += " AND weapon_id = ?"
                params.append(weapon_id)
            if stat_name:
                query += " AND stat_name = ?"
                params.append(stat_name)
            if patch_version_id:
                query += " AND patch_version_id = ?"
                params.append(patch_version_id)
            query += " ORDER BY effective_date ASC, captured_timestamp ASC"

            rows = conn.execute(query, params).fetchall()
            return [
                StatDeltaEvent(
                    event_id=r[0],
                    weapon_id=r[1],
                    stat_name=r[2],
                    patch_version_id=r[3],
                    effective_date=r[4],
                    previous_value=float(r[5]),
                    delta_type=r[6],
                    delta_value=float(r[7]),
                    new_value=float(r[8]),
                    official_patch_url=r[9],
                    developer_notes=r[10],
                    captured_timestamp=r[11]
                )
                for r in rows
            ]
        finally:
            conn.close()

    def upsert_stat_delta_event(self, event: StatDeltaEvent) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO stat_delta_events
                (event_id, weapon_id, stat_name, patch_version_id, effective_date,
                 previous_value, delta_type, delta_value, new_value,
                 official_patch_url, developer_notes, captured_timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    event.event_id,
                    event.weapon_id,
                    event.stat_name,
                    event.patch_version_id,
                    event.effective_date,
                    event.previous_value,
                    event.delta_type,
                    event.delta_value,
                    event.new_value,
                    event.official_patch_url,
                    event.developer_notes,
                    event.captured_timestamp
                ]
            )
        finally:
            conn.close()

    # -----------------------------------------------------------------------
    # Community Meta Consensus (WZStats, WZRanked, CODMunity, Dexerto, CharlieIntel, Dot Esports)
    # -----------------------------------------------------------------------
    def get_community_consensus(self, game_version_id: Optional[str] = None) -> Dict[str, CommunityMetaConsensus]:
        conn = self.manager.get_connection()
        try:
            query = """
            SELECT consensus_id, weapon_id, game_version_id,
                   wzstats_tier, wzranked_tier, codmunity_tier,
                   dexerto_tier, charlie_tier, dotesports_tier,
                   consensus_tag, badge_color,
                   community_pick_rate_pct, community_kd_ratio, recommended_secondary,
                   global_win_rate_pct, meta_trend_delta_pct, headshot_pct, kills_per_minute,
                   last_updated
            FROM community_meta_consensus WHERE 1=1
            """
            params: List[Any] = []
            if game_version_id:
                query += " AND game_version_id = ?"
                params.append(game_version_id)

            rows = conn.execute(query, params).fetchall()
            result: Dict[str, CommunityMetaConsensus] = {}
            for r in rows:
                result[r[1]] = CommunityMetaConsensus(
                    consensus_id=r[0],
                    weapon_id=r[1],
                    game_version_id=r[2],
                    wzstats_tier=r[3],
                    wzranked_tier=r[4],
                    codmunity_tier=r[5],
                    dexerto_tier=r[6],
                    charlie_tier=r[7],
                    dotesports_tier=r[8],
                    consensus_tag=r[9],
                    badge_color=r[10],
                    community_pick_rate_pct=float(r[11]) if r[11] is not None else 5.0,
                    community_kd_ratio=float(r[12]) if r[12] is not None else 1.05,
                    recommended_secondary=str(r[13]) if r[13] else "Renetti 3-Burst",
                    global_win_rate_pct=float(r[14]) if len(r) > 14 and r[14] is not None else 50.0,
                    meta_trend_delta_pct=float(r[15]) if len(r) > 15 and r[15] is not None else 0.0,
                    headshot_pct=float(r[16]) if len(r) > 16 and r[16] is not None else 18.0,
                    kills_per_minute=float(r[17]) if len(r) > 17 and r[17] is not None else 1.85,
                    last_updated=r[18] if len(r) > 18 else datetime.now(timezone.utc).isoformat()
                )
            return result
        finally:
            conn.close()

    def upsert_community_consensus(self, item: CommunityMetaConsensus) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO community_meta_consensus
                (consensus_id, weapon_id, game_version_id,
                 wzstats_tier, wzranked_tier, codmunity_tier,
                 dexerto_tier, charlie_tier, dotesports_tier,
                 consensus_tag, badge_color,
                 community_pick_rate_pct, community_kd_ratio, recommended_secondary,
                 global_win_rate_pct, meta_trend_delta_pct, headshot_pct, kills_per_minute,
                 last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    item.consensus_id,
                    item.weapon_id,
                    item.game_version_id,
                    item.wzstats_tier,
                    item.wzranked_tier,
                    item.codmunity_tier,
                    item.dexerto_tier,
                    item.charlie_tier,
                    item.dotesports_tier,
                    item.consensus_tag,
                    item.badge_color,
                    item.community_pick_rate_pct,
                    item.community_kd_ratio,
                    item.recommended_secondary,
                    item.global_win_rate_pct,
                    item.meta_trend_delta_pct,
                    item.headshot_pct,
                    item.kills_per_minute,
                    item.last_updated
                ]
            )
        finally:
            conn.close()

    def get_meta_builds(
        self,
        weapon_id: Optional[str] = None,
        game_version_id: Optional[str] = None,
        archetype: Optional[str] = None
    ) -> List[MetaBuildPreset]:
        conn = self.manager.get_connection()
        try:
            query = """
            SELECT build_id, weapon_id, game_version_id, build_name,
                   archetype, archetype_display, source_outlet,
                   attachment_ids_json, perk_1_name, perk_2_name, perk_3_name,
                   tactical_name, lethal_name, field_upgrade_name,
                   secondary_name, secondary_role, secondary_attachments_json,
                   best_maps, playstyle_notes, share_code, is_verified_meta, created_at
            FROM meta_build_presets WHERE 1=1
            """
            params: List[Any] = []
            if weapon_id:
                query += " AND weapon_id = ?"
                params.append(weapon_id)
            if game_version_id:
                query += " AND game_version_id = ?"
                params.append(game_version_id)
            if archetype:
                query += " AND archetype = ?"
                params.append(archetype)

            query += " ORDER BY created_at ASC"

            rows = conn.execute(query, params).fetchall()
            result: List[MetaBuildPreset] = []
            for r in rows:
                att_ids = json.loads(r[7]) if r[7] else []
                sec_att_ids = json.loads(r[16]) if r[16] else []
                result.append(
                    MetaBuildPreset(
                        build_id=r[0],
                        weapon_id=r[1],
                        game_version_id=r[2],
                        build_name=r[3],
                        archetype=r[4],
                        archetype_display=r[5],
                        source_outlet=r[6],
                        attachment_ids=att_ids,
                        perk_1_name=r[8],
                        perk_2_name=r[9],
                        perk_3_name=r[10],
                        tactical_name=r[11],
                        lethal_name=r[12],
                        field_upgrade_name=r[13],
                        secondary_name=r[14] or "Renetti 3-Burst",
                        secondary_role=r[15] or "180ms Fast-Swap Pocket Pistol",
                        secondary_attachments=sec_att_ids,
                        best_maps=r[17],
                        playstyle_notes=r[18],
                        share_code=r[19],
                        is_verified_meta=bool(r[20]),
                        created_at=r[21]
                    )
                )
            return result
        finally:
            conn.close()

    def upsert_meta_build(self, item: MetaBuildPreset) -> None:
        conn = self.manager.get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO meta_build_presets
                (build_id, weapon_id, game_version_id, build_name,
                 archetype, archetype_display, source_outlet,
                 attachment_ids_json, perk_1_name, perk_2_name, perk_3_name,
                 tactical_name, lethal_name, field_upgrade_name,
                 secondary_name, secondary_role, secondary_attachments_json,
                 best_maps, playstyle_notes, share_code, is_verified_meta, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    item.build_id,
                    item.weapon_id,
                    item.game_version_id,
                    item.build_name,
                    item.archetype,
                    item.archetype_display,
                    item.source_outlet,
                    json.dumps(item.attachment_ids),
                    item.perk_1_name,
                    item.perk_2_name,
                    item.perk_3_name,
                    item.tactical_name,
                    item.lethal_name,
                    item.field_upgrade_name,
                    item.secondary_name,
                    item.secondary_role,
                    json.dumps(item.secondary_attachments),
                    item.best_maps,
                    item.playstyle_notes,
                    item.share_code,
                    item.is_verified_meta,
                    item.created_at
                ]
            )
        finally:
            conn.close()


# Default singleton instance
repo = IntelligenceRepository()


