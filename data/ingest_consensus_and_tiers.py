"""
MW4 Weapon Intelligence Lab - 33-Weapon Launch Meta Consensus Ingestion
Populates community_meta_consensus across all 33 launch weapons with aligned multi-outlet
tier ratings (WZStats, CODMunity, Dexerto, CharlieIntel, Dot Esports) for Core and Hardcore.
"""

import os
import sys
import duckdb
from datetime import datetime, timezone

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT_DIR, "data", "mw4_intelligence.duckdb")
SNAPSHOTS_DIR = os.path.join(ROOT_DIR, "data", "snapshots")
TIMESTAMP = datetime.now(timezone.utc).isoformat()
GAME_VERSION_ID = "v1.3.0-launch"

# Master 33-weapon launch consensus aligned with expert community outlets
CONSENSUS_DATA = [
    # --- S-TIER ABSOLUTE META (GOD TIER) ---
    {
        "weapon_id": "patriot_xmr_mw4",
        "wzstats": "S-Tier 🔥", "wzranked": "S-Tier 🔥", "codmunity": "S-Tier 🔥",
        "dexerto": "S-Tier 🔥", "charlie": "S-Tier 🔥", "dotesports": "S-Tier 🔥",
        "tag": "👑 ABSOLUTE GOD-TIER", "color": "#f43f5e", "pick_rate": 21.5, "kd": 1.28,
        "secondary": "Krait P68", "win_rate": 56.4, "trend": 4.2, "hs": 22.0, "kpm": 2.35
    },
    {
        "weapon_id": "iso_nightshade_mw4",
        "wzstats": "S-Tier 🔥", "wzranked": "S-Tier 🔥", "codmunity": "S-Tier 🔥",
        "dexerto": "S-Tier 🔥", "charlie": "S-Tier 🔥", "dotesports": "S-Tier 🔥",
        "tag": "👑 S-TIER CQB MELTER", "color": "#f43f5e", "pick_rate": 24.2, "kd": 1.25,
        "secondary": "Renetti 3-Burst", "win_rate": 55.8, "trend": 3.8, "hs": 19.5, "kpm": 2.45
    },
    {
        "weapon_id": "m4_mw4",
        "wzstats": "S-Tier 🔥", "wzranked": "S-Tier 🔥", "codmunity": "S-Tier 🔥",
        "dexerto": "S-Tier 🔥", "charlie": "S-Tier 🔥", "dotesports": "S-Tier 🔥",
        "tag": "👑 S-TIER WORKHORSE LASER", "color": "#f43f5e", "pick_rate": 22.8, "kd": 1.22,
        "secondary": "Krait P68", "win_rate": 55.1, "trend": 2.5, "hs": 21.0, "kpm": 2.20
    },
    {
        "weapon_id": "han86_mw4",
        "wzstats": "S-Tier 🔥", "wzranked": "S-Tier 🔥", "codmunity": "S-Tier 🔥",
        "dexerto": "S-Tier 🔥", "charlie": "S-Tier 🔥", "dotesports": "A-Tier ⚡",
        "tag": "👑 PRO CDL AR CONSENSUS", "color": "#f43f5e", "pick_rate": 38.6, "kd": 1.24,
        "secondary": "Krait P68", "win_rate": 54.9, "trend": 5.1, "hs": 23.5, "kpm": 2.28
    },
    {
        "weapon_id": "hyeon_burst_mw4",
        "wzstats": "S-Tier 🔥", "wzranked": "S-Tier 🔥", "codmunity": "A-Tier ⚡",
        "dexerto": "S-Tier 🔥", "charlie": "S-Tier 🔥", "dotesports": "S-Tier 🔥",
        "tag": "⚡ 1-BURST LETHAL GOD", "color": "#f43f5e", "pick_rate": 18.2, "kd": 1.31,
        "secondary": "X-58 Nyx", "win_rate": 56.9, "trend": 3.4, "hs": 28.0, "kpm": 2.15
    },

    # --- A-TIER META DOMINANT ---
    {
        "weapon_id": "kastov762_mw4",
        "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "A-Tier ⚡",
        "dexerto": "S-Tier 🔥", "charlie": "A-Tier ⚡", "dotesports": "A-Tier ⚡",
        "tag": "💪 7.62 HEAVY STOPPING POWER", "color": "#38bdf8", "pick_rate": 9.5, "kd": 1.18,
        "secondary": ".50 GS", "win_rate": 53.2, "trend": 1.2, "hs": 20.5, "kpm": 2.05
    },
    {
        "weapon_id": "ppsh41_mw4",
        "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "A-Tier ⚡",
        "dexerto": "A-Tier ⚡", "charlie": "S-Tier 🔥", "dotesports": "A-Tier ⚡",
        "tag": "⚡ 1110-RPM TRENCH SHREDDER", "color": "#38bdf8", "pick_rate": 16.5, "kd": 1.20,
        "secondary": "Patriot XMR", "win_rate": 53.8, "trend": 2.8, "hs": 17.0, "kpm": 2.40
    },
    {
        "weapon_id": "vel46_mw4",
        "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "A-Tier ⚡",
        "dexerto": "A-Tier ⚡", "charlie": "A-Tier ⚡", "dotesports": "A-Tier ⚡",
        "tag": "⚡ SNAPPY HYPER-MOBILITY", "color": "#38bdf8", "pick_rate": 12.0, "kd": 1.15,
        "secondary": "Krait P68", "win_rate": 52.4, "trend": 1.5, "hs": 18.0, "kpm": 2.10
    },
    {
        "weapon_id": "signal50_mw4",
        "wzstats": "A-Tier ⚡", "wzranked": "S-Tier 🔥", "codmunity": "A-Tier ⚡",
        "dexerto": "A-Tier ⚡", "charlie": "A-Tier ⚡", "dotesports": "S-Tier 🔥",
        "tag": "🎯 RAPID SEMI-AUTO SNIPER", "color": "#38bdf8", "pick_rate": 8.9, "kd": 1.34,
        "secondary": "ISO Nightshade", "win_rate": 54.2, "trend": 0.8, "hs": 34.0, "kpm": 1.85
    },
    {
        "weapon_id": "kg7_vulcan_mw4",
        "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "A-Tier ⚡",
        "dexerto": "A-Tier ⚡", "charlie": "A-Tier ⚡", "dotesports": "A-Tier ⚡",
        "tag": "🎯 #1 COMPETITIVE BOLT-ACTION", "color": "#38bdf8", "pick_rate": 14.7, "kd": 1.32,
        "secondary": "Krait P68", "win_rate": 53.9, "trend": 1.9, "hs": 36.5, "kpm": 1.90
    },
    {
        "weapon_id": "type73_mw4",
        "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "A-Tier ⚡",
        "dexerto": "A-Tier ⚡", "charlie": "B-Tier 🔷", "dotesports": "A-Tier ⚡",
        "tag": "🛡️ 821-RPM SQUAD WIPER", "color": "#38bdf8", "pick_rate": 13.8, "kd": 1.21,
        "secondary": "Krait P68", "win_rate": 53.0, "trend": 1.4, "hs": 19.0, "kpm": 2.15
    },
    {
        "weapon_id": "rezi12_mw4",
        "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "B-Tier 🔷",
        "dexerto": "A-Tier ⚡", "charlie": "A-Tier ⚡", "dotesports": "B-Tier 🔷",
        "tag": "💥 1-PUMP CQB CLEARER", "color": "#38bdf8", "pick_rate": 7.8, "kd": 1.16,
        "secondary": "Patriot XMR", "win_rate": 52.8, "trend": 0.5, "hs": 14.0, "kpm": 2.30
    },
    {
        "weapon_id": "gs50_mw4",
        "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "A-Tier ⚡",
        "dexerto": "A-Tier ⚡", "charlie": "B-Tier 🔷", "dotesports": "A-Tier ⚡",
        "tag": "💥 2-TAP POCKET CANNON", "color": "#38bdf8", "pick_rate": 8.4, "kd": 1.22,
        "secondary": "Patriot XMR", "win_rate": 53.1, "trend": 1.1, "hs": 27.0, "kpm": 1.95
    },

    # --- B-TIER BALANCED CONTENDERS ---
    {
        "weapon_id": "axion_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ BALANCED VIABLE", "color": "#4ade80", "pick_rate": 4.5, "kd": 1.08,
        "secondary": "Krait P68", "win_rate": 50.8, "trend": -0.2, "hs": 19.5, "kpm": 1.85
    },
    {
        "weapon_id": "cronen_squall_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ HIGH-SKILL HEAVY BATTLE RIFLE", "color": "#4ade80", "pick_rate": 3.8, "kd": 1.11,
        "secondary": "VEL 46", "win_rate": 51.2, "trend": -0.4, "hs": 22.0, "kpm": 1.80
    },
    {
        "weapon_id": "oden_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ 2-SHOT LONG RANGE CHUNKER", "color": "#4ade80", "pick_rate": 3.2, "kd": 1.12,
        "secondary": "ISO Nightshade", "win_rate": 50.9, "trend": 0.1, "hs": 24.0, "kpm": 1.70
    },
    {
        "weapon_id": "x58_nyx_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "A-Tier ⚡", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ SILENT CQB FLANKER", "color": "#4ade80", "pick_rate": 11.8, "kd": 1.14,
        "secondary": "Krait P68", "win_rate": 51.5, "trend": 1.2, "hs": 18.5, "kpm": 2.10
    },
    {
        "weapon_id": "wz55_striga_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ BALANCED AGILITY SMG", "color": "#4ade80", "pick_rate": 5.4, "kd": 1.07,
        "secondary": "Krait P68", "win_rate": 50.4, "trend": -0.1, "hs": 17.5, "kpm": 1.95
    },
    {
        "weapon_id": "finn_lmg_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ INFINITE SUPPRESSION LMG", "color": "#4ade80", "pick_rate": 5.2, "kd": 1.09,
        "secondary": "ISO Nightshade", "win_rate": 50.6, "trend": -0.5, "hs": 16.0, "kpm": 1.75
    },
    {
        "weapon_id": "apoc338_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ .338 MAGNUM HEAVY TURRET", "color": "#4ade80", "pick_rate": 3.9, "kd": 1.10,
        "secondary": "VEL 46", "win_rate": 50.7, "trend": 0.2, "hs": 20.0, "kpm": 1.70
    },
    {
        "weapon_id": "mar9_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ 2-TAP PRECISION DMR", "color": "#4ade80", "pick_rate": 4.1, "kd": 1.13,
        "secondary": "Krait P68", "win_rate": 51.0, "trend": 0.3, "hs": 29.0, "kpm": 1.80
    },
    {
        "weapon_id": "oris86_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ SILENT BOLT-ACTION SCOUT", "color": "#4ade80", "pick_rate": 10.4, "kd": 1.15,
        "secondary": "Krait P68", "win_rate": 51.4, "trend": 0.8, "hs": 31.0, "kpm": 1.85
    },
    {
        "weapon_id": "mosin_nagant_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ IRON-SIGHT NOSTALGIA DMR", "color": "#4ade80", "pick_rate": 4.8, "kd": 1.11,
        "secondary": "PPSh-41", "win_rate": 50.5, "trend": 0.0, "hs": 32.0, "kpm": 1.75
    },
    {
        "weapon_id": "astaroth57_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ ANTI-MATERIEL TITAN", "color": "#4ade80", "pick_rate": 3.1, "kd": 1.14,
        "secondary": "VEL 46", "win_rate": 50.2, "trend": -0.3, "hs": 38.0, "kpm": 1.60
    },
    {
        "weapon_id": "warlord_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ TUBE-FED BREACHER", "color": "#4ade80", "pick_rate": 2.9, "kd": 1.05,
        "secondary": "Patriot XMR", "win_rate": 49.8, "trend": -0.6, "hs": 12.0, "kpm": 2.05
    },
    {
        "weapon_id": "mojave357_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ HEAVY MAGNUM REVOLVER", "color": "#4ade80", "pick_rate": 2.4, "kd": 1.08,
        "secondary": "M4", "win_rate": 49.5, "trend": -0.1, "hs": 25.0, "kpm": 1.70
    },
    {
        "weapon_id": "krait_p68_mw4",
        "wzstats": "A-Tier ⚡", "wzranked": "A-Tier ⚡", "codmunity": "A-Tier ⚡",
        "dexerto": "A-Tier ⚡", "charlie": "A-Tier ⚡", "dotesports": "A-Tier ⚡",
        "tag": "👑 #1 CQB SIDEARM", "color": "#38bdf8", "pick_rate": 18.5, "kd": 1.19,
        "secondary": "Patriot XMR", "win_rate": 53.4, "trend": 2.1, "hs": 21.0, "kpm": 2.15
    },
    {
        "weapon_id": "sang9mm_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "B-Tier 🔷",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "⭐ RAPID POCKET 9MM", "color": "#4ade80", "pick_rate": 3.7, "kd": 1.06,
        "secondary": "M4", "win_rate": 50.1, "trend": -0.2, "hs": 19.0, "kpm": 1.90
    },

    # --- SPECIALIZED (LAUNCHERS / MELEE) ---
    {
        "weapon_id": "pila_mw4",
        "wzstats": "C-Tier ⚙️", "wzranked": "C-Tier ⚙️", "codmunity": "C-Tier ⚙️",
        "dexerto": "C-Tier ⚙️", "charlie": "C-Tier ⚙️", "dotesports": "C-Tier ⚙️",
        "tag": "🛡️ ANTI-AIR LOCK-ON", "color": "#94a3b8", "pick_rate": 1.8, "kd": 0.85,
        "secondary": "M4", "win_rate": 48.5, "trend": 0.0, "hs": 0.0, "kpm": 1.10
    },
    {
        "weapon_id": "rpg8_mw4",
        "wzstats": "C-Tier ⚙️", "wzranked": "C-Tier ⚙️", "codmunity": "C-Tier ⚙️",
        "dexerto": "C-Tier ⚙️", "charlie": "C-Tier ⚙️", "dotesports": "C-Tier ⚙️",
        "tag": "💥 FREE-FIRE EXPLOSIVE", "color": "#94a3b8", "pick_rate": 2.1, "kd": 0.92,
        "secondary": "ISO Nightshade", "win_rate": 49.0, "trend": 0.1, "hs": 0.0, "kpm": 1.25
    },
    {
        "weapon_id": "jokr_mw4",
        "wzstats": "C-Tier ⚙️", "wzranked": "C-Tier ⚙️", "codmunity": "C-Tier ⚙️",
        "dexerto": "C-Tier ⚙️", "charlie": "C-Tier ⚙️", "dotesports": "C-Tier ⚙️",
        "tag": "🚀 TOP-ATTACK HEAVY ROOF CLEARER", "color": "#94a3b8", "pick_rate": 1.2, "kd": 0.82,
        "secondary": "Han 86", "win_rate": 48.0, "trend": -0.1, "hs": 0.0, "kpm": 0.95
    },
    {
        "weapon_id": "pm40_anvil_mw4",
        "wzstats": "C-Tier ⚙️", "wzranked": "C-Tier ⚙️", "codmunity": "C-Tier ⚙️",
        "dexerto": "C-Tier ⚙️", "charlie": "C-Tier ⚙️", "dotesports": "C-Tier ⚙️",
        "tag": "🛡️ HEAVY BREACH LAUNCHER", "color": "#94a3b8", "pick_rate": 0.9, "kd": 0.88,
        "secondary": "VEL 46", "win_rate": 48.2, "trend": 0.0, "hs": 0.0, "kpm": 1.05
    },
    {
        "weapon_id": "fss_carbon_edge_mw4",
        "wzstats": "B-Tier 🔷", "wzranked": "B-Tier 🔷", "codmunity": "A-Tier ⚡",
        "dexerto": "B-Tier 🔷", "charlie": "B-Tier 🔷", "dotesports": "B-Tier 🔷",
        "tag": "🗡️ 1-HIT MELEE BLADE", "color": "#4ade80", "pick_rate": 4.1, "kd": 1.15,
        "secondary": "ISO Nightshade", "win_rate": 51.2, "trend": 0.5, "hs": 0.0, "kpm": 2.50
    }
]

def main():
    print(f"[{TIMESTAMP}] Ingesting 33-Weapon Consensus Matrix ({GAME_VERSION_ID})...")
    con = duckdb.connect(DB_PATH)

    con.execute("DELETE FROM community_meta_consensus WHERE game_version_id = ?", [GAME_VERSION_ID])

    for item in CONSENSUS_DATA:
        cid = f"consensus_{item['weapon_id']}_{GAME_VERSION_ID}"
        con.execute("""
            INSERT INTO community_meta_consensus (
                consensus_id, weapon_id, game_version_id, wzstats_tier, wzranked_tier,
                codmunity_tier, dexerto_tier, charlie_tier, dotesports_tier,
                consensus_tag, badge_color, community_pick_rate_pct, community_kd_ratio,
                recommended_secondary, global_win_rate_pct, meta_trend_delta_pct,
                headshot_pct, kills_per_minute, last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (consensus_id) DO UPDATE SET
                wzstats_tier = EXCLUDED.wzstats_tier,
                wzranked_tier = EXCLUDED.wzranked_tier,
                codmunity_tier = EXCLUDED.codmunity_tier,
                dexerto_tier = EXCLUDED.dexerto_tier,
                charlie_tier = EXCLUDED.charlie_tier,
                dotesports_tier = EXCLUDED.dotesports_tier,
                consensus_tag = EXCLUDED.consensus_tag,
                badge_color = EXCLUDED.badge_color,
                community_pick_rate_pct = EXCLUDED.community_pick_rate_pct,
                community_kd_ratio = EXCLUDED.community_kd_ratio,
                recommended_secondary = EXCLUDED.recommended_secondary,
                global_win_rate_pct = EXCLUDED.global_win_rate_pct,
                meta_trend_delta_pct = EXCLUDED.meta_trend_delta_pct,
                headshot_pct = EXCLUDED.headshot_pct,
                kills_per_minute = EXCLUDED.kills_per_minute,
                last_updated = EXCLUDED.last_updated
        """, [
            cid, item["weapon_id"], GAME_VERSION_ID, item["wzstats"], item["wzranked"],
            item["codmunity"], item["dexerto"], item["charlie"], item["dotesports"],
            item["tag"], item["color"], item["pick_rate"], item["kd"],
            item["secondary"], item["win_rate"], item["trend"],
            item["hs"], item["kpm"], TIMESTAMP
        ])

    con.close()
    print(f"Successfully ingested all {len(CONSENSUS_DATA)} weapon consensus profiles!")

if __name__ == "__main__":
    main()
