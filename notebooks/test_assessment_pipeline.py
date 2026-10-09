
from datetime import datetime

from src.assessment.pipeline import run_assessment
from src.evidence.schema import EvidenceRecord


evidence = [
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_001",
        source_device="phone",
        artifact_type="location",
        description="Phone location event for testing",
        source_tool="synthetic_test",
        event_time=datetime(2026, 1, 15, 18, 0),
        reliability=0.9,
        metadata={"location": "home"},
    ),
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_002",
        source_device="phone",
        artifact_type="location",
        description="Phone location event for testing",
        source_tool="synthetic_test",
        event_time=datetime(2026, 1, 15, 19, 0),
        reliability=0.85,
        metadata={"location": "office"},
    ),
]

statement = (
    "The person left home at 6 PM. "
    "They arrived at the office at 7 PM."
)

assessment = run_assessment(
    statement_id="ST_001",
    statement=statement,
    evidence=evidence,
)

print(assessment.model_dump())

assert assessment.total_claims == 2
assert len(assessment.results) == 2

print("End-to-end assessment pipeline test passed!")