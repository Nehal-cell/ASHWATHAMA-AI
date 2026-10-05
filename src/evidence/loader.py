import json
from pathlib import Path

from pydantic import ValidationError
from src.evidence.schema import EvidenceRecord


def load_evidence(file_path: str) -> list[EvidenceRecord]:
    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        raw_records = json.load(file)

    if not isinstance(raw_records, list):
        raise ValueError("Evidence JSON must contain a list of records.")

    validated_records = []

    for index, record in enumerate(raw_records):
        try:
            validated_records.append(EvidenceRecord(**record))
        except ValidationError as error:
            evidence_id = record.get("evidence_id", "UNKNOWN")
            raise ValueError(
                f"Invalid evidence at index {index}, "
                f"evidence_id={evidence_id}: {error}"
            ) from error

    return validated_records