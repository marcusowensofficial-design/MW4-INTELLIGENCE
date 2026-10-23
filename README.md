# 🎯 MW4 Weapon Intelligence Lab

> **Evidence-Backed Competitive FPS Ballistics, Gunsmith Intelligence & Patch Dashboard**  
> Engineered exclusively for **Call of Duty: Modern Warfare 4 (Worldwide Launch: October 22nd / 23rd, 2026, version `v1.3.0-launch`)**.

---

## ⚠️ CRITICAL ARCHITECTURAL MANDATE: 2026 MW4 EXCLUSIVITY

> [!IMPORTANT]
> **PERMANENT SCOPE DIRECTIVE**:
> Even if a brand new conversation or contributor opens this repository with zero context:
> - **We ONLY care about the 2026 Modern Warfare 4 game launch (`v1.3.0-launch`).**
> - There were previous titles called "Modern Warfare" (MW 2019, MWII 2022, MWIII 2023) and Black Ops games. **WE DO NOT CARE ABOUT ANY PAST TITLES.**
> - Strictly forbid scraping, suggesting, or displaying weapons, attachments, or stats from previous Call of Duty titles (e.g., MCW, Rival-9, BAS-B, KVD Enforcer, Slate Reflector, or XM4).
> - The roster strictly comprises the authentic 33 MW4 launch weapons (M4, Han 86, Patriot XMR, ISO Nightshade, Kastov 762, Hyeon Burst, Signal 50, KG-7 Vulcan, Type 73, Rezi 12, Krait P-68, .50 GS, etc.) and their exact Gunsmith attachment slots.

---

## 🎮 Dual-Experience Architecture: Gamer Mode vs Lab Pro Math

To ensure the lab eliminates cognitive friction for casual players while maintaining complete mathematical rigor for esports analysts, the application is built on a **Dual-Mode Experience**:

```mermaid
flowchart TD
    User([Player Enters MW4 Gunbeast]) --> ModeChoice{Select Complexity Level}
    ModeChoice -->|Casual Gamer (Default)| GamerMode[🎮 Gamer Mode]
    ModeChoice -->|Esports Analyst| ProLab[🔬 Lab Pro Math]

    subgraph GamerMode [Zero-Confusion Experience]
        G1[0–100 Visual Stat Bars]
        G2[1-Sentence Bottom-Line Verdict]
        G3[Green/Red Tradeoff Quick-Pills]
        G4[1-Click Smart Build Solvers]
        G5[Quick Answers TTK Podium Deck]
    end

    subgraph ProLab [Deep Ballistics Lab (Expandable)]
        P1[Frame-by-Frame Millisecond TTK Curves]
        P2[2D Wall Recoil Spray Pattern Simulation]
        P3[Practical Engagement Latency - PET]
        P4[Multi-Objective Pareto-Frontier Optimizer]
        P5[4-Tier Sourced Evidence Ledger]
    end
```

### 1. 🎮 Gamer Mode (Default)
- **Visual 0–100 Stat Bars**: Clean, color-coded progress bars for Recoil Control, Aim Speed, Damage Range, Velocity, and Mag Capacity.
- **Bottom-Line Verdicts**: 1-sentence plain-English tactical verdicts (e.g., *"Pinpoint Laser Beam: Recoil reduced by 22% with negligible aim slowdown"*).
- **Tradeoff Quick-Pills**: Clear badges highlighting instant benefits vs drawbacks (e.g., `+25% Less Kick`, `+15 Extra Bullets`, `Slightly Slower Aim`).
- **🏆 1-Click Smart Build Solvers**: Instant solvers for *Zero-Recoil Laser*, *Fast CQB Rusher*, and *Balanced Pro Meta* that evaluate 500 combinations in milliseconds.
- **⚡ Quick Answers Podium**: High-visibility answers to *"Who kills fastest?"* across close (0–15m), mid (15–35m), long (35m+), and Hardcore (30 HP).

### 2. 🔬 Lab Pro Math Mode (Expandable)
- Tucked cleanly into collapsible sections (`st.expander`), offering tournament-grade formulas, 2D recoil spray simulations, and Pareto trade-off curves without cluttering the screen.

---

## 🛠️ 1:1 In-Game Gunsmith Fidelity Engine

MW4 Gunbeast enforces true 1:1 fidelity with the in-game Modern Warfare 4 Gunsmith:

- **Strict Weapon Isolation (`weapon_attachments`)**:
  - Weapons strictly display attachments they can legitimately equip. Pistols never show rifle stocks; snipers only show sniper-compatible barrels.
- **Complete 9-Slot Gunsmith Coverage**:
  - Muzzle, Barrel, Optic, Stock, Underbarrel, Magazine, Ammunition, Rear Grip, Laser + Apex Conversion Kits.
- **Database Scale**:
  - **645 unique attachments** cataloged.
  - **1,592 weapon-attachment compatibility pairs** mapped.
  - **1,538 empirical modifier deltas** calibrated for version `v1.3.0-launch`.
- **Live Performance Recalculations**:
  - Selecting any attachment instantly recalculates ADS (Aim-Down-Sights), STF (Sprint-to-Fire), Recoil Index, Effective Range %, Bullet Velocity, Mag Capacity, Add-Ammo Reload, and Practical Combat Time.

---

## 🌐 Multi-Authority Meta Consensus Matrix

The lab continuously synthesizes mathematical ballistic data with official rankings from 6 leading competitive publications:
- **WZStats.gg** • **WZRanked** • **CODMunity** • **Dexerto** • **CharlieIntel** • **Dot Esports**

Integrated for both **Core (100 HP)** and **Hardcore (30 HP)** rulesets, giving players a unified consensus on every single launch weapon.

---

## 🗺️ Application Page & Feature Guide

| Route | Page Name | Core Functionality |
| :--- | :--- | :--- |
| `app.py` | **🏠 Command Center** | System health, active launch patch overview (`v1.3.0-launch`), and quick navigation. |
| `pages/0_🎯_Arsenal_Matchmaker.py` | **🎯 Arsenal Matchmaker** | 3-question guided role questionnaire recommending tailored 5-slot classes for any playstyle. |
| `pages/1_🏆_META_Board.py` | **🏆 META Board** | S/A/B/C/D tournament tier classifications, radar balance charts, and multi-authority consensus matrix. |
| `pages/2_🎯_META_Builds.py` | **🎯 META Builds** | Curated pro tournament loadouts, attachment benefits in plain English, and QR share codes. |
| `pages/3_⚡_Fastest_TTK.py` | **⚡ Fastest TTK** | Zero-confusion Quick Answers podium, dual 15m vs 25m dropoff matrix, Core vs Hardcore comparison. |
| `pages/4_🔄_Version_Diff.py` | **🔄 Version Diff** | Patch-over-patch ballistic auditing, buff/nerf deltas, and automated regression detection. |
| `pages/5_🛠️_Build_Optimizer.py` | **🛠️ Build Optimizer** | Interactive Gunsmith customizer, 1-Click Smart Solvers, 2D recoil spray patterns, and Pareto optimizer. |
| `pages/6_⚖️_Weapon_Duel_Arena.py` | **⚖️ Duel Arena** | Millisecond-accurate 1v1 shootout duel simulator calculating aim time, trigger pull, and bullet travel. |
| `pages/7_🔬_Shot_Distribution_Lab.py` | **🔬 Shot Distribution** | Monte Carlo hitbox dispersion simulations evaluating headshot/chest distribution on true TTK. |
| `pages/8_📑_Evidence_Ledger.py` | **📑 Evidence Ledger** | Immutable 4-tier provenance audit trail with test methodology, confidence ratings, and source URLs. |
| `pages/9_🛠️_Data_Admin.py` | **🛠️ Data Admin** | Administrative tools for patch ingestion, OCR screenshot scanning, and database management. |

---

## 📁 Repository Directory Structure

```text
MW4GUNBEAST/
├── app.py                             # Main Streamlit entrance & command dashboard
├── SKILL.md                           # Strict 2026 MW4 launch domain mandate & guidelines
├── README.md                          # Repository documentation & architecture guide
├── requirements.txt                   # Production Python dependencies
├── M4_Meta_Build_Audit_Report.md      # Official M4 launch engineering audit
│
├── assets/                            # Tactical graphics & transparent weapon PNGs
│   ├── mw4_hero_banner.png
│   ├── mw4_logo.png
│   └── weapons/                       # Authentic MW4 launch weapon renders
│
├── data/                              # Database, ingestion scripts & snapshots
│   ├── mw4_intelligence.duckdb        # Active embedded DuckDB database
│   ├── ingest_mw4_launch_attachments.py # Ingestion engine for launch attachments
│   ├── ingest_consensus_and_tiers.py  # 6-outlet consensus ingestion script
│   └── snapshots/                     # Version-controlled Parquet tables for deployment
│       ├── weapons.parquet
│       ├── weapon_attachments.parquet
│       ├── attachments.parquet
│       ├── attachment_modifiers.parquet
│       └── community_meta_consensus.parquet
│
├── pages/                             # 10 dedicated Streamlit application modules
│   ├── 0_🎯_Arsenal_Matchmaker.py
│   ├── 1_🏆_META_Board.py
│   ├── 2_🎯_META_Builds.py
│   ├── 3_⚡_Fastest_TTK.py
│   ├── 4_🔄_Version_Diff.py
│   ├── 5_🛠️_Build_Optimizer.py
│   ├── 6_⚖️_Weapon_Duel_Arena.py
│   ├── 7_🔬_Shot_Distribution_Lab.py
│   ├── 8_📑_Evidence_Ledger.py
│   └── 9_🛠️_Data_Admin.py
│
├── src/                               # Core Python engine suite
│   ├── database/                      # Schema, connection manager, and models
│   ├── engines/                       # TTK, Recoil, Pareto, Duel, Share Code engines
│   ├── ingestion/                     # Scrapers, OCR parser, auto-promotion engine
│   └── ui/                            # Plain English suite, themes, charts, state
│
└── tests/                             # Automated test suite (76 passing tests)
    ├── test_attachment_stacking.py
    ├── test_gunsmith_fidelity.py
    ├── test_pareto_optimizer.py
    ├── test_plain_english_and_matchmaker.py
    ├── test_ttk_engine.py
    └── ...
```

---

## 🧪 Quality Assurance & Test Verification

The codebase maintains a rigorous test suite of **76 automated unit and integration tests** verifying ballistic formulas, attachment stacking, build legality, and matchmaker logic:

```bash
python -m pytest tests/
# Output: 76 passed in 11.01s (100% pass rate)
```

---

## 🚀 Running Locally

```bash
# 1. Clone repository
git clone https://github.com/marcusowensofficial-design/MW4-INTELLIGENCE.git
cd MW4-INTELLIGENCE

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch application
streamlit run app.py
```
