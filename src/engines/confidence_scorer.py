"""
MW4 Weapon Intelligence Lab - Confidence & Freshness Scoring Engine
Computes source reliability, temporal freshness decay, and multi-tester consensus index.
"""

from datetime import datetime
from typing import List, Optional
from ..database.models import EvidenceLedgerEntry, SourceTier, VerificationStatus


TIER_CONFIDENCE_WEIGHTS = {
    SourceTier.TIER_1: 0.98,  # Official first-party patch notes
    SourceTier.TIER_2: 0.92,  # 240fps controlled frame capture
    SourceTier.TIER_3: 0.78,  # Public community measurements
    SourceTier.TIER_4: 0.40   # AI drafts / OCR clips (Quarantined)
}


def calculate_evidence_confidence(
    entries: List[EvidenceLedgerEntry],
    target_version_id: str = "v1.1.0-launch"
) -> float:
    """
    Computes an aggregated confidence score (0.0 to 1.0) across all evidence entries
    for a given weapon or metric.
    """
    if not entries:
        return 0.50  # Default baseline for unverified placeholder

    total_weight = 0.0
    weighted_confidence_sum = 0.0

    for e in entries:
        base_tier_weight = TIER_CONFIDENCE_WEIGHTS.get(e.source_tier, 0.50)

        # Status modifier
        if e.verification_status == VerificationStatus.VERIFIED:
            status_mult = 1.0
        elif e.verification_status == VerificationStatus.ILLUSTRATIVE:
            status_mult = 0.85
        elif e.verification_status == VerificationStatus.PENDING_REVIEW:
            status_mult = 0.40
        else:
            status_mult = 0.10

        item_score = e.confidence_score * base_tier_weight * status_mult
        weighted_confidence_sum += item_score
        total_weight += 1.0

    consensus_bonus = min(0.05, 0.015 * (len(entries) - 1)) if len(entries) > 1 else 0.0
    final_score = (weighted_confidence_sum / total_weight) + consensus_bonus
    return max(0.10, min(1.0, round(final_score, 3)))
