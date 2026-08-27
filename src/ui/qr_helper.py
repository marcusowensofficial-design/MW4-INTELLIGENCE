"""
MW4 Weapon Intelligence Lab - Loadout QR & Clipboard Sharing Engine
Generates sleek tactical QR codes and interactive 1-click clipboard copy triggers for loadout cards.
"""

import io
import base64
from typing import Optional
from PIL import Image

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


def generate_loadout_qr_image(share_code: str, fill_color: str = "#38bdf8", back_color: str = "#0f172a") -> Optional[Image.Image]:
    """Generates a PIL Image QR code for any MW4 loadout share string."""
    if not HAS_QRCODE:
        return None
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=2
        )
        qr.add_data(share_code)
        qr.make(fit=True)
        return qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")
    except Exception:
        return None


def generate_loadout_qr_base64(share_code: str, fill_color: str = "#38bdf8", back_color: str = "#0f172a") -> str:
    """Returns a base64 data-URI string of the loadout QR code for fast in-memory HTML rendering."""
    img = generate_loadout_qr_image(share_code, fill_color=fill_color, back_color=back_color)
    if img is None:
        return ""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


def render_copy_button_html(text_to_copy: str, btn_id: str, btn_label: str = "📋 Copy Share Code to Clipboard") -> str:
    """Renders a self-contained responsive button with native browser clipboard copy and visual feedback."""
    safe_text = text_to_copy.replace('"', '\\"').replace("'", "\\'")
    return f"""
    <div style="margin: 10px 0;">
        <button id="copy_btn_{btn_id}" onclick="
            navigator.clipboard.writeText('{safe_text}').then(function() {{
                var b = document.getElementById('copy_btn_{btn_id}');
                var orig = b.innerHTML;
                b.innerHTML = '✅ Copied to Clipboard!';
                b.style.backgroundColor = '#16a34a';
                b.style.borderColor = '#22c55e';
                setTimeout(function() {{
                    b.innerHTML = orig;
                    b.style.backgroundColor = 'rgba(56, 189, 248, 0.15)';
                    b.style.borderColor = '#38bdf8';
                }}, 2500);
            }});
        " style="
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            background-color: rgba(56, 189, 248, 0.15);
            color: #38bdf8;
            border: 1px solid #38bdf8;
            border-radius: 6px;
            padding: 10px 16px;
            font-size: 13.5px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease-in-out;
        " onmouseover="this.style.backgroundColor='rgba(56, 189, 248, 0.3)';" onmouseout="this.style.backgroundColor='rgba(56, 189, 248, 0.15)';">
            {btn_label}
        </button>
    </div>
    """
