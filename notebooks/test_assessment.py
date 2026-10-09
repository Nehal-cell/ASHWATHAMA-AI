
from src.assessment.assessment import assess_case
from src.evidence_matching.match_schema import MatchResult


results = [
    MatchResult(
        claim_id="CL_001",
        evidence_id="EV_001",
        status="SUPPORTED",
        confidence=0.8,
        reason="Evidence is consistent with the claim."
    ),
    MatchResult(
        claim_id="CL_002",
        evidence_id="EV_002",
        status="CONTRADICTED",
        confidence=0.7,
        reason="Evidence conflicts with the claim."
    ),
    MatchResult(
        claim_id="CL_003",
        status="INSUFFICIENT_EVIDENCE",
        confidence=None,
        reason="Not enough evidence to assess this claim."
    ),
    MatchResult(
        claim_id="CL_004",
        evidence_id="EV_004",
        status="MIXED",
        confidence=0.5,
        reason="Available evidence is conflicting."
    ),
]

assessment = assess_case(results)

print(assessment.model_dump())