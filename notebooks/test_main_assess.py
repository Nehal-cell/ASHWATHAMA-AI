
from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def make_assessment_request(location_metadata):
    return {
        "statement_id": "STMT_TEST_001",
        "statement": "I was at home at 6:00 PM.",
        "evidence": [
            {
                "case_id": "CASE_TEST_001",
                "evidence_id": "EV_TEST_001",
                "source_device": "test_phone",
                "artifact_type": "location",
                "event_time": "2026-01-15T18:00:00",
                "description": "Synthetic location evidence recorded at 6 PM.",
                "source_tool": "synthetic_test",
                "reliability": 0.95,
                "metadata": location_metadata,
            }
        ],
    }


def test_assess_endpoint_supports_matching_location():
    response = client.post(
        "/assess",
        json=make_assessment_request({"location": "home"}),
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total_claims"] == 1
    assert result["supported_claims"] == 1
    assert result["contradicted_claims"] == 0
    assert result["mixed_claims"] == 0
    assert result["insufficient_evidence_claims"] == 0
    assert result["results"][0]["status"] == "SUPPORTED"
    assert result["results"][0]["confidence"] == 0.95


def test_assess_endpoint_contradicts_different_location():
    response = client.post(
        "/assess",
        json=make_assessment_request({"location": "office"}),
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total_claims"] == 1
    assert result["supported_claims"] == 0
    assert result["contradicted_claims"] == 1
    assert result["mixed_claims"] == 0
    assert result["insufficient_evidence_claims"] == 0
    assert result["results"][0]["status"] == "CONTRADICTED"
    assert result["results"][0]["confidence"] == 0.95


def test_assess_endpoint_returns_insufficient_without_location_metadata():
    response = client.post(
        "/assess",
        json=make_assessment_request({}),
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total_claims"] == 1
    assert result["supported_claims"] == 0
    assert result["contradicted_claims"] == 0
    assert result["mixed_claims"] == 0
    assert result["insufficient_evidence_claims"] == 1
    assert result["results"][0]["status"] == "INSUFFICIENT_EVIDENCE"
    assert result["results"][0]["confidence"] is None


def test_assess_endpoint_rejects_empty_evidence():
    request_data = make_assessment_request({"location": "home"})
    request_data["evidence"] = []

    response = client.post("/assess", json=request_data)

    assert response.status_code == 422


def test_assess_endpoint_rejects_empty_statement():
    request_data = make_assessment_request({"location": "home"})
    request_data["statement"] = ""

    response = client.post("/assess", json=request_data)

    assert response.status_code == 422
