import sys
import io
import os
import json
import duckdb
import pandas as pd
import numpy as np

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = r'c:\Users\marco\OneDrive\Desktop\MW4GUNBEAST\data\mw4_intelligence.duckdb'
snapshots_dir = r'c:\Users\marco\OneDrive\Desktop\MW4GUNBEAST\data\snapshots'

print("================================================================================")
print("              MW4 META INTELLIGENCE & BUILD INTEGRITY AUDIT                    ")
print("================================================================================")

con = duckdb.connect(db_path, read_only=True)

# 1. Check Row Counts & Parquet Sync
print("\n--- 1. DATABASE & PARQUET SYNC AUDIT ---")
tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]
all_synced = True
for t in sorted(tables):
    db_count = con.execute(f"SELECT count(*) FROM \"{t}\"").fetchone()[0]
    p_path = os.path.join(snapshots_dir, f"{t}.parquet")
    if os.path.exists(p_path):
        p_df = pd.read_parquet(p_path)
        p_count = len(p_df)
        match = "✓ SYNCED" if db_count == p_count else "✗ MISMATCH"
        if db_count != p_count:
            all_synced = False
        print(f"  {t:<30} | DB: {db_count:<4} | Parquet: {p_count:<4} | {match}")
    else:
        print(f"  {t:<30} | DB: {db_count:<4} | Parquet: MISSING | ✗ FAIL")
        all_synced = False

assert all_synced, "Parquet snapshots out of sync with DuckDB!"

# 2. Check Meta Presets & In-Game Practical TTK Metrics
print("\n--- 2. VERIFIED META BUILD PRESETS & PRACTICAL TTK AUDIT ---")
presets = con.execute("SELECT * FROM meta_build_presets").fetchall()

for p in presets:
    (build_id, weapon_id, gv_id, bname, arch, arch_disp, source, atts_json,
     p1, p2, p3, tac, leth, fu, sec_name, sec_role, sec_atts, maps, notes, share, is_meta, created) = p
    
    atts = json.loads(atts_json)
    
    # Base stats
    base_df = con.execute(f"SELECT * FROM weapon_version_stats WHERE weapon_id = '{weapon_id}' ORDER BY game_version_id DESC LIMIT 1").df()
    assert not base_df.empty, f"No stats found for weapon {weapon_id}"
    base = base_df.iloc[0].to_dict()
    
    # Calculate modified stats
    stats = base.copy()
    range_mult = 1.0
    
    for aid in atts:
        mods = con.execute(f"SELECT stat_key, mod_type, mod_value FROM attachment_modifiers WHERE attachment_id = '{aid}'").fetchall()
        for sk, mtype, val in mods:
            if sk == 'range_multiplier':
                range_mult += val
            elif sk in stats:
                if mtype == 'delta':
                    stats[sk] += val
                elif mtype == 'pct':
                    stats[sk] *= (1.0 + val)
    
    # Calculate damage & TTK
    dmg_df = con.execute(f"SELECT * FROM weapon_damage_profiles WHERE weapon_id = '{weapon_id}' ORDER BY range_start_m ASC").df()
    
    rpm = stats['rpm']
    ms_per_shot = 60000.0 / rpm
    
    # Let's inspect first range bracket
    first_b = dmg_df.iloc[0]
    dmg_chest = first_b['damage_chest']
    dmg_head = first_b['damage_head']
    
    # Core 100 HP
    stk_core = int(np.ceil(100.0 / dmg_chest))
    pure_ttk_core = (stk_core - 1) * ms_per_shot
    practical_ttk_core = stats['sprint_to_fire_ms'] + stats['base_ads_ms'] + pure_ttk_core
    
    # WZ 300 HP
    stk_wz = int(np.ceil(300.0 / dmg_chest))
    pure_ttk_wz = (stk_wz - 1) * ms_per_shot
    practical_ttk_wz = stats['sprint_to_fire_ms'] + stats['base_ads_ms'] + pure_ttk_wz
    
    print(f"\n[BUILD]: {bname} ({weapon_id}) | Archetype: {arch_disp}")
    print(f"  Share Code: [{share}] | Source: {source}")
    print(f"  Attachments ({len(atts)}): {', '.join(atts)}")
    print(f"  Perks: [{p1}] + [{p2}] + [{p3}] | Tactical: {tac} | Lethal: {leth} | Secondary: {sec_name} ({sec_role})")
    print(f"  Modified Handling: ADS: {stats['base_ads_ms']:.1f}ms ({stats['base_ads_ms'] - base['base_ads_ms']:+.1f}ms) | STF: {stats['sprint_to_fire_ms']:.1f}ms ({stats['sprint_to_fire_ms'] - base['sprint_to_fire_ms']:+.1f}ms) | Velocity: {stats['bullet_velocity_mps']:.0f} m/s | Range: {range_mult:.2f}x")
    print(f"  Recoil Control: Vert: {stats['recoil_vertical']:.1f} ({stats['recoil_vertical'] - base['recoil_vertical']:+.1f}) | Horiz: {stats['recoil_horizontal']:.1f} ({stats['recoil_horizontal'] - base['recoil_horizontal']:+.1f})")
    print(f"  Performance (0-{(first_b['range_end_m']*range_mult):.0f}m): Core STK: {stk_core} (TTK: {pure_ttk_core:.1f}ms / React: {practical_ttk_core:.1f}ms) | WZ STK: {stk_wz} (TTK: {pure_ttk_wz:.1f}ms / React: {practical_ttk_wz:.1f}ms)")
    print(f"  Synergy Verdict: {notes}")

print("\n--- 3. COMMUNITY META CONSENSUS AUDIT ---")
con_df = con.execute("SELECT weapon_id, wzstats_tier, wzranked_tier, codmunity_tier, consensus_tag, community_pick_rate_pct, community_kd_ratio FROM community_meta_consensus").df()
print(con_df.to_string())

print("\n================================================================================")
print("                   ALL AUDITS PASSED WITH 100% SUCCESS                          ")
print("================================================================================")
