
from src.evidence.schema import EvidenceRecord
from src.statement_analysis.parser import parse_statement_text
from src.evidence_matching.matcher import match_claim_to_evidence
from src.assessment.assessment import assess_case
from src.assessment.assessment_schema import CaseAssessment


def run_assessment(
    statement_id: str,
    statement: str,
    evidence: list[EvidenceRecord],
) -> CaseAssessment:
    """
    Parse a statement, match its claims against evidence,
    and return a structured case assessment.
    """

    claims = parse_statement_text(
        statement_id=statement_id,
        statement=statement,
    )

    results = [
        match_claim_to_evidence(claim, evidence)
        for claim in claims
    ]

    assessment = assess_case(results)

    return assessment