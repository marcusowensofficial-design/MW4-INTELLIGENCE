"""
MW4 Weapon Intelligence Lab - AI Review Queue & Gatekeeper
Enforces strict quarantine: AI-synthesized claims can NEVER write directly to verified tables.
All AI inputs enter the AI Review Queue and require explicit human triage and promotion.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
from src.database.models import (
    AIReviewItem,
    EvidenceLedgerEntry,
    WeaponVersionStats,
    SourceTier,
    VerificationStatus
)
from src.database.repository import IntelligenceRepository


def submit_ai_claim_to_review_queue(
    proposed_payload: Dict[str, Any],
    ai_model: str,
    confidence_claim: float,
    rationale: str,
    repo: IntelligenceRepository
) -> str:
    """
    Safely captures AI-generated claims into the review queue.
    Zero verified tables are modified during this call.
    """
    queue_id = f"ai_claim_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
    item = AIReviewItem(
        queue_id=queue_id,
        proposed_payload=proposed_payload,
        ai_model=ai_model,
        confidence_claim=confidence_claim,
        rationale=rationale,
        status="pending",
        created_at=datetime.now(timezone.utc).isoformat()
    )
    repo.upsert_ai_review_item(item)
    return queue_id


def promote_ai_claim_to_verified(
    queue_id: str,
    reviewer_name: str,
    target_version_id: str,
    repo: IntelligenceRepository
) -> Tuple[bool, str]:
    """
    Human analyst approves an AI claim, applying it to verified tables and recording an audit trail.
    """
    queue_items = repo.get_ai_review_queue(status="pending")
    target_item = next((i for i in queue_items if i.queue_id == queue_id), None)

    if not target_item:
        return False, f"Queue item '{queue_id}' not found or already processed."

    payload = target_item.proposed_payload
    weapon_id = payload.get("weapon_id")

    if not weapon_id:
        return False, "Invalid payload: missing weapon_id"

    # Fetch existing stats for version
    existing_stats = repo.get_weapon_stats(weapon_id, target_version_id)
    if not existing_stats:
        return False, f"Weapon stats for '{weapon_id}' under '{target_version_id}' do not exist."

    # Apply proposed fields
    stat_dict = existing_stats.model_dump()
    for k, v in payload.items():
        if k in stat_dict and k not in ["stat_id", "weapon_id", "game_version_id"]:
            stat_dict[k] = float(v)

    updated_stats = WeaponVersionStats(**stat_dict)
    repo.upsert_weapon_stats(updated_stats)

    # Record verified evidence entry linking reviewer promotion
    evidence = EvidenceLedgerEntry(
        evidence_id=f"ev_promoted_{queue_id}",
        target_entity_type="weapon_stats",
        target_entity_id=weapon_id,
        field_name="ai_promoted_stat",
        observed_value=str(payload),
        source_url="local://ai-review-queue",
        source_name=f"Human Approved AI Draft ({target_item.ai_model})",
        source_tier=SourceTier.TIER_3,
        test_method=f"Human Reviewer ({reviewer_name}) verified & promoted claim",
        verification_status=VerificationStatus.VERIFIED,
        confidence_score=target_item.confidence_claim,
        notes=f"Promoted from AI queue: {target_item.rationale}"
    )
    repo.upsert_evidence_entry(evidence)

    # Mark queue item as approved
    repo.update_ai_review_status(
        queue_id=queue_id,
        status="approved",
        reviewed_by=reviewer_name
    )

    return True, f"Claim {queue_id} successfully promoted to verified stats by {reviewer_name}."


def reject_ai_claim(
    queue_id: str,
    reviewer_name: str,
    rejection_reason: str,
    repo: IntelligenceRepository
) -> Tuple[bool, str]:
    """
    Human analyst rejects an AI claim with rationale.
    """
    repo.update_ai_review_status(
        queue_id=queue_id,
        status="rejected",
        reviewed_by=reviewer_name,
        rejection_reason=rejection_reason
    )
    return True, f"Claim {queue_id} rejected by {reviewer_name}."
