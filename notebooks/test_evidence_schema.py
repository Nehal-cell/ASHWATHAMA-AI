from src.evidence.schema import EvidenceRecord

sample = EvidenceRecord(
    case_id="CASE_001",
    evidence_id="EV_001",
    source_device="phone",
    artifact_type="call_log",
    event_time="2026-01-15T18:30:00",
    description="An outgoing call was recorded.",
    source_tool="synthetic_test",
    reliability=0.8,
    metadata={
        "duration_seconds": 120,
        "direction": "outgoing"
    }
)

print(sample.model_dump())