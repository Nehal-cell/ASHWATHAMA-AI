from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.matcher import match_claim_to_evidence


claim = Claim(
    claim_id="CL_005",
    statement_id="STMT_003",
    subject="person",
    action="was_present",
    start_time=datetime(2026, 1, 15, 18, 30),
    location="home",
    description="The person stated that they were at home at 6:30 PM.",
)

evidence = [
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_LOW",
        source_device="phone",
        artifact_type="location_event",
        event_time=datetime(2026, 1, 15, 18, 30),
        description="Low reliability location evidence.",
        source_tool="synthetic_test",
        reliability=0.3,
        metadata={"location": "home"},
    ),
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_HIGH",
        source_device="laptop",
        artifact_type="location_event",
        event_time=datetime(2026, 1, 15, 18, 30),
        description="High reliability location evidence.",
        source_tool="synthetic_test",
        reliability=0.9,
        metadata={"location": "home"},
    ),
]

result = match_claim_to_evidence(
    claim=claim,
    evidence=evidence,
)

print("Reliability-aware match result:")
print(result.model_dump())

assert result.status == "SUPPORTED"
assert result.evidence_id == "EV_HIGH"
assert result.confidence == 0.9

print("PASS: Higher reliability evidence was selected.")