
from typing import List

from src.assessment.assessment_schema import CaseAssessment
from src.evidence_matching.match_schema import MatchResult


def assess_case(results: List[MatchResult]) -> CaseAssessment:
    supported = sum(
        result.status == "SUPPORTED" for result in results
    )
    contradicted = sum(
        result.status == "CONTRADICTED" for result in results
    )
    mixed = sum(
        result.status == "MIXED" for result in results
    )
    insufficient = sum(
        result.status == "INSUFFICIENT_EVIDENCE"
        for result in results
    )

    total = len(results)

    summary = (
        f"Assessed {total} claim(s): "
        f"{supported} supported, "
        f"{contradicted} contradicted, "
        f"{mixed} mixed, and "
        f"{insufficient} with insufficient evidence."
    )

    return CaseAssessment(
        total_claims=total,
        supported_claims=supported,
        contradicted_claims=contradicted,
        mixed_claims=mixed,
        insufficient_evidence_claims=insufficient,
        results=results,
        summary=summary,
    )