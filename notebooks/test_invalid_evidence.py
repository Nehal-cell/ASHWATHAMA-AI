from pydantic import ValidationError
from src.evidence.schema import EvidenceRecord

invalid_record = {
    "case_id": "CASE_001",
    "evidence_id": "EV_BAD",
    "source_device": "phone",
    "artifact_type": "call_log",
    "event_time": "2026-01-15T18:30:00",
    "description": "Synthetic invalid test record.",
    "source_tool": "synthetic_test",
    "reliability": 1.5,
    "metadata": {}
}

try:
    EvidenceRecord(**invalid_record)
    print("ERROR: Invalid record was accepted!")
except ValidationError as error:
    print("PASS: Invalid record was rejected.")
    print(error)