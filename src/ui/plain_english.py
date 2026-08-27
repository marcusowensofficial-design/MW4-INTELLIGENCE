"""
MW4 Weapon Intelligence Lab - Plain English Intelligence & Field Codex
Provides friendly translations, 1-5 star ratings, attachment benefit badges,
the Tactical Ballistics Codex, and the Tactical Arsenal Matchmaker logic.
"""

import streamlit as st
from typing import Dict, List, Any, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Curated Plain-English Weapon Dossiers
# ---------------------------------------------------------------------------
WEAPON_PLAIN_DOSSIERS: Dict[str, Dict[str, Any]] = {
    # Assault Rifles
    "xm4": {
        "role_title": "🎯 Laser Beam All-Rounder",
        "summary": "The ultimate reliable workhorse. Shoots like a laser beam with almost zero gun kick and very forgiving fire rate.",
        "best_for": "Players who want an easy-to-aim gun that works great in every medium-range gunfight.",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Laser Beam)",
        "recoil_profile": "Minimal upward climb, virtually zero side-to-side bounce.",
        "pro_tip": "Aim at the chest and let the slight upward drift land effortless headshots."
    },
    "mcw": {
        "role_title": "🎯 Tournament Precision Rifle",
        "summary": "Pinpoint accuracy with extreme stability at distance. Low damage up close, but an absolute laser past 25 meters.",
        "best_for": "Holding down lanes, head glitches, and picking off enemies across the map.",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Pinpoint)",
        "recoil_profile": "Extremely smooth and predictable straight-line recoil.",
        "pro_tip": "Keep your distance from SMGs—your strength is beaming at mid-to-long range."
    },
    "m4": {
        "role_title": "⚡ Fast-Firing Combat Rifle",
        "summary": "Fires fast with great handling. It kicks a bit more than the XM4, but rewards you with quick eliminations.",
        "best_for": "Aggressive assault rifle players who like pushing into objectives.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Moderate (Manageable)",
        "recoil_profile": "Vertical kick with moderate rightward pull during sustained fire.",
        "pro_tip": "Equip an underbarrel grip to tighten up the burst spread."
    },
    "holger_556": {
        "role_title": "💥 Hard-Hitting Heavy Rifle",
        "summary": "Packs a heavy punch with high damage per bullet. Slightly slower fire rate means every shot counts.",
        "best_for": "Accurate shooters who want high damage per magazine without needing to reload often.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Moderate (Solid)",
        "recoil_profile": "Heavier initial jump, but settles into a steady rhythm.",
        "pro_tip": "Great for 1v2 gunfights because 3 to 4 bullets drop enemies fast."
    },
    "mtz_556": {
        "role_title": "🚀 Hyperspeed Close-Range AR",
        "summary": "Feels almost like a Submachine Gun. Extreme fire rate and snappy aim speed make it deadly up close.",
        "best_for": "Run-and-gun players who want AR range with SMG reaction speed.",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ Moderate Kick (Fast Fire)",
        "recoil_profile": "Fast upward climb due to rapid fire rate.",
        "pro_tip": "Slap on a 40-round magazine because it burns through ammo quickly."
    },
    "dg_56": {
        "role_title": "🎯 3-Round Burst One-Burst Machine",
        "summary": "Fires in deadly 3-round bursts. If you land all 3 bullets to the upper chest, it deletes enemies instantly.",
        "best_for": "Patient marksmen who prefer precise bursts over spraying full auto.",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ Skill-Based Burst",
        "recoil_profile": "Very tight burst grouping, slight pause between bursts.",
        "pro_tip": "Do not rush into tight corners; hold medium sightlines where your burst excels."
    },
    "fr_556": {
        "role_title": "🎯 High-Velocity Burst Rifle",
        "summary": "Classic bullpup burst rifle designed for lethal mid-range precision.",
        "best_for": "Longer-distance burst control with crisp optical sights.",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ Skill-Based Burst",
        "recoil_profile": "Tight vertical burst pattern.",
        "pro_tip": "Aim high-chest so burst recoil naturally catches the head."
    },

    # Submachine Guns
    "rival_9": {
        "role_title": "⚡ Ultimate CDL Tournament SMG",
        "summary": "The reigning king of close-quarters combat. Blistering sprint speed, lightning-fast aim, and rapid time-to-kill.",
        "best_for": "Aggressive rushers who slide, jump, and dive into enemy spawns.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Very Agile / Easy CQB",
        "recoil_profile": "Quick vertical rise that is easy to pull down on controller/mouse.",
        "pro_tip": "Use your movement speed to break enemy cameras around corners."
    },
    "striker": {
        "role_title": "🛡️ The Consistent Workhorse SMG",
        "summary": "Very easy to shoot with great range for an SMG. It fires at a steady rhythm so you rarely miss shots.",
        "best_for": "Beginner and casual players transitioning into aggressive SMG play.",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Best First SMG)",
        "recoil_profile": "Gentle, slow climb with virtually no horizontal drift.",
        "pro_tip": "Equip hollow point ammo or damage range barrels to extend its reach."
    },
    "striker_9": {
        "role_title": "⚡ High-RPM Room Clearer",
        "summary": "9mm converted Striker with a dramatically faster fire rate. Melts opponents in tight hallways.",
        "best_for": "Close-range building clearing and high-tempo run-and-gun.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Snappy & Fast",
        "recoil_profile": "Rapid vertical climb, smooth horizontal control.",
        "pro_tip": "Best used inside 12 meters where its rapid fire rate shreds."
    },
    "superi_46": {
        "role_title": "🏃 Omnimovement Speed Demon",
        "summary": "The fastest strafe and movement speed in the entire game. Enemies will struggle to track you as you slide.",
        "best_for": "High-mobility players who love out-maneuvering enemies during gunfights.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Super Agile",
        "recoil_profile": "Mild recoil, super clean iron sights.",
        "pro_tip": "Strafe left and right while aiming down sights to dodge enemy bullets."
    },
    "amr9": {
        "role_title": "🔋 Extended Mag Powerhouse SMG",
        "summary": "Hybrid between an assault rifle and an SMG. Huge magazine options and great bullet velocity.",
        "best_for": "Taking on multiple enemies back-to-back without running out of bullets.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Forgiving & High Capacity",
        "recoil_profile": "Steady vertical rise.",
        "pro_tip": "Slap on a 50-round drum for relentless multi-kill feeds."
    },
    "hrm_9": {
        "role_title": "⚡ Hyper-Snappy Point-Blank Shredder",
        "summary": "Instant sprint-to-fire speed and blistering close-range elimination time.",
        "best_for": "Close-quarters rushers on tight maps.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Snappy CQB",
        "recoil_profile": "Initial quick pop, easy to center.",
        "pro_tip": "Combine with laser and lightweight stock for instant hip-to-ADS speed."
    },
    "wsp_9": {
        "role_title": "💥 Heavy-Punch Slow-Fire SMG",
        "summary": "Slow chugging fire rate with massive damage per shot. Hits like a truck at medium distance.",
        "best_for": "Calm, accurate shooters who don't want erratic recoil.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Very Stable",
        "recoil_profile": "Low recoil due to slower fire cadence.",
        "pro_tip": "Keep gunfights between 10m and 20m where your heavy damage wins."
    },
    "wsp_swallow": {
        "role_title": "💨 Bullet Hose Spray Machine",
        "summary": "Absurdly fast fire rate that spits a wall of lead in under a second.",
        "best_for": "Point-blank hipfiring and tight corner surprises.",
        "ease_rating": 2,
        "ease_label": "⭐⭐☆☆☆ Wild Recoil (Point-Blank)",
        "recoil_profile": "Aggressive upward kick; requires close range or strong recoil attachments.",
        "pro_tip": "Stick to hipfire and point-blank range—avoid long sightlines."
    },

    # Battle Rifles
    "bas_b": {
        "role_title": "💥 7.62 High-Caliber Sledgehammer",
        "summary": "Shoots full-power 7.62 rounds that tear through armor and health in just 3 clean body shots.",
        "best_for": "Players who want heavy stopping power and quick TTK across all distances.",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ Heavy Punch / Medium Kick",
        "recoil_profile": "Solid vertical punch per shot; best fired in 4-to-5 bullet bursts.",
        "pro_tip": "Use a heavy compensator and stock to turn this into a laser sledgehammer."
    },
    "sidewinder": {
        "role_title": "💥 Heavy Punch Battle Rifle",
        "summary": "Massive damage per bullet that punishes enemies at mid-to-long range.",
        "best_for": "Controlled single-tap or short-burst lane locking.",
        "ease_rating": 2,
        "ease_label": "⭐⭐☆☆☆ Heavy Kick (High Skill)",
        "recoil_profile": "Noticeable vertical kick on sustained automatic fire.",
        "pro_tip": "Switch to semi-auto mode or tap-fire for laser-beam accuracy."
    },
    "mtz_762": {
        "role_title": "⚡ High-Speed Battle Rifle",
        "summary": "Combines high 7.62 damage with a surprisingly fast fire rate.",
        "best_for": "Experienced players who can manage heavy recoil in exchange for rapid kills.",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ Punchy & Fast",
        "recoil_profile": "Strong vertical climb; requires recoil control attachments.",
        "pro_tip": "Equip 30-round mag and heavy muzzle brake."
    },

    # Light Machine Guns
    "pulemyot_762": {
        "role_title": "🛡️ 100-Round Endless Laser LMG",
        "summary": "With the Bullpup conversion kit, this handles like an assault rifle with a massive 100-round magazine and zero recoil.",
        "best_for": "Players who hate reloading and want to wipe whole teams from medium to long range.",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (No Reloading)",
        "recoil_profile": "Extremely smooth, minimal climb, very comfortable to hold down the trigger.",
        "pro_tip": "You can pre-fire around corners without worrying about running out of ammo."
    },
    "bruen_mk9": {
        "role_title": "🎯 Classic Lane-Holding Beamer LMG",
        "summary": "Deep ammo reserves with rock-solid stability. Perfect for suppressing objective points.",
        "best_for": "Defensive players locking down hardpoints and capture flags.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Very Stable",
        "recoil_profile": "Gradual, predictable vertical climb.",
        "pro_tip": "Mount on cover to eliminate 90% of all gun recoil."
    },
    "dg_58_lsb": {
        "role_title": "⚡ Lightweight Agile LMG",
        "summary": "Lighter and faster than standard LMGs with fast aim speed and generous magazine size.",
        "best_for": "Mobile support gunners pushing objectives with teammates.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Snappy for an LMG",
        "recoil_profile": "Gentle upward drift.",
        "pro_tip": "Equip sprint-to-fire grips to keep up with SMG teammates."
    },

    # Marksman & Sniper Rifles
    "katt_amr": {
        "role_title": "💀 1-Shot Lethal Anti-Material Sniper",
        "summary": "Guaranteed 1-shot kill anywhere on the torso or head. Hits like a freight train.",
        "best_for": "Traditional snipers who want guaranteed one-hit eliminations.",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ 1-Shot Power (Slow Handling)",
        "recoil_profile": "Heavy bolt action kick between shots.",
        "pro_tip": "Position yourself on high ground or long sightlines before scoping in."
    },
    "longbow": {
        "role_title": "⚡ Rapid Quick-Scope Sniper",
        "summary": "Snappy aim speed and high magazine capacity. Perfect for fast-paced aggressive sniping.",
        "best_for": "Quick-scopers and aggressive marksmen on medium-sized maps.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Fast & Fun",
        "recoil_profile": "Fast bolt cycle allowing quick follow-up shots.",
        "pro_tip": "Aim upper chest or head for instant 1-shot kills."
    },
    "kv_inhibitor": {
        "role_title": "🎯 Semi-Auto Spammer Sniper",
        "summary": "Semi-automatic sniper that lets you fire repeated high-caliber shots without bolt cycling.",
        "best_for": "Snipers who want quick 2-shot follow-ups without getting punished for missing.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Forgiving Semi-Auto",
        "recoil_profile": "Recoil resets quickly between semi-auto trigger pulls.",
        "pro_tip": "Double-tap the trigger to land a guaranteed 2-shot kill in half a second."
    }
}


# Fallback generator for uncataloged weapons
def get_weapon_plain_summary(weapon_id: str, weapon_name: str = "", weapon_class_val: str = "") -> Dict[str, Any]:
    """Returns curated plain-English summary or dynamically formats a friendly fallback."""
    clean_id = weapon_id.lower().replace("-", "_").replace(" ", "_")
    if clean_id in WEAPON_PLAIN_DOSSIERS:
        return WEAPON_PLAIN_DOSSIERS[clean_id]
    
    # Generic fallback
    cls_name = weapon_class_val.replace("_", " ").title() or "Weapon"
    name = weapon_name or weapon_id.upper()
    return {
        "role_title": f"🎯 Standard {cls_name} Platform",
        "summary": f"{name} is a balanced {cls_name.lower()} offering reliable combat performance in standard engagements.",
        "best_for": "General combat scenarios across small to medium map sightlines.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Balanced Control",
        "recoil_profile": "Standard class recoil curve.",
        "pro_tip": "Test with recoil-reducing muzzle and underbarrel attachments in the Build Optimizer."
    }


# ---------------------------------------------------------------------------
# 2. Dynamic 1-5 Star Ratings Calculator
# ---------------------------------------------------------------------------
def get_weapon_star_ratings(stats: Any, weapon_class: Any) -> Dict[str, Tuple[int, str]]:
    """
    Computes intuitive 1 to 5 star ratings for physical weapon stats:
    - Kill Speed (TTK / RPM)
    - Ease of Control (Recoil)
    - Quick-Aim Speed (ADS)
    - Mobility (Sprint-to-Fire & Movement)
    - Long Range Punch (Bullet Velocity & Range)
    """
    # 1. Kill Speed (Higher RPM / Lower TTK = more stars)
    rpm = getattr(stats, "rpm", 600.0) or 600.0
    if rpm >= 850:
        star_kill = (5, "★★★★★ (Blistering Fast)")
    elif rpm >= 720:
        star_kill = (4, "★★★★☆ (Fast)")
    elif rpm >= 600:
        star_kill = (3, "★★★☆☆ (Balanced)")
    else:
        star_kill = (3, "★★★☆☆ (Heavy / Chugging)")

    # 2. Ease of Control (Lower recoil = more stars)
    h_rec = getattr(stats, "recoil_horizontal", 12.0) or 12.0
    v_rec = getattr(stats, "recoil_vertical", 24.0) or 24.0
    rec_sum = h_rec + v_rec
    if rec_sum <= 28.0:
        star_ctrl = (5, "★★★★★ (Zero Kick / Laser)")
    elif rec_sum <= 38.0:
        star_ctrl = (4, "★★★★☆ (Very Manageable)")
    elif rec_sum <= 50.0:
        star_ctrl = (3, "★★★☆☆ (Moderate Kick)")
    else:
        star_ctrl = (2, "★★☆☆☆ (Heavy Kick / High Skill)")

    # 3. Quick-Aim Speed (Lower ADS ms = more stars)
    ads = getattr(stats, "base_ads_ms", 250.0) or 250.0
    if ads <= 190.0:
        star_ads = (5, "★★★★★ (Lightning Fast)")
    elif ads <= 245.0:
        star_ads = (4, "★★★★☆ (Snappy & Quick)")
    elif ads <= 300.0:
        star_ads = (3, "★★★☆☆ (Average AR Speed)")
    else:
        star_ads = (2, "★★☆☆☆ (Slower / Heavy Weapon)")

    # 4. Long Range Power (Higher Velocity = more stars)
    vel = getattr(stats, "bullet_velocity_mps", 700.0) or 700.0
    if vel >= 850.0:
        star_range = (5, "★★★★★ (Instant Long-Range Hit)")
    elif vel >= 700.0:
        star_range = (4, "★★★★☆ (Great Velocity)")
    elif vel >= 550.0:
        star_range = (3, "★★★☆☆ (Standard)")
    else:
        star_range = (2, "★★☆☆☆ (Close-Range Focus)")

    return {
        "kill_speed": star_kill,
        "ease_of_control": star_ctrl,
        "quick_aim_speed": star_ads,
        "long_range_power": star_range
    }


# ---------------------------------------------------------------------------
# 3. Attachment Plain-English Benefit Translator
# ---------------------------------------------------------------------------
def get_attachment_plain_effects(att_id: str, att_name: str = "") -> List[str]:
    """Translates technical attachment names into instant, intuitive gameplay benefit tags."""
    a_id = att_id.lower()
    tags = []

    # Muzzles
    if "spiritfire" in a_id or "suppressor" in a_id:
        tags.append("🤫 Hides you from enemy radar")
        tags.append("🟢 Smoother bullet velocity")
    elif "compensator" in a_id or "brake" in a_id or "billeted" in a_id:
        tags.append("🟢 Calms down weapon kick")
        tags.append("🎯 Keeps gun straight while firing")
    elif "flash_hider" in a_id:
        tags.append("🟢 Eliminates muzzle flash glare")

    # Barrels
    if "long" in a_id or "cyclone" in a_id or "heavy" in a_id:
        tags.append("🎯 More damage at longer distance")
        tags.append("🟢 Bullets hit target faster")
        tags.append("⚠️ Slightly slower aim speed")
    elif "short" in a_id or "phantom" in a_id or "carbine" in a_id:
        tags.append("⚡ Faster movement & aim speed")
        tags.append("⚠️ Slightly less damage far away")

    # Underbarrels
    if "heavy" in a_id or "bruen" in a_id or "stabilizer" in a_id:
        tags.append("🟢 Huge recoil reduction")
        tags.append("🎯 Eliminates side-to-side gun shake")
    elif "handstop" in a_id or "dr6" in a_id or "angled" in a_id:
        tags.append("⚡ Snappy sprint-to-fire speed")
        tags.append("⚡ Faster Aim Down Sights")

    # Optics
    if "reflector" in a_id or "slate" in a_id or "dot" in a_id or "holo" in a_id:
        tags.append("🎯 Clean, clutter-free red dot sight")
        tags.append("👁️ Makes targets 10x easier to track")
    elif "scope" in a_id or "zoom" in a_id or "corio" in a_id:
        tags.append("🔭 High zoom for far away targets")

    # Magazines
    if "40" in a_id or "45" in a_id:
        tags.append("🔋 +10 to +15 extra bullets per mag")
        tags.append("🛡️ Win 1v2 and 1v3 fights without reloading")
    elif "50" in a_id or "60" in a_id or "drum" in a_id:
        tags.append("🔋 Huge ammo capacity (Endless firing)")
        tags.append("⚠️ Slightly slower movement speed")

    # Stocks
    if "skeleton" in a_id or "cqb" in a_id or "light" in a_id:
        tags.append("🏃 Super fast strafing & aim speed")
    elif "heavy" in a_id or "tac" in a_id or "precision" in a_id:
        tags.append("🎯 Rock-solid aim stability when taking hits")

    # Rear Grips / Lasers
    if "laser" in a_id or "grimline" in a_id:
        tags.append("⚡ Instant sprint-to-shoot reaction")
    elif "grip" in a_id:
        tags.append("🟢 Extra flinch & recoil control")

    if not tags:
        tags = ["✅ Enhances weapon combat performance", "🎯 Tuned for competitive consistency"]

    return tags


# ---------------------------------------------------------------------------
# 4. Field Intel Callout Component
# ---------------------------------------------------------------------------
def render_field_intel_box(title: str, text: str, tip: str = "") -> None:
    """Renders a sleek, dark-tactical 'Field Intel / In Plain English' explainer card."""
    tip_html = f'<div style="margin-top: 6px; padding-top: 6px; border-top: 1px dashed rgba(56, 189, 248, 0.25); color: #7dd3fc; font-size: 11.5px;"><b>💡 Tactical Pro-Tip:</b> {tip}</div>' if tip else ""
    
    html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.7) 100%);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-left: 5px solid #38bdf8;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    ">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
            <span style="font-size: 15px;">💡</span>
            <span style="font-size: 13px; font-weight: 700; color: #38bdf8; letter-spacing: 0.5px; text-transform: uppercase;">
                Field Intel • In Plain English: {title}
            </span>
        </div>
        <div style="color: #cbd5e1; font-size: 12.5px; line-height: 1.5;">
            {text}
        </div>
        {tip_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# 5. Tactical Arsenal Matchmaker Recommendation Logic
# ---------------------------------------------------------------------------
def get_matchmaker_recommendation(
    playstyle_choice: str,
    distance_choice: str,
    control_pref: str
) -> Dict[str, Any]:
    """
    Maps 3 intuitive player questions to the ultimate matched weapon,
    a ready-to-use 5-slot build preset, and a 10-second plain-English guide.
    """
    # 1. Aggressive Run & Gun / Fast CQB
    if "Aggressive CQB" in playstyle_choice or "Run & Gun" in playstyle_choice:
        return {
            "weapon_id": "rival_9",
            "weapon_name": "Rival-9 (Submachine Gun)",
            "build_name": "⚡ CDL Pro Tournament Shredder",
            "role_badge": "👑 #1 Competitive Close-Quarters SMG",
            "ease_rating": "★★★★☆ (Super Snappy & Agile)",
            "why_it_works": "The fastest killing SMG in the game up close with lightning-fast sprint-to-fire speed. If you like sliding around corners and deleting enemies in half a second, this is your weapon.",
            "attachments": [
                ("Muzzle", "Shadowstrike Suppressor", "Silent gunfire with zero aiming speed penalty"),
                ("Barrel", "Rival-C Clear Shot Barrel", "Boosts bullet velocity for reliable hit registration"),
                ("Underbarrel", "DR-6 Handstop", "Lightning-fast sprint-to-fire and ADS speed"),
                ("Stock", "MTZ Marauder Stock", "Improves firing aim stability while strafing"),
                ("Rear Grip", "Rival Vice Assault Grip", "Keeps rapid-fire recoil centered")
            ],
            "combat_tip": "Keep moving! Slide into rooms and hip-fire to ADS immediately to catch enemies off-guard."
        }

    # 2. Heavy Punch / Maximum Impact (Battle Rifle / Heavy AR)
    elif "Heavy Punch" in playstyle_choice or "Stopping Power" in playstyle_choice:
        return {
            "weapon_id": "bas_b",
            "weapon_name": "BAS-B (Battle Rifle)",
            "build_name": "💥 7.62 Sledgehammer Meta",
            "role_badge": "👑 Hardest Hitting Full-Auto in MW4",
            "ease_rating": "★★★★☆ (Massive Bullet Damage)",
            "why_it_works": "Fires full-size 7.62 battle rifle cartridges. Drops enemies in just 3 chest shots at close-to-medium range.",
            "attachments": [
                ("Muzzle", "VT-7 Spiritfire Suppressor", "Reduces recoil and keeps you off radar"),
                ("Barrel", "Bruen Venom Long Barrel", "Boosts bullet velocity to 850+ m/s"),
                ("Underbarrel", "Bruen Heavy Support Grip", "Tames the heavy 7.62 recoil punch"),
                ("Optic", "Slate Reflector", "Clear red dot sight"),
                ("Magazine", "30-Round Extended Mag", "Essential upgrade over default 20-round magazine")
            ],
            "combat_tip": "Fire in 4-to-5 bullet bursts at long distance; hold full auto in close quarters."
        }

    # 3. Long-Range Lane Anchor / Marksman
    elif "Long-Range" in playstyle_choice or "Sniper" in playstyle_choice or "Precision" in control_pref:
        if "Sniper" in playstyle_choice:
            return {
                "weapon_id": "longbow",
                "weapon_name": "Longbow (Sniper Rifle)",
                "build_name": "🎯 Aggressive Quick-Scope 1-Shot",
                "role_badge": "👑 Most Fun & Forgiving Sniper",
                "ease_rating": "★★★★☆ (Fast Bolt + Big Mag)",
                "why_it_works": "Unlike heavy snipers that take 2 seconds to aim, the Longbow scopes in instantly and holds 30 rounds in the magazine with a rapid bolt cycle.",
                "attachments": [
                    ("Muzzle", "Shadowstrike Suppressor", "Undetected firing with no ADS penalty"),
                    ("Barrel", "Pro-99 Long Barrel", "Increases 1-shot lethal kill distance"),
                    ("Laser", "FSS OLE-V Laser", "Maximum scope-in aim speed"),
                    ("Stock", "Tactical Light Stock", "Snappy aim-walking speed"),
                    ("Bolt", "Quick-Bolt Mechanism", "Fastest follow-up shot chambering")
                ],
                "combat_tip": "Aim at the upper torso and shoulders for guaranteed 1-shot eliminations."
            }
        else:
            return {
                "weapon_id": "mcw",
                "weapon_name": "MCW (Assault Rifle)",
                "build_name": "🔭 Tournament Lane Anchor Laser",
                "role_badge": "👑 #1 Long-Range Precision AR",
                "ease_rating": "★★★★★ (Zero Sway & Pinpoint)",
                "why_it_works": "Designed specifically for picking off head-glitching enemies across the longest sightlines in the game. It never kicks off-target.",
                "attachments": [
                    ("Muzzle", "VT-7 Spiritfire Suppressor", "Radar stealth & maximum bullet speed"),
                    ("Barrel", "16.5' MCW Cyclone Long Barrel", "Extends max damage range by +20%"),
                    ("Underbarrel", "Bruen Heavy Support Grip", "Rock-solid horizontal gun steadiness"),
                    ("Optic", "Corio Eagleseye 2.5x", "Magnified optical sight for picking off distant targets"),
                    ("Magazine", "40-Round Mag", "Extended capacity for sustained lane suppression")
                ],
                "combat_tip": "Mount on low walls or crates to hold down capture points with 100% pinpoint accuracy."
            }

    # 4. Zero Recoil Laser Beam (Ease of Control Priority) / Default
    else:
        if "Close" in distance_choice:
            return {
                "weapon_id": "striker",
                "weapon_name": "Striker (Submachine Gun)",
                "build_name": "⚡ Zero-Kick CQB Laser",
                "role_badge": "👑 Undisputed Easiest SMG to Aim",
                "ease_rating": "★★★★★ (Zero Kick)",
                "why_it_works": "The Striker has almost no horizontal drift and fires at a predictable cadence, meaning all your bullets hit the target without you needing to fight the joystick or mouse.",
                "attachments": [
                    ("Muzzle", "VT-7 Spiritfire Suppressor", "Hides gunfire from enemy mini-map & calms recoil"),
                    ("Barrel", "Striker Recon Long Barrel", "Pushes maximum damage out to longer distance"),
                    ("Underbarrel", "Bruen Heavy Support Grip", "Stops side-to-side gun shake completely"),
                    ("Optic", "Slate Reflector", "Super clean red dot for effortless target acquisition"),
                    ("Magazine", "48-Round Extended Mag", "Enough ammo to eliminate 3 enemies in a row")
                ],
                "combat_tip": "Point, hold the trigger, and stay centered on the torso. This gun does the work for you."
            }
        elif "Large" in distance_choice or "Long-Range" in distance_choice:
            return {
                "weapon_id": "pulemyot_762",
                "weapon_name": "Pulemyot 762 (Bullpup LMG)",
                "build_name": "🛡️ 100-Round Zero-Recoil Turret",
                "role_badge": "👑 Endless Ammo & Zero Kick",
                "ease_rating": "★★★★★ (No Recoil + Never Reload)",
                "why_it_works": "With the Bullpup conversion, this LMG transforms into a lightweight assault rifle that holds 100 rounds and shoots in a dead-straight line at any distance.",
                "attachments": [
                    ("Muzzle", "VT-7 Spiritfire Suppressor", "Silences weapon and boosts bullet velocity"),
                    ("Barrel", "JAK Annihilator Long Barrel", "Max damage range and bullet speed"),
                    ("Underbarrel", "Bruen Heavy Support Grip", "Maximum horizontal gun stability"),
                    ("Optic", "Corio Eagleseye 2.5x", "Crisp medium-range magnification"),
                    ("Stock", "Rubberized Recoil Stock", "Cushions vertical kick")
                ],
                "combat_tip": "Don't be afraid to hold down the trigger through walls and doorways. You have 100 bullets!"
            }
        else:
            return {
                "weapon_id": "xm4",
                "weapon_name": "XM4 (Assault Rifle)",
                "build_name": "👑 CDL Pro Zero-Recoil Beam",
                "role_badge": "👑 #1 Best All-Rounder in MW4",
                "ease_rating": "★★★★★ (Effortless Laser)",
                "why_it_works": "The XM4 is the gold standard of MW4. It has a forgiving fire rate, rapid aim speed, and virtually zero kick, making it dominate both 15m and 35m gunfights.",
                "attachments": [
                    ("Muzzle", "VT-7 Spiritfire Suppressor", "Hides gunfire on radar and smooths recoil"),
                    ("Barrel", "Cyclone Long Barrel", "Increases bullet velocity and effective range"),
                    ("Underbarrel", "Bruen Heavy Support Grip", "Stops horizontal gun shake"),
                    ("Optic", "Slate Reflector", "Ultra-clean sight picture with zero visual clutter"),
                    ("Magazine", "40-Round Mag", "Extra bullets for multiple enemy encounters")
                ],
                "combat_tip": "Aim at the chest. The gentle upward drift will land automatic headshots for super fast kills."
            }


# ---------------------------------------------------------------------------
# 6. Tactical Ballistics Codex & Jargon Translator
# ---------------------------------------------------------------------------
def render_tactical_ballistics_codex() -> None:
    """Renders an interactive plain-English translation codex for FPS ballistics."""
    with st.expander("📖 Tactical Ballistics Codex & Jargon Translator (Plain-English Cheat Sheet)", expanded=False):
        st.caption("Quickly understand the key competitive stats and what they actually mean during a real gunfight:")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            #### ⚡ Speed & Killing Power
            * **TTK (Time-To-Kill):** *How fast the gun eliminates an enemy.*
              * Lower milliseconds = Faster kill (e.g., `210ms` is lightning fast; `320ms` is on the slower side).
            * **STK (Shots-To-Kill):** *How many physical bullets you must land to get the elimination.*
              * (e.g. `4 Bullets to Kill` vs `5 Bullets to Kill`).
            * **RPM (Rounds Per Minute):** *How fast the gun spits bullets when you hold the trigger.*
              * High RPM (`800+ RPM`) is forgiving if you miss a shot. Slow RPM (`500 RPM`) means each missed shot hurts.
            * **Bullet Velocity (m/s):** *How fast the projectile flies through the air.*
              * High velocity (`800+ m/s`) means you don't need to lead moving targets at long range.
            """)
            
        with c2:
            st.markdown("""
            #### 🏃 Handling, Recoil & Movement
            * **ADS Speed (Aim-Down-Sights):** *How fast you bring your weapon up to your eye.*
              * Snappy ADS (`<200ms`) lets you react instantly to unexpected enemies.
            * **Sprint-to-Fire (STF):** *How long it takes to fire your first shot after running.*
              * Critical for aggressive rushers who sprint into rooms.
            * **Recoil (Kick & Stability):** *How much the gun jumps off-center.*
              * **Vertical Recoil:** Gun climbs straight up (easy to pull down).
              * **Horizontal Recoil:** Gun shakes left and right (harder to control; use underbarrel grips).
            * **Pareto-Optimal Build:** *The absolute best mathematical loadouts where no stat is wasted.*
            """)
