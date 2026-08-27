"""
MW4 Tactical Asset Generator
Generates high-definition tactical HUD banner and SpecOps logo for Streamlit.
"""

import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

os.makedirs("assets", exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Generate 1:1 SpecOps Emblem Logo (assets/mw4_logo.png)
# ---------------------------------------------------------------------------
def generate_specops_logo():
    size = (512, 512)
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = 256, 256
    
    # Outer glowing shield
    shield_pts = [
        (cx, 40),
        (cx + 190, 110),
        (cx + 160, 360),
        (cx, 470),
        (cx - 160, 360),
        (cx - 190, 110)
    ]
    
    # Draw dark carbon shield base
    draw.polygon(shield_pts, fill=(15, 23, 42, 240), outline=(56, 189, 248, 255), width=6)
    
    # Inner tactical shield outline (amber)
    inner_shield = [
        (cx, 65),
        (cx + 160, 125),
        (cx + 135, 340),
        (cx, 440),
        (cx - 135, 340),
        (cx - 160, 125)
    ]
    draw.polygon(inner_shield, fill=(30, 41, 59, 200), outline=(245, 158, 11, 200), width=3)

    # Crosshair Reticle Ring
    r_outer = 110
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], outline=(56, 189, 248, 180), width=3)
    
    r_inner = 65
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], outline=(245, 158, 11, 220), width=2)
    
    # Crosshair tick marks
    draw.line([(cx - 140, cy), (cx - 80, cy)], fill=(56, 189, 248, 255), width=4)
    draw.line([(cx + 80, cy), (cx + 140, cy)], fill=(56, 189, 248, 255), width=4)
    draw.line([(cx, cy - 140), (cx, cy - 80)], fill=(56, 189, 248, 255), width=4)
    draw.line([(cx, cy + 80), (cx, cy + 140)], fill=(56, 189, 248, 255), width=4)

    # Central Chevron & Target Triangle
    chevron = [(cx, cy - 35), (cx + 35, cy + 25), (cx, cy + 10), (cx - 35, cy + 25)]
    draw.polygon(chevron, fill=(56, 189, 248, 255), outline=(255, 255, 255, 255), width=2)

    # Glow effect
    glow = img.filter(ImageFilter.GaussianBlur(radius=3))
    final_img = Image.alpha_composite(glow, img)
    final_img.save("assets/mw4_logo.png", "PNG")
    print("Created assets/mw4_logo.png")


# ---------------------------------------------------------------------------
# 2. Generate 16:9 Tactical Military HUD Banner (assets/mw4_hero_banner.png)
# ---------------------------------------------------------------------------
def generate_hero_banner():
    w, h = 1600, 520
    img = Image.new("RGBA", (w, h), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)

    # 1. Draw subtle carbon fiber grid pattern
    grid_spacing = 40
    for x in range(0, w, grid_spacing):
        alpha = 35 if x % (grid_spacing * 4) == 0 else 15
        draw.line([(x, 0), (x, h)], fill=(56, 189, 248, alpha), width=1)
    for y in range(0, h, grid_spacing):
        alpha = 35 if y % (grid_spacing * 4) == 0 else 15
        draw.line([(0, y), (w, y)], fill=(56, 189, 248, alpha), width=1)

    # 2. Cyan & Amber Radar Sweeps on right side
    cx_radar, cy_radar = 1350, 260
    for r in [60, 120, 180, 240]:
        draw.ellipse([cx_radar - r, cy_radar - r, cx_radar + r, cy_radar + r], outline=(56, 189, 248, 40), width=1)
    
    # Angled telemetry rays
    for angle_deg in [0, 30, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle_deg)
        x2 = cx_radar + int(240 * math.cos(rad))
        y2 = cy_radar + int(240 * math.sin(rad))
        draw.line([(cx_radar, cy_radar), (x2, y2)], fill=(56, 189, 248, 25), width=1)

    # 3. Waveform / Ballistics Telemetry in lower right
    wave_y = 440
    prev_pt = (900, wave_y)
    for idx, x in enumerate(range(900, 1550, 25)):
        dy = int(18 * math.sin(idx * 0.7) * math.cos(idx * 0.3))
        curr_pt = (x, wave_y + dy)
        draw.line([prev_pt, curr_pt], fill=(245, 158, 11, 160), width=2)
        prev_pt = curr_pt

    # 4. Top & Bottom Neon Cyan Cyber Trim
    draw.line([(0, 0), (w, 0)], fill=(56, 189, 248, 255), width=4)
    draw.line([(0, 4), (w, 4)], fill=(56, 189, 248, 100), width=2)
    draw.line([(0, h - 2), (w, h - 2)], fill=(245, 158, 11, 200), width=3)

    # 5. Diagonal tactical corner cuts
    draw.polygon([(0, 0), (70, 0), (0, 70)], fill=(30, 41, 59, 255))
    draw.line([(70, 0), (0, 70)], fill=(56, 189, 248, 255), width=3)

    draw.polygon([(w, h), (w - 70, h), (w, h - 70)], fill=(30, 41, 59, 255))
    draw.line([(w - 70, h), (w, h - 70)], fill=(245, 158, 11, 255), width=3)

    # 6. Paste Emblem Badge in Banner
    logo = Image.open("assets/mw4_logo.png").resize((220, 220), Image.Resampling.LANCZOS)
    img.paste(logo, (80, 140), logo)

    # Save final banner
    img.save("assets/mw4_hero_banner.png", "PNG")
    print("Created assets/mw4_hero_banner.png")


if __name__ == "__main__":
    generate_specops_logo()
    generate_hero_banner()
