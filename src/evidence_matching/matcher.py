from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.match_schema import MatchResult


def _get_reliability(record: EvidenceRecord) -> float:
    """
    Return evidence reliability.

    If reliability is not available, use a neutral value of 0.5.
    """
    if record.reliability is None:
        return 0.5

    return record.reliability


def match_claim_to_evidence(
    claim: Claim,
    evidence: list[EvidenceRecord],
) -> MatchResult:
    """
    Match a claim against all available evidence.

    Possible outcomes:
    - SUPPORTED
    - CONTRADICTED
    - MIXED
    - INSUFFICIENT_EVIDENCE

    Confidence is influenced by evidence reliability.

    This system evaluates evidence consistency.
    It does not determine truthfulness or guilt.
    """

    if not evidence:
        return MatchResult(
            claim_id=claim.claim_id,
            status="INSUFFICIENT_EVIDENCE",
            reason="No evidence records are available for comparison.",
        )

    supported_records = []
    contradicted_records = []

    for record in evidence:

        # Check time compatibility
        time_matches = (
            claim.start_time is None
            or record.event_time == claim.start_time
        )

        if not time_matches:
            continue

        evidence_location = record.metadata.get("location")

        if claim.location is not None and evidence_location is not None:

            if (
                claim.location.lower()
                == str(evidence_location).lower()
            ):
                supported_records.append(record)
            else:
                contradicted_records.append(record)

        else:
            supported_records.append(record)

    if supported_records and contradicted_records:

        best_support = max(
            supported_records,
            key=_get_reliability,
        )

        best_contradiction = max(
            contradicted_records,
            key=_get_reliability,
        )

        support_reliability = _get_reliability(best_support)
        contradiction_reliability = _get_reliability(
            best_contradiction
        )

        confidence = max(
            support_reliability,
            contradiction_reliability,
        )

        return MatchResult(
            claim_id=claim.claim_id,
            evidence_id=(
                best_support.evidence_id
                if support_reliability >= contradiction_reliability
                else best_contradiction.evidence_id
            ),
            status="MIXED",
            confidence=confidence,
            reason=(
                "Some evidence is consistent with the claim, "
                "while other evidence conflicts with it. "
                "Evidence reliability was considered."
            ),
        )

    if supported_records:

        best_record = max(
            supported_records,
            key=_get_reliability,
        )

        reliability = _get_reliability(best_record)

        return MatchResult(
            claim_id=claim.claim_id,
            evidence_id=best_record.evidence_id,
            status="SUPPORTED",
            confidence=reliability,
            reason=(
                "The available matching evidence is consistent "
                "with the claim. Confidence reflects evidence "
                "reliability."
            ),
        )

    if contradicted_records:

        best_record = max(
            contradicted_records,
            key=_get_reliability,
        )
        