
from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.matcher import match_claim_to_evidence


def test_matcher_returns_mixed_when_evidence_conflicts():
    claim = Claim(
        claim_id="CL_004",
        statement_id="STMT_002",
        subject="person",
        action="was_present",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="home",
        description="The person stated that they were at home at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_001",
            evidence_id="EV_004",
            source_device="phone",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="Device location event recorded at home.",
            source_tool="synthetic_test",
            metadata={"location": "home"},
        ),
        EvidenceRecord(
            case_id="CASE_001",
            evidence_id="EV_005",
            source_device="laptop",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="Device location event recorded at office.",
            source_tool="synthetic_test",
            metadata={"location": "office"},
        ),
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "MIXED"
    assert result.claim_id == "CL_004"

def test_mixed_result_reports_reliability_scores_separately():
    claim = Claim(
        claim_id="CL_MIXED",
        statement_id="STMT_MIXED",
        subject="person",
        action="was_present",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="home",
        description="The person stated that they were at home at 6:30 PM.",

    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_001",
            evidence_id="EV_SUPPORT",
            source_device="phone",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="Location evidence recorded at home.",
            source_tool="synthetic_test",
            reliability=0.9,
            metadata={"location": "home"},
        ),
        EvidenceRecord(
            case_id="CASE_001",
            evidence_id="EV_CONTRADICT",
            source_device="laptop",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="Location evidence recorded at office.",
            source_tool="synthetic_test",
            reliability=0.6,
            metadata={"location": "office"},
        ),
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "MIXED"
    assert result.confidence is None
    assert result.supporting_reliability == 0.9
    assert result.contradicting_reliability == 0.6
    assert result.evidence_id == "EV_SUPPORT"
