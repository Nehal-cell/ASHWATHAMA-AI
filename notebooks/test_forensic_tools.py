from datetime import datetime

import pytest

from src.chatbot.forensic_tools import analyze_case_timeline
from src.evidence.schema import EvidenceRecord


def make_evidence(
    evidence_id: str,
    case_id: str,
    event_time: str,
    description: str = "Synthetic test event",
    metadata: dict | None = None,
) -> EvidenceRecord:
    return EvidenceRecord(
        case_id=case_id,
        evidence_id=evidence_id,
        source_device="test_device",
        artifact_type="test_event",
        event_time=datetime.fromisoformat(event_time),
        description=description,
        source_tool="synthetic_test",
        reliability=0.9,
        metadata=metadata or {},
    )


def test_analyze_case_timeline_sorts_events_and_filters_case():
    records = [
        make_evidence(
            "EV_003",
            "CASE_A",
            "2026-01-15T20:00:00",
        ),
        make_evidence(
            "EV_001",
            "CASE_A",
            "2026-01-15T18:00:00",
        ),
        make_evidence(
            "EV_002",
            "CASE_B",
            "2026-01-15T19:00:00",
        ),
    ]

    result = analyze_case_timeline(records, "CASE_A")

    assert result["case_id"] == "CASE_A"
    assert result["event_count"] == 2
    assert [
        event["evidence_id"] for event in result["timeline"]
    ] == ["EV_001", "EV_003"]


def test_analyze_case_timeline_reports_gap():
    records = [
        make_evidence(
            "EV_001",
            "CASE_A",
            "2026-01-15T18:00:00",
        ),
        make_evidence(
            "EV_002",
            "CASE_A",
            "2026-01-15T19:00:00",
        ),
    ]

    result = analyze_case_timeline(records, "CASE_A")

    assert result["gap_count"] == 1
    assert result["gaps"][0]["duration_seconds"] == 3600


def test_analyze_case_timeline_reports_overlapping_events():
    records = [
        make_evidence(
            "EV_001",
            "CASE_A",
            "2026-01-15T18:00:00",
            metadata={"duration_seconds": 3600},
        ),
        make_evidence(
            "EV_002",
            "CASE_A",
            "2026-01-15T18:30:00",
            metadata={"duration_seconds": 600},
        ),
    ]

    result = analyze_case_timeline(records, "CASE_A")

    assert result["overlap_count"] == 1
    assert result["overlaps"][0]["first_evidence_id"] == "EV_001"
    assert result["overlaps"][0]["second_evidence_id"] == "EV_002"


def test_analyze_case_timeline_returns_empty_result_for_unknown_case():
    records = [
        make_evidence(
            "EV_001",
            "CASE_A",
            "2026-01-15T18:00:00",
        ),
    ]

    result = analyze_case_timeline(records, "CASE_UNKNOWN")

    assert result["event_count"] == 0
    assert result["timeline"] == []
    assert result["gap_count"] == 0
    assert result["overlap_count"] == 0


def test_analyze_case_timeline_rejects_empty_case_id():
    with pytest.raises(ValueError, match="case_id cannot be empty"):
        analyze_case_timeline([], "   ")