from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.matcher import match_claim_to_evidence


def create_test_data():
    claim = Claim(
        claim_id="CL_001",
        statement_id="STMT_001",
        subject="person",
        action="left",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="home",
        description="The person stated that they left home at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_001",
            evidence_id="EV_001",
            source_device="phone",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="Device location event recorded.",
            source_tool="synthetic_test",
            metadata={"location": "home"},
        )
    ]

    return claim, evidence


def test_matcher_uses_default_reliability():
    claim, evidence = create_test_data()

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "SUPPORTED"
    assert result.evidence_id == "EV_001"
    assert result.confidence == 0.5


if __name__ == "__main__":
    claim, evidence = create_test_data()

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    print("Match result:")
    print(result.model_dump())