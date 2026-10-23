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


def test_gps_coordinates_without_location_label_do_not_claim_location_match():
    claim = Claim(
        claim_id="CL_GPS_001",
        statement_id="STMT_GPS_001",
        subject="person",
        action="arrived",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="home",
        description="The person stated they arrived home.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_GPS_001",
            evidence_id="GPS_001",
            source_device="Google Maps Timeline",
            artifact_type="location_record",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="GPS point from synthetic test data.",
            source_tool="Google Maps Timeline Parser",
            metadata={
                "latitude": 28.6,
                "longitude": 77.2,
            },
        )
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "INSUFFICIENT_EVIDENCE"
