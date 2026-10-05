from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.timeline_analysis.timeline import find_timeline_gaps


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


gaps = find_timeline_gaps(records)

print("Timeline gaps:")

for start, end, duration in gaps:
    print(
        f"{start} → {end} | "
        f"Duration: {duration / 60:.1f} minutes"
    )

print(f"\nTotal gaps: {len(gaps)}")