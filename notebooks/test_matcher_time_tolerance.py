from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.matcher import _event_matches_claim_window, match_claim_to_evidence


def test_matcher_accepts_small_time_difference():
    claim = Claim(
        claim_id="CL_TOL_001",
        statement_id="ST_TOL_001",
        subject="the person",
        action="arrived",
        start_time=datetime(2026, 1, 15, 19, 0),
        location="office",
        description="The person arrived at the office at 7 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_TOL_001",
            evidence_id="EV_TOL_001",
            source_device="phone",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 19, 4),
            description="Phone location indicates office.",
            source_tool="synthetic_test",
            reliability=0.8,
            metadata={"location": "office"},
        )
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "SUPPORTED"
    assert result.evidence_id == "EV_TOL_001"


def test_matcher_rejects_time_difference_beyond_tolerance():
    claim = Claim(
        claim_id="CL_TOL_002",
        statement_id="ST_TOL_002",
        subject="the person",
        action="arrived",
        start_time=datetime(2026, 1, 15, 19, 0),
        location="office",
        description="The person arrived at the office at 7 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_TOL_002",
            evidence_id="EV_TOL_002",
            source_device="phone",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 19, 6),
            description="Phone location indicates office.",
            source_tool="synthetic_test",
            reliability=0.8,
            metadata={"location": "office"},
        )
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "INSUFFICIENT_EVIDENCE"

def test_event_matches_claim_window():
    claim = Claim(
        claim_id="CL_WINDOW_001",
        statement_id="ST_WINDOW_001",
        subject="the person",
        action="stayed",
        start_time=datetime(2026, 1, 15, 19, 0),
        end_time=datetime(2026, 1, 15, 21, 0),
        location="office",
        description="The person stayed at the office from 7 PM until 9 PM.",
    )

    evidence_inside = EvidenceRecord(
        case_id="CASE_WINDOW_001",
        evidence_id="EV_WINDOW_001",
        source_device="phone",
        artifact_type="location_event",
        event_time=datetime(2026, 1, 15, 20, 0),
        description="Phone location indicates office.",
        source_tool="synthetic_test",
        reliability=0.8,
        metadata={"location": "office"},
    )

    assert _event_matches_claim_window(
        claim,
        evidence_inside.event_time,
    )

def test_event_outside_claim_window_is_rejected():
    claim = Claim(
        claim_id="CL_WINDOW_002",
        statement_id="ST_WINDOW_002",
        subject="the person",
        action="stayed",
        start_time=datetime(2026, 1, 15, 19, 0),
        end_time=datetime(2026, 1, 15, 21, 0),
        location="office",
        description="The person stayed at the office from 7 PM until 9 PM.",
    )

    evidence_outside = EvidenceRecord(
        case_id="CASE_WINDOW_002",
        evidence_id="EV_WINDOW_002",
        source_device="phone",
        artifact_type="location_event",
        event_time=datetime(2026, 1, 15, 21, 6),
        description="Phone location indicates office.",
        source_tool="synthetic_test",
        reliability=0.8,
        metadata={"location": "office"},
    )

    from src.evidence_matching.matcher import _event_matches_claim_window

    assert not _event_matches_claim_window(
        claim,
        evidence_outside.event_time,
    )

def test_matcher_accepts_evidence_inside_claim_window():
    claim = Claim(
        claim_id="CL_WINDOW_003",
        statement_id="ST_WINDOW_003",
        subject="the person",
        action="stayed",
        start_time=datetime(2026, 1, 15, 19, 0),
        end_time=datetime(2026, 1, 15, 21, 0),
        location="office",
        description="The person stayed at the office from 7 PM until 9 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_WINDOW_003",
            evidence_id="EV_WINDOW_003",
            source_device="phone",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 20, 0),
            description="Phone location indicates office.",
            source_tool="synthetic_test",
            reliability=0.8,
            metadata={"location": "office"},
        )
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "SUPPORTED"
    assert result.evidence_id == "EV_WINDOW_003"

def test_matcher_rejects_evidence_outside_claim_window():
    claim = Claim(
        claim_id="CL_WINDOW_004",
        statement_id="ST_WINDOW_004",
        subject="the person",
        action="stayed",
        start_time=datetime(2026, 1, 15, 19, 0),
        end_time=datetime(2026, 1, 15, 21, 0),
        location="office",
        description="The person stayed at the office from 7 PM until 9 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_WINDOW_004",
            evidence_id="EV_WINDOW_004",
            source_device="phone",
            artifact_type="location_event",
            event_time=datetime(2026, 1, 15, 21, 6),
            description="Phone location indicates office.",
            source_tool="synthetic_test",
            reliability=0.8,
            metadata={"location": "office"},
        )
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "INSUFFICIENT_EVIDENCE"