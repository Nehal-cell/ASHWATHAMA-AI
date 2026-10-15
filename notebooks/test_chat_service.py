from types import SimpleNamespace

import pytest

import src.chatbot.chat_service as chat_service
from src.chatbot.chat_service import (
    build_system_instruction,
    build_chat_context,
    generate_chat_response,
)


def test_system_instruction_has_forensic_safety_rules():
    instruction = build_system_instruction()

    assert "digital forensics" in instruction.lower()
    assert "Never invent evidence" in instruction
    assert "Never modify or delete forensic evidence" in instruction


def test_build_chat_context_strips_question_whitespace():
    context = build_chat_context("  What does this evidence show?  ")

    assert context["question"] == "What does this evidence show?"


def test_build_chat_context_includes_assessment():
    assessment = {"supported_claims": 1}

    context = build_chat_context(
        "Explain the result",
        assessment=assessment,
    )

    assert context["assessment"] == assessment


def test_build_chat_context_rejects_empty_question():
    with pytest.raises(ValueError, match="Question cannot be empty"):
        build_chat_context("   ")


def test_generate_chat_response_returns_gemini_text(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")

    class FakeInteractions:
        def create(self, **kwargs):
            assert kwargs["model"] == "gemini-3.5-flash-lite"
            assert "Explain the result" in kwargs["input"]
            assert "Never invent evidence" in kwargs["input"]

            return SimpleNamespace(
                output_text="Evidence supports this claim."
            )

    class FakeClient:
        def __init__(self, api_key):
            assert api_key == "fake-test-key"
            self.interactions = FakeInteractions()

    monkeypatch.setattr(chat_service.genai, "Client", FakeClient)

    result = generate_chat_response("Explain the result")

    assert result == "Evidence supports this claim."


def test_generate_chat_response_handles_api_failure(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "fake-test-key")

    def raise_api_error(**kwargs):
        raise Exception("Simulated API failure with sensitive details")

    class FakeClient:
        def __init__(self, api_key):
            self.interactions = SimpleNamespace(
                create=raise_api_error
            )

    monkeypatch.setattr(chat_service.genai, "Client", FakeClient)

    with pytest.raises(RuntimeError, match="Please retry later") as exc_info:
        generate_chat_response("Explain the result")

    assert "sensitive details" not in str(exc_info.value)


def test_generate_chat_response_rejects_missing_api_key(monkeypatch):
    monkeypatch.setattr(chat_service, "load_dotenv", lambda: None)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY is missing"):
        generate_chat_response("Explain the result")


def test_empty_question_does_not_call_gemini(monkeypatch):
    def unexpected_client(*args, **kwargs):
        raise AssertionError("Gemini client should not be created")

    monkeypatch.setattr(chat_service.genai, "Client", unexpected_client)

    with pytest.raises(ValueError, match="Question cannot be empty"):
        generate_chat_response("   ")