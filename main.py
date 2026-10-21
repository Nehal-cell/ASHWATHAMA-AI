from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from src.evidence.schema import EvidenceRecord
from src.assessment.pipeline import run_assessment
from src.assessment.assessment_schema import CaseAssessment
from src.chatbot.chat_service import generate_chat_response
from src.chatbot.forensic_tools import analyze_case_timeline


app = FastAPI(
    title="ASHWATHAMA AI",
    description=(
        "A digital forensics prototype for comparing "
        "statement claims with available evidence."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class AssessmentRequest(BaseModel):
    statement_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    evidence: list[EvidenceRecord] = Field(min_length=1)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    assessment: dict[str, Any] | None = None
    case_id: str | None = Field(default=None, min_length=1, max_length=100)
    evidence: list[EvidenceRecord] | None = None

@app.get("/")
def home():
    return {
        "project": "ASHWATHAMA AI",
        "status": "running",
        "message": "Digital forensics assessment API is ready.",
    }


@app.post(
    "/assess",
    response_model=CaseAssessment,
)
def assess(request: AssessmentRequest):
    try:
        return run_assessment(
            statement_id=request.statement_id,
            statement=request.statement,
            evidence=request.evidence,
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=(
                "Assessment could not be completed "
                "due to an internal server error."
            ),
        ) from None


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        tool_result = None

        if request.case_id is not None:
            if request.evidence is None:
                raise HTTPException(
                    status_code=400,
                    detail="Evidence records are required for timeline analysis.",
                )

            tool_result = analyze_case_timeline(
                records=request.evidence,
                case_id=request.case_id,
            )
        answer = generate_chat_response(
            question=request.question,
            assessment=request.assessment,
            tool_result=tool_result,
        )

        return {"answer": answer}

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from None

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from None
