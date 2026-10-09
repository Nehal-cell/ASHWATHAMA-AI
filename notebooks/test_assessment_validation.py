
from pydantic import ValidationError

from src.assessment.assessment_schema import CaseAssessment
from src.evidence_matching.match_schema import MatchResult


result = MatchResult(
    claim_id="CL_001",
    status="SUPPORTED",
    confidence=0.8,
    reason="Evidence is consistent with the claim."
)

try:
    CaseAssessment(
        total_claims=1,
        supported_claims=0,
        contradicted_claims=0,
        mixed_claims=0,
        insufficient_evidence_claims=0,
        results=[result],
        summary="Test assessment"
    )
except ValidationError:
    print("Invalid assessment rejected successfully!")
else:
    raise AssertionError("Invalid assessment was not rejected!")