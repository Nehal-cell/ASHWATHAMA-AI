
from datetime import datetime, timezone

from src.evidence.location_history_parser import (
    normalize_location_timestamps,
    summarize_duplicate_location_points,
    summarize_timestamp_timezones,
    validate_location_timestamps,
)


def test_validate_location_timestamps():
    records = [
        {"timestamp": "2026-01-15T10:00:00Z"},
        {"timestamp": "2026-01-15T11:00:00+05:30"},
        {"timestamp": "not-a-timestamp"},
        {"timestamp": None},
    ]

    result = validate_location_timestamps(records)

    assert result == {
        "total_records": 4,
        "valid_timestamps": 2,
        "invalid_or_missing_timestamps": 2,
    }


def test_normalize_location_timestamps():
    records = [
        {
            "timestamp": "2026-01-15T10:00:00Z",
            "latitude": 28.6,
            "longitude": 77.2,
            "source": "timelinePath",
        },
        {"timestamp": "invalid"},
    ]

    result = normalize_location_timestamps(records)

    assert len(result) == 1
    assert isinstance(result[0]["event_time"], datetime)
    assert result[0]["event_time"].utcoffset().total_seconds() == 0
    assert result[0]["latitude"] == 28.6
    assert result[0]["longitude"] == 77.2


def test_summarize_duplicate_location_points():
    records = [
        {
            "timestamp": "2026-01-15T10:00:00Z",
            "latitude": 28.6,
            "longitude": 77.2,
        },
        {
            "timestamp": "2026-01-15T10:00:00Z",
            "latitude": 28.6,
            "longitude": 77.2,
        },
        {
            "timestamp": "2026-01-15T10:01:00Z",
            "latitude": 28.6,
            "longitude": 77.2,
        },
    ]

    result = summarize_duplicate_location_points(records)

    assert result == {
        "total_records": 3,
        "unique_points": 2,
        "duplicate_groups": 1,
        "duplicate_excess_records": 1,
    }

    # Duplicate detection must not delete or mutate records.
    assert len(records) == 3


def test_summarize_timestamp_timezones():
    records = [
        {"event_time": datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc)},
        {"event_time": datetime(2026, 1, 15, 10, 0)},
        {"event_time": "not-a-datetime"},
        {},
    ]

    result = summarize_timestamp_timezones(records)

    assert result == {
        "total_records": 4,
        "timezone_aware": 1,
        "timezone_naive": 1,
        "missing_or_invalid": 2,
    }


def test_extract_raw_position_metadata(tmp_path):
    import json

    from src.evidence.location_history_parser import extract_location_records

    timeline_data = {
        "semanticSegments": [],
        "rawSignals": [
            {
                "position": {
                    "LatLng": "geo:28.6,77.2",
                    "timestamp": "2026-01-15T10:00:00Z",
                    "accuracyMeters": 12.5,
                    "altitudeMeters": 210.0,
                    "speedMetersPerSecond": 1.5,
                    "source": "GPS",
                }
            }
        ],
    }

    json_path = tmp_path / "timeline_test.json"
    json_path.write_text(json.dumps(timeline_data), encoding="utf-8")

    records = extract_location_records(json_path)

    assert len(records) == 1
    assert records[0]["accuracy_meters"] == 12.5
    assert records[0]["altitude_meters"] == 210.0
    assert records[0]["speed_meters_per_second"] == 1.5
    assert records[0]["original_source"] == "GPS"
