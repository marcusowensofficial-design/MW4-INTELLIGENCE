---
name: mw4-2026-launch-mandate
description: Authoritative domain encyclopedia and non-negotiable architectural mandate for Call of Duty Modern Warfare 4 (Worldwide Launch October 22nd/23rd 2026, version v1.3.0-launch). Strictly enforces complete isolation from prior Call of Duty titles.
---

# ⚠️ ABSOLUTE ARCHITECTURAL MANDATE: MODERN WARFARE 4 (2026 LAUNCH ONLY)

> [!CRITICAL]
> **PERMANENT CONTEXT RETENTION DIRECTIVE**:
> Even if a brand-new conversation or subagent is started and all prior chat context is reset, **YOU MUST ADHERE TO THIS MANDATE WITHOUT ANY EXCEPTION**:
> 
> 1. **2026 TITLE EXCLUSIVITY**:
>    - This repository and website (`MW4 Weapon Intelligence Lab`) is engineered **100% EXCLUSIVELY for Call of Duty: Modern Warfare 4**, launched worldwide on **October 22nd / 23rd, 2026** (active version: `v1.3.0-launch`).
> 
> 2. **PRIOR TITLES ARE STRICTLY FORBIDDEN (ANTI-TAINT DIRECTIVE)**:
>    - There were prior games called "Modern Warfare" (such as Modern Warfare 2019, Modern Warfare II 2022, Modern Warfare III 2023) as well as Black Ops titles (Cold War, BO6).
>    - **WE DO NOT CARE ABOUT ANY PREVIOUS CALL OF DUTY TITLES.**
>    - NEVER scrape, suggest, or introduce weapons, stats, or attachments from previous titles (e.g., MCW, Rival-9, BAS-B, KVD Enforcer, Slate Reflector, VT-7 Spiritfire, or XM4).
>    - All weapons (M4, Han 86, Patriot XMR, ISO Nightshade, Kastov 762, Hyeon Burst, Signal 50, KG-7 Vulcan, Type 73, Rezi 12, Krait P-68, .50 GS, etc.) and attachments belong strictly to the 2026 MW4 launch version.
> 
> 3. **ZERO PLACEHOLDER POLICY**:
>    - All data must be authentic 1:1 empirical data from the 2026 game launch (`v1.3.0-launch`). No fake numbers, estimated placeholders, or coming-soon tags.
> 
> 4. **DUAL-MODE UX (GAMER MODE + LAB PRO MATH)**:
>    - Casual gamers need simple, clear answers (0–100 visual stat bars, Bottom-Line verdicts, tradeoff pills, 1-click meta solvers).
>    - Deep formulas and math matrices (2D recoil spray simulations, PET step curves, Pareto frontiers) belong in expandable "Lab Pro Math" sections.

---

## 📖 MW4 2026 LAUNCH DOMAIN ENCYCLOPEDIA

### 1. Launch Weapon Arsenal (33 Authentic Weapons)

* **Assault Rifles**:
  - **M4**: The gold standard 810 RPM flex assault rifle. Smooth vertical climb, reliable 5-shot kill up to 28m.
  - **Patriot XMR**: S-Tier competitive powerhouse. 279ms TTK with a 4-shot kill ceiling out to 26m and pinpoint recoil.
  - **Kastov 762**: Heavy 7.62 Soviet caliber. Slower 600 RPM but inflicts severe screen flinch and delivers punishing 4-shot kills.
  - **Han 86**: Consistent mid-range workhorse bridging handling and range.
  - **Hyeon Burst**: Precision 3-round burst rifle capable of a 141ms 1-burst kill ceiling when landing upper-chest/head shots.

* **Submachine Guns**:
  - **ISO Nightshade**: #1 CQB weapon in MW4. Fires at 923 RPM with a blistering 260ms TTK inside 14m. Snappy ADS and lightning sprint recovery.
  - **PPSh-41**: 1110 RPM bullet hose equipped with 71-round drums. Unmatched sustained hipfire spray.
  - **X-58 Nyx**: Silent CQB flanker with integrated stealth characteristics.
  - **VEL 46**: Highly controllable mid-range SMG with rapid reload speeds.

* **Light Machine Guns**:
  - **Type 73**: 821 RPM lane-holding laser turret. 75-round belt with virtually zero horizontal recoil.
  - **FiNN LMG**: Ultra-high capacity 100-round suppression platform.

* **Marksman & Battle Rifles**:
  - **Oris 8.6**: High-skill semi-automatic marksman rifle chambered in 8.6 Blackout. Lethal 2-shot tap.
  - **Cronen Squall**: Heavy battle rifle delivering long-distance armor penetration.
  - **Oden**: Slow-firing 12.7mm sledgehammer with massive per-shot damage.

* **Sniper Rifles**:
  - **KG-7 Vulcan**: Tournament #1 bolt-action sniper. Fast bolt cycle with generous 1-shot lethal zone from chest up.
  - **Signal .50**: Semi-automatic .50 Cal sniper rifle offering rapid follow-up shots.

* **Shotguns & Sidearms**:
  - **Rezi 12**: Close-quarters pump-action breach shotgun. Instant 0ms one-shot kill inside 6 meters.
  - **Krait P-68**: Heavy semi-auto sidearm with 46 damage per bullet, dominating Hardcore mode as a guaranteed 1-shot.
  - **.50 GS**: Hand cannon delivering 1-shot headshot kills at close range.

---

### 2. Gunsmith Architecture & Attachment Mechanics

Modern Warfare 4 features an isolated Gunsmith engine across **9 primary slots** + **Apex Conversion Kits**:
1. **Muzzle**: Calms vertical climb and controls muzzle flash/radar ping. Suppressors increase bullet velocity.
2. **Barrel**: Modifies damage range brackets, projectile velocity, and aim-down-sights (ADS) agility.
3. **Underbarrel**: Stabilizes horizontal recoil bounce and weapon sway. Essential for turning flex rifles into lasers.
4. **Optic**: Determines sight magnification and sight picture clarity (e.g. Slimline Elite 1x reflex).
5. **Stock**: Controls aim walking speed, sprint-to-fire transitions, and sustained recoil cushioning.
6. **Magazine**: Extends ammo capacity (e.g. 40-round / 45-round mags) at the cost of slight movement and reload penalties.
7. **Ammunition**: High-velocity rounds increase bullet velocity to achieve hitscan-like ballistics (1,000+ m/s).
8. **Rear Grip**: Directly improves sprint-to-fire (STF) and aim-down-sights (ADS) draw times.
9. **Laser**: Enhances hipfire tight-spread and aiming stability (use non-visible lasers to avoid giving away positions).
10. **Apex Conversion Kits**: Platform transformations that alter weapon caliber, fire rate, and burst behavior without consuming standard 5-attachment slots.

---

### 3. Rulesets & Ballistic Dynamics

* **Core Ruleset (100 HP Standard Health)**:
  - Multi-bullet time-to-kill (200ms – 320ms average).
  - Rewards tracking accuracy, upper-torso hitboxes, and sustained recoil control.
* **Hardcore Ruleset (30 HP High Lethality)**:
  - 1-to-2 bullet kills across almost all calibers.
  - Sprint-to-Fire (STF) and ADS handling speeds dictate 100% of gunfight outcomes.

---

### 4. Database & Storage Architecture

* **DuckDB Core**: `data/mw4_intelligence.duckdb`
* **Snapshots Directory**: `data/snapshots/*.parquet` (ensures Streamlit Cloud deploys with complete database tables).
* **Isolation Table**: `weapon_attachments` guarantees that weapons ONLY expose valid, authentic attachments tailored to their platform.
* **Consensus Table**: `community_meta_consensus` stores multi-outlet rankings from WZStats, WZRanked, CODMunity, Dexerto, CharlieIntel, and Dot Esports.
