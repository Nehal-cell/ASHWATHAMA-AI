
from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.matcher import match_claim_to_evidence


claim = Claim(
    claim_id="CL_HOME",
    statement_id="ST_001",
    subject="the person",
    action="left",
    start_time=datetime(2026, 1, 15, 18, 0),
    location="home",
    description="The person left home at 6 PM.",
)

evidence = [
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_HOME",
        source_device="phone",
        artifact_type="location",
        description="Synthetic test location at home",
        source_tool="synthetic_test",
        event_time=datetime(2026, 1, 15, 18, 0),
        reliability=0.9,
        metadata={"location": "home"},
    ),
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_OFFICE",
        source_device="phone",
        artifact_type="location",
        description="Synthetic test location at office",
        source_tool="synthetic_test",
        event_time=datetime(2026, 1, 15, 19, 0),
        reliability=0.85,
        metadata={"location": "office"},
    ),
]

result = match_claim_to_evidence(claim, evidence)

print(result.model_dump())


# Test: office evidence occurs at 7 PM, but the claim
# says the person left home at 6 PM.

office_only_result = match_claim_to_evidence(
    claim,
    [evidence[1]],
)

print("Office-only result:", office_only_result.model_dump())