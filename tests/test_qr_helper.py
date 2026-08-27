"""
Unit tests for QR Code and Clipboard Sharing Engine
"""

import pytest
from src.ui.qr_helper import (
    generate_loadout_qr_image,
    generate_loadout_qr_base64,
    render_copy_button_html,
    HAS_QRCODE
)


def test_generate_loadout_qr_image():
    """Verify QR code PIL image generation."""
    if not HAS_QRCODE:
        pytest.skip("qrcode not installed")
    img = generate_loadout_qr_image("MW4-TEST-CODE-12345")
    assert img is not None
    assert img.size[0] > 50
    assert img.size[1] > 50


def test_generate_loadout_qr_base64():
    """Verify base64 data-URI string generation."""
    if not HAS_QRCODE:
        pytest.skip("qrcode not installed")
    b64 = generate_loadout_qr_base64("MW4-TEST-CODE-12345")
    assert b64.startswith("data:image/png;base64,")
    assert len(b64) > 100


def test_render_copy_button_html():
    """Verify copy button HTML rendering with safe escaping."""
    btn_html = render_copy_button_html("MW4-eyJ3ZWFwb25faWQi...", "test_btn_1")
    assert "copy_btn_test_btn_1" in btn_html
    assert "navigator.clipboard.writeText" in btn_html
    assert "Copied to Clipboard!" in btn_html
