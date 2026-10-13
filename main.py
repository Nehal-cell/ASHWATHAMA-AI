
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

from src.evidence.schema import EvidenceRecord
from src.assessment.pipeline import run_assessment
from src.assessment.assessment_schema import CaseAssessment


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
    
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Assessment could not be completed due to an internal server error.",
        )

