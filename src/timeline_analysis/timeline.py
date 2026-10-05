from datetime import datetime, timedelta
from src.evidence.schema import EvidenceRecord


def build_timeline(records: list[EvidenceRecord]) -> list[EvidenceRecord]:
    """
    Sort evidence records chronologically.
    """
    return sorted(records, key=lambda record: record.event_time)


def build_case_timeline(
    records: list[EvidenceRecord],
    case_id: str,
) -> list[EvidenceRecord]:
    """
    Filter evidence for a specific case and sort it chronologically.
    """
    case_records = [
        record
        for record in records
        if record.case_id == case_id
    ]

    return build_timeline(case_records)




def get_event_end_time(record: EvidenceRecord) -> datetime:
    """
    Return the estimated end time of an event.

    If duration_seconds exists in metadata, use it.
    Otherwise, treat the event as a point-in-time event.
    """
    duration = record.metadata.get("duration_seconds", 0)

    if not isinstance(duration, (int, float)) or duration < 0:
        duration = 0

    return record.event_time + timedelta(seconds=duration)

def find_overlapping_events(
    records: list[EvidenceRecord],
) -> list[tuple[EvidenceRecord, EvidenceRecord]]:
    """
    Find pairs of evidence events whose time windows overlap.
    """

    overlaps = []

    timeline = build_timeline(records)

    for index, current in enumerate(timeline):
        current_end = get_event_end_time(current)

        for next_record in timeline[index + 1:]:
            next_start = next_record.event_time

            # Since timeline is sorted, no later events can overlap
            # once their start time is after the current event's end.
            if next_start > current_end:
                break

            next_end = get_event_end_time(next_record)

            if next_start < current_end and current.event_time < next_end:
                overlaps.append((current, next_record))

    return overlaps

def find_timeline_gaps(
    records: list[EvidenceRecord],
) -> list[tuple[datetime, datetime, float]]:
    """
    Find gaps between consecutive evidence events.

    Returns:
        A list containing:
        (gap_start, gap_end, gap_duration_seconds)
    """

    if len(records) < 2:
        return []

    timeline = build_timeline(records)
    gaps = []

    for current, next_record in zip(timeline, timeline[1:]):
        current_end = get_event_end_time(current)
        next_start = next_record.event_time

        if next_start > current_end:
            gap_duration = (
                next_start - current_end
            ).total_seconds()

            gaps.append(
                (
                    current_end,
                    next_start,
                    gap_duration,
                )
            )

    return gaps