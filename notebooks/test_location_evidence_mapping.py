
from datetime import datetime, timezone

from src.evidence.schema import EvidenceRecord
from src.evidence.location_history_parser import (
    convert_location_records_to_evidence,
)
import json

from src.evidence.location_history_parser import (
    extract_location_records,
    normalize_location_timestamps,
)

def test_gps_point_maps_to_evidence_record():
    gps_point = {
        "timestamp": "2026-01-15T10:00:00Z",
        "event_time": datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
        "latitude": 28.6,
        "longitude": 77.2,
        "source": "raw_position",
        "accuracy_meters": 12.5,
        "altitude_meters": 210.0,
        "speed_meters_per_second": 1.5,
        "original_source": "GPS",
    }

    evidence = EvidenceRecord(
        case_id="CASE_TEST_001",
        evidence_id="GPS_TEST_001",
        source_device="Google Maps Timeline",
        artifact_type="location_record",
        event_time=gps_point["event_time"],
        description="GPS location point from imported timeline",
        source_tool="Google Maps Timeline Parser",
        reliability=None,
        metadata={
            "latitude": gps_point["latitude"],
            "longitude": gps_point["longitude"],
            "accuracy_meters": gps_point["accuracy_meters"],
            "altitude_meters": gps_point["altitude_meters"],
            "speed_meters_per_second": gps_point[
                "speed_meters_per_second"
            ],
            "original_source": gps_point["original_source"],
            "timestamp_original": gps_point["timestamp"],
        },
        source_reference="synthetic_test_data",
        collection_method="JSON import",
    )

    assert evidence.artifact_type == "location_record"
    assert evidence.event_time == gps_point["event_time"]
    assert evidence.metadata["latitude"] == 28.6
    assert evidence.metadata["longitude"] == 77.2
    assert evidence.metadata["accuracy_meters"] == 12.5
    assert evidence.reliability is None


def test_convert_location_records_to_evidence():
    records = [
        {
            "timestamp": "2026-01-15T10:00:00Z",
            "event_time": datetime(
                2026, 1, 15, 10, 0, tzinfo=timezone.utc
            ),
            "latitude": 28.6,
            "longitude": 77.2,
            "source": "raw_position",
            "accuracy_meters": 12.5,
            "altitude_meters": 210.0,
            "speed_meters_per_second": 1.5,
            "original_source": "GPS",
        },
        {
            "timestamp": "invalid",
            "latitude": 28.7,
            "longitude": 77.3,
            "source": "timelinePath",
        },
    ]

    evidence_records = convert_location_records_to_evidence(
        records,
        case_id="CASE_TEST_001",
    )

    assert len(evidence_records) == 1

    evidence = evidence_records[0]

    assert isinstance(evidence, EvidenceRecord)
    assert evidence.case_id == "CASE_TEST_001"
    assert evidence.evidence_id == "GPS_000001"
    assert evidence.artifact_type == "location_record"
    assert evidence.event_time == records[0]["event_time"]
    assert evidence.metadata["latitude"] == 28.6
    assert evidence.metadata["longitude"] == 77.2
    assert evidence.metadata["accuracy_meters"] == 12.5
    assert evidence.metadata["altitude_meters"] == 210.0
    assert evidence.metadata["speed_meters_per_second"] == 1.5
    assert evidence.metadata["original_source"] == "GPS"
    assert evidence.reliability is None


def test_timeline_json_to_evidence_end_to_end(tmp_path):
    timeline_data = {
        "semanticSegments": [
            {
                "timelinePath": [
                    {
                        "point": "geo:28.6,77.2",
                        "time": "2026-01-15T10:00:00Z",
                    }
                ]
            }
        ],
        "rawSignals": [],
    }

    json_path = tmp_path / "synthetic_timeline.json"
    json_path.write_text(
        json.dumps(timeline_data),
        encoding="utf-8",
    )

    extracted = extract_location_records(json_path)
    normalized = normalize_location_timestamps(extracted)
    evidence_records = convert_location_records_to_evidence(
        normalized,
        case_id="CASE_E2E_001",
    )

    assert len(evidence_records) == 1

    evidence = evidence_records[0]

    assert isinstance(evidence, EvidenceRecord)
    assert evidence.case_id == "CASE_E2E_001"
    assert evidence.artifact_type == "location_record"
    assert evidence.event_time == datetime(
        2026, 1, 15, 10, 0, tzinfo=timezone.utc
    )
    assert evidence.metadata["latitude"] == 28.6
    assert evidence.metadata["longitude"] == 77.2
