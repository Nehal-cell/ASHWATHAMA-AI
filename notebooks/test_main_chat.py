from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_chat_endpoint_returns_answer(monkeypatch):
    def fake_generate_chat_response(
    question,
    assessment=None,
    tool_result=None,
):
        assert question == "What is digital forensics?"
        assert assessment is None
        assert tool_result is None
        return "Digital forensics examines digital evidence."

    monkeypatch.setattr(
        main,
        "generate_chat_response",
        fake_generate_chat_response,
    )

    response = client.post(
        "/chat",
        json={"question": "What is digital forensics?"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "Digital forensics examines digital evidence."
    }


def test_chat_endpoint_passes_assessment(monkeypatch):
    assessment = {
        "total_claims": 1,
        "supported_claims": 1,
        "contradicted_claims": 0,
        "mixed_claims": 0,
        "insufficient_evidence_claims": 0,
        "results": [],
        "summary": "One claim is supported.",
    }

    def fake_generate_chat_response(
    question,
    assessment=None,
    tool_result=None,
):
        assert assessment == assessment_data
        return "The supplied assessment reports one supported claim."

    assessment_data = assessment

    monkeypatch.setattr(
        main,
        "generate_chat_response",
        fake_generate_chat_response,
    )

    response = client.post(
        "/chat",
        json={
            "question": "Explain this result.",
            "assessment": assessment,
        },
    )

    assert response.status_code == 200
    assert "one supported claim" in response.json()["answer"]


def test_chat_endpoint_rejects_empty_question():
    response = client.post(
        "/chat",
        json={"question": ""},
    )

    assert response.status_code == 422


def test_chat_endpoint_runs_timeline_analysis(monkeypatch):
    expected_tool_result = {
        "case_id": "CASE_A",
        "event_count": 1,
        "timeline": [],
        "gap_count": 0,
        "gaps": [],
        "overlap_count": 0,
        "overlaps": [],
        "limitations": [],
    }

    def fake_analyze_case_timeline(records, case_id):
        assert case_id == "CASE_A"
        assert len(records) == 1
        return expected_tool_result

    def fake_generate_chat_response(
        question,
        assessment=None,
        tool_result=None,
    ):
        assert question == "Analyze CASE_A timeline."
        assert assessment is None
        assert tool_result == expected_tool_result
        return "CASE_A timeline analysis completed."

    monkeypatch.setattr(
        main,
        "analyze_case_timeline",
        fake_analyze_case_timeline,
    )
    monkeypatch.setattr(
        main,
        "generate_chat_response",
        fake_generate_chat_response,
    )

    response = client.post(
        "/chat",
        json={
            "question": "Analyze CASE_A timeline.",
            "case_id": "CASE_A",
            "evidence": [
                {
                    "case_id": "CASE_A",
                    "evidence_id": "EV_001",
                    "source_device": "test_phone",
                    "artifact_type": "call_log",
                    "event_time": "2026-01-15T18:00:00",
                    "description": "Synthetic test event",
                    "source_tool": "synthetic_test",
                    "reliability": 0.9,
                }
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "CASE_A timeline analysis completed."
    }