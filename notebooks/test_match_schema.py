from src.evidence_matching.match_schema import MatchResult


result = MatchResult(
    claim_id="CL_001",
    evidence_id="EV_001",
    status="SUPPORTED",
    confidence=0.85,
    reason="The evidence is consistent with the claimed time and activity.",
)


print("Match result created successfully:")
print(result.model_dump())