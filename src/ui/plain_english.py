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
    # 5 Assault Rifles
    "patriot_xmr_mw4": {
        "role_title": "👑 S-Tier 4-Shot CQB / Mid-Range Laser",
        "playstyle_category": "Assault Rifle",
        "summary": "The definitive fastest-killing assault rifle in MW4 Beta. 4-shot kill with laser precision up to 26 meters.",
        "plain_summary": "The definitive fastest-killing assault rifle in MW4 Beta. 4-shot kill with laser precision up to 26 meters.",
        "best_for": "Medium-range power positions, head-glitch clearing, and aggressive AR lane control.",
        "key_strength": "Fastest AR TTK (279ms) & 4-Shot Kill Ceiling",
        "primary_flaw": "Slightly smaller 25-round base magazine",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Pinpoint Laser)",
        "recoil_profile": "Dead straight vertical climb with near-zero horizontal deviation.",
        "recoil_feel": "Extremely smooth and predictable straight-line vertical kick.",
        "pro_tip": "Run a 40-round magazine and vertical grip to maximize multi-kill potential."
    },
    "m4_mw4": {
        "role_title": "🛡️ 810-RPM High-Tempo Workhorse AR",
        "playstyle_category": "Assault Rifle",
        "summary": "Rapid 810 RPM fire rate and snappy aim speed make it the most versatile all-around rifle in the beta.",
        "plain_summary": "Rapid 810 RPM fire rate and snappy aim speed make it the most versatile all-around rifle in the beta.",
        "best_for": "Aggressive run-and-gun players who want AR range with SMG responsiveness.",
        "key_strength": "High 810 RPM cadence & generous 30-round mag",
        "primary_flaw": "Requires 5 shots to kill at close range (296ms TTK)",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Easy (Very Smooth)",
        "recoil_profile": "Gentle upward climb with slight rightward drift on sustained fire.",
        "recoil_feel": "Predictable upward climb with minor right drift.",
        "pro_tip": "Equip the FSS Fireline Grip to tighten grouping for cross-map beaming."
    },
    "hyeon_burst_mw4": {
        "role_title": "⚡ 1-Burst Lethal Precision AR",
        "playstyle_category": "Assault Rifle",
        "summary": "High-velocity 3-round burst rifle. Landing a full 3-bullet cluster with a headshot instantly deletes targets in under 145ms.",
        "plain_summary": "High-velocity 3-round burst rifle. Landing a full 3-bullet cluster with a headshot instantly deletes targets in under 145ms.",
        "best_for": "Pinpoint marksmen holding medium sightlines and pre-aiming lanes.",
        "key_strength": "Instantaneous 1-Burst TTK Ceiling",
        "primary_flaw": "Missing a burst creates a punish window between cycles",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Skill-Based (Tight Cluster)",
        "recoil_profile": "Extremely tight burst grouping that naturally climbs toward the neck.",
        "recoil_feel": "Tight burst grouping with slight upward rise between rounds.",
        "pro_tip": "Aim upper chest; the 3rd bullet in the burst will naturally connect with the head."
    },
    "kastov762_mw4": {
        "role_title": "💪 Heavy 7.62 High-Impact Battle Rifle",
        "playstyle_category": "Assault Rifle",
        "summary": "Hard-hitting 7.62mm caliber rifle delivering heavy per-bullet damage and high flinch induction.",
        "plain_summary": "Hard-hitting 7.62mm caliber rifle delivering heavy per-bullet damage and high flinch induction.",
        "best_for": "Locking down long lanes and winning trades through severe target flinch.",
        "key_strength": "High single-shot damage & extreme flinch dealt to enemies",
        "primary_flaw": "Chunky vertical recoil requires active thumbstick/mouse compensation",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ Moderate (Punchy 7.62 Kick)",
        "recoil_profile": "Pronounced vertical jump on initial shots that levels off during sustained fire.",
        "recoil_feel": "Punchy vertical climb with strong initial visual kick.",
        "pro_tip": "Fire in 4 to 5 bullet bursts at ranges past 35 meters for maximum accuracy."
    },
    "han86_mw4": {
        "role_title": "🎯 Compact Bullpup Stability Platform",
        "playstyle_category": "Assault Rifle",
        "summary": "Bullpup configuration providing superior mobility and smooth recoil handling across all combat brackets.",
        "plain_summary": "Bullpup configuration providing superior mobility and smooth recoil handling across all combat brackets.",
        "best_for": "Mid-range duels and players who want effortless sightline control.",
        "key_strength": "Exceptional handling speeds & clean recoil recovery",
        "primary_flaw": "Moderate 740 RPM fire rate can lose point-blank 50/50s to SMGs",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Flat Shooting)",
        "recoil_profile": "Very low horizontal bounce with smooth, linear vertical rise.",
        "recoil_feel": "Smooth linear climb with minimal horizontal bounce.",
        "pro_tip": "Use a low-magnification optic like the SZ Micro O-3 for crystal-clear target acquisition."
    },

    # 3 Submachine Guns
    "iso_nightshade_mw4": {
        "role_title": "👑 S-Tier #1 Fast-Killing CQB SMG",
        "playstyle_category": "Submachine Gun",
        "summary": "The undisputed #1 close-quarters weapon in the MW4 Beta. 923 RPM with a blistering 260ms close-range TTK.",
        "plain_summary": "The undisputed #1 close-quarters weapon in the MW4 Beta. 923 RPM with a blistering 260ms close-range TTK.",
        "best_for": "Aggressive slide-canceling, room clearing, and close-quarters dominance inside 14m.",
        "key_strength": "Fastest SMG TTK (260ms) & Rapid 923 RPM Cadence",
        "primary_flaw": "Severe damage falloff beyond 16 meters",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (CQB Melter)",
        "recoil_profile": "Fast upward pull that is effortless to control inside 20 meters.",
        "recoil_feel": "Snappy upward pull that is very easy to manage inside 20m.",
        "pro_tip": "Combine with the Blood Rush perk for endless tactical sprint and aggressive flanking."
    },
    "ppsh41_mw4": {
        "role_title": "⚡ 1110-RPM 71-Round Drum Bullet Hose",
        "playstyle_category": "Submachine Gun",
        "summary": "Fires at an astronomical 1110 RPM with an iconic 71-round drum magazine. Shreds whole squads without reloading.",
        "plain_summary": "Fires at an astronomical 1110 RPM with an iconic 71-round drum magazine. Shreds whole squads without reloading.",
        "best_for": "Wiping multiple enemies in tight corridors and hipfire spraying.",
        "key_strength": "Massive 71-round base capacity & 1110 RPM fire rate",
        "primary_flaw": "Slower tactical reload time (2.75s) and 6-shot base kill requirement",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Snappy Bullet Hose",
        "recoil_profile": "High frequency recoil vibration with moderate vertical rise.",
        "recoil_feel": "High-frequency vibration with moderate vertical rise.",
        "pro_tip": "Equip laser attachments to maximize hipfire accuracy for point-blank hip spraying."
    },
    "x58_nyx_mw4": {
        "role_title": "🤫 Integrally Suppressed Infiltrator SMG",
        "playstyle_category": "Submachine Gun",
        "summary": "Integrally suppressed 800 RPM submachine gun with 40-round standard magazine. Keeps you off enemy radar.",
        "plain_summary": "Integrally suppressed 800 RPM submachine gun with 40-round standard magazine. Keeps you off enemy radar.",
        "best_for": "Stealth flankers and objective infiltrators navigating behind enemy lines.",
        "key_strength": "Built-in radar stealth, generous 40-rnd mag & smooth recoil",
        "primary_flaw": "Slightly slower bullet velocity (360 m/s)",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Stealth Laser)",
        "recoil_profile": "Gentle, steady climb with almost no horizontal deviation.",
        "recoil_feel": "Gentle, steady climb with almost no horizontal shake.",
        "pro_tip": "Flank around objective choke points to eliminate enemies from behind without pinging the minimap."
    },

    # 1 Shotgun
    "rezi12_mw4": {
        "role_title": "🚪 1-Shot Semi-Auto CQB Breacher",
        "playstyle_category": "Shotgun",
        "summary": "Semi-automatic combat shotgun delivering devastating 1-shot lethality inside 6 meters.",
        "plain_summary": "Semi-automatic combat shotgun delivering devastating 1-shot lethality inside 6 meters.",
        "best_for": "Holding doorways, clearing tight rooms, and point-blank defensive play.",
        "key_strength": "0ms instant 1-shot kill inside 6m & rapid semi-auto follow-ups",
        "primary_flaw": "Extremely steep pellet spread falloff past 10 meters",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Easy (Point-Blank Power)",
        "recoil_profile": "Heavy visual kick between semi-auto trigger pulls.",
        "recoil_feel": "Heavy kick between trigger pulls, resets before next chamber.",
        "pro_tip": "Always aim down sights to tighten pellet spread for guaranteed 1-shot kills up to 7m."
    },

    # 2 Light Machine Guns
    "type73_mw4": {
        "role_title": "⚡ 821-RPM 60-Round Aggressive LMG",
        "playstyle_category": "Light Machine Gun",
        "summary": "High-cadence 821 RPM light machine gun with top-loading 60-round drum. Plays like an oversized assault rifle.",
        "plain_summary": "High-cadence 821 RPM light machine gun with top-loading 60-round drum. Plays like an oversized assault rifle.",
        "best_for": "Suppressing choke points, team-wiping pushes, and aggressive support fire.",
        "key_strength": "Blistering 821 RPM fire rate & 60-round magazine",
        "primary_flaw": "60ms open bolt chambering delay",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Easy (Sustained Fire)",
        "recoil_profile": "Smooth, gradual vertical climb that is easily managed.",
        "recoil_feel": "Smooth, gradual vertical climb with high stability.",
        "pro_tip": "Pre-aim corners to compensate for the 60ms open bolt delay."
    },
    "finn_lmg_mw4": {
        "role_title": "🛡️ 100-Round Sustained Suppression Titan",
        "playstyle_category": "Light Machine Gun",
        "summary": "Heavy 100-round belt-fed machine gun with exceptionally smooth recoil and endless suppression capability.",
        "plain_summary": "Heavy 100-round belt-fed machine gun with exceptionally smooth recoil and endless suppression capability.",
        "best_for": "Locking down hardpoints, suppressing sniper nests, and long-range lane denial.",
        "key_strength": "100-round continuous belt & ultra-smooth recoil pattern",
        "primary_flaw": "Slower ADS time (420ms) and reload time (5.2s)",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (No Recoil Beamer)",
        "recoil_profile": "Almost purely vertical recoil with negligible horizontal wobble.",
        "recoil_feel": "Almost purely vertical with negligible horizontal wobble.",
        "pro_tip": "Mount on low cover to turn this weapon into a pinpoint laser across any distance."
    },

    # 2 Marksman Rifles
    "mar9_mw4": {
        "role_title": "🎯 Rapid Semi-Auto Precision DMR",
        "playstyle_category": "Marksman Rifle",
        "summary": "Fast-firing 315 RPM semi-automatic rifle capable of dropping opponents in 2 crisp torso hits.",
        "plain_summary": "Fast-firing 315 RPM semi-automatic rifle capable of dropping opponents in 2 crisp torso hits.",
        "best_for": "Semi-auto trigger spammers who want fast 2-shot kills across mid-to-long ranges.",
        "key_strength": "Fast 315 RPM fire rate & forgiving 20-round magazine",
        "primary_flaw": "Requires 2 hits minimum; cannot 1-shot to the torso",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Forgiving Semi-Auto",
        "recoil_profile": "Quick visual bounce that recenters rapidly between semi-auto clicks.",
        "recoil_feel": "Quick visual bounce that recenters rapidly before the next shot.",
        "pro_tip": "Equip a 2.5x to 4x optic to easily track moving targets across medium ranges."
    },
    "oris86_mw4": {
        "role_title": "🎯 High-Caliber Heavy Precision DMR",
        "playstyle_category": "Marksman Rifle",
        "summary": "Heavy 8.6mm bolt-action marksman rifle delivering lethal 1-shot headshot kills and massive torso damage.",
        "plain_summary": "Heavy 8.6mm bolt-action marksman rifle delivering lethal 1-shot headshot kills and massive torso damage.",
        "best_for": "Aggressive quick-scoping and high-accuracy marksmen.",
        "key_strength": "Guaranteed 1-shot headshot lethality & faster handling than heavy snipers",
        "primary_flaw": "89 RPM bolt cycle punishes missed initial shots",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ High-Skill Precision",
        "recoil_profile": "Sharp bolt action kick with quick sightline re-centering.",
        "recoil_feel": "Sharp bolt action kick with quick re-centering.",
        "pro_tip": "Aim high-chest so minor flinch converts your shot into an instant 1-shot headshot."
    },

    # 2 Sniper Rifles
    "kg7_vulcan_mw4": {
        "role_title": "💀 1-Shot Lethal Torso/Head Bolt Sniper",
        "playstyle_category": "Sniper Rifle",
        "summary": "Top-tier heavy bolt-action sniper rifle. Delivers guaranteed 1-shot eliminations to the chest, neck, and head.",
        "plain_summary": "Top-tier heavy bolt-action sniper rifle. Delivers guaranteed 1-shot eliminations to the chest, neck, and head.",
        "best_for": "Traditional snipers, long-distance overwatch, and holding power lanes.",
        "key_strength": "Enormous 1-shot lethal zone (Upper Torso, Neck, Head) & 10-round magazine",
        "primary_flaw": "Slow 37 RPM bolt-action cycle rate",
        "ease_rating": 4,
        "ease_label": "⭐⭐⭐⭐☆ Consistent 1-Shot Power",
        "recoil_profile": "Heavy bolt action kick with full reset during chambering.",
        "recoil_feel": "Heavy kick with full reset during chambering.",
        "pro_tip": "Hold your breath right before pulling the trigger to eliminate all idle sway."
    },
    "signal50_mw4": {
        "role_title": "🎯 111-RPM Semi-Auto .50 Cal Sniper",
        "playstyle_category": "Sniper Rifle",
        "summary": "Semi-automatic .50 BMG anti-material sniper rifle. Allows rapid follow-up shots without un-scoping.",
        "plain_summary": "Semi-automatic .50 BMG anti-material sniper rifle. Allows rapid follow-up shots without un-scoping.",
        "best_for": "Sniping multiple moving targets and rapid long-range double-taps.",
        "key_strength": "111 RPM semi-auto fire rate & 1-shot headshot lethality",
        "primary_flaw": "Heavy visual kick between rapid semi-auto trigger pulls",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ Semi-Auto .50 Cal Power",
        "recoil_profile": "Strong vertical kick between semi-auto shots; settle aim before second trigger pull.",
        "recoil_feel": "Strong vertical kick between shots; settle aim before second shot.",
        "pro_tip": "Pace your shots slightly to allow the heavy reticle to return to center."
    },

    # 2 Secondaries
    "krait_p68_mw4": {
        "role_title": "🔫 450-RPM 46-Damage Combat Pistol",
        "playstyle_category": "Handgun",
        "summary": "Fast-firing 450 RPM semi-automatic handgun buffed to 46 base damage. Delivers ultra-fast 3-shot CQB eliminations.",
        "plain_summary": "Fast-firing 450 RPM semi-automatic handgun buffed to 46 base damage. Delivers ultra-fast 3-shot CQB eliminations.",
        "best_for": "Quick-drawing when primary runs dry and agile pistol-only CQB rushing.",
        "key_strength": "Rapid fast-swap draw speed & lethal 3-shot close-range TTK",
        "primary_flaw": "Requires fast trigger finger clicking speed",
        "ease_rating": 5,
        "ease_label": "⭐⭐⭐⭐⭐ Very Easy (Pocket Shredder)",
        "recoil_profile": "Crisp, fast-centering visual recoil.",
        "recoil_feel": "Crisp, fast-centering visual kick.",
        "pro_tip": "Swap to this weapon instead of reloading your primary in the middle of a gunfight."
    },
    "gs50_mw4": {
        "role_title": "💥 1-Shot Headshot Hand Cannon",
        "playstyle_category": "Handgun",
        "summary": "Iconic .50 caliber heavy magnum pistol. Delivers 70 damage per torso shot and instant 1-shot headshot eliminations.",
        "plain_summary": "Iconic .50 caliber heavy magnum pistol. Delivers 70 damage per torso shot and instant 1-shot headshot eliminations.",
        "best_for": "High-skill marksmen who can flick to the head for instant pocket eliminations.",
        "key_strength": "Instant 1-shot headshot lethality & 2-shot torso power",
        "primary_flaw": "Slower 180 RPM fire rate and heavy muzzle jump",
        "ease_rating": 3,
        "ease_label": "⭐⭐⭐☆☆ Skill Cannon (Heavy Kick)",
        "recoil_profile": "Massive vertical jump that takes a fraction of a second to settle.",
        "recoil_feel": "Massive vertical jump that takes a moment to settle.",
        "pro_tip": "Equip laser sights to gain razor-sharp hipfire accuracy in emergency CQB encounters."
    }
}


def get_weapon_plain_summary(
    weapon_id: str,
    weapon_name: str = "",
    weapon_class_val: str = "",
    stats: Optional[Any] = None
) -> Dict[str, Any]:
    """Returns curated plain-English summary with guaranteed keys and true data-driven recoil ratings."""
    clean_id = weapon_id.lower().replace("-", "_").replace(" ", "_")
    matched_dossier = None

    if clean_id in WEAPON_PLAIN_DOSSIERS:
        matched_dossier = dict(WEAPON_PLAIN_DOSSIERS[clean_id])
    else:
        # Check alias keys
        for d_key, data in WEAPON_PLAIN_DOSSIERS.items():
            base_key = d_key.replace("_mw4", "")
            if base_key in clean_id or clean_id.replace("_mw4", "") in base_key:
                matched_dossier = dict(data)
                break

    cls_name = weapon_class_val.replace("_", " ").title() or "Weapon"
    name = weapon_name or weapon_id.upper()

    if not matched_dossier:
        matched_dossier = {
            "role_title": f"🎯 Standard {cls_name} Platform",
            "playstyle_category": cls_name,
            "plain_summary": f"{name} is a balanced {cls_name.lower()} offering reliable combat performance in standard engagements.",
            "summary": f"{name} is a balanced {cls_name.lower()} offering reliable combat performance in standard engagements.",
            "best_for": "General combat scenarios across small to medium map sightlines.",
            "key_strength": "Consistent handling & predictable fire cadence",
            "primary_flaw": "Requires sustained accuracy on target",
            "ease_rating": 4,
            "ease_label": "⭐⭐⭐⭐☆ Easy (Very Smooth)",
            "recoil_profile": "Standard class recoil curve.",
            "recoil_feel": "Smooth, predictable vertical climb.",
            "pro_tip": "Test with recoil-reducing muzzle and underbarrel attachments in the Build Optimizer."
        }

    # Ensure all required keys exist
    if "summary" not in matched_dossier:
        matched_dossier["summary"] = matched_dossier.get("plain_summary", f"{name} standard platform.")
    if "plain_summary" not in matched_dossier:
        matched_dossier["plain_summary"] = matched_dossier["summary"]
    if "best_for" not in matched_dossier:
        matched_dossier["best_for"] = "General combat scenarios across standard map sightlines."
    if "role_title" not in matched_dossier:
        matched_dossier["role_title"] = f"🎯 {cls_name} Platform"
    if "recoil_profile" not in matched_dossier:
        matched_dossier["recoil_profile"] = matched_dossier.get("recoil_feel", "Predictable recoil profile.")
    if "recoil_feel" not in matched_dossier:
        matched_dossier["recoil_feel"] = matched_dossier["recoil_profile"]
    if "pro_tip" not in matched_dossier:
        matched_dossier["pro_tip"] = "Pair with a clean optic and recoil-reducing underbarrel grip."
    if "ease_rating" not in matched_dossier:
        matched_dossier["ease_rating"] = 4
    if "ease_label" not in matched_dossier:
        matched_dossier["ease_label"] = "⭐⭐⭐⭐☆ Easy (Very Smooth)"

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

