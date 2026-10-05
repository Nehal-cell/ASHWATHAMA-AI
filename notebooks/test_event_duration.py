from src.evidence.loader import load_evidence
from src.timeline_analysis.timeline import get_event_end_time


evidence = load_evidence("data/sample/evidence.json")

for record in evidence:
    end_time = get_event_end_time(record)

    print(
        f"{record.evidence_id} | "
        f"Start: {record.event_time} | "
        f"End: {end_time}"
    )