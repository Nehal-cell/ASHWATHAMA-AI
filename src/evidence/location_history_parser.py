
import json
import re
from pathlib import Path
from datetime import datetime
from src.evidence.schema import EvidenceRecord


def _extract_coordinates(value):
    """Extract latitude and longitude from a Google Timeline location string."""
    if not isinstance(value, str):
        return None, None

    numbers = re.findall(r"[-+]?\d+(?:\.\d+)?", value)

    if len(numbers) < 2:
        return None, None

    latitude, longitude = float(numbers[0]), float(numbers[1])

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None, None

    return latitude, longitude


def extract_location_records(json_path):
    """Read Google Timeline JSON and return normalized location records."""
    path = Path(json_path)

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    records = []

    # Extract path points from semantic timeline segments.
    for segment in data.get("semanticSegments", []):
        for point in segment.get("timelinePath", []):
            latitude, longitude = _extract_coordinates(point.get("point"))

            if latitude is None:
                continue

            records.append({
                "timestamp": point.get("time"),
                "latitude": latitude,
                "longitude": longitude,
                "source": "timelinePath",
            })

    
    # Extract raw GPS position signals.
    for signal in data.get("rawSignals", []):
        position = signal.get("position")

        if not isinstance(position, dict):
            continue

        latitude, longitude = _extract_coordinates(
            position.get("LatLng")
        )

        if latitude is None:
            continue

        records.append({
            "timestamp": position.get("timestamp"),
            "latitude": latitude,
            "longitude": longitude,
            "source": "raw_position",
            "accuracy_meters": position.get("accuracyMeters"),
            "altitude_meters": position.get("altitudeMeters"),
            "speed_meters_per_second": position.get(
                "speedMetersPerSecond"
            ),
            "original_source": position.get("source"),
        })


    return records


def summarize_location_records(records):
    """Return counts only; do not print personal location details."""
    timestamps = [
        record["timestamp"]
        for record in records
        if record.get("timestamp")
    ]

    return {
        "total_records": len(records),
        "timeline_path_records": sum(
            record["source"] == "timelinePath" for record in records
        ),
        "raw_position_records": sum(
            record["source"] == "raw_position" for record in records
        ),
        "records_with_timestamp": len(timestamps),
        "records_without_timestamp": len(records) - len(timestamps),
    }


def validate_location_timestamps(records):
    """Validate timestamps without printing personal location information."""
    from datetime import datetime

    valid_count = 0
    invalid_count = 0

    for record in records:
        timestamp = record.get("timestamp")

        if not isinstance(timestamp, str) or not timestamp.strip():
            invalid_count += 1
            continue

        try:
            # Google Timeline timestamps commonly use ISO 8601.
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            valid_count += 1
        except ValueError:
            invalid_count += 1

    return {
        "total_records": len(records),
        "valid_timestamps": valid_count,
        "invalid_or_missing_timestamps": invalid_count,
    }

def normalize_location_timestamps(records):
    """Convert valid ISO timestamps to Python datetime objects."""
    from datetime import datetime

    normalized = []

    for record in records:
        timestamp = record.get("timestamp")

        try:
            event_time = datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            )
        except (AttributeError, ValueError):
            continue

        normalized.append({
            **record,
            "event_time": event_time,
        })

    return normalized


def summarize_duplicate_location_points(records):
    """Count exact duplicate points without removing any records."""
    from collections import Counter

    keys = [
        (
            record.get("timestamp"),
            record.get("latitude"),
            record.get("longitude"),
        )
        for record in records
    ]

    counts = Counter(keys)
    duplicate_groups = sum(count > 1 for count in counts.values())
    duplicate_excess_records = sum(
        count - 1 for count in counts.values() if count > 1
    )

    return {
        "total_records": len(records),
        "unique_points": len(counts),
        "duplicate_groups": duplicate_groups,
        "duplicate_excess_records": duplicate_excess_records,
    }


def summarize_timestamp_timezones(records):
    """Count timezone-aware and timezone-naive normalized timestamps."""
    from datetime import datetime

    aware = 0
    naive = 0
    missing_or_invalid = 0

    for record in records:
        event_time = record.get("event_time")

        if not isinstance(event_time, datetime):
            missing_or_invalid += 1
        elif (
            event_time.tzinfo is not None
            and event_time.utcoffset() is not None
        ):
            aware += 1
        else:
            naive += 1

    return {
        "total_records": len(records),
        "timezone_aware": aware,
        "timezone_naive": naive,
        "missing_or_invalid": missing_or_invalid,
    }


def convert_location_records_to_evidence(
    records,
    case_id: str,
) -> list[EvidenceRecord]:
    """Convert normalized location records into EvidenceRecord objects."""
    evidence_records = []

    for index, record in enumerate(records, start=1):
        event_time = record.get("event_time")

        if not isinstance(event_time, datetime):
            continue

        latitude = record.get("latitude")
        longitude = record.get("longitude")

        if latitude is None or longitude is None:
            continue

        evidence = EvidenceRecord(
            case_id=case_id,
            evidence_id=f"GPS_{index:06d}",
            source_device="Google Maps Timeline",
            artifact_type="location_record",
            event_time=event_time,
            description="Location point imported from Google Maps Timeline",
            source_tool="Google Maps Timeline Parser",
            reliability=None,
            metadata={
                "latitude": latitude,
                "longitude": longitude,
                "source": record.get("source"),
                "accuracy_meters": record.get("accuracy_meters"),
                "altitude_meters": record.get("altitude_meters"),
                "speed_meters_per_second": record.get(
                    "speed_meters_per_second"
                ),
                "original_source": record.get("original_source"),
                "timestamp_original": record.get("timestamp"),
            },
            source_reference="Google Maps Timeline JSON",
            collection_method="JSON import",
        )

        evidence_records.append(evidence)

    return evidence_records
