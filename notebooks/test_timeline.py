from src.evidence.schema import EvidenceRecord
from src.timeline_analysis.timeline import build_case_timeline


records = [
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_002",
        source_device="laptop",
        artifact_type="file_activity",
        event_time="2026-01-15T19:10:00",
        description="A document was modified.",
        source_tool="synthetic_test",
        reliability=0.7,
        metadata={"file_name": "meeting_notes.txt"},
    ),
    EvidenceRecord(
        case_id="CASE_002",
        evidence_id="EV_003",
        source_device="phone",
        artifact_type="message",
        event_time="2026-01-15T17:00:00",
        description="A message was recorded.",
        source_tool="synthetic_test",
        reliability=0.9,
        metadata={},
    ),
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_001",
        source_device="phone",
        artifact_type="call_log",
        event_time="2026-01-15T18:30:00",
        description="An outgoing call was recorded.",
        source_tool="synthetic_test",
        reliability=0.8,
        metadata={"duration_seconds": 120},
    ),
]


timeline = build_case_timeline(records, "CASE_001")

print("CASE_001 timeline:")

for event in timeline:
    print(
        event.event_time,
        "|",
        event.evidence_id,
        "|",
        event.source_device,
        "|",
        event.artifact_type,
    )

print("\nTotal events:", len(timeline))

