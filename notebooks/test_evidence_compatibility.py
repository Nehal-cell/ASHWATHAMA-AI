from datetime import datetime

from src.evidence.schema import EvidenceRecord
from src.statement_analysis.claim_schema import Claim
from src.evidence_matching.matcher import match_claim_to_evidence


def test_call_log_does_not_prove_location_claim_by_itself():
    claim = Claim(
        claim_id="CL_COMPAT_001",
        statement_id="ST_COMPAT_001",
        subject="the person",
        action="arrived",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="office",
        description="The person arrived at the office at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_COMPAT_001",
            evidence_id="EV_COMPAT_001",
            source_device="phone",
            artifact_type="call_log",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="An outgoing call was recorded.",
            source_tool="synthetic_test",
            reliability=0.8,
            metadata={"direction": "outgoing"},
        )
    ]

    result = match_claim_to_evidence(claim, evidence)

    assert result.status == "INSUFFICIENT_EVIDENCE"

def test_file_activity_without_location_does_not_prove_location_claim():
    claim = Claim(
        claim_id="CL_COMPAT_002",
        statement_id="ST_COMPAT_002",
        subject="the person",
        action="arrived",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="office",
        description="The person arrived at the office at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_COMPAT_002",
            evidence_id="EV_COMPAT_002",
            source_device="laptop",
            artifact_type="file_activity",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="A document was opened.",
            source_tool="synthetic_test",
            reliability=0.8,
            metadata={"file_name": "report.pdf"},
        )
    ]

    result = match_claim_to_evidence(claim, evidence)

    assert result.status == "INSUFFICIENT_EVIDENCE"

def test_evidence_with_matching_location_supports_location_claim():
    claim = Claim(
        claim_id="CL_COMPAT_003",
        statement_id="ST_COMPAT_003",
        subject="the person",
        action="arrived",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="office",
        description="The person arrived at the office at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_COMPAT_003",
            evidence_id="EV_COMPAT_003",
            source_device="phone",
            artifact_type="location_record",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="A location record places the device at the office.",
            source_tool="synthetic_test",
            reliability=0.9,
            metadata={"location": "office"},
        )
    ]

    result = match_claim_to_evidence(claim, evidence)

    assert result.status == "SUPPORTED"
    assert result.evidence_id == "EV_COMPAT_003"

def test_file_activity_can_support_digital_activity_claim():
    claim = Claim(
        claim_id="CL_COMPAT_004",
        statement_id="ST_COMPAT_004",
        subject="the person",
        action="opened",
        start_time=datetime(2026, 1, 15, 18, 30),
        location=None,
        description="The person opened a document at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_COMPAT_004",
            evidence_id="EV_COMPAT_004",
            source_device="laptop",
            artifact_type="file_activity",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="A document was opened on the laptop.",
            source_tool="synthetic_test",
            reliability=0.9,
            metadata={"file_name": "report.pdf"},
        )
    ]

    result = match_claim_to_evidence(claim, evidence)

    assert result.status == "SUPPORTED"
    assert result.evidence_id == "EV_COMPAT_004"


def test_file_activity_with_different_location_does_not_contradict_location_claim():
    claim = Claim(
        claim_id="CL_COMPAT_005",
        statement_id="ST_COMPAT_005",
        subject="the person",
        action="arrived",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="office",
        description="The person arrived at the office at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_COMPAT_005",
            evidence_id="EV_COMPAT_005",
            source_device="laptop",
            artifact_type="file_activity",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="A document was opened on the laptop.",
            source_tool="synthetic_test",
            reliability=0.9,
            metadata={"location": "home", "file_name": "report.pdf"},
        )
    ]

    result = match_claim_to_evidence(claim, evidence)

    assert result.status == "INSUFFICIENT_EVIDENCE"


def test_unknown_artifact_does_not_automatically_support_claim():
    claim = Claim(
        claim_id="CL_UNKNOWN",
        statement_id="STMT_UNKNOWN",
        subject="person",
        action="left",
        start_time=datetime(2026, 1, 15, 18, 30),
        location="home",
        description="The person stated that they left home at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_UNKNOWN",
            evidence_id="EV_UNKNOWN",
            source_device="unknown_device",
            artifact_type="unknown_artifact",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="An artifact with no established connection to the claim.",
            source_tool="synthetic_test",
            metadata={},
        )
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "INSUFFICIENT_EVIDENCE"


def test_unknown_artifact_does_not_support_opened_claim():
    claim = Claim(
        claim_id="CL_OPEN_UNKNOWN",
        statement_id="ST_OPEN_UNKNOWN",
        subject="the person",
        action="opened",
        start_time=datetime(2026, 1, 15, 18, 30),
        description="The person opened a file at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_OPEN_UNKNOWN",
            evidence_id="EV_OPEN_UNKNOWN",
            source_device="unknown_device",
            artifact_type="unknown_artifact",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="An artifact with no established connection to file activity.",
            source_tool="synthetic_test",
            metadata={},
        )
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "INSUFFICIENT_EVIDENCE"


def test_file_modification_does_not_support_opened_claim():
    claim = Claim(
        claim_id="CL_OPEN_MODIFIED",
        statement_id="ST_OPEN_MODIFIED",
        subject="the person",
        action="opened",
        start_time=datetime(2026, 1, 15, 18, 30),
        description="The person opened a document at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_OPEN_MODIFIED",
            evidence_id="EV_MODIFIED",
            source_device="laptop",
            artifact_type="file_activity",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="A document was modified on the laptop.",
            source_tool="synthetic_test",
            metadata={
                "file_name": "report.pdf",
                "action": "modified",
            },
        )
    ]

    result = match_claim_to_evidence(
        claim=claim,
        evidence=evidence,
    )

    assert result.status == "INSUFFICIENT_EVIDENCE"


def test_different_file_does_not_support_digital_activity_claim():
    claim = Claim(
        claim_id="CL_FILE_MISMATCH",
        statement_id="ST_FILE_MISMATCH",
        subject="the person",
        action="opened",
        start_time=datetime(2026, 1, 15, 18, 30),
        object="report.pdf",
        description="The person opened report.pdf at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_FILE_MISMATCH",
            evidence_id="EV_FILE_MISMATCH",
            source_device="laptop",
            artifact_type="file_activity",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="A document was opened on the laptop.",
            source_tool="synthetic_test",
            reliability=0.9,
            metadata={
                "file_name": "notes.pdf",
                "action": "opened",
            },
        )
    ]

    result = match_claim_to_evidence(claim, evidence)

    assert result.status == "INSUFFICIENT_EVIDENCE"


def test_missing_file_name_does_not_support_specific_file_claim():
    claim = Claim(
        claim_id="CL_MISSING_FILE_NAME",
        statement_id="ST_MISSING_FILE_NAME",
        subject="the person",
        action="opened",
        start_time=datetime(2026, 1, 15, 18, 30),
        object="report.pdf",
        description="The person opened report.pdf at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_MISSING_FILE_NAME",
            evidence_id="EV_MISSING_FILE_NAME",
            source_device="laptop",
            artifact_type="file_activity",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="A document was opened on the laptop.",
            source_tool="synthetic_test",
            reliability=0.9,
            metadata={"action": "opened"},
        )
    ]

    result = match_claim_to_evidence(claim, evidence)

    assert result.status == "INSUFFICIENT_EVIDENCE"


def test_matching_file_name_supports_specific_file_claim():
    claim = Claim(
        claim_id="CL_MATCHING_FILE",
        statement_id="ST_MATCHING_FILE",
        subject="the person",
        action="opened",
        start_time=datetime(2026, 1, 15, 18, 30),
        object="report.pdf",
        description="The person opened report.pdf at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_MATCHING_FILE",
            evidence_id="EV_MATCHING_FILE",
            source_device="laptop",
            artifact_type="file_activity",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="A document was opened on the laptop.",
            source_tool="synthetic_test",
            reliability=0.9,
            metadata={
                "file_name": "report.pdf",
                "action": "opened",
            },
        )
    ]

    result = match_claim_to_evidence(claim, evidence)

    assert result.status == "SUPPORTED"
    assert result.evidence_id == "EV_MATCHING_FILE"


def test_digital_action_matching_ignores_case_and_extra_spaces():
    claim = Claim(
        claim_id="CL_ACTION_NORMALIZATION",
        statement_id="ST_ACTION_NORMALIZATION",
        subject="the person",
        action="opened",
        start_time=datetime(2026, 1, 15, 18, 30),
        object="report.pdf",
        description="The person opened report.pdf at 6:30 PM.",
    )

    evidence = [
        EvidenceRecord(
            case_id="CASE_ACTION_NORMALIZATION",
            evidence_id="EV_ACTION_NORMALIZATION",
            source_device="laptop",
            artifact_type="file_activity",
            event_time=datetime(2026, 1, 15, 18, 30),
            description="A document was opened on the laptop.",
            source_tool="synthetic_test",
            reliability=0.9,
            metadata={
                "file_name": "REPORT.PDF",
                "action": " Opened ",
            },
        )
    ]

    result = match_claim_to_evidence(claim, evidence)

    assert result.status == "SUPPORTED"
    assert result.evidence_id == "EV_ACTION_NORMALIZATION"
