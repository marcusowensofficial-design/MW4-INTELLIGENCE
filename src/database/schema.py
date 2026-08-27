"""
MW4 Weapon Intelligence Lab - DuckDB Schema Definitions
DDL commands, table initialization, and index setup.
"""

SCHEMA_DDL = """
-- 1. Game Versions (Immutable records per patch)
CREATE TABLE IF NOT EXISTS game_versions (
    version_id VARCHAR PRIMARY KEY,
    release_date VARCHAR NOT NULL,
    patch_name VARCHAR NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- 2. Rulesets (Core, Hardcore, Custom)
CREATE TABLE IF NOT EXISTS rulesets (
    ruleset_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    description TEXT,
    target_health DOUBLE NOT NULL DEFAULT 100.0,
    regen_delay_ms DOUBLE NOT NULL DEFAULT 5000.0,
    regen_rate_hp_per_sec DOUBLE NOT NULL DEFAULT 25.0,
    friendly_fire BOOLEAN DEFAULT FALSE,
    min_stk_cap INTEGER DEFAULT 1,
    body_multipliers_json TEXT NOT NULL
);

-- 3. Base Weapons Catalog
CREATE TABLE IF NOT EXISTS weapons (
    weapon_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    weapon_class VARCHAR NOT NULL,
    firing_mode VARCHAR NOT NULL DEFAULT 'full_auto',
    default_rpm DOUBLE NOT NULL,
    base_mag_size INTEGER NOT NULL DEFAULT 30,
    burst_count INTEGER NOT NULL DEFAULT 1,
    burst_delay_ms DOUBLE NOT NULL DEFAULT 0.0,
    is_dlc BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    description TEXT
);

-- 4. Versioned Weapon Physical Stats (Never overwrite old versions)
CREATE TABLE IF NOT EXISTS weapon_version_stats (
    stat_id VARCHAR PRIMARY KEY,
    weapon_id VARCHAR NOT NULL,
    game_version_id VARCHAR NOT NULL,
    rpm DOUBLE NOT NULL,
    base_ads_ms DOUBLE NOT NULL,
    sprint_to_fire_ms DOUBLE NOT NULL,
    tactical_sprint_to_fire_ms DOUBLE NOT NULL DEFAULT 0.0,
    bullet_velocity_mps DOUBLE NOT NULL,
    reload_empty_s DOUBLE NOT NULL,
    reload_tactical_s DOUBLE NOT NULL,
    recoil_horizontal DOUBLE NOT NULL,
    recoil_vertical DOUBLE NOT NULL,
    hipfire_spread_deg DOUBLE NOT NULL,
    move_speed_mps DOUBLE NOT NULL,
    ads_move_speed_mps DOUBLE NOT NULL,
    flinch_resistance DOUBLE NOT NULL DEFAULT 1.0,
    open_bolt_delay_ms DOUBLE NOT NULL DEFAULT 0.0
);

-- 5. Versioned Weapon Damage Range Profiles
CREATE TABLE IF NOT EXISTS weapon_damage_profiles (
    profile_id VARCHAR PRIMARY KEY,
    weapon_id VARCHAR NOT NULL,
    game_version_id VARCHAR NOT NULL,
    ruleset_id VARCHAR NOT NULL DEFAULT 'core',
    range_start_m DOUBLE NOT NULL,
    range_end_m DOUBLE NOT NULL,
    damage_head DOUBLE NOT NULL,
    damage_neck DOUBLE NOT NULL,
    damage_chest DOUBLE NOT NULL,
    damage_stomach DOUBLE NOT NULL,
    damage_limbs DOUBLE NOT NULL
);

-- 6. Attachments Catalog
CREATE TABLE IF NOT EXISTS attachments (
    attachment_id VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    slot VARCHAR NOT NULL,
    weapon_id_compat VARCHAR,
    is_universal BOOLEAN DEFAULT TRUE,
    unlock_level INTEGER DEFAULT 1,
    description TEXT
);

-- 7. Versioned Attachment Modifiers
CREATE TABLE IF NOT EXISTS attachment_modifiers (
    mod_id VARCHAR PRIMARY KEY,
    attachment_id VARCHAR NOT NULL,
    game_version_id VARCHAR NOT NULL,
    stat_key VARCHAR NOT NULL,
    mod_type VARCHAR NOT NULL, -- 'pct' or 'delta'
    mod_value DOUBLE NOT NULL,
    notes TEXT
);

-- 8. Evidence Ledger (Provenance tracking for every metric)
CREATE TABLE IF NOT EXISTS evidence_ledger (
    evidence_id VARCHAR PRIMARY KEY,
    target_entity_type VARCHAR NOT NULL,
    target_entity_id VARCHAR NOT NULL,
    field_name VARCHAR NOT NULL,
    observed_value VARCHAR NOT NULL,
    source_url VARCHAR NOT NULL,
    source_name VARCHAR NOT NULL,
    source_tier VARCHAR NOT NULL,
    test_method VARCHAR NOT NULL,
    captured_timestamp VARCHAR NOT NULL,
    recorded_by VARCHAR NOT NULL DEFAULT 'system',
    verification_status VARCHAR NOT NULL DEFAULT 'verified',
    confidence_score DOUBLE NOT NULL DEFAULT 0.90,
    notes TEXT
);

-- 9. AI Review Queue (Quarantine for AI-generated / unverified inputs)
CREATE TABLE IF NOT EXISTS ai_review_queue (
    queue_id VARCHAR PRIMARY KEY,
    proposed_payload_json TEXT NOT NULL,
    ai_model VARCHAR NOT NULL,
    confidence_claim DOUBLE NOT NULL,
    rationale TEXT NOT NULL,
    status VARCHAR NOT NULL DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    created_at VARCHAR NOT NULL,
    reviewed_by VARCHAR,
    reviewed_at VARCHAR,
    rejection_reason TEXT
);

-- 10. Source Raw Snapshots & Diff Log
CREATE TABLE IF NOT EXISTS source_snapshots (
    snapshot_id VARCHAR PRIMARY KEY,
    source_id VARCHAR NOT NULL,
    fetch_timestamp VARCHAR NOT NULL,
    content_hash VARCHAR NOT NULL,
    raw_payload_path VARCHAR NOT NULL,
    diff_summary TEXT
);

-- 11. User Custom Builds (Saved Gunsmith loadouts)
CREATE TABLE IF NOT EXISTS custom_builds (
    build_id VARCHAR PRIMARY KEY,
    user_label VARCHAR NOT NULL,
    weapon_id VARCHAR NOT NULL,
    game_version_id VARCHAR NOT NULL,
    ruleset_id VARCHAR NOT NULL DEFAULT 'core',
    attachment_ids_json TEXT NOT NULL,
    notes TEXT,
    created_at VARCHAR NOT NULL
);

-- 12. Chronological Stat Delta Events (Patch Lineage Tracking)
CREATE TABLE IF NOT EXISTS stat_delta_events (
    event_id VARCHAR PRIMARY KEY,
    weapon_id VARCHAR NOT NULL,
    stat_name VARCHAR NOT NULL,
    patch_version_id VARCHAR NOT NULL,
    effective_date VARCHAR NOT NULL,
    previous_value DOUBLE NOT NULL,
    delta_type VARCHAR NOT NULL DEFAULT 'DELTA_ADD',
    delta_value DOUBLE NOT NULL,
    new_value DOUBLE NOT NULL,
    official_patch_url TEXT NOT NULL,
    developer_notes TEXT NOT NULL,
    captured_timestamp VARCHAR NOT NULL
);

-- 13. Community Meta Consensus (Multi-Outlet Ratings)
CREATE TABLE IF NOT EXISTS community_meta_consensus (
    consensus_id VARCHAR PRIMARY KEY,
    weapon_id VARCHAR NOT NULL,
    game_version_id VARCHAR NOT NULL,
    wzstats_tier VARCHAR NOT NULL DEFAULT 'B-Tier 🔷',
    wzranked_tier VARCHAR NOT NULL DEFAULT 'B-Tier 🔷',
    codmunity_tier VARCHAR NOT NULL DEFAULT 'B-Tier 🔷',
    dexerto_tier VARCHAR NOT NULL DEFAULT 'B-Tier 🔷',
    charlie_tier VARCHAR NOT NULL DEFAULT 'B-Tier 🔷',
    dotesports_tier VARCHAR NOT NULL DEFAULT 'B-Tier 🔷',
    consensus_tag VARCHAR NOT NULL DEFAULT '⭐ BALANCED VIABLE',
    badge_color VARCHAR NOT NULL DEFAULT '#4ade80',
    community_pick_rate_pct DOUBLE NOT NULL DEFAULT 5.0,
    community_kd_ratio DOUBLE NOT NULL DEFAULT 1.05,
    recommended_secondary VARCHAR NOT NULL DEFAULT 'Renetti 3-Burst',
    last_updated VARCHAR NOT NULL
);

-- 14. Verified Meta Build Presets (Pro, Community & Lab Classes)
CREATE TABLE IF NOT EXISTS meta_build_presets (
    build_id VARCHAR PRIMARY KEY,
    weapon_id VARCHAR NOT NULL,
    game_version_id VARCHAR NOT NULL DEFAULT 'v1.0.0-beta',
    build_name VARCHAR NOT NULL,
    archetype VARCHAR NOT NULL DEFAULT 'cdl_pro',
    archetype_display VARCHAR NOT NULL DEFAULT '👑 CDL Pro Meta',
    source_outlet VARCHAR NOT NULL DEFAULT 'CODMunity / CDL Pro Consensus',
    attachment_ids_json TEXT NOT NULL DEFAULT '[]',
    perk_1_name VARCHAR NOT NULL DEFAULT 'Quick Fix',
    perk_2_name VARCHAR NOT NULL DEFAULT 'Fast Hands',
    perk_3_name VARCHAR NOT NULL DEFAULT 'Battle Hardened',
    tactical_name VARCHAR NOT NULL DEFAULT 'Shock Stick',
    lethal_name VARCHAR NOT NULL DEFAULT 'Semtex',
    field_upgrade_name VARCHAR NOT NULL DEFAULT 'Trophy System',
    secondary_name VARCHAR NOT NULL DEFAULT 'Renetti 3-Burst',
    secondary_role VARCHAR NOT NULL DEFAULT '180ms Fast-Swap Pocket Pistol',
    secondary_attachments_json TEXT NOT NULL DEFAULT '[]',
    best_maps VARCHAR NOT NULL DEFAULT 'Skyline, Babylon, Protocol',
    playstyle_notes TEXT NOT NULL DEFAULT '',
    share_code VARCHAR NOT NULL DEFAULT '',
    is_verified_meta BOOLEAN NOT NULL DEFAULT TRUE,
    created_at VARCHAR NOT NULL
);

-- Backward-compatible column migrations
ALTER TABLE weapon_version_stats ADD COLUMN IF NOT EXISTS open_bolt_delay_ms DOUBLE DEFAULT 0.0;
ALTER TABLE community_meta_consensus ADD COLUMN IF NOT EXISTS community_pick_rate_pct DOUBLE DEFAULT 5.0;
ALTER TABLE community_meta_consensus ADD COLUMN IF NOT EXISTS community_kd_ratio DOUBLE DEFAULT 1.05;
ALTER TABLE community_meta_consensus ADD COLUMN IF NOT EXISTS recommended_secondary VARCHAR DEFAULT 'Renetti 3-Burst';
ALTER TABLE meta_build_presets ADD COLUMN IF NOT EXISTS secondary_name VARCHAR DEFAULT 'Renetti 3-Burst';
ALTER TABLE meta_build_presets ADD COLUMN IF NOT EXISTS secondary_role VARCHAR DEFAULT '180ms Fast-Swap Pocket Pistol';
ALTER TABLE meta_build_presets ADD COLUMN IF NOT EXISTS secondary_attachments_json TEXT DEFAULT '[]';
"""

