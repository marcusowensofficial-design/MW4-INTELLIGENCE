"""
MW4 Weapon Intelligence Lab - Data Models & Pydantic Schemas
Strict validation for data ingestion, database integrity, and calculation engines.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class SourceTier(str, Enum):
    TIER_1 = "tier_1"  # Official Patch Notes (Infinity Ward / Activision)
    TIER_2 = "tier_2"  # Controlled Measured Tests (240fps / 120fps frame-by-frame)
    TIER_3 = "tier_3"  # Reproducible Public Testing (Sym.gg / TrueGameData)
    TIER_4 = "tier_4"  # Community Leads & AI Drafts

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            v = value.lower().strip()
            for m in cls:
                if m.value == v or m.name.lower() == v:
                    return m
        return cls.TIER_3


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"
    ILLUSTRATIVE = "illustrative"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            v = value.lower().strip()
            for m in cls:
                if m.value == v or m.name.lower() == v:
                    return m
        return cls.VERIFIED


class WeaponClass(str, Enum):
    ASSAULT_RIFLE = "assault_rifle"
    SUBMACHINE_GUN = "submachine_gun"
    BATTLE_RIFLE = "battle_rifle"
    MARKSMAN_RIFLE = "marksman_rifle"
    SNIPER_RIFLE = "sniper_rifle"
    LIGHT_MACHINE_GUN = "light_machine_gun"
    SHOTGUN = "shotgun"
    HANDGUN = "handgun"
    LAUNCHER = "launcher"
    MELEE = "melee"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            v = value.lower().strip().replace(" ", "_").replace("-", "_")
            for m in cls:
                if m.value == v or m.name.lower() == v:
                    return m
        return cls.ASSAULT_RIFLE


class FiringMode(str, Enum):
    FULL_AUTO = "full_auto"
    SEMI_AUTO = "semi_auto"
    BURST_3 = "burst_3"
    BURST_2 = "burst_2"
    BURST_4 = "burst_4"
    BOLT_ACTION = "bolt_action"
    PUMP_ACTION = "pump_action"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            v = value.lower().strip().replace(" ", "_").replace("-", "_")
            for m in cls:
                if m.value == v or m.name.lower() == v:
                    return m
            if "burst" in v:
                return cls.BURST_3
            elif "bolt" in v:
                return cls.BOLT_ACTION
            elif "semi" in v or "single" in v:
                return cls.SEMI_AUTO
            elif "pump" in v:
                return cls.PUMP_ACTION
            elif "auto" in v:
                return cls.FULL_AUTO
        return cls.FULL_AUTO


class AttachmentSlot(str, Enum):
    MUZZLE = "muzzle"
    BARREL = "barrel"
    LASER = "laser"
    OPTIC = "optic"
    STOCK = "stock"
    UNDERBARREL = "underbarrel"
    MAGAZINE = "magazine"
    AMMUNITION = "ammunition"
    REAR_GRIP = "rear_grip"
    COMB = "comb"
    GUARD = "guard"
    TRIGGER_ACTION = "trigger_action"
    CONVERSION_KIT = "conversion_kit"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            v = value.lower().strip().replace(" ", "_").replace("-", "_")
            for m in cls:
                if m.value == v or m.name.lower() == v:
                    return m
            if "grip" in v:
                return cls.UNDERBARREL
            elif "sight" in v or "scope" in v or "dot" in v:
                return cls.OPTIC
            elif "mag" in v:
                return cls.MAGAZINE
            elif "ammo" in v or "round" in v:
                return cls.AMMUNITION
        return cls.UNDERBARREL


class ModifierType(str, Enum):
    PERCENTAGE = "pct"  # e.g., +0.10 (+10%) or -0.15 (-15%)
    DELTA = "delta"       # e.g., +50 ms or -2.5 m

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            v = value.lower().strip()
            if v in ("pct", "percentage", "percent", "%", "multiplier", "mult"):
                return cls.PERCENTAGE
            elif v in ("delta", "delta_ms", "additive", "flat", "+", "-"):
                return cls.DELTA
        return cls.DELTA


# ---------------------------------------------------------------------------
# Database Core Entities
# ---------------------------------------------------------------------------

class GameVersion(BaseModel):
    version_id: str = Field(..., description="Unique version identifier, e.g. 'v1.0.0-beta'")
    release_date: str = Field(..., description="Release date YYYY-MM-DD")
    patch_name: str = Field(..., description="Marketing or patch title, e.g. 'Beta Launch'")
    is_active: bool = Field(default=False, description="Whether this is the default selected version")
    notes: Optional[str] = Field(default=None, description="Patch highlights or patch notes summary")


class Ruleset(BaseModel):
    ruleset_id: str = Field(..., description="Unique ruleset identifier: 'core', 'hardcore', etc.")
    name: str = Field(..., description="Display name")
    description: str = Field(default="")
    target_health: float = Field(default=100.0, gt=0, description="Base health points")
    regen_delay_ms: float = Field(default=5000.0, ge=0)
    regen_rate_hp_per_sec: float = Field(default=25.0, ge=0)
    friendly_fire: bool = Field(default=False)
    min_stk_cap: int = Field(default=1, ge=1)
    body_multipliers: Dict[str, float] = Field(
        default_factory=lambda: {
            "head": 1.40,
            "neck": 1.25,
            "upper_torso": 1.10,
            "lower_torso": 1.00,
            "limbs": 0.90,
        }
    )


class Weapon(BaseModel):
    weapon_id: str = Field(..., description="Unique weapon code, e.g. 'patriot_xmr_mw4'")
    name: str = Field(..., description="In-game display name, e.g. 'XM4'")
    weapon_class: WeaponClass
    firing_mode: FiringMode = Field(default=FiringMode.FULL_AUTO)
    default_rpm: float = Field(..., gt=0, description="Rounds per minute")
    base_mag_size: int = Field(default=30, gt=0)
    burst_count: int = Field(default=1, ge=1, description="Number of rounds per trigger pull")
    burst_delay_ms: float = Field(default=0.0, ge=0, description="Delay between bursts in ms")
    is_dlc: bool = Field(default=False)
    is_active: bool = Field(default=True)
    description: Optional[str] = None


class WeaponVersionStats(BaseModel):
    stat_id: str = Field(..., description="Primary key: weapon_id + '_' + game_version_id")
    weapon_id: str
    game_version_id: str
    rpm: float = Field(..., gt=0)
    base_ads_ms: float = Field(..., ge=0, description="Aim Down Sights time in ms")
    sprint_to_fire_ms: float = Field(..., ge=0, description="Sprint to fire time in ms")
    tactical_sprint_to_fire_ms: float = Field(default=0.0, ge=0)
    bullet_velocity_mps: float = Field(..., gt=0, description="Muzzle velocity in meters/second")
    reload_empty_s: float = Field(..., gt=0, description="Full empty reload time in seconds")
    reload_tactical_s: float = Field(..., gt=0, description="Tactical/partial reload in seconds")
    recoil_horizontal: float = Field(..., ge=0, description="Horizontal recoil index (lower = better)")
    recoil_vertical: float = Field(..., ge=0, description="Vertical recoil index (lower = better)")
    hipfire_spread_deg: float = Field(..., ge=0, description="Hipfire cone in degrees")
    move_speed_mps: float = Field(..., gt=0, description="Base movement speed m/s")
    ads_move_speed_mps: float = Field(..., gt=0, description="Strafe / ADS movement speed m/s")
    flinch_resistance: float = Field(default=1.0, ge=0, le=2.0)
    open_bolt_delay_ms: float = Field(default=0.0, ge=0.0, description="Delay before first round discharges (common on LMGs)")
    reload_add_ammo_s: float = Field(default=0.0, ge=0, description="Tactical reload cancel / add-ammo timing in seconds")
    swap_speed_raise_ms: float = Field(default=350.0, ge=0, description="Weapon ready / raise time in ms")
    swap_speed_stow_ms: float = Field(default=250.0, ge=0, description="Weapon holster / stow time in ms")
    tac_sprint_speed_mps: float = Field(default=7.0, gt=0, description="Tactical sprint movement speed in m/s")


class DamageRangeBracket(BaseModel):
    profile_id: str
    weapon_id: str
    game_version_id: str
    ruleset_id: str = Field(default="core")
    range_start_m: float = Field(ge=0)
    range_end_m: float = Field(gt=0)
    damage_head: float = Field(..., gt=0)
    damage_neck: float = Field(..., gt=0)
    damage_chest: float = Field(..., gt=0)
    damage_stomach: float = Field(..., gt=0)
    damage_limbs: float = Field(..., gt=0)

    @model_validator(mode="after")
    def validate_range_order(self):
        if self.range_end_m <= self.range_start_m:
            raise ValueError(f"range_end_m ({self.range_end_m}) must be greater than range_start_m ({self.range_start_m})")
        return self


class Attachment(BaseModel):
    attachment_id: str
    name: str
    slot: AttachmentSlot
    weapon_id_compat: Optional[str] = Field(default=None, description="Specific weapon ID or None if universal")
    is_universal: bool = Field(default=True)
    unlock_level: int = Field(default=1, ge=1)
    description: Optional[str] = None
    pick_rate_pct: float = Field(default=0.0, ge=0.0, le=100.0, description="Community pick rate percentage in meta builds")
    is_meta_favorite: bool = Field(default=False, description="Whether this attachment is the #1 community favorite for its slot")


class AttachmentModifier(BaseModel):
    mod_id: str
    attachment_id: str
    game_version_id: str
    stat_key: str = Field(..., description="Target stat, e.g. 'base_ads_ms', 'range_multiplier', 'recoil_vertical'")
    mod_type: ModifierType
    mod_value: float = Field(..., description="Multiplier delta (e.g. -0.10 for -10%) or absolute delta")
    notes: Optional[str] = None


class EvidenceLedgerEntry(BaseModel):
    evidence_id: str
    target_entity_type: str = Field(..., description="'weapon_stats', 'damage_profile', 'attachment_mod'")
    target_entity_id: str
    field_name: str
    observed_value: Union[float, str, int]
    source_url: str
    source_name: str
    source_tier: SourceTier
    test_method: str
    captured_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    recorded_by: str = Field(default="system")
    verification_status: VerificationStatus = Field(default=VerificationStatus.VERIFIED)
    confidence_score: float = Field(default=0.90, ge=0.0, le=1.0)
    notes: Optional[str] = None


class AIReviewItem(BaseModel):
    queue_id: str
    proposed_payload: Dict[str, Any]
    ai_model: str = Field(..., description="Name/version of AI model that generated this suggestion")
    confidence_claim: float = Field(ge=0.0, le=1.0)
    rationale: str
    status: str = Field(default="pending", description="'pending', 'approved', 'rejected'")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    rejection_reason: Optional[str] = None


class SourceSnapshot(BaseModel):
    snapshot_id: str
    source_id: str
    fetch_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_hash: str
    raw_payload_path: str
    diff_summary: Optional[str] = None


class CustomBuild(BaseModel):
    build_id: str
    user_label: str
    weapon_id: str
    game_version_id: str
    ruleset_id: str = Field(default="core")
    attachment_ids: List[str] = Field(default_factory=list, max_length=5)
    notes: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CommunityMetaConsensus(BaseModel):
    consensus_id: str
    weapon_id: str
    game_version_id: str
    wzstats_tier: str = Field(default="B-Tier 🔷")
    wzranked_tier: str = Field(default="B-Tier 🔷")
    codmunity_tier: str = Field(default="B-Tier 🔷")
    dexerto_tier: str = Field(default="B-Tier 🔷")
    charlie_tier: str = Field(default="B-Tier 🔷")
    dotesports_tier: str = Field(default="B-Tier 🔷")
    consensus_tag: str = Field(default="⭐ BALANCED VIABLE")
    badge_color: str = Field(default="#4ade80")
    community_pick_rate_pct: float = Field(default=5.0, description="Global pick rate percentage (e.g. 18.4%)")
    community_kd_ratio: float = Field(default=1.05, description="Average global player K/D ratio")
    recommended_secondary: str = Field(default="Renetti 3-Burst", description="Recommended companion secondary")
    global_win_rate_pct: float = Field(default=50.0, ge=0.0, le=100.0, description="Global match win rate percentage when equipped")
    meta_trend_delta_pct: float = Field(default=0.0, description="7-day pick-rate velocity change (e.g. +2.4% or -1.5%)")
    headshot_pct: float = Field(default=18.0, ge=0.0, le=100.0, description="Average headshot elimination percentage")
    kills_per_minute: float = Field(default=1.85, ge=0.0, description="Average kills per minute")
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Engine Output & Analytics DTOs
# ---------------------------------------------------------------------------

class HitLocation(str, Enum):
    HEAD = "head"
    NECK = "neck"
    CHEST = "chest"
    STOMACH = "stomach"
    LIMBS = "limbs"
    COMPOSITE = "composite"  # Realistic weighted blend


class TTKPoint(BaseModel):
    distance_m: float
    damage_per_shot: float
    shots_to_kill: int
    ttk_ms: float
    bullet_travel_time_ms: float = 0.0
    impact_ttk_ms: float = 0.0
    hit_location: str
    is_lethal_1shot: bool = False


class TTKCalculationResult(BaseModel):
    weapon_id: str
    weapon_name: str
    game_version_id: str
    ruleset_id: str
    target_health: float
    rpm: float
    hit_location: str
    open_bolt_delay_ms: float = 0.0
    curve_points: List[TTKPoint]
    close_range_ttk_ms: float
    mid_range_ttk_ms: float
    long_range_ttk_ms: float
    max_1shot_kill_range_m: Optional[float] = None
    headshots_for_stk_drop: Optional[int] = None

    @field_validator("curve_points", mode="before")
    @classmethod
    def coerce_curve_points(cls, v: Any) -> Any:
        if isinstance(v, list):
            return [item.model_dump() if isinstance(item, BaseModel) else item for item in v]
        return v


class PracticalEngagementResult(BaseModel):
    weapon_id: str
    weapon_name: str
    distance_m: float
    reaction_ms: float
    ads_ms: float
    sprint_to_fire_ms: float
    theoretical_ttk_ms: float
    expected_miss_penalty_ms: float
    practical_engagement_time_ms: float
    accuracy_used: float
    is_sprinting: bool
    stk: int


class EvaluatedBuildStats(BaseModel):
    weapon_id: str
    weapon_name: str
    build_id: Optional[str] = None
    build_label: str
    game_version_id: str
    ruleset_id: str
    attachment_ids: List[str]
    attachments_applied: List[Attachment]

    # Effective Stats
    effective_rpm: float
    effective_ads_ms: float
    effective_sprint_to_fire_ms: float
    effective_bullet_velocity_mps: float
    effective_reload_empty_s: float
    effective_reload_tactical_s: float
    effective_recoil_horizontal: float
    effective_recoil_vertical: float
    effective_hipfire_spread_deg: float
    effective_move_speed_mps: float
    effective_ads_move_speed_mps: float
    effective_mag_size: int
    range_multiplier: float

    # Practical Metrics
    close_ttk_ms: float
    mid_ttk_ms: float
    long_ttk_ms: float
    close_pet_ms: float
    mid_pet_ms: float
    balance_score: float
    recoil_index: float
    mobility_index: float
    effective_reload_add_ammo_s: float = 0.0
    effective_swap_speed_raise_ms: float = 350.0
    damage_per_mag: float = 0.0
    kills_per_mag: float = 0.0

    @field_validator("attachments_applied", mode="before")
    @classmethod
    def coerce_attachments_applied(cls, v: Any) -> Any:
        if isinstance(v, list):
            return [item.model_dump() if isinstance(item, BaseModel) else item for item in v]
        return v


class ParetoBuildPoint(BaseModel):
    build_label: str
    attachment_ids: List[str]
    attachment_names: List[str]
    practical_engagement_ms: float  # Objective 1: Minimize PET
    recoil_index: float             # Objective 2: Minimize Recoil
    mobility_index: float           # Objective 3: Maximize Mobility
    effective_ads_ms: float
    effective_range_multiplier: float
    is_pareto_optimal: bool
    dominance_rank: int = 1


class BalanceScoreBreakdown(BaseModel):
    weapon_id: str
    weapon_name: str
    weapon_class: WeaponClass
    game_version_id: str
    ruleset_id: str
    composite_balance_score: float = Field(ge=0.0, le=100.0)
    tier_rating: str  # "S", "A", "B", "C", "D"

    # Normalized component scores (0 to 100)
    cqb_ttk_score: float
    mid_ttk_score: float
    long_ttk_score: float
    handling_score: float
    recoil_score: float
    sustainability_score: float

    # Raw metrics for transparency
    raw_close_ttk_ms: float
    raw_ads_ms: float
    raw_recoil_vertical: float
    raw_mag_size: int
    confidence_score: float
    weights_used: Dict[str, float]
    assumptions_log: List[str]


class StatDeltaEvent(BaseModel):
    event_id: str
    weapon_id: str
    stat_name: str  # e.g. 'damage_chest', 'range_effective_m', 'rpm', 'base_ads_ms', 'recoil_vertical'
    patch_version_id: str
    effective_date: str  # 'YYYY-MM-DD'
    previous_value: float
    delta_type: str = "DELTA_ADD"  # 'SET_ABSOLUTE', 'DELTA_ADD', 'DELTA_PERCENT'
    delta_value: float
    new_value: float
    official_patch_url: str
    developer_notes: str
    captured_timestamp: str


class StatLineageReconstruction(BaseModel):
    weapon_id: str
    stat_name: str
    baseline_date: str
    baseline_value: float
    as_of_date: str
    reconstructed_value: float
    total_patches_applied: int
    patch_trail: List[StatDeltaEvent]
    is_continuity_verified: bool

    @field_validator("patch_trail", mode="before")
    @classmethod
    def coerce_patch_trail(cls, v: Any) -> Any:
        if isinstance(v, list):
            return [item.model_dump() if isinstance(item, BaseModel) else item for item in v]
        return v


class MetaBuildPreset(BaseModel):
    build_id: str = Field(..., description="Unique key: mb_{weapon_id}_{archetype}_{version}")
    weapon_id: str
    game_version_id: str = Field(default="v1.0.0-beta")
    build_name: str
    archetype: str  # "cdl_pro", "lab_pareto", "max_speed", "zero_recoil", "stealth_snd"
    archetype_display: str = "👑 CDL Pro Meta"
    source_outlet: str = "CODMunity / CDL Pro Consensus"
    attachment_ids: List[str] = Field(default_factory=list)
    perk_1_name: str = "Quick Fix"
    perk_2_name: str = "Fast Hands"
    perk_3_name: str = "Battle Hardened"
    tactical_name: str = "Shock Stick"
    lethal_name: str = "Semtex"
    field_upgrade_name: str = "Trophy System"
    secondary_name: str = "Renetti 3-Burst"
    secondary_role: str = "180ms Fast-Swap Pocket Pistol"
    secondary_attachments: List[str] = Field(default_factory=list)
    best_maps: str = "Skyline, Babylon, Protocol"
    playstyle_notes: str = ""
    share_code: str = ""
    is_verified_meta: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


