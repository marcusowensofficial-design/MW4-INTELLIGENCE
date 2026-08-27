"""
MW4 Weapon Intelligence Lab - Weapon Asset Manager & UI Visual Components
Loads and formats transparent weapon renders with high-performance base64 caching,
crisp sizing, and professional glassmorphic card layouts.
"""

import os
import base64
import functools
from pathlib import Path
from typing import Optional, Dict

ASSETS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "assets",
    "weapons"
)

# Canonical mapping from database weapon_id to authentic WZStats asset filename
WEAPON_FILE_MAP: Dict[str, str] = {
    # Assault Rifles
    "xm4_mw4": "m4-mw4.png",
    "mcw_mw4": "mcw.png",
    "ak74m_mw4": "kastov-762-mw4.png",
    "holger556_mw4": "holger-556.png",
    "han86_mw4": "han-86-mw4.png",
    "hyeon_burst_mw4": "hyeon-burst-mw4.png",
    # Submachine Guns
    "rival9_mw4": "rival-9.png",
    "striker45_mw4": "striker.png",
    "amr9_mw4": "amr9.png",
    "wsp_swarm_mw4": "wsp-swarm.png",
    "ppsh41_mw4": "ppsh-41-mw4.png",
    "iso_nightshade_mw4": "iso-nightshade-mw4.png",
    # Battle Rifles
    "basb_mw4": "bas-b.png",
    "sidewinder_mw4": "sidewinder.png",
    # Marksman Rifles
    "kvd_enforcer_mw4": "kvd-enforcer.png",
    # Sniper Rifles
    "longbow_mw4": "longbow.png",
    "katt_amr_mw4": "katt-amr.png",
    "signal50_mw4": "signal-50-mw4.png",
    # Light Machine Guns
    "pulemyot762_mw4": "pulemyot-762.png",
    "bruen_mk9_mw4": "bruen-mk9.png",
    # Shotguns
    "lockwood680_mw4": "lockwood-680.png",
    "rezi12_mw4": "rezi-12-mw4.png",
    # Handguns
    "cor45_mw4": "cor-45.png",
    "renetti_mw4": "renetti.png",
}


@functools.lru_cache(maxsize=128)
def get_weapon_image_b64(weapon_id: str) -> Optional[str]:
    """
    Returns base64 data URI string for the weapon image, cached in memory.
    Falls back to fuzzy substring matching if exact weapon_id is not mapped.
    """
    fname = WEAPON_FILE_MAP.get(weapon_id)
    
    if not fname:
        # Fuzzy fallback based on weapon_id prefix
        wid_clean = weapon_id.lower().replace("-", "").replace("_", "")
        for key, mapped_file in WEAPON_FILE_MAP.items():
            key_clean = key.lower().replace("-", "").replace("_", "").replace("mw4", "")
            if key_clean and key_clean in wid_clean:
                fname = mapped_file
                break

    if not fname:
        fname = "w_xm4.png"  # Default clean fallback

    full_path = os.path.join(ASSETS_DIR, fname)
    if not os.path.exists(full_path):
        return None

    try:
        with open(full_path, "rb") as f:
            data = f.read()
            mime = "image/png"
            if data[:4] == b"RIFF" and b"WEBP" in data[:16]:
                mime = "image/webp"
            b64_str = base64.b64encode(data).decode("utf-8")
            return f"data:{mime};base64,{b64_str}"
    except Exception:
        return None


def get_weapon_img_tag(
    weapon_id: str,
    max_height_px: int = 75,
    max_width_px: int = 180,
    extra_style: str = ""
) -> str:
    """
    Generates a professionally styled <img> HTML snippet for inline cards and tables.
    """
    b64 = get_weapon_image_b64(weapon_id)
    if not b64:
        return ""
    
    default_style = (
        f"max-height: {max_height_px}px; "
        f"max-width: {max_width_px}px; "
        "object-fit: contain; "
        "filter: drop-shadow(0 6px 14px rgba(0, 0, 0, 0.7)) drop-shadow(0 0 10px rgba(56, 189, 248, 0.25)); "
        "transition: transform 0.2s ease; "
    )
    style = f"{default_style} {extra_style}".strip()
    return f'<img src="{b64}" alt="Weapon Render" style="{style}" />'


def render_weapon_meta_header(
    weapon,
    tier_badge: str,
    consensus_tag: str,
    pick_pct: float,
    kd_val: float
) -> str:
    """
    Renders an authentic, professional weapon header card styled identically to WZStats/CODMunity,
    with title info on the left, an authentic transparent weapon render in the center, and badges on the right.
    """
    img_tag = get_weapon_img_tag(
        weapon.weapon_id,
        max_height_px=78,
        max_width_px=210
    )
    
    class_label = weapon.weapon_class.value.replace('_', ' ').title()
    firing_label = weapon.firing_mode.value.replace('_', ' ').title()

    html = (
        f'<div style="background: linear-gradient(135deg, rgba(30, 41, 59, 0.85) 0%, rgba(15, 23, 42, 0.95) 100%); '
        f'border: 1px solid rgba(56, 189, 248, 0.25); border-left: 4px solid #38bdf8; border-radius: 12px; '
        f'padding: 16px 22px; margin-top: 20px; margin-bottom: 12px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">'
        f'<div style="flex: 1; min-width: 200px;">'
        f'<h2 style="margin: 0; color: #f8fafc; font-size: 1.65rem; font-weight: 800; letter-spacing: -0.02em;">{weapon.name}</h2>'
        f'<p style="margin: 6px 0 0 0; color: #94a3b8; font-size: 0.92rem;">'
        f'<b style="color: #cbd5e1;">Class:</b> {class_label} &nbsp;|&nbsp; '
        f'<b style="color: #cbd5e1;">RPM:</b> {weapon.default_rpm:.0f} &nbsp;|&nbsp; '
        f'<b style="color: #cbd5e1;">Base Mag:</b> {weapon.base_mag_size} Rnd &nbsp;|&nbsp; '
        f'<b style="color: #cbd5e1;">Fire Mode:</b> {firing_label}'
        f'</p>'
        f'</div>'
        f'<div style="flex: 0 0 auto; display: flex; align-items: center; justify-content: center; min-width: 180px; padding: 0 10px;">'
        f'{img_tag}'
        f'</div>'
        f'<div style="text-align: right; min-width: 170px;">'
        f'<div style="display: flex; gap: 6px; justify-content: flex-end; align-items: center; margin-bottom: 6px; flex-wrap: wrap;">'
        f'<span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #38bdf8; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;">🔥 {pick_pct:.1f}% Pick</span>'
        f'<span style="background: rgba(34, 197, 94, 0.2); color: #22c55e; border: 1px solid #22c55e; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 0.85rem;">⭐ {kd_val:.2f} K/D</span>'
        f'<span style="background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.88rem;">{tier_badge}</span>'
        f'</div>'
        f'<p style="margin: 0; color: #38bdf8; font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{consensus_tag}</p>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    return html
