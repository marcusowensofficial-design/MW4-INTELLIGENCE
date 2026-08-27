"""
MW4 Weapon Intelligence Lab - Gunsmith Loadout Share Code Engine
Encodes and decodes 5-slot Gunsmith builds into compact, shareable string tokens.
"""

import json
import base64
from typing import Dict, Any, List, Optional, Tuple
from pydantic import BaseModel


class DecodedLoadout(BaseModel):
    weapon_id: str
    game_version_id: str
    ruleset_id: str
    attachment_ids: List[str]
    user_label: Optional[str] = None
    created_timestamp: Optional[str] = None


def encode_loadout_share_code(
    weapon_id: str,
    attachment_ids: List[str],
    game_version_id: str = "v1.1.0-launch",
    ruleset_id: str = "core",
    user_label: Optional[str] = None
) -> str:
    """
    Encodes a custom weapon build into a compact, standardized share code.
    Format: MW4-BASE64(JSON_PAYLOAD)
    """
    payload = {
        "w": weapon_id,
        "v": game_version_id,
        "r": ruleset_id,
        "a": sorted(attachment_ids[:5]),
        "l": user_label or "Custom Build"
    }
    raw_json = json.dumps(payload, separators=(',', ':'))
    b64_str = base64.urlsafe_b64encode(raw_json.encode("utf-8")).decode("ascii").rstrip("=")
    return f"MW4-{b64_str}"


def decode_loadout_share_code(share_code: str) -> Tuple[bool, Optional[DecodedLoadout], str]:
    """
    Decodes a share code string back into a verified DecodedLoadout structure.
    """
    code = share_code.strip()
    if not code.startswith("MW4-"):
        return False, None, "Invalid share code format (must start with 'MW4-')"

    b64_part = code[4:]
    # Re-add padding if needed
    padding = len(b64_part) % 4
    if padding != 0:
        b64_part += "=" * (4 - padding)

    try:
        raw_bytes = base64.urlsafe_b64decode(b64_part.encode("ascii"))
        payload = json.loads(raw_bytes.decode("utf-8"))

        if "w" not in payload or "a" not in payload:
            return False, None, "Malformed payload inside share code"

        decoded = DecodedLoadout(
            weapon_id=payload["w"],
            game_version_id=payload.get("v", "v1.1.0-launch"),
            ruleset_id=payload.get("r", "core"),
            attachment_ids=payload.get("a", []),
            user_label=payload.get("l", "Imported Build")
        )
        return True, decoded, "Loadout successfully decoded"
    except Exception as e:
        return False, None, f"Failed to decode share code: {str(e)}"
