import pytest
from pydantic import ValidationError

from src.evidence_matching.match_schema import MatchResult


def test_match_result_accepts_valid_confidence():
    result = MatchResult(
        claim_id="CL_001",
        evidence_id="EV_001",
        status="SUPPORTED",
        confidence=0.85,
        reason="Evidence is consistent with the claim.",
    )

    assert result.confidence == 0.85


def test_match_result_accepts_confidence_boundaries():
    for confidence in (0.0, 1.0):
        result = MatchResult(
            claim_id="CL_002",
            status="SUPPORTED",
            confidence=confidence,
            reason="Testing valid confidence boundary.",
        )

        assert result.confidence == confidence


def test_match_result_rejects_invalid_status():
    with pytest.raises(ValidationError):
        MatchResult(
            claim_id="CL_003",
            status="UNKNOWN",
            confidence=0.5,
            reason="Testing invalid status.",
        )


@pytest.mark.parametrize("confidence", [-0.1, 1.1])
def test_match_result_rejects_confidence_outside_range(confidence):
    with pytest.raises(ValidationError):
        MatchResult(
            claim_id="CL_004",
            status="SUPPORTED",
            confidence=confidence,
            reason="Testing invalid confidence.",
        )


def test_insufficient_evidence_requires_none_confidence():
    with pytest.raises(ValidationError):
        MatchResult(
            claim_id="CL_005",
            status="INSUFFICIENT_EVIDENCE",
            confidence=0.5,
            reason="Testing insufficient evidence.",
        )


def test_insufficient_evidence_accepts_none_confidence():
    result = MatchResult(
        claim_id="CL_006",
        status="INSUFFICIENT_EVIDENCE",
        confidence=None,
        reason="No sufficient evidence is available.",
    )

    assert result.confidence is None


def test_mixed_result_requires_both_reliability_scores():
    with pytest.raises(ValidationError):
        MatchResult(
            claim_id="CL_MIXED_INVALID",
            status="MIXED",
            confidence=None,
            supporting_reliability=0.9,
            reason="Evidence is conflicting.",
        )