# 🎯 MW4 Weapon Intelligence Lab

> **Evidence-Backed Competitive FPS Ballistics, Gunsmith Pareto Optimization & Patch Intelligence Dashboard**

Built for **Modern Warfare 4 beta and launch updates** with **Python, Streamlit, DuckDB, Parquet, Plotly, Pydantic, and APScheduler**.

---

## 🔒 Safety & Anti-Cheat Compliance Notice

The **MW4 Weapon Intelligence Lab** is an offline analytical research suite. It operates exclusively on publicly available patch notes, controlled frame-by-frame match recordings, community spreadsheets, and user-provided screenshots. 

**This software does NOT:**
- Hook, read, or write to game process memory
- Reverse engineer or modify game executable binaries
- Automate player input or gameplay
- Connect to or interact with live Activision / Call of Duty game servers

---

## 🏗️ Architecture & Non-Negotiable Engineering Rules

1. **Strict Versioning (`game_version_id`)**: Every stat is immutable and versioned by patch release (e.g. `v1.0.0-beta`, `v1.1.0-launch`). Prior stats are never overwritten.
2. **Full Provenance (`evidence_id`)**: Sourced metrics track their source URL, source tier (1-4), test methodology, timestamp, and confidence rating.
3. **Source Truth Hierarchy**:
   - **Tier 1**: Official Patch Notes (Activision / Infinity Ward) — 98-100% confidence.
   - **Tier 2**: Controlled Measured Tests (240fps / 120fps video frame capture) — 92-95% confidence.
   - **Tier 3**: Reproducible Public Testing (Sym.gg / TrueGameData datasets) — 78-88% confidence.
   - **Tier 4**: Community Leads & AI Drafts — 40-65% confidence (**Quarantined in AI Review Queue**).
4. **AI Review Quarantine**: AI-synthesized claims can **never** write directly to verified stats. They must be reviewed and promoted by a human analyst in the Evidence Review queue.
5. **Independent Rulesets**: Core (100 HP) and Hardcore (30 HP) are completely independent rulesets. Hardcore lethality and damage profiles are never assumed without confirmed evidence.
6. **Multi-Objective Pareto-Frontier Optimization**: Gunsmith optimization produces non-dominated builds across Practical Engagement Time, Recoil Stability, Mobility, and Range rather than opaque single recommendations.
7. **Transparent Balance Scoring**: Scoring normalizes sub-metrics (0-100) and exposes all underlying math, weights, and assumptions.

---

## 📐 Mathematical Models & Core Formulas

### 1. Shots to Kill (STK) & Theoretical TTK
$$STK = \left\lceil \frac{\text{Target Health}}{\text{Damage per Shot}} \right\rceil$$

For fully automatic / semi-automatic weapons:
$$TTK_{ms} = \begin{cases} 
0 & \text{if } STK \le 1 \\
(STK - 1) \times \frac{60000}{RPM} & \text{if } STK > 1
\end{cases}$$

For burst weapons with burst size $B$ and burst delay $D_{ms}$:
$$TTK_{ms} = (STK - 1) \times \frac{60000}{RPM_{\text{cyclic}}} + \left\lfloor \frac{STK - 1}{B} \right\rfloor \times D_{ms}$$

### 2. Practical Engagement Time (PET)
$$PET = T_{\text{reaction}} + T_{\text{ads}} + T_{\text{sprint\_to\_fire}} + TTK_{ms} + T_{\text{miss\_penalty}}$$

Where the miss penalty models player accuracy $A \in (0, 1]$:
$$T_{\text{miss\_penalty}} = \left( STK \times \frac{1 - A}{A} \right) \times \frac{60000}{RPM}$$

### 3. Pareto Frontier Dominance Condition
Build $B_1$ dominates $B_2$ ($B_1 \succ B_2$) iff:
$$\forall j \in \{PET, \text{Recoil}, \text{Mobility}, \text{Range}\}, \text{Metric}_j(B_1) \text{ is at least as good as } \text{Metric}_j(B_2)$$
$$\text{and } \exists k \in \{PET, \text{Recoil}, \text{Mobility}, \text{Range}\}, \text{Metric}_k(B_1) \text{ is strictly better than } \text{Metric}_k(B_2)$$

---

## 🚀 Windows PowerShell Quickstart Guide

### Prerequisites
- **Windows 10 / 11**
- **Python 3.10+** (Tested on Python 3.14)
- **PowerShell 5.1+ or PowerShell 7**

### 1. Open PowerShell and Navigate to Workspace
```powershell
cd c:\Users\marco\OneDrive\Desktop\MW4GUNBEAST
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Initialize & Seed Database
Initialize DuckDB schema and seed illustrative Modern Warfare 4 baseline data:
```powershell
python -c "from src.database.seed_data import seed_database; seed_database(); print('Database ready!')"
```

### 4. Run Pytest Verification Suite
Run the full 33-test automated validation suite:
```powershell
python -m pytest -v
```

### 5. Launch the Streamlit Dashboard
Launch the interactive local web dashboard:
```powershell
python -m streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🗺️ Application Page Guide

| Page | Title | Key Features |
| :--- | :--- | :--- |
| **`app.py`** | **Command Center** | Intelligence KPIs, active version banner, weapon roster table, and module launcher. |
| **`1_🔫_Weapon_Lab.py`** | **Weapon Lab** | Multi-weapon TTK step curves, human performance PET breakdown, hit-location matrix, radar charts, and evidence drill-down. |
| **`2_🛠️_Build_Optimizer.py`** | **Build Optimizer** | 5-slot Gunsmith customizer with live stat deltas, Pareto-frontier non-dominated solver, and custom build saver. |
| **`3_🏆_META_Board.py`** | **META Board** | Dynamic S/A/B/C/D tier list with live weight sliders, transparent sub-score breakdowns, and class rankings. |
| **`4_💀_Hardcore_Lab.py`** | **Hardcore Lab** | Dedicated 30 HP analysis, 1-shot lethality range breakpoints, STK comparison against Core ruleset. |
| **`5_📜_Patch_Tracker.py`** | **Patch Tracker** | Side-by-side version diff viewer with green (Buff) and red (Nerf) delta indicators and changelog history. |
| **`6_🔍_Evidence_Review.py`** | **Evidence Review** | Evidence ledger audit trail, source tier filtering, and AI Review Queue triage (Approve / Reject). |
| **`7_⚙️_Data_Admin.py`** | **Data Admin** | CSV batch importer, screenshot OCR ingest, Parquet snapshot management, and APScheduler background tasks. |

---

## 📁 Repository File Tree

```
MW4GUNBEAST/
├── configs/
│   ├── rulesets.yaml              # Core (100 HP) and Hardcore (30 HP) definitions & multipliers
│   ├── score_weights.yaml          # Weapon class balance weights (CQB, Range, Recoil, Handling)
│   └── source_registry.yaml        # Evidence source tiers (Tier 1-4) & confidence ratings
├── src/
│   ├── __init__.py
│   ├── database/
│   │   ├── connection.py          # Thread-safe DuckDB connection manager & Parquet snapshotting
│   │   ├── schema.py              # DDL scripts with constraints, indexes, and versioning
│   │   ├── models.py              # Pydantic v2 schemas for all entities and ingestion payloads
│   │   ├── repository.py          # Parameterized data access layer for weapons, stats, builds, evidence
│   │   └── seed_data.py           # Comprehensive illustrative seed catalog (Weapons, Attachments, Evidence)
│   ├── engines/
│   │   ├── ttk_engine.py          # STK & TTK calculation with hit distribution & burst logic
│   │   ├── engagement_engine.py   # Practical Engagement Time (PET) with ADS, STF, and miss penalty
│   │   ├── attachment_engine.py   # Attachment stacking, modifier application, and legality checks
│   │   ├── pareto_optimizer.py    # Multi-objective Pareto-frontier build finder (PET vs Recoil vs Mobility)
│   │   ├── balance_scorer.py      # Transparent composite balance scoring engine
│   │   └── confidence_scorer.py   # Evidence source freshness and confidence indexer
│   ├── ingestion/
│   │   ├── patch_notes.py         # Official patch note parser & version changelog generator
│   │   ├── csv_importer.py        # Strict Pydantic-validated CSV batch importer
│   │   ├── ocr_parser.py          # In-game stat card screenshot data extractor & normalizer
│   │   ├── diff_engine.py         # Deep version-to-version diffing for stealth balance changes
│   │   └── ai_gatekeeper.py       # Strict AI review queue isolation & promotion manager
│   ├── ui/
│   │   ├── theme.py               # Modern dark tactical UI styles, CSS tokens, and component cards
│   │   ├── state.py               # Global Streamlit state manager (Version, Ruleset, Filters)
│   │   └── charts.py              # Plotly chart builders (TTK curves, Pareto scatter, Radar, Hitbox)
│   └── scheduler/
│       └── jobs.py                # APScheduler background tasks for snapshot exports & feed polling
├── pages/
│   ├── 1_🔫_Weapon_Lab.py         # Interactive TTK & PET curves, damage tables, hit-location matrix
│   ├── 2_🛠️_Build_Optimizer.py    # 5-slot Gunsmith & Pareto-Frontier multi-objective loadout finder
│   ├── 3_🏆_META_Board.py          # S/A/B/C/D Tier lists with customizable balance weights
│   ├── 4_💀_Hardcore_Lab.py        # Hardcore 30HP lethality, 1-shot range breakpoints & Core comparison
│   ├── 5_📜_Patch_Tracker.py       # Version diff viewer with visual Buff/Nerf delta indicators
│   ├── 6_🔍_Evidence_Review.py     # Evidence ledger drill-down & AI review queue triage
│   └── 7_⚙️_Data_Admin.py          # CSV/Screenshot import, Parquet backups, DB reset, Scheduler
├── tests/
│   ├── test_ttk_engine.py         # STK, TTK, RPM scaling, burst delay, edge cases
│   ├── test_practical_engagement.py # Reaction, ADS, Sprint-to-Fire, accuracy miss penalty
│   ├── test_attachment_stacking.py  # Modifier calculation, stacking rules, stat bounds
│   ├── test_build_legality.py     # 5-slot limit, duplicate slot restrictions, compatibility
│   ├── test_pareto_optimizer.py   # Pareto dominance & frontier selection
│   ├── test_balance_scoring.py    # Normalized scoring & custom weight matrices
│   ├── test_versioning_and_diff.py # Game version immutability & changelog detection
│   └── test_evidence_and_ai_queue.py # AI isolation & evidence promotion workflow
├── data/
│   ├── mw4_intelligence.duckdb    # DuckDB primary database file (auto-generated)
│   ├── snapshots/                 # Parquet historical snapshots
│   └── samples/                   # Sample CSVs and sample patch JSONs for testing
├── app.py                         # Main Streamlit entrance & overview dashboard
├── requirements.txt               # Pinned dependencies
└── README.md                      # Complete documentation & setup instructions
```
