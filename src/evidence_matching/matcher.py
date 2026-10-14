from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.match_schema import MatchResult
from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))

def _get_reliability(record: EvidenceRecord) -> float:
    """
    Return evidence reliability.

    If reliability is not available, use a neutral value of 0.5.
    """
    if record.reliability is None:
        return 0.5

    return record.reliability
def _time_matches(
    claim_time,
    evidence_time,
    tolerance_minutes: int = 5,
) -> bool:
    if claim_time is None:
        return True

    difference = abs(claim_time - evidence_time)

    return difference <= timedelta(minutes=tolerance_minutes)

def _normalize_datetime(value: datetime) -> datetime:
    """Normalize datetimes to UTC, treating naive values as IST."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=IST)

    return value.astimezone(timezone.utc)



def _event_matches_claim_window(
    claim: Claim,
    evidence_time,
    tolerance_minutes: int = 5,
) -> bool:
    """
    Check whether evidence falls within a claim's time window.

    Naive timestamps are treated as UTC so comparisons are consistent.
    """
    tolerance = timedelta(minutes=tolerance_minutes)

    start_time = claim.start_time
    end_time = claim.end_time

    if start_time is None and end_time is None:
        return True

    evidence_time = _normalize_datetime(evidence_time)

    if start_time is not None:
        start_time = _normalize_datetime(start_time)

    if end_time is not None:
        end_time = _normalize_datetime(end_time)

    if start_time is not None and end_time is None:
        return start_time - tolerance <= evidence_time <= start_time + tolerance

    if start_time is None and end_time is not None:
        return end_time - tolerance <= evidence_time <= end_time + tolerance

    return start_time - tolerance <= evidence_time <= end_time + tolerance

def _is_evidence_relevant(
    claim: Claim,
    record: EvidenceRecord,
) -> bool:
    """
    Check whether an evidence record can directly support
    the current basic claim type.
    """

    location_actions = {
        "left",
        "arrived",
        "went",
        "stayed",
        "visited",
    }

    digital_actions = {
        "opened",
        "modified",
        "deleted",
        "created",
        "downloaded",
    }

    action = claim.action.strip().casefold()

    if action in digital_actions:
        if record.artifact_type != "file_activity":
            return False

        claim_object = claim.object

        if claim_object is not None:
            evidence_file_name = record.metadata.get("file_name")

            if evidence_file_name is None:
                return False

            if str(claim_object).strip().casefold() != str(
                evidence_file_name
            ).strip().casefold():
                return False


        evidence_action = record.metadata.get("action")

        if evidence_action is not None:
            return str(evidence_action).strip().casefold() == action

        return action in record.description.strip().casefold()

    if action in location_actions:
        if record.artifact_type in {
            "call_log",
            "file_activity",
        }:
            return bool(record.metadata.get("location"))

        if record.artifact_type not in {
            "location",
            "location_event",
            "location_record",
        }:
            return False

    return True



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
        time_matches = _event_matches_claim_window(
            claim,
                record.event_time,
        )

        if not time_matches:
            continue
        if not _is_evidence_relevant(claim, record):
            continue

        evidence_location = record.metadata.get("location")

        location_unreliable_artifacts = {
            "call_log",
            "file_activity",
        }

        if (
            claim.location is not None
            and evidence_location is not None
            and record.artifact_type not in location_unreliable_artifacts
        ):
            if (
                claim.location.lower()
                == str(evidence_location).lower()
            ):
                supported_records.append(record)
            else:
                contradicted_records.append(record)

        elif (
            claim.location is not None
            and record.artifact_type in location_unreliable_artifacts
        ):
            continue

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

        return MatchResult(
            claim_id=claim.claim_id,
            evidence_id=(
                best_support.evidence_id
                if support_reliability >= contradiction_reliability
                else best_contradiction.evidence_id
            ),
            status="MIXED",
            confidence=None,
            supporting_reliability=support_reliability,
            contradicting_reliability=contradiction_reliability,
            reason=(
                "Some evidence is consistent with the claim, "
                "while other evidence conflicts with it. "
                "Supporting and contradicting evidence reliability "
                "scores are reported separately."
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


        reliability = _get_reliability(best_record)

        return MatchResult(
            claim_id=claim.claim_id,
            evidence_id=best_record.evidence_id,
            status="CONTRADICTED",
            confidence=reliability,
            reason=(
                "The available evidence conflicts with the claim. "
                "Confidence reflects evidence reliability."
            ),
        )

    return MatchResult(
        claim_id=claim.claim_id,
        status="INSUFFICIENT_EVIDENCE",
        reason=(
            "No evidence records were sufficiently compatible "
            "with the claim's time and available details."
        ),
    )