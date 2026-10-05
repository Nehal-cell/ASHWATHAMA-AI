from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.matcher import match_claim_to_evidence


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

print("Match result:")
print(result.model_dump())