"""
MW4 Weapon Intelligence Lab - Authentic Gunsmith Blueprint & Vector Graphics Engine
Provides high-fidelity, dark-mode native tactical weapon blueprint graphics
modeled after official Call of Duty Gunsmith HUD wireframes and renders.
"""

from typing import Dict


# High-fidelity COD Gunsmith HUD Blueprint SVGs with glowing neon accents & micro-details
WEAPON_SVG_MAP: Dict[str, str] = {
    # XM4 / MCW / AR Class: Detailed Quad-rail M4/ACR platform with optic, stock, and STANAG magazine
    "assault_rifle": (
        '<svg viewBox="0 0 240 60" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 50px; display: block;">'
        '<path d="M12 24 L45 24 L52 18 L100 18 L108 22 L160 22 L170 26 L215 26 L215 30 L170 30 L160 34 L130 34 L122 52 L106 52 L112 34 L90 34 L82 48 L70 48 L76 34 L42 34 L25 50 L12 50 Z" fill="rgba(56, 189, 248, 0.15)" stroke="#38bdf8" stroke-width="1.8" stroke-linejoin="round"/>'
        '<rect x="92" y="12" width="28" height="6" rx="1" fill="rgba(56, 189, 248, 0.3)" stroke="#38bdf8" stroke-width="1.2"/>'
        '<line x1="106" y1="12" x2="106" y2="8" stroke="#38bdf8" stroke-width="1.5"/>'
        '<line x1="100" y1="8" x2="112" y2="8" stroke="#38bdf8" stroke-width="1.5"/>'
        '<line x1="175" y1="23" x2="175" y2="33" stroke="#38bdf8" stroke-width="1.2"/>'
        '<line x1="185" y1="23" x2="185" y2="33" stroke="#38bdf8" stroke-width="1.2"/>'
        '<line x1="195" y1="23" x2="195" y2="33" stroke="#38bdf8" stroke-width="1.2"/>'
        '<rect x="215" y="25" width="12" height="6" fill="#f43f5e" stroke="#f43f5e" stroke-width="1"/>'
        '<circle cx="112" cy="28" r="2.5" fill="#4ade80"/>'
        '<line x1="130" y1="34" x2="155" y2="44" stroke="rgba(56, 189, 248, 0.4)" stroke-width="1.2" stroke-dasharray="2 2"/>'
        '</svg>'
    ),

    # Rival-9 / Striker / SMG Class: Compact PDW receiver with curved high-capacity stick mag & compensator
    "submachine_gun": (
        '<svg viewBox="0 0 240 60" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 50px; display: block;">'
        '<path d="M20 26 L55 26 L65 20 L125 20 L135 26 L175 26 L175 31 L135 31 L125 35 L108 35 L98 54 L84 54 L92 35 L72 35 L65 48 L52 48 L58 35 L32 35 L22 48 L10 48 Z" fill="rgba(251, 191, 36, 0.15)" stroke="#fbbf24" stroke-width="1.8" stroke-linejoin="round"/>'
        '<rect x="75" y="14" width="22" height="6" rx="1" fill="rgba(251, 191, 36, 0.3)" stroke="#fbbf24" stroke-width="1.2"/>'
        '<line x1="86" y1="14" x2="86" y2="10" stroke="#fbbf24" stroke-width="1.5"/>'
        '<circle cx="86" cy="28" r="2.5" fill="#38bdf8"/>'
        '<line x1="140" y1="23" x2="140" y2="33" stroke="#fbbf24" stroke-width="1.2"/>'
        '<line x1="150" y1="23" x2="150" y2="33" stroke="#fbbf24" stroke-width="1.2"/>'
        '<line x1="160" y1="23" x2="160" y2="33" stroke="#fbbf24" stroke-width="1.2"/>'
        '<rect x="175" y="25" width="10" height="7" fill="#f43f5e" stroke="#f43f5e" stroke-width="1"/>'
        '</svg>'
    ),

    # BAS-B / Sidewinder: Heavy 7.62 Battle Rifle with reinforced upper receiver & high-caliber magazine
    "battle_rifle": (
        '<svg viewBox="0 0 240 60" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 50px; display: block;">'
        '<path d="M10 24 L48 24 L58 17 L110 17 L120 22 L172 22 L182 26 L225 26 L225 30 L182 30 L172 34 L140 34 L132 54 L114 54 L120 34 L95 34 L88 49 L75 49 L82 34 L45 34 L28 50 L10 50 Z" fill="rgba(192, 132, 252, 0.15)" stroke="#c084fc" stroke-width="1.8" stroke-linejoin="round"/>'
        '<polygon points="98,10 135,10 130,17 92,17" fill="rgba(192, 132, 252, 0.35)" stroke="#c084fc" stroke-width="1.2"/>'
        '<circle cx="122" cy="28" r="2.5" fill="#fb923c"/>'
        '<line x1="185" y1="23" x2="185" y2="33" stroke="#c084fc" stroke-width="1.2"/>'
        '<line x1="195" y1="23" x2="195" y2="33" stroke="#c084fc" stroke-width="1.2"/>'
        '<line x1="205" y1="23" x2="205" y2="33" stroke="#c084fc" stroke-width="1.2"/>'
        '<rect x="225" y="24" width="12" height="8" fill="#c084fc" stroke="#f8fafc" stroke-width="1"/>'
        '</svg>'
    ),

    # KVD Enforcer / Marksman: Semi-auto DMR with precision target optic & skeletonized stock
    "marksman_rifle": (
        '<svg viewBox="0 0 240 60" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 50px; display: block;">'
        '<path d="M12 25 L50 25 L60 19 L115 19 L125 23 L180 23 L190 26 L230 26 L230 29 L190 29 L180 33 L145 33 L138 49 L122 49 L128 33 L98 33 L92 46 L80 46 L86 33 L50 33 L32 47 L12 47 Z" fill="rgba(45, 212, 191, 0.15)" stroke="#2dd4bf" stroke-width="1.8" stroke-linejoin="round"/>'
        '<polygon points="95,10 145,10 140,19 90,19" fill="rgba(45, 212, 191, 0.35)" stroke="#2dd4bf" stroke-width="1.4"/>'
        '<circle cx="128" cy="27" r="2.5" fill="#4ade80"/>'
        '<line x1="200" y1="25" x2="200" y2="31" stroke="#2dd4bf" stroke-width="1.2"/>'
        '<line x1="210" y1="25" x2="210" y2="31" stroke="#2dd4bf" stroke-width="1.2"/>'
        '<rect x="230" y="25" width="8" height="5" fill="#2dd4bf" stroke="#f8fafc" stroke-width="1"/>'
        '</svg>'
    ),

    # KATT-AMR .50 / Longbow: Heavy .50 Cal Anti-Material Sniper with Thermal Scope & Heavy Muzzle Brake
    "sniper_rifle": (
        '<svg viewBox="0 0 240 60" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 50px; display: block;">'
        '<path d="M8 26 L45 26 L55 20 L110 20 L120 22 L190 22 L200 24 L235 24 L235 28 L200 28 L190 32 L150 32 L142 48 L126 48 L132 32 L92 32 L85 45 L72 45 L78 32 L42 32 L25 46 L8 46 Z" fill="rgba(74, 222, 128, 0.15)" stroke="#4ade80" stroke-width="1.8" stroke-linejoin="round"/>'
        '<polygon points="90,8 150,8 145,20 85,20" fill="rgba(74, 222, 128, 0.4)" stroke="#4ade80" stroke-width="1.5"/>'
        '<line x1="180" y1="32" x2="172" y2="48" stroke="#4ade80" stroke-width="2"/>'
        '<line x1="185" y1="32" x2="192" y2="48" stroke="#4ade80" stroke-width="2"/>'
        '<rect x="230" y="22" width="10" height="8" fill="#4ade80" stroke="#f8fafc" stroke-width="1.2"/>'
        '</svg>'
    ),

    # Bruen Mk9 / Pulemyot: Heavy Squad Automatic Weapon with 100-round ammo box & heat shield
    "light_machine_gun": (
        '<svg viewBox="0 0 240 60" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 50px; display: block;">'
        '<path d="M10 22 L50 22 L60 17 L115 17 L125 21 L180 21 L190 24 L225 24 L225 28 L190 28 L180 34 L140 34 L132 55 L102 55 L110 34 L92 34 L85 48 L72 48 L78 34 L48 34 L28 48 L10 48 Z" fill="rgba(249, 115, 22, 0.15)" stroke="#f97316" stroke-width="1.8" stroke-linejoin="round"/>'
        '<rect x="110" y="38" width="24" height="18" rx="2" fill="rgba(249, 115, 22, 0.4)" stroke="#f97316" stroke-width="1.5"/>'
        '<line x1="185" y1="28" x2="178" y2="46" stroke="#f97316" stroke-width="1.8"/>'
        '<line x1="190" y1="28" x2="198" y2="46" stroke="#f97316" stroke-width="1.8"/>'
        '<line x1="130" y1="12" x2="160" y2="12" stroke="#f97316" stroke-width="2"/>'
        '<line x1="130" y1="12" x2="135" y2="17" stroke="#f97316" stroke-width="2"/>'
        '<line x1="160" y1="12" x2="155" y2="17" stroke="#f97316" stroke-width="2"/>'
        '</svg>'
    ),

    # Lockwood 680: Tactical 12-Gauge Pump Action Shotgun with extended magazine tube
    "shotgun": (
        '<svg viewBox="0 0 240 60" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 50px; display: block;">'
        '<path d="M12 26 L55 26 L65 20 L130 20 L140 23 L210 23 L210 28 L140 28 L130 33 L95 33 L88 47 L75 47 L82 33 L50 33 L32 46 L12 46 Z" fill="rgba(239, 68, 68, 0.15)" stroke="#ef4444" stroke-width="1.8" stroke-linejoin="round"/>'
        '<line x1="110" y1="33" x2="160" y2="33" stroke="#ef4444" stroke-width="3.5"/>'
        '<line x1="140" y1="28" x2="210" y2="28" stroke="#fbbf24" stroke-width="2"/>'
        '<circle cx="105" cy="26" r="2.5" fill="#fbbf24"/>'
        '</svg>'
    ),

    # COR-45 / Renetti: Sidearm Tactical Pistol with light rail & serrated slide
    "handgun": (
        '<svg viewBox="0 0 240 60" fill="none" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: 50px; display: block;">'
        '<path d="M65 20 L160 20 L160 28 L135 28 L128 52 L98 52 L110 33 L82 33 L65 33 Z" fill="rgba(168, 85, 247, 0.15)" stroke="#a855f7" stroke-width="1.8" stroke-linejoin="round"/>'
        '<line x1="88" y1="20" x2="88" y2="15" stroke="#a855f7" stroke-width="2"/>'
        '<line x1="150" y1="20" x2="150" y2="15" stroke="#a855f7" stroke-width="2"/>'
        '<line x1="135" y1="28" x2="155" y2="28" stroke="#38bdf8" stroke-width="2"/>'
        '<circle cx="115" cy="27" r="2.5" fill="#38bdf8"/>'
        '</svg>'
    )
}


def get_weapon_svg(weapon_class_key: str) -> str:
    """Returns SVG vector graphic for a given weapon class key."""
    norm_key = weapon_class_key.lower().replace(" ", "_").replace("-", "_")
    return WEAPON_SVG_MAP.get(norm_key, WEAPON_SVG_MAP["assault_rifle"])


def render_weapon_podium_card(
    medal_label: str,
    border_color: str,
    weapon_name: str,
    weapon_class: str,
    rpm: float,
    active_ttk_ms: float,
    stk: int,
    damage_per_shot: float,
    bullet_velocity: float,
    weapon_id: str = None
) -> str:
    """Renders an authentic Call of Duty Gunsmith style tactical card with transparent weapon render."""
    from .weapon_assets import get_weapon_img_tag
    img_tag = get_weapon_img_tag(weapon_id, max_height_px=46, max_width_px=140) if weapon_id else ""
    
    if img_tag:
        graphic_html = f'<div style="height: 52px; display: flex; align-items: center; justify-content: center; margin: 8px 0 4px 0; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 4px; border: 1px solid rgba(148, 163, 184, 0.1);">{img_tag}</div>'
    else:
        svg_graphic = get_weapon_svg(weapon_class)
        graphic_html = f'<div style="margin: 8px 0 4px 0; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 4px; border: 1px solid rgba(148, 163, 184, 0.1);">{svg_graphic}</div>'

    card_html = (
        f'<div style="background: linear-gradient(145deg, rgba(15, 23, 42, 0.95) 0%, rgba(2, 6, 23, 0.98) 100%); '
        f'border: 2px solid {border_color}; border-top: 6px solid {border_color}; border-radius: 10px; padding: 12px 14px; margin-bottom: 12px; box-shadow: 0 6px 16px rgba(0,0,0,0.6);">'
        f'<div style="display: flex; justify-content: space-between; align-items: center;">'
        f'<span style="font-size: 13px; font-weight: 800; color: {border_color}; text-transform: uppercase; letter-spacing: 0.5px;">{medal_label}</span>'
        f'<span style="font-size: 11px; background: rgba(148, 163, 184, 0.15); color: #94a3b8; padding: 2px 8px; border-radius: 4px; font-weight: 600;">{weapon_class}</span>'
        f'</div>'
        f'{graphic_html}'
        f'<div style="font-size: 18px; font-weight: 800; color: #f8fafc; margin: 4px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{weapon_name}</div>'
        f'<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 6px;">'
        f'<span style="font-size: 32px; font-weight: 900; color: #4ade80; line-height: 1;">{active_ttk_ms:.0f} <span style="font-size: 14px; color: #94a3b8; font-weight: 600;">ms</span></span>'
        f'<span style="font-size: 12px; color: #38bdf8; font-weight: 700;">{rpm:.0f} RPM</span>'
        f'</div>'
        f'<div style="font-size: 11px; color: #cbd5e1; border-top: 1px solid rgba(148, 163, 184, 0.15); padding-top: 6px; display: flex; justify-content: space-between;">'
        f'<span><b>{stk} Shots</b> ({damage_per_shot:.1f} DMG)</span>'
        f'<span style="color: #94a3b8;">{bullet_velocity:.0f} m/s</span>'
        f'</div>'
        f'</div>'
    )
    return card_html
