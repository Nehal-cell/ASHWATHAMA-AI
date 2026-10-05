from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.timeline_analysis.timeline import find_overlapping_events


records = [
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_001",
        source_device="phone",
        artifact_type="call_log",
        event_time=datetime(2026, 1, 15, 18, 30),
        description="Outgoing call recorded.",
        source_tool="synthetic_test",
        metadata={"duration_seconds": 120},
    ),
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_002",
        source_device="laptop",
        artifact_type="file_activity",
        event_time=datetime(2026, 1, 15, 18, 31),
        description="Document modified.",
        source_tool="synthetic_test",
        metadata={"duration_seconds": 240},
    ),
    EvidenceRecord(
        case_id="CASE_001",
        evidence_id="EV_003",
        source_device="laptop",
        artifact_type="file_activity",
        event_time=datetime(2026, 1, 15, 19, 10),
        description="Another document modified.",
        source_tool="synthetic_test",
        metadata={},
    ),
]


overlaps = find_overlapping_events(records)

print("Overlapping events:")

for first, second in overlaps:
    print(
        f"{first.evidence_id} <-> {second.evidence_id}"
    )

print(f"\nTotal overlaps: {len(overlaps)}")