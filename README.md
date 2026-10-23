# 🎯 MW4 Weapon Intelligence Lab

> **Evidence-Backed Competitive FPS Ballistics, Gunsmith Intelligence & Patch Dashboard**
> Built exclusively for **Call of Duty: Modern Warfare 4 (Worldwide Launch: October 22nd / 23rd, 2026, version `v1.3.0-launch`)**.

---

## ⚠️ CRITICAL ARCHITECTURAL MANDATE: 2026 MW4 EXCLUSIVITY

> [!IMPORTANT]
> **PERMANENT SCOPE DIRECTIVE**:
> Even if a brand new conversation or contributor opens this repository with zero context:
> - **We ONLY care about the 2026 Modern Warfare 4 game launch (`v1.3.0-launch`).**
> - There were previous titles called "Modern Warfare" (MW 2019, MWII 2022, MWIII 2023) and Black Ops games. **WE DO NOT CARE ABOUT ANY PAST TITLES.**
> - Strictly forbid scraping, suggesting, or displaying weapons, attachments, or stats from previous Call of Duty titles.
> - The roster strictly comprises the authentic 33 MW4 launch weapons (M4, Han 86, Patriot XMR, ISO Nightshade, Kastov 762, Hyeon Burst, Signal 50, KG-7 Vulcan, Type 73, Rezi 12, .50 GS, etc.) and their exact Gunsmith attachment slots.

---

## 🎮 Dual-Experience Architecture: Gamer Mode vs Lab Pro Mode

To ensure the lab is accessible to all players while maintaining complete mathematical rigor, the UI features two modes:

1. **🎮 Gamer Mode (Default)**:
   - **Visual 0–100 Stat Bars**: Normalized progress bars for Damage, Recoil Control, Handling/Aim Speed, Range, and Mag Capacity.
   - **Bottom-Line Verdicts**: 1-sentence plain-English tactical summaries of every weapon and build.
   - **Visual Pros & Cons Badges**: Green/red tags highlighting key tradeoffs (e.g. `+25% Less Kick`, `+15 Extra Bullets`, `Slightly Slower Aim`).
   - **1-Click Smart Build Solver**: Instant one-click buttons for *Zero-Recoil Laser*, *Fast CQB Rusher*, and *Balanced Pro Meta*.

2. **🔬 Lab Pro Math Mode (Expandable)**:
   - Full frame-accurate millisecond TTK step-curves, Practical Engagement Time (PET) breakdowns, 2D recoil spray pattern simulations, and Pareto-frontier optimization matrices for tournament competitors and analysts.

---

## 🔒 Safety & Anti-Cheat Compliance Notice

The **MW4 Weapon Intelligence Lab** is an offline analytical research suite. It operates exclusively on publicly available patch notes, controlled frame-by-frame match recordings, community telemetry, and user-provided screenshots. 

**This software does NOT:**
- Hook, read, or write to game process memory
- Reverse engineer or modify game executable binaries
- Automate player input or gameplay
- Connect to or interact with live Activision / Call of Duty game servers

---

## 🏗️ Architecture & Non-Negotiable Engineering Rules

1. **Strict Versioning (`game_version_id`)**: Every stat is immutable and versioned by patch release (e.g. `v1.3.0-launch`). Prior stats are never overwritten.
2. **Full Provenance (`evidence_id`)**: Sourced metrics track their source URL, source tier (1-4), test methodology, timestamp, and confidence rating.
3. **Source Truth Hierarchy**:
   - **Tier 1**: Official Patch Notes (Activision / Infinity Ward) — 98-100% confidence.
   - **Tier 2**: Controlled Measured Tests (240fps / 120fps video frame capture) — 92-95% confidence.
   - **Tier 3**: Reproducible Empirical Datasets (CODMunity, WZStats, MW4.gg) — 88-95% confidence.
   - **Tier 4**: Community Leads & AI Drafts — 40-65% confidence (**Quarantined in AI Review Queue**).
4. **Gunsmith Platform Isolation (`weapon_attachments`)**: Attachments are strictly mapped to weapon platforms. Weapons only display attachments they can legitimately equip.
5. **Independent Rulesets**: Core (100 HP) and Hardcore (30 HP) are completely independent rulesets.

---

## 🚀 Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the Web App
streamlit run app.py
```
