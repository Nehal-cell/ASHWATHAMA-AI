
from src.assessment.assessment_schema import CaseAssessment
from src.evidence_matching.match_schema import MatchResult


result = MatchResult(
    claim_id="CL_001",
    evidence_id="EV_001",
    status="SUPPORTED",
    confidence=0.8,
    reason="Evidence is consistent with the claim's time."
)

assessment = CaseAssessment(
    total_claims=1,
    supported_claims=1,
    contradicted_claims=0,
    mixed_claims=0,
    insufficient_evidence_claims=0,
    results=[result],
    summary="One claim was supported by the available evidence."
)

print(assessment.model_dump())