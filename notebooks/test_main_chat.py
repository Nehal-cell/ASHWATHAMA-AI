from fastapi.testclient import TestClient

import main


client = TestClient(main.app)


def test_chat_endpoint_returns_answer(monkeypatch):
    def fake_generate_chat_response(question, assessment=None):
        assert question == "What is digital forensics?"
        assert assessment is None
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

    def fake_generate_chat_response(question, assessment=None):
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