from src.evidence.schema import EvidenceRecord
from src.timeline_analysis.timeline import build_timeline


records = [
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_003",
        source_device="laptop",
        artifact_type="file_activity",
        event_time="2026-01-15T18:30:00",
        description="A file was modified.",
        source_tool="synthetic_test",
        reliability=0.7,
    ),
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_002",
        source_device="phone",
        artifact_type="message",
        event_time="2026-01-15T18:30:00",
        description="A message was recorded.",
        source_tool="synthetic_test",
        reliability=0.9,
    ),
]


timeline = build_timeline(records)

print("Same-time events:")

for event in timeline:
    print(event.event_time, "|", event.evidence_id)