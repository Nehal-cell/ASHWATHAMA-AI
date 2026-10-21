from datetime import datetime
from typing import Any

from src.evidence.schema import EvidenceRecord
from src.timeline_analysis.timeline import (
    build_case_timeline,
    find_overlapping_events,
    find_timeline_gaps,
    get_event_end_time,
)


def analyze_case_timeline(
    records: list[EvidenceRecord],
    case_id: str,
) -> dict[str, Any]:
    """
    Analyze the timeline for a specific case using supplied evidence.

    This function does not access external files or devices and does
    not modify the supplied evidence records.
    """
    cleaned_case_id = case_id.strip()

    if not cleaned_case_id:
        raise ValueError("case_id cannot be empty.")

    case_records = build_case_timeline(records, cleaned_case_id)

    timeline_events = [
        {
            "evidence_id": record.evidence_id,
            "event_time": record.event_time.isoformat(),
            "estimated_end_time": get_event_end_time(record).isoformat(),
            "source_device": record.source_device,
            "artifact_type": record.artifact_type,
            "description": record.description,
            "source_tool": record.source_tool,
            "reliability": record.reliability,
        }
        for record in case_records
    ]

    gaps = find_timeline_gaps(case_records)
    overlaps = find_overlapping_events(case_records)

    gap_results = [
        {
            "gap_start": gap_start.isoformat(),
            "gap_end": gap_end.isoformat(),
            "duration_seconds": duration_seconds,
        }
        for gap_start, gap_end, duration_seconds in gaps
    ]

    overlap_results = [
        {
            "first_evidence_id": first.evidence_id,
            "second_evidence_id": second.evidence_id,
            "first_event_time": first.event_time.isoformat(),
            "second_event_time": second.event_time.isoformat(),
        }
        for first, second in overlaps
    ]

    return {
        "case_id": cleaned_case_id,
        "event_count": len(timeline_events),
        "timeline": timeline_events,
        "gap_count": len(gap_results),
        "gaps": gap_results,
        "overlap_count": len(overlap_results),
        "overlaps": overlap_results,
        "limitations": [
            "Analysis uses only the evidence records supplied to this function.",
            "A timeline gap does not establish that an event occurred.",
            "Overlapping timestamps do not, by themselves, indicate wrongdoing.",
            "Event end times may be estimated from duration metadata.",
        ],
    }