from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.matcher import match_claim_to_evidence


claim = Claim(
    claim_id="CL_002",
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
        evidence_id="EV_002",
        source_device="phone",
        artifact_type="location_event",
        event_time=datetime(2026, 1, 15, 19, 0),
        description="Device location event recorded.",
        source_tool="synthetic_test",
        metadata={
            "location": "office"
        },
    )
]


result = match_claim_to_evidence(
    claim=claim,
    evidence=evidence,
)


print("Match result:")
print(result.model_dump())