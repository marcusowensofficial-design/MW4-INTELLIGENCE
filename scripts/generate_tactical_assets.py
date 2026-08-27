"""
MW4 Tactical Asset Generator - SAIL6 INTELLIGENCE RESEARCH HUB
Generates high-definition tactical HUD banner and SpecOps logo with custom SAIL6 branding.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

os.makedirs("assets", exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Generate 1:1 SpecOps Emblem Logo with "SAIL6" (assets/mw4_logo.png)
# ---------------------------------------------------------------------------
def generate_specops_logo():
    size = (512, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 256, 256
    
    # Outer glowing shield
    shield_pts = [
        (cx, 35),
        (cx + 195, 105),
        (cx + 165, 365),
        (cx, 475),
        (cx - 165, 365),
        (cx - 195, 105)
    ]
    
    # Draw dark carbon shield base
    draw.polygon(shield_pts, fill=(15, 23, 42, 245), outline=(56, 189, 248, 255), width=6)
    
    # Inner tactical shield outline (amber)
    inner_shield = [
        (cx, 60),
        (cx + 165, 120),
        (cx + 140, 345),
        (cx, 445),
        (cx - 140, 345),
        (cx - 165, 120)
    ]
    draw.polygon(inner_shield, fill=(24, 32, 47, 220), outline=(245, 158, 11, 220), width=3)

    # Crosshair Reticle Ring
    r_outer = 115
    draw.ellipse([cx - r_outer, cy - r_outer - 15, cx + r_outer, cy + r_outer - 15], outline=(56, 189, 248, 180), width=3)
    
    r_inner = 70
    draw.ellipse([cx - r_inner, cy - r_inner - 15, cx + r_inner, cy + r_inner - 15], outline=(245, 158, 11, 220), width=2)
    
    # Crosshair tick marks
    draw.line([(cx - 145, cy - 15), (cx - 85, cy - 15)], fill=(56, 189, 248, 255), width=4)
    draw.line([(cx + 85, cy - 15), (cx + 145, cy - 15)], fill=(56, 189, 248, 255), width=4)
    draw.line([(cx, cy - 155), (cx, cy - 95)], fill=(56, 189, 248, 255), width=4)
    draw.line([(cx, cy + 65), (cx, cy + 125)], fill=(56, 189, 248, 255), width=4)

    # Central Chevron
    chevron = [(cx, cy - 55), (cx + 35, cy + 5), (cx, cy - 10), (cx - 35, cy + 5)]
    draw.polygon(chevron, fill=(56, 189, 248, 255), outline=(255, 255, 255, 255), width=2)

    # Text "SAIL6" on lower shield
    try:
        font_logo = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 16)
    except Exception:
        font_logo = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    draw.text((cx, 345), "SAIL6", fill=(255, 255, 255, 255), font=font_logo, anchor="mm")
    draw.text((cx, 385), "INTELLIGENCE", fill=(245, 158, 11, 240), font=font_sub, anchor="mm")

    # Glow effect
    glow = img.filter(ImageFilter.GaussianBlur(radius=2))
    final_img = Image.alpha_composite(glow, img)
    final_img.save("assets/mw4_logo.png", "PNG")
    print("Created assets/mw4_logo.png with SAIL6 branding")


# ---------------------------------------------------------------------------
# 2. Generate 16:9 Tactical Military HUD Banner with SAIL6 Typography
# ---------------------------------------------------------------------------
def generate_hero_banner():
    w, h = 1600, 520
    img = Image.new("RGBA", (w, h), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)

    # 1. Subtle carbon fiber grid pattern
    grid_spacing = 40
    for x in range(0, w, grid_spacing):
        alpha = 40 if x % (grid_spacing * 4) == 0 else 18
        draw.line([(x, 0), (x, h)], fill=(56, 189, 248, alpha), width=1)
    for y in range(0, h, grid_spacing):
        alpha = 40 if y % (grid_spacing * 4) == 0 else 18
        draw.line([(0, y), (w, y)], fill=(56, 189, 248, alpha), width=1)

    # 2. Cyan & Amber Radar Sweeps on right side
    cx_radar, cy_radar = 1380, 260
    for r in [70, 140, 210, 280]:
        draw.ellipse([cx_radar - r, cy_radar - r, cx_radar + r, cy_radar + r], outline=(56, 189, 248, 45), width=1)
    
    # Angled telemetry rays
    for angle_deg in [0, 30, 45, 60, 90, 120, 135, 150, 180, 210, 225, 240, 270, 300, 315, 330]:
        rad = math.radians(angle_deg)
        x2 = cx_radar + int(280 * math.cos(rad))
        y2 = cy_radar + int(280 * math.sin(rad))
        draw.line([(cx_radar, cy_radar), (x2, y2)], fill=(56, 189, 248, 20), width=1)

    # 3. Waveform / Ballistics Telemetry in lower right
    wave_y = 445
    prev_pt = (920, wave_y)
    for idx, x in enumerate(range(920, 1550, 20)):
        dy = int(18 * math.sin(idx * 0.65) * math.cos(idx * 0.35))
        curr_pt = (x, wave_y + dy)
        draw.line([prev_pt, curr_pt], fill=(245, 158, 11, 180), width=2)
        prev_pt = curr_pt

    # 4. Top & Bottom Neon Cyan Cyber Trim
    draw.line([(0, 0), (w, 0)], fill=(56, 189, 248, 255), width=5)
    draw.line([(0, 5), (w, 5)], fill=(56, 189, 248, 120), width=2)
    draw.line([(0, h - 3), (w, h - 3)], fill=(245, 158, 11, 220), width=4)

    # 5. Diagonal tactical corner cuts
    draw.polygon([(0, 0), (80, 0), (0, 80)], fill=(30, 41, 59, 255))
    draw.line([(80, 0), (0, 80)], fill=(56, 189, 248, 255), width=3)

    draw.polygon([(w, h), (w - 80, h), (w, h - 80)], fill=(30, 41, 59, 255))
    draw.line([(w - 80, h), (w, h - 80)], fill=(245, 158, 11, 255), width=3)

    # 6. Paste Emblem Badge on the left
    logo = Image.open("assets/mw4_logo.png").resize((250, 250), Image.Resampling.LANCZOS)
    img.paste(logo, (60, 135), logo)

    # 7. Typography - "SAIL6 INTELLIGENCE RESEARCH HUB"
    try:
        font_tag = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
        font_sail6 = ImageFont.truetype("C:/Windows/Fonts/impact.ttf", 92)
        font_hub = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 36)
        font_telemetry = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 15)
        font_footer = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 13)
    except Exception:
        font_tag = ImageFont.load_default()
        font_sail6 = ImageFont.load_default()
        font_hub = ImageFont.load_default()
        font_telemetry = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    tx = 340

    # Clearance Level Tag
    draw.rectangle([tx, 90, tx + 460, 118], fill=(15, 23, 42, 220), outline=(56, 189, 248, 180), width=1)
    draw.text((tx + 12, 95), "TACTICAL WEAPON COMMAND • CLEARANCE: S-TIER TOP SECRET", fill=(56, 189, 248, 255), font=font_tag)

    # Main Brand "SAIL6" with glowing drop shadow
    # Drop shadow
    draw.text((tx + 3, 138), "SAIL6", fill=(14, 116, 144, 180), font=font_sail6)
    # Bright White / Cyan Core
    draw.text((tx, 135), "SAIL6", fill=(248, 250, 252, 255), font=font_sail6)

    # Accent Cyan Slash
    draw.line([(tx + 270, 150), (tx + 250, 230)], fill=(56, 189, 248, 255), width=4)

    # "INTELLIGENCE RESEARCH HUB"
    draw.text((tx + 290, 152), "INTELLIGENCE", fill=(245, 158, 11, 255), font=font_hub)
    draw.text((tx + 290, 195), "RESEARCH HUB", fill=(56, 189, 248, 255), font=font_hub)

    # Horizontal tactical divider
    draw.line([(tx, 255), (tx + 750, 255)], fill=(56, 189, 248, 160), width=2)
    draw.line([(tx, 259), (tx + 400, 259)], fill=(245, 158, 11, 200), width=2)

    # Telemetry Subtitle
    draw.text(
        (tx, 275),
        "🎯 EVIDENCE-BACKED COMPETITIVE FPS BALLISTICS • CDL META SYNTHESIS",
        fill=(226, 232, 240, 240),
        font=font_telemetry
    )
    draw.text(
        (tx, 305),
        "⚡ 5-SLOT ATTACHMENT GUNSMITH SOLVER • ZERO-RECOIL PRO PLATFORMS",
        fill=(148, 163, 184, 220),
        font=font_telemetry
    )

    # Footer HUD telemetry status badges
    draw.rectangle([tx, 350, tx + 210, 385], fill=(15, 23, 42, 200), outline=(34, 197, 94, 180), width=1)
    draw.text((tx + 12, 360), "🟢 SYSTEM STATUS: ONLINE", fill=(74, 222, 128, 255), font=font_footer)

    draw.rectangle([tx + 225, 350, tx + 480, 385], fill=(15, 23, 42, 200), outline=(56, 189, 248, 180), width=1)
    draw.text((tx + 237, 360), "🗄️ ENGINE: LOCAL DUCKDB v1.1.0", fill=(56, 189, 248, 255), font=font_footer)

    draw.rectangle([tx + 495, 350, tx + 730, 385], fill=(15, 23, 42, 200), outline=(245, 158, 11, 180), width=1)
    draw.text((tx + 507, 360), "🔒 LOCAL-FIRST • ZERO HOOKS", fill=(245, 158, 11, 255), font=font_footer)

    # Save final banner
    img.save("assets/mw4_hero_banner.png", "PNG")
    print("Created assets/mw4_hero_banner.png with SAIL6 INTELLIGENCE RESEARCH HUB")


if __name__ == "__main__":
    generate_specops_logo()
    generate_hero_banner()
