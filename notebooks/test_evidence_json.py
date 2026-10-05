import json
from pathlib import Path

from src.evidence.schema import EvidenceRecord

# Project root se sample JSON file ka path
file_path = Path("data/sample/evidence.json")

with open(file_path, "r") as file:
    records = json.load(file)

validated_records = [
    EvidenceRecord(**record)
    for record in records
]

print(f"Total records loaded: {len(validated_records)}")

for record in validated_records:
    print(record.evidence_id, "-", record.artifact_type, "-", record.source_device)