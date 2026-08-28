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
    "patriot_xmr": {
        "role_title": "🎯 Laser Beam All-Rounder",
        "summary": "The ultimate reliable workhorse. Shoots like a laser beam with almost zero gun kick and very forgiving fire rate.",
        "best_for": "Players who want an easy-to-aim gun that works great in every medium-range gunfight.",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Laser Beam)",
        "recoil_profile": "Minimal upward climb, virtually zero side-to-side bounce.",
        "pro_tip": "Aim at the chest and let the slight upward drift land effortless headshots."
    },
    "m4": {
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
    "iso_nightshade": {
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
    },
    "han_86": {
        "role_title": "🎯 Bullpup Laser Beamer",
        "summary": "Ultra-tight bullpup recoil architecture. Virtually zero muzzle climb during sustained full-auto fire.",
        "best_for": "Beaming enemies off power positions and head glitches across mid-range lanes.",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Zero Kick)",
        "recoil_profile": "Dead straight line recoil pattern.",
        "pro_tip": "Pair with a clean red dot for unmatched sightline lockdown."
    },
    "hyeon_burst": {
        "role_title": "🎯 1-Burst Lethal Marksman AR",
        "summary": "Fires hyper-compact 3-round bursts with pinpoint grouping.",
        "best_for": "High-accuracy players seeking 1-burst eliminations.",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Tight Burst)",
        "recoil_profile": "Minimal recoil inside each 3-round burst cluster.",
        "pro_tip": "Aim at the neck/upper-torso; the 3rd bullet will headshot for an instant kill."
    },
    "kastov_74m": {
        "role_title": "💥 Heavy 7.62 Punch Rifle",
        "summary": "Hard-hitting assault rifle with high bullet damage, balanced by punchy vertical climb.",
        "best_for": "Aggressive AR players who can pull down on recoil to melt targets fast.",
        "ease_rating": 2,
        "ease_label": "⭐⭐☆☆☆ Punchy (Heavy Kick)",
        "recoil_profile": "Steep upward vertical climb on sustained automatic fire.",
        "pro_tip": "Equip a heavy compensator and vertical underbarrel grip."
    },
    "signal_50": {
        "role_title": "💀 .50 BMG Semi-Auto Sniper",
        "summary": "Heavy anti-materiel rifle with rapid semi-automatic follow-up shots.",
        "best_for": "Snipers holding long lines who want quick multi-target eliminations.",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ Heavy .50 Cal Kick",
        "recoil_profile": "High vertical jump with fast centering.",
        "pro_tip": "Wait a fraction of a second for the reticle to settle before your second shot."
    },
    "kvd_enforcer": {
        "role_title": "🎯 2-Shot Precision Marksman",
        "summary": "Semi-automatic designated marksman rifle offering consistent 2-shot lethality.",
        "best_for": "Mid-to-long range tap-firing.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Very Manageable",
        "recoil_profile": "Predictable vertical jump on each trigger pull.",
        "pro_tip": "Paces shots smoothly for guaranteed double-tap kills."
    },
    "lockwood_680": {
        "role_title": "💥 1-Pump Lethal Breaching Shotgun",
        "summary": "Devastating pump-action shotgun that deletes enemies in 1 point-blank blast.",
        "best_for": "Room clearing, stairwell defense, and slide-in point blank encounters.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Simple Pump Reset",
        "recoil_profile": "Heavy single-shot pump kick.",
        "pro_tip": "Slide into enemies before firing to maximize pellet spread density."
    },
    "haymaker": {
        "role_title": "💨 Semi-Auto Drum Spammer",
        "summary": "Spam-fire shotgun with massive drum magazine for continuous room clearing.",
        "best_for": "Close-quarters chaos and multi-enemy objective pushes.",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Easy Hipfire",
        "recoil_profile": "Continuous moderate rise.",
        "pro_tip": "Use hipfire attachments and never stop moving."
    },
    "cor_45": {
        "role_title": "⚡ Lightning Semi-Auto Sidearm",
        "summary": "Snappy tactical pistol with fast swap speed and minimal recoil.",
        "best_for": "Finishing off weak enemies when your primary runs dry.",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Instant Swap)",
        "recoil_profile": "Light pistol muzzle pop.",
        "pro_tip": "Switching to your pistol is always faster than reloading!"
    },
    "renetti": {
        "role_title": "🎯 3-Round Burst Pocket Shredder",
        "summary": "Burst fire handgun that melts enemies at point-blank range.",
        "best_for": "CQB backup sidearm for sniper or LMG classes.",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Burst Control)",
        "recoil_profile": "Tight, fast burst cluster.",
        "pro_tip": "Aim at the chest for an instant burst elimination."
    }
}


# Fallback generator and dynamic stat calculator for all weapons
def get_weapon_plain_summary(
    weapon_id: str,
    weapon_name: str = "",
    weapon_class_val: str = "",
    stats: Optional[Any] = None
) -> Dict[str, Any]:
    """Returns curated plain-English summary with true dynamic data-driven recoil ratings."""
    clean_id = weapon_id.lower().replace("-", "_").replace(" ", "_")
    matched_dossier = None

    if clean_id in WEAPON_PLAIN_DOSSIERS:
        matched_dossier = dict(WEAPON_PLAIN_DOSSIERS[clean_id])
    else:
        # Fuzzy alias resolver
        normalized_keys = {
            "patriot_xmr": ["xm4"],
            "m4": ["mcw"],
            "m4": ["m4_"],
            "holger_556": ["holger", "holger556"],
            "mtz_556": ["mtz556", "mtz_556"],
            "kastov_74m": ["ak74m", "kastov"],
            "hyeon_burst": ["hyeon"],
            "han_86": ["han86", "han_86"],
            "iso_nightshade": ["rival9", "rival_9"],
            "striker": ["striker45", "striker_45", "striker"],
            "striker_9": ["striker9", "striker_9"],
            "superi_46": ["superi"],
            "amr9": ["amr9", "amr_9"],
            "hrm_9": ["hrm9", "hrm_9"],
            "wsp_9": ["wsp9", "wsp_9"],
            "wsp_swallow": ["wsp_swarm", "wsp_swallow", "wsp"],
            "bas_b": ["basb", "bas_b"],
            "sidewinder": ["sidewinder"],
            "mtz_762": ["mtz762", "mtz_762"],
            "pulemyot_762": ["pulemyot", "pulemyot762"],
            "bruen_mk9": ["bruen", "bruen_mk9"],
            "dg_58_lsb": ["dg58", "dg_58"],
            "katt_amr": ["katt", "katt_amr"],
            "longbow": ["longbow"],
            "signal_50": ["signal50", "signal_50", "dmr_signal50"],
            "kvd_enforcer": ["kvd", "kvd_enforcer"],
            "lockwood_680": ["lockwood", "lockwood680"],
            "haymaker": ["haymaker"],
            "cor_45": ["cor45", "cor_45"],
            "renetti": ["renetti"]
        }
        for d_key, aliases in normalized_keys.items():
            if any(alias in clean_id for alias in aliases):
                if d_key in WEAPON_PLAIN_DOSSIERS:
                    matched_dossier = dict(WEAPON_PLAIN_DOSSIERS[d_key])
                    break

    if not matched_dossier:
        cls_name = weapon_class_val.replace("_", " ").title() or "Weapon"
        name = weapon_name or weapon_id.upper()
        matched_dossier = {
            "role_title": f"🎯 Standard {cls_name} Platform",
            "summary": f"{name} is a balanced {cls_name.lower()} offering reliable combat performance in standard engagements.",
            "best_for": "General combat scenarios across small to medium map sightlines.",
            "ease_rating": 3,
            "ease_label": "⭐⭐⭐☆☆ Balanced Kick",
            "recoil_profile": "Standard class recoil curve.",
            "pro_tip": "Test with recoil-reducing muzzle and underbarrel attachments in the Build Optimizer."
        }

    # If physical stats are provided, compute TRUE physical recoil rating dynamically!
    if stats is not None:
        h_rec = getattr(stats, "recoil_horizontal", 16.0) or 16.0
        v_rec = getattr(stats, "recoil_vertical", 24.0) or 24.0
        rec_sum = float(h_rec) + float(v_rec)
        
        if rec_sum <= 28.0:
            matched_dossier["ease_rating"] = 5
            matched_dossier["ease_label"] = "⭐⭐⭐⭐⭐ Very Easy (Zero Kick)"
        elif rec_sum <= 38.0:
            matched_dossier["ease_rating"] = 4
            matched_dossier["ease_label"] = "⭐⭐⭐⭐☆ Easy (Very Smooth)"
        elif rec_sum <= 50.0:
            matched_dossier["ease_rating"] = 3
            matched_dossier["ease_label"] = "⭐⭐⭐☆☆ Moderate (Balanced Kick)"
        elif rec_sum <= 65.0:
            matched_dossier["ease_rating"] = 2
            matched_dossier["ease_label"] = "⭐⭐☆☆☆ Punchy (Heavy Kick)"
        else:
            matched_dossier["ease_rating"] = 1
            matched_dossier["ease_label"] = "⭐☆☆☆☆ High Skill (Severe Kick)"

    return matched_dossier


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
# 3b. Attachment Weapon Unlock Levels Mapping & Helper
# ---------------------------------------------------------------------------
ATTACHMENT_UNLOCK_LEVELS: Dict[str, int] = {
    "shadowstrike suppressor": 2,
    "vt-7 spiritfire suppressor": 14,
    "casus brake compensator": 8,
    "casus brake": 8,
    "ported tactical compensator": 5,
    "l4r flash hider": 3,
    "colossus heavy silencer": 17,
    "crown-50 muzzle brake": 11,
    "purifier horizontal brake": 19,
    "cyclone heavy long barrel": 12,
    "cyclone long barrel": 12,
    "16.5' mcw cyclone long barrel": 12,
    "phantom cqb short barrel": 6,
    "reinforced match barrel": 16,
    "ultralight fluted barrel": 9,
    "chf heavy cold-forged barrel": 20,
    "triton integrally suppressed barrel": 18,
    "short carbine speed barrel": 4,
    "rival-c clear shot barrel": 8,
    "bruen venom long barrel": 15,
    "pro-99 long barrel": 14,
    "striker recon long barrel": 12,
    "jak annihilator long barrel": 18,
    "ftac grimline tac laser": 5,
    "corio laz-44 precision laser": 10,
    "schlager peq box iv": 8,
    "fss ole-v laser": 14,
    "point-g3p 1mw tactical laser": 3,
    "dxs flash 90 tac-stance laser": 11,
    "slate reflector": 3,
    "mk.3 reflector": 2,
    "corio eagleseye 2.5x scope": 16,
    "corio eagleseye 2.5x": 16,
    "cronen mini pro (blue dot)": 7,
    "sz sro-7 holographic": 11,
    "acog 4.0x tactical scope": 19,
    "thermo-optic x9 thermal": 21,
    "elite match iron sights": 1,
    "skeletonized cqb stock": 9,
    "heavy precision buffer stock": 18,
    "no stock mod": 15,
    "heavy tactical anchor stock": 12,
    "commando lightweight stock": 4,
    "buffer tube ultralight stock": 7,
    "mtz marauder stock": 9,
    "tactical light stock": 6,
    "rubberized recoil stock": 11,
    "dr-6 handstop": 7,
    "bruen heavy support grip": 15,
    "ftac ripper 56 stabilizer": 10,
    "xten phantom-5 handstop": 6,
    "merc foregrip": 4,
    "operator vertical foregrip": 13,
    "chemerov heavy angled grip": 17,
    "40-round extended magazine": 4,
    "40-round mag": 4,
    "50-round heavy drum": 14,
    "60-round super drum": 22,
    "20-round fast speed mag": 8,
    "30-round extended mag": 6,
    "48-round extended mag": 10,
    "100-round ammo belt box": 24,
    "high grain match ammunition": 11,
    "overpressured +p match ammo": 7,
    "armor piercing tungsten rounds": 13,
    "low grain subsonic rounds": 5,
    "hollow point frangible ammo": 9,
    "dragon's breath incendiary rounds": 18,
    "explosive heavy slug rounds": 21,
    "frangible disabling rounds": 15,
    "phantom tactical grip": 6,
    "heavy ergonomic tac grip": 14,
    "stippled rubberized grip": 10,
    "granulated match grip": 3,
    "rival vice assault grip": 10,
    "quick-bolt mechanism": 8,
}


def get_attachment_unlock_level(att_name_or_id: str) -> int:
    """Returns the weapon level required to unlock a specific attachment in MW4."""
    clean = (att_name_or_id or "").strip().lower()
    if clean in ATTACHMENT_UNLOCK_LEVELS:
        return ATTACHMENT_UNLOCK_LEVELS[clean]
    for k, v in ATTACHMENT_UNLOCK_LEVELS.items():
        if k in clean or clean in k:
            return v
    return 10


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
            "weapon_name": "ISO Nightshade (Submachine Gun)",
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
                "weapon_name": "M4 (Assault Rifle)",
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
                "weapon_name": "Patriot XMR (Assault Rifle)",
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

WEAPON_PLAIN_INTELLIGENCE = {
    "patriot_xmr_mw4": {
        "title": "🔥 4-Shot Fast Full-Auto Laser",
        "best_at": "Mid-range duels where you want the fastest automatic kill time in the beta.",
        "pros": ["#1 Fastest TTK full-auto AR (279ms)", "Very easy vertical recoil", "Excellent 32.5m damage range"],
        "cons": ["25-round base magazine requires trigger discipline", "Moderate reload time"],
        "summary": "The undisputed king of assault rifles in the 2026 MW4 Beta. Deals 28 chest damage for an ultra-fast 4-shot kill."
    },
    "iso_nightshade_mw4": {
        "title": "⚡ 923-RPM #1 Fastest TTK SMG",
        "best_at": "Aggressive close-quarters rushing and room clearing.",
        "pros": ["#1 Fastest TTK SMG in the game (260ms)", "Blistering 923 RPM rate of fire", "Fastest sprint-out time"],
        "cons": ["High fire rate burns through 30 rounds quickly", "Damage falls off sharply past 10 meters"],
        "summary": "The ultimate close-range weapon in the Beta. If you love rushing and slide-canceling into rooms, this is your #1 primary."
    },
    "hyeon_burst_mw4": {
        "title": "⚡ 1-Burst Lethal Marksman AR",
        "best_at": "Precision players who can land upper-chest and headshots.",
        "pros": ["Lethal 1-burst kill potential (141ms TTK)", "Extremely flat recoil within the 3-round burst", "Class-leading 38.1m range"],
        "cons": ["Punishing delay between bursts if you miss", "Struggles against multiple rushing enemies"],
        "summary": "A high-skill ceiling rifle with a North Korean prototype burst mechanism. One headshot guarantees a 1-burst instant kill."
    },
    "type73_mw4": {
        "title": "💥 821-RPM High-Cadence LMG",
        "best_at": "Locking down lanes, objective defense, and multi-kill squad wipes.",
        "pros": ["Blazing 821 RPM fire rate", "60-round drum capacity", "Dominates medium and long sightlines"],
        "cons": ["Heavier ADS time than assault rifles", "Slower tactical reload"],
        "summary": "An absolute monster of an LMG. Combines the high rate of fire of an SMG with the sustained 60-round drum and range of an LMG."
    },
    "kg7_vulcan_mw4": {
        "title": "🎯 1-Shot Bolt Anti-Personnel Sniper",
        "best_at": "Long-range sniping and holding power positions.",
        "pros": ["1-shot kill to head and upper chest at all ranges", "10-round detachable magazine", "Crisp scope reticle"],
        "cons": ["37 RPM bolt cycle requires accurate first shots", "Slow ADS handling"],
        "summary": "The premier sniper rifle in the MW4 Beta. Rewards steady aim with guaranteed one-shot eliminations across all map sightlines."
    },
    "krait_p68_mw4": {
        "title": "🔫 Buffed 46-Damage Sidearm",
        "best_at": "Finishing off weak enemies and lightning-fast weapon swaps.",
        "pros": ["Massive 46 chest damage (3-shot kill)", "450 RPM semi-auto trigger cap", "15-round standard capacity"],
        "cons": ["Semi-auto trigger finger required", "Severe recoil at long range"],
        "summary": "The best secondary in the beta. Receives massive damage buffs that allow it to out-duel primary weapons in close quarters."
    },
    "ppsh41_mw4": {
        "title": "⚡ 1110-RPM 71-Round Drum Hose",
        "best_at": "Hipfiring, hip-sliding, and sustained multi-target hipfire sprays.",
        "pros": ["Extreme 1110 RPM rate of fire", "Huge 71-round drum from level 11", "Great hipfire spread"],
        "cons": ["6-shot kill requirement (19 chest damage)", "Open-bolt delay of 30ms"],
        "summary": "A legendary bullet hose that never stops shooting. Perfect for clearing hardpoints and hipfiring through choke points."
    },
    "x58_nyx_mw4": {
        "title": "🤫 Integrally Suppressed Infiltrator",
        "best_at": "Flanking behind enemy lines without appearing on the radar.",
        "pros": ["Built-in monolithic suppressor keeps you off the minimap", "Generous 40-round magazine", "Smooth controllable recoil"],
        "cons": ["Moderate 800 RPM fire rate", "Slightly slower sprint-to-fire than ISO"],
        "summary": "The ultimate stealth SMG. Completely silenced out of the box with 40 rounds, making it ideal for flanking on high-traffic maps."
    },
    "oris86_mw4": {
        "title": "🎯 8.6 Blackout Bolt-Action DMR",
        "best_at": "Mid-to-long range precision tap-firing and aggressive recon.",
        "pros": ["Heavy 8.6mm Blackout stopping power", "Fast handling compared to snipers", "High bullet velocity"],
        "cons": ["89 RPM bolt cycle punishes missed shots", "Requires upper torso hits for maximum damage"],
        "summary": "A specialized bolt-action marksman rifle chambered in 8.6 Blackout. Bridges the gap between agile DMRs and heavy snipers."
    },
    "kastov762_mw4": {
        "title": "💥 Heavy 7.62 Punch Rifle",
        "best_at": "Mid-range lane holding and high-damage per bullet tapping.",
        "pros": ["Highest damage per bullet among assault rifles (30 dmg)", "Consistent 4-shot kill", "3-shot kill with 1 headshot"],
        "cons": ["Moderate 600 RPM fire rate", "Notable vertical recoil jump"],
        "summary": "Hits like a freight train. Deals 30 chest damage for a guaranteed 4-shot kill with great headshot multipliers."
    },
    "signal50_mw4": {
        "title": "💀 .50 BMG Semi-Auto Sniper",
        "best_at": "Rapid follow-up anti-materiel sniper fire.",
        "pros": ["111 RPM rapid semi-auto firing", "Heavy .50 BMG kinetic shock", "Devastating vehicle/streak damage"],
        "cons": ["Strong visual recoil kick", "7-round magazine"],
        "summary": "A semi-automatic .50 BMG sniper rifle with a reciprocating barrel system that allows instant follow-up shots."
    },
    "mar9_mw4": {
        "title": "🎯 315-RPM Rapid Precision DMR",
        "best_at": "Spamming precision shots at medium to long range.",
        "pros": ["315 RPM semi-auto speed", "20-round magazine", "Low recoil rise"],
        "cons": ["Requires 3 to 4 hits to eliminate", "Loses to full-auto ARs inside 15m"],
        "summary": "A rapid-firing semi-auto marksman rifle that lets you pepper targets down long sightlines with pinpoint precision."
    },
    "rezi12_mw4": {
        "title": "🚪 CQB 150-RPM Room Breacher",
        "best_at": "Instant point-blank corner clearing and tight interior hallways.",
        "pros": ["Semi-auto 150 RPM rapid follow-up shells", "Deadly 1-2 pump close-range burst", "Fast pump cycling"],
        "cons": ["Useless past 10 meters", "6-round tube requires frequent reloads"],
        "summary": "A semi-automatic 12-gauge shotgun designed for aggressive CQB breaching and tight room engagements."
    },
    "m4_mw4": {
        "title": "🛡️ 810-RPM Reliable Workhorse",
        "best_at": "All-around gameplay for players who want a balanced, reliable weapon.",
        "pros": ["Fast 810 RPM fire rate", "Predictable, easy-to-control recoil", "Extensive attachment customization"],
        "cons": ["5-shot kill in Weekend 2 patch", "Moderate 27.4m range"],
        "summary": "The classic Modern Warfare workhorse. Dependable, balanced, and highly adaptable across every combat distance."
    },
    "finn_lmg_mw4": {
        "title": "🛡️ 100-Round Sustained Belt",
        "best_at": "Continuous suppressive fire and holding objective lanes.",
        "pros": ["100-round endless ammo belt", "Laser-beam flat recoil curve", "Great long-range velocity"],
        "cons": ["Slow 587 RPM cadence", "Heavy 6.2s empty reload time"],
        "summary": "A true heavy machine gun with virtually zero recoil. Holds 100 rounds in a single belt to suppress entire teams."
    },
    "han86_mw4": {
        "title": "🎯 Bullpup Laser Beamer",
        "best_at": "Long-range precision beaming and lane control.",
        "pros": ["Extremely low horizontal recoil", "Good 740 RPM fire rate", "Clean iron sights"],
        "cons": ["5-shot kill requires 100 HP Core consistency", "Moderate reload speed"],
        "summary": "A South Korean bullpup rifle engineered for extreme accuracy and low recoil across medium to long distances."
    },
    "gs50_mw4": {
        "title": "🔫 .50 Cal 1-Tap Head Cannon",
        "best_at": "High-skill flick shots and finishing blows.",
        "pros": ["Massive 70 chest damage", "Guaranteed 1-shot headshot kill", "Huge intimidation factor"],
        "cons": ["180 RPM slow trigger", "Heavy visual muzzle climb", "7-round magazine"],
        "summary": "The iconic hand cannon. Deals 70 base damage and guarantees an instant 1-shot kill on any headshot."
    }
}


WEAPON_PLAIN_DOSSIERS = {
    "patriot_xmr_mw4": {
        "role_title": "🔥 4-Shot Fast Full-Auto Laser",
        "playstyle_category": "Competitive Aggressive Rifle",
        "plain_summary": "The undisputed #1 assault rifle in the MW4 Beta. Features a rapid 4-shot kill with minimal vertical recoil.",
        "best_for": "Mid-range duels and competitive tournament play.",
        "key_strength": "279ms TTK, 4-shot chest kill, 32.5m range.",
        "primary_flaw": "25-round magazine requires accurate bursts.",
        "recoil_feel": "Smooth straight-up climb. Virtually no side-to-side bounce."
    },
    "iso_nightshade_mw4": {
        "role_title": "⚡ 923-RPM #1 Fastest TTK SMG",
        "playstyle_category": "Fast CQB Rusher",
        "plain_summary": "The fastest killing submachine gun in the game. Melts enemies in 260ms at close range.",
        "best_for": "Slide-canceling, room clearing, and close-quarters duels.",
        "key_strength": "Blistering 923 RPM rate of fire and fast sprint-out.",
        "primary_flaw": "Burns through 30 rounds in 2 seconds.",
        "recoil_feel": "High vertical climb that requires pulling down on the stick."
    },
    "hyeon_burst_mw4": {
        "role_title": "⚡ 1-Burst Lethal Marksman AR",
        "playstyle_category": "High-Skill Marksman AR",
        "plain_summary": "Prototype 3-round burst rifle. One headshot secures an instant 141ms 1-burst kill.",
        "best_for": "Precision shooters who hit upper chest and headshots.",
        "key_strength": "141ms lethal 1-burst TTK ceiling out to 38.1m.",
        "primary_flaw": "Punishing delay between bursts if you miss.",
        "recoil_feel": "Extremely tight 3-bullet grouping."
    },
    "type73_mw4": {
        "role_title": "💥 821-RPM High-Cadence LMG",
        "playstyle_category": "Heavy Lane Anchor",
        "plain_summary": "Combines the fire rate of an SMG with the sustained 60-round drum of an LMG.",
        "best_for": "Locking down objectives and multi-kill squad wipes.",
        "key_strength": "821 RPM cadence and 60-round drum capacity.",
        "primary_flaw": "Slower ADS and movement speed.",
        "recoil_feel": "Moderate predictable climb with steady visual sights."
    },
    "kg7_vulcan_mw4": {
        "role_title": "🎯 1-Shot Bolt Anti-Personnel Sniper",
        "playstyle_category": "Precision Sniper",
        "plain_summary": "The premier bolt-action sniper rifle. One-shot kills to the upper torso and head.",
        "best_for": "Long-range lane holding and pickoffs.",
        "key_strength": "Guaranteed 1-shot elimination and 10-round detachable box magazine.",
        "primary_flaw": "37 RPM bolt cycle punishes missed shots.",
        "recoil_feel": "Heavy visual kick, recenters cleanly between bolt pulls."
    },
    "krait_p68_mw4": {
        "role_title": "🔫 Buffed 46-Damage Sidearm",
        "playstyle_category": "High-Damage Pocket Pistol",
        "plain_summary": "Massively buffed 46-damage sidearm that eliminates enemies in 3 rapid shots.",
        "best_for": "Emergency weapon swaps and close-range backup.",
        "key_strength": "3-shot kill stopping power and 450 RPM semi-auto cap.",
        "primary_flaw": "High visual kick on rapid trigger spam.",
        "recoil_feel": "Snappy upward muzzle rise."
    },
    "ppsh41_mw4": {
        "role_title": "⚡ 1110-RPM 71-Round Drum Hose",
        "playstyle_category": "Sustained Spray Machine",
        "plain_summary": "A legendary bullet hose that fires at 1110 RPM with a massive 71-round drum.",
        "best_for": "Hipfire sprays, multiple enemies, and hardpoint clearing.",
        "key_strength": "Huge 71-round drum and unmatched 1110 RPM fire rate.",
        "primary_flaw": "6-shot kill requirement at range.",
        "recoil_feel": "Chaotic upward spray, best controlled with hipfire builds."
    },
    "x58_nyx_mw4": {
        "role_title": "🤫 Integrally Suppressed Infiltrator",
        "playstyle_category": "Stealth Flanker SMG",
        "plain_summary": "Built-in monolithic suppressor keeps you completely invisible on enemy radar.",
        "best_for": "Flanking enemy spawns and stealth eliminations.",
        "key_strength": "Built-in suppressor and generous 40-round magazine.",
        "primary_flaw": "Moderate 800 RPM fire rate.",
        "recoil_feel": "Smooth, gentle recoil that is very easy to manage."
    },
    "oris86_mw4": {
        "role_title": "🎯 8.6 Blackout Bolt-Action DMR",
        "playstyle_category": "Tactical Heavy Marksman",
        "plain_summary": "Hard-hitting bolt-action DMR chambered in 8.6 Blackout with fast handling.",
        "best_for": "Aggressive sniping and medium-to-long range picking.",
        "key_strength": "High damage per shot and faster handling than snipers.",
        "primary_flaw": "89 RPM cycle rate.",
        "recoil_feel": "Clean, crisp single-shot jump."
    },
    "kastov762_mw4": {
        "role_title": "💥 Heavy 7.62 Punch Rifle",
        "playstyle_category": "Heavy Hard-Hitting AR",
        "plain_summary": "Fires heavy 7.62 rounds dealing 30 chest damage for a guaranteed 4-shot kill.",
        "best_for": "Holding long power positions and headshot tapping.",
        "key_strength": "30 chest damage and high headshot multiplier.",
        "primary_flaw": "600 RPM slower cadence.",
        "recoil_feel": "Strong vertical kick that rewards burst control."
    },
    "signal50_mw4": {
        "role_title": "💀 .50 BMG Semi-Auto Sniper",
        "playstyle_category": "Semi-Auto Anti-Materiel",
        "plain_summary": "Semi-automatic .50 BMG anti-materiel sniper with rapid follow-up fire.",
        "best_for": "Suppressing sniper positions and fast follow-up shots.",
        "key_strength": "111 RPM rapid semi-auto firing and massive bullet punch.",
        "primary_flaw": "Heaviest weapon handling in the beta.",
        "recoil_feel": "Significant barrel rise with reciprocating dampening."
    },
    "mar9_mw4": {
        "role_title": "🎯 315-RPM Rapid Precision DMR",
        "playstyle_category": "Rapid Semi-Auto DMR",
        "plain_summary": "Fast semi-auto marksman rifle with a 20-round magazine and pinpoint accuracy.",
        "best_for": "Mid-to-long range trigger spamming.",
        "key_strength": "315 RPM semi-auto rate of fire and low recoil.",
        "primary_flaw": "Requires 3-4 hits to eliminate.",
        "recoil_feel": "Minimal kick with fast reticle centering."
    },
    "rezi12_mw4": {
        "role_title": "🚪 CQB 150-RPM Room Breacher",
        "playstyle_category": "Semi-Auto Breaching Shotgun",
        "plain_summary": "Semi-automatic 12-gauge shotgun that clears tight rooms and doorways instantly.",
        "best_for": "Extreme close-quarters and interior building clearing.",
        "key_strength": "Fast 150 RPM semi-auto cycling and lethal 1-2 pump close range.",
        "primary_flaw": "No damage beyond 10 meters.",
        "recoil_feel": "Heavy muzzle rise on rapid trigger pulls."
    },
    "m4_mw4": {
        "role_title": "🛡️ 810-RPM Reliable Workhorse",
        "playstyle_category": "Versatile All-Round AR",
        "plain_summary": "The classic Modern Warfare workhorse. Fast 810 RPM fire rate and dependable handling.",
        "best_for": "All-around play across every map and game mode.",
        "key_strength": "Fast fire rate, predictable recoil, and deep customization.",
        "primary_flaw": "5-shot kill at standard ranges.",
        "recoil_feel": "Very gentle S-curve recoil, extremely easy to learn."
    },
    "finn_lmg_mw4": {
        "role_title": "🛡️ 100-Round Sustained Belt",
        "playstyle_category": "Zero-Recoil Heavy Turret",
        "plain_summary": "Features a 100-round belt and laser-beam accuracy for endless suppressive fire.",
        "best_for": "Locking down long sightlines without reloading.",
        "key_strength": "100-round continuous belt and almost zero recoil.",
        "primary_flaw": "Slow 587 RPM cadence and 6.2s empty reload.",
        "recoil_feel": "Virtually non-existent recoil, stays pinned to target."
    },
    "han86_mw4": {
        "role_title": "🎯 Bullpup Laser Beamer",
        "playstyle_category": "Precision Bullpup AR",
        "plain_summary": "South Korean bullpup assault rifle with exceptional long-range stability.",
        "best_for": "Beaming enemies off headglitches at medium-to-long distance.",
        "key_strength": "Pinpoint stability and high accuracy at range.",
        "primary_flaw": "5-shot kill requirement.",
        "recoil_feel": "Flat horizontal stability with mild vertical rise."
    },
    "gs50_mw4": {
        "role_title": "🔫 .50 Cal 1-Tap Head Cannon",
        "playstyle_category": "High-Damage Precision Pistol",
        "plain_summary": "Heavy caliber handgun that deals 70 damage and guarantees a 1-shot headshot kill.",
        "best_for": "Finishing weakened enemies and showing off precision aim.",
        "key_strength": "70 base damage and 1-shot lethal headshots.",
        "primary_flaw": "180 RPM fire rate and heavy visual jump.",
        "recoil_feel": "Massive muzzle jump that obscures targets briefly."
    }
}


def get_weapon_plain_summary(
    weapon_id: str,
    weapon_name: str = "",
    weapon_class_val: str = "",
    stats: Optional[Any] = None
) -> Dict[str, Any]:
    """Returns curated plain-English summary with true dynamic data-driven recoil ratings."""
    clean_id = weapon_id.lower().replace("-", "_").replace(" ", "_")
    matched_dossier = None

    if clean_id in WEAPON_PLAIN_DOSSIERS:
        matched_dossier = dict(WEAPON_PLAIN_DOSSIERS[clean_id])
    else:
        # Fuzzy alias resolver
        normalized_keys = {
            "patriot_xmr": ["xm4"],
            "m4": ["mcw"],
            "m4": ["m4_"],
            "holger_556": ["holger", "holger556"],
            "mtz_556": ["mtz556", "mtz_556"],
            "kastov_74m": ["ak74m", "kastov"],
            "hyeon_burst": ["hyeon"],
            "han_86": ["han86", "han_86"],
            "iso_nightshade": ["rival9", "rival_9"],
            "striker": ["striker45", "striker_45", "striker"],
            "striker_9": ["striker9", "striker_9"],
            "superi_46": ["superi"],
            "amr9": ["amr9", "amr_9"],
            "hrm_9": ["hrm9", "hrm_9"],
            "wsp_9": ["wsp9", "wsp_9"],
            "wsp_swallow": ["wsp_swarm", "wsp_swallow", "wsp"],
            "bas_b": ["basb", "bas_b"],
            "sidewinder": ["sidewinder"],
            "mtz_762": ["mtz762", "mtz_762"],
            "pulemyot_762": ["pulemyot", "pulemyot762"],
            "bruen_mk9": ["bruen", "bruen_mk9"],
            "dg_58_lsb": ["dg58", "dg_58"],
            "katt_amr": ["katt", "katt_amr"],
            "longbow": ["longbow"],
            "signal_50": ["signal50", "signal_50", "dmr_signal50"],
            "kvd_enforcer": ["kvd", "kvd_enforcer"],
            "lockwood_680": ["lockwood", "lockwood680"],
            "haymaker": ["haymaker"],
            "cor_45": ["cor45", "cor_45"],
            "renetti": ["renetti"]
        }
        for d_key, aliases in normalized_keys.items():
            if any(alias in clean_id for alias in aliases):
                if d_key in WEAPON_PLAIN_DOSSIERS:
                    matched_dossier = dict(WEAPON_PLAIN_DOSSIERS[d_key])
                    break

    if not matched_dossier:
        cls_name = weapon_class_val.replace("_", " ").title() or "Weapon"
        name = weapon_name or weapon_id.upper()
        matched_dossier = {
            "role_title": f"🎯 Standard {cls_name} Platform",
            "summary": f"{name} is a balanced {cls_name.lower()} offering reliable combat performance in standard engagements.",
            "best_for": "General combat scenarios across small to medium map sightlines.",
            "ease_rating": 3,
            "ease_label": "⭐⭐⭐☆☆ Balanced Kick",
            "recoil_profile": "Standard class recoil curve.",
            "pro_tip": "Test with recoil-reducing muzzle and underbarrel attachments in the Build Optimizer."
        }

    # If physical stats are provided, compute TRUE physical recoil rating dynamically!
    if stats is not None:
        h_rec = getattr(stats, "recoil_horizontal", 16.0) or 16.0
        v_rec = getattr(stats, "recoil_vertical", 24.0) or 24.0
        rec_sum = float(h_rec) + float(v_rec)
        
        if rec_sum <= 28.0:
            matched_dossier["ease_rating"] = 5
            matched_dossier["ease_label"] = "⭐⭐⭐⭐⭐ Very Easy (Zero Kick)"
        elif rec_sum <= 38.0:
            matched_dossier["ease_rating"] = 4
            matched_dossier["ease_label"] = "⭐⭐⭐⭐☆ Easy (Very Smooth)"
        elif rec_sum <= 50.0:
            matched_dossier["ease_rating"] = 3
            matched_dossier["ease_label"] = "⭐⭐⭐☆☆ Moderate (Balanced Kick)"
        elif rec_sum <= 65.0:
            matched_dossier["ease_rating"] = 2
            matched_dossier["ease_label"] = "⭐⭐☆☆☆ Punchy (Heavy Kick)"
        else:
            matched_dossier["ease_rating"] = 1
            matched_dossier["ease_label"] = "⭐☆☆☆☆ High Skill (Severe Kick)"

    return matched_dossier


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
# 3b. Attachment Weapon Unlock Levels Mapping & Helper
# ---------------------------------------------------------------------------
ATTACHMENT_UNLOCK_LEVELS: Dict[str, int] = {
    "shadowstrike suppressor": 2,
    "vt-7 spiritfire suppressor": 14,
    "casus brake compensator": 8,
    "casus brake": 8,
    "ported tactical compensator": 5,
    "l4r flash hider": 3,
    "colossus heavy silencer": 17,
    "crown-50 muzzle brake": 11,
    "purifier horizontal brake": 19,
    "cyclone heavy long barrel": 12,
    "cyclone long barrel": 12,
    "16.5' mcw cyclone long barrel": 12,
    "phantom cqb short barrel": 6,
    "reinforced match barrel": 16,
    "ultralight fluted barrel": 9,
    "chf heavy cold-forged barrel": 20,
    "triton integrally suppressed barrel": 18,
    "short carbine speed barrel": 4,
    "rival-c clear shot barrel": 8,
    "bruen venom long barrel": 15,
    "pro-99 long barrel": 14,
    "striker recon long barrel": 12,
    "jak annihilator long barrel": 18,
    "ftac grimline tac laser": 5,
    "corio laz-44 precision laser": 10,
    "schlager peq box iv": 8,
    "fss ole-v laser": 14,
    "point-g3p 1mw tactical laser": 3,
    "dxs flash 90 tac-stance laser": 11,
    "slate reflector": 3,
    "mk.3 reflector": 2,
    "corio eagleseye 2.5x scope": 16,
    "corio eagleseye 2.5x": 16,
    "cronen mini pro (blue dot)": 7,
    "sz sro-7 holographic": 11,
    "acog 4.0x tactical scope": 19,
    "thermo-optic x9 thermal": 21,
    "elite match iron sights": 1,
    "skeletonized cqb stock": 9,
    "heavy precision buffer stock": 18,
    "no stock mod": 15,
    "heavy tactical anchor stock": 12,
    "commando lightweight stock": 4,
    "buffer tube ultralight stock": 7,
    "mtz marauder stock": 9,
    "tactical light stock": 6,
    "rubberized recoil stock": 11,
    "dr-6 handstop": 7,
    "bruen heavy support grip": 15,
    "ftac ripper 56 stabilizer": 10,
    "xten phantom-5 handstop": 6,
    "merc foregrip": 4,
    "operator vertical foregrip": 13,
    "chemerov heavy angled grip": 17,
    "40-round extended magazine": 4,
    "40-round mag": 4,
    "50-round heavy drum": 14,
    "60-round super drum": 22,
    "20-round fast speed mag": 8,
    "30-round extended mag": 6,
    "48-round extended mag": 10,
    "100-round ammo belt box": 24,
    "high grain match ammunition": 11,
    "overpressured +p match ammo": 7,
    "armor piercing tungsten rounds": 13,
    "low grain subsonic rounds": 5,
    "hollow point frangible ammo": 9,
    "dragon's breath incendiary rounds": 18,
    "explosive heavy slug rounds": 21,
    "frangible disabling rounds": 15,
    "phantom tactical grip": 6,
    "heavy ergonomic tac grip": 14,
    "stippled rubberized grip": 10,
    "granulated match grip": 3,
    "rival vice assault grip": 10,
    "quick-bolt mechanism": 8,
}


def get_attachment_unlock_level(att_name_or_id: str) -> int:
    """Returns the weapon level required to unlock a specific attachment in MW4."""
    clean = (att_name_or_id or "").strip().lower()
    if clean in ATTACHMENT_UNLOCK_LEVELS:
        return ATTACHMENT_UNLOCK_LEVELS[clean]
    for k, v in ATTACHMENT_UNLOCK_LEVELS.items():
        if k in clean or clean in k:
            return v
    return 10


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
            "weapon_name": "ISO Nightshade (Submachine Gun)",
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
                "weapon_name": "M4 (Assault Rifle)",
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
                "weapon_name": "Patriot XMR (Assault Rifle)",
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

WEAPON_PLAIN_INTELLIGENCE = {
    "patriot_xmr_mw4": {
        "title": "🔥 4-Shot Fast Full-Auto Laser",
        "best_at": "Mid-range duels where you want the fastest automatic kill time in the beta.",
        "pros": ["#1 Fastest TTK full-auto AR (279ms)", "Very easy vertical recoil", "Excellent 32.5m damage range"],
        "cons": ["25-round base magazine requires trigger discipline", "Moderate reload time"],
        "summary": "The undisputed king of assault rifles in the 2026 MW4 Beta. Deals 28 chest damage for an ultra-fast 4-shot kill."
    },
    "iso_nightshade_mw4": {
        "title": "⚡ 923-RPM #1 Fastest TTK SMG",
        "best_at": "Aggressive close-quarters rushing and room clearing.",
        "pros": ["#1 Fastest TTK SMG in the game (260ms)", "Blistering 923 RPM rate of fire", "Fastest sprint-out time"],
        "cons": ["High fire rate burns through 30 rounds quickly", "Damage falls off sharply past 10 meters"],
        "summary": "The ultimate close-range weapon in the Beta. If you love rushing and slide-canceling into rooms, this is your #1 primary."
    },
    "hyeon_burst_mw4": {
        "title": "⚡ 1-Burst Lethal Marksman AR",
        "best_at": "Precision players who can land upper-chest and headshots.",
        "pros": ["Lethal 1-burst kill potential (141ms TTK)", "Extremely flat recoil within the 3-round burst", "Class-leading 38.1m range"],
        "cons": ["Punishing delay between bursts if you miss", "Struggles against multiple rushing enemies"],
        "summary": "A high-skill ceiling rifle with a North Korean prototype burst mechanism. One headshot guarantees a 1-burst instant kill."
    },
    "type73_mw4": {
        "title": "💥 821-RPM High-Cadence LMG",
        "best_at": "Locking down lanes, objective defense, and multi-kill squad wipes.",
        "pros": ["Blazing 821 RPM fire rate", "60-round drum capacity", "Dominates medium and long sightlines"],
        "cons": ["Heavier ADS time than assault rifles", "Slower tactical reload"],
        "summary": "An absolute monster of an LMG. Combines the high rate of fire of an SMG with the sustained 60-round drum and range of an LMG."
    },
    "kg7_vulcan_mw4": {
        "title": "🎯 1-Shot Bolt Anti-Personnel Sniper",
        "best_at": "Long-range sniping and holding power positions.",
        "pros": ["1-shot kill to head and upper chest at all ranges", "10-round detachable magazine", "Crisp scope reticle"],
        "cons": ["37 RPM bolt cycle requires accurate first shots", "Slow ADS handling"],
        "summary": "The premier sniper rifle in the MW4 Beta. Rewards steady aim with guaranteed one-shot eliminations across all map sightlines."
    },
    "krait_p68_mw4": {
        "title": "🔫 Buffed 46-Damage Sidearm",
        "best_at": "Finishing off weak enemies and lightning-fast weapon swaps.",
        "pros": ["Massive 46 chest damage (3-shot kill)", "450 RPM semi-auto trigger cap", "15-round standard capacity"],
        "cons": ["Semi-auto trigger finger required", "Severe recoil at long range"],
        "summary": "The best secondary in the beta. Receives massive damage buffs that allow it to out-duel primary weapons in close quarters."
    },
    "ppsh41_mw4": {
        "title": "⚡ 1110-RPM 71-Round Drum Hose",
        "best_at": "Hipfiring, hip-sliding, and sustained multi-target hipfire sprays.",
        "pros": ["Extreme 1110 RPM rate of fire", "Huge 71-round drum from level 11", "Great hipfire spread"],
        "cons": ["6-shot kill requirement (19 chest damage)", "Open-bolt delay of 30ms"],
        "summary": "A legendary bullet hose that never stops shooting. Perfect for clearing hardpoints and hipfiring through choke points."
    },
    "x58_nyx_mw4": {
        "title": "🤫 Integrally Suppressed Infiltrator",
        "best_at": "Flanking behind enemy lines without appearing on the radar.",
        "pros": ["Built-in monolithic suppressor keeps you off the minimap", "Generous 40-round magazine", "Smooth controllable recoil"],
        "cons": ["Moderate 800 RPM fire rate", "Slightly slower sprint-to-fire than ISO"],
        "summary": "The ultimate stealth SMG. Completely silenced out of the box with 40 rounds, making it ideal for flanking on high-traffic maps."
    },
    "oris86_mw4": {
        "title": "🎯 8.6 Blackout Bolt-Action DMR",
        "best_at": "Mid-to-long range precision tap-firing and aggressive recon.",
        "pros": ["Heavy 8.6mm Blackout stopping power", "Fast handling compared to snipers", "High bullet velocity"],
        "cons": ["89 RPM bolt cycle punishes missed shots", "Requires upper torso hits for maximum damage"],
        "summary": "A specialized bolt-action marksman rifle chambered in 8.6 Blackout. Bridges the gap between agile DMRs and heavy snipers."
    },
    "kastov762_mw4": {
        "title": "💥 Heavy 7.62 Punch Rifle",
        "best_at": "Mid-range lane holding and high-damage per bullet tapping.",
        "pros": ["Highest damage per bullet among assault rifles (30 dmg)", "Consistent 4-shot kill", "3-shot kill with 1 headshot"],
        "cons": ["Moderate 600 RPM fire rate", "Notable vertical recoil jump"],
        "summary": "Hits like a freight train. Deals 30 chest damage for a guaranteed 4-shot kill with great headshot multipliers."
    },
    "signal50_mw4": {
        "title": "💀 .50 BMG Semi-Auto Sniper",
        "best_at": "Rapid follow-up anti-materiel sniper fire.",
        "pros": ["111 RPM rapid semi-auto firing", "Heavy .50 BMG kinetic shock", "Devastating vehicle/streak damage"],
        "cons": ["Strong visual recoil kick", "7-round magazine"],
        "summary": "A semi-automatic .50 BMG sniper rifle with a reciprocating barrel system that allows instant follow-up shots."
    },
    "mar9_mw4": {
        "title": "🎯 315-RPM Rapid Precision DMR",
        "best_at": "Spamming precision shots at medium to long range.",
        "pros": ["315 RPM semi-auto speed", "20-round magazine", "Low recoil rise"],
        "cons": ["Requires 3 to 4 hits to eliminate", "Loses to full-auto ARs inside 15m"],
        "summary": "A rapid-firing semi-auto marksman rifle that lets you pepper targets down long sightlines with pinpoint precision."
    },
    "rezi12_mw4": {
        "title": "🚪 CQB 150-RPM Room Breacher",
        "best_at": "Instant point-blank corner clearing and tight interior hallways.",
        "pros": ["Semi-auto 150 RPM rapid follow-up shells", "Deadly 1-2 pump close-range burst", "Fast pump cycling"],
        "cons": ["Useless past 10 meters", "6-round tube requires frequent reloads"],
        "summary": "A semi-automatic 12-gauge shotgun designed for aggressive CQB breaching and tight room engagements."
    },
    "m4_mw4": {
        "title": "🛡️ 810-RPM Reliable Workhorse",
        "best_at": "All-around gameplay for players who want a balanced, reliable weapon.",
        "pros": ["Fast 810 RPM fire rate", "Predictable, easy-to-control recoil", "Extensive attachment customization"],
        "cons": ["5-shot kill in Weekend 2 patch", "Moderate 27.4m range"],
        "summary": "The classic Modern Warfare workhorse. Dependable, balanced, and highly adaptable across every combat distance."
    },
    "finn_lmg_mw4": {
        "title": "🛡️ 100-Round Sustained Belt",
        "best_at": "Continuous suppressive fire and holding objective lanes.",
        "pros": ["100-round endless ammo belt", "Laser-beam flat recoil curve", "Great long-range velocity"],
        "cons": ["Slow 587 RPM cadence", "Heavy 6.2s empty reload time"],
        "summary": "A true heavy machine gun with virtually zero recoil. Holds 100 rounds in a single belt to suppress entire teams."
    },
    "han86_mw4": {
        "title": "🎯 Bullpup Laser Beamer",
        "best_at": "Long-range precision beaming and lane control.",
        "pros": ["Extremely low horizontal recoil", "Good 740 RPM fire rate", "Clean iron sights"],
        "cons": ["5-shot kill requires 100 HP Core consistency", "Moderate reload speed"],
        "summary": "A South Korean bullpup rifle engineered for extreme accuracy and low recoil across medium to long distances."
    },
    "gs50_mw4": {
        "title": "🔫 .50 Cal 1-Tap Head Cannon",
        "best_at": "High-skill flick shots and finishing blows.",
        "pros": ["Massive 70 chest damage", "Guaranteed 1-shot headshot kill", "Huge intimidation factor"],
        "cons": ["180 RPM slow trigger", "Heavy visual muzzle climb", "7-round magazine"],
        "summary": "The iconic hand cannon. Deals 70 base damage and guarantees an instant 1-shot kill on any headshot."
    }
}



