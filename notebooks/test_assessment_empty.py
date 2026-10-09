
from src.assessment.assessment import assess_case


assessment = assess_case([])

print(assessment.model_dump())

assert assessment.total_claims == 0
assert assessment.supported_claims == 0
assert assessment.contradicted_claims == 0
assert assessment.mixed_claims == 0
assert assessment.insufficient_evidence_claims == 0
assert assessment.results == []

print("Empty assessment test passed!")