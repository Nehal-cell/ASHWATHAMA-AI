from src.evidence.loader import load_evidence

records = load_evidence("data/sample/evidence.json")

print(f"Loaded {len(records)} evidence records")

for record in records:
    print(f"\nEvidence ID: {record.evidence_id}")
    print(f"Device: {record.source_device}")
    print(f"Artifact: {record.artifact_type}")
    print(f"Source tool: {record.source_tool}")
    print(f"Collection method: {record.collection_method}")