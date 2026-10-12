
from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.matcher import match_claim_to_evidence


def test_matcher_detects_contradicted_claim():
    claim = Claim(
        claim_id="CL_003",
        statement_id="STMT_001",
        subject="person",
        action="was_present",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="home",
        description="The person stated that they were at home at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_001",
            evidence_id="EV_003",
            source_device="phone",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="Device location event recorded.",
            source_tool="synthetic_test",
            metadata={"location": "office"},
        )
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "CONTRADICTED"
    assert result.claim_id == "CL_003"
    assert result.evidence_id == "EV_003"
