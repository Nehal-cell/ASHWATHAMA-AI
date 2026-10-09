
from typing import List

from pydantic import BaseModel, Field, model_validator

from src.evidence_matching.match_schema import MatchResult


class CaseAssessment(BaseModel):
    total_claims: int = Field(ge=0)

    supported_claims: int = Field(ge=0)
    contradicted_claims: int = Field(ge=0)
    mixed_claims: int = Field(ge=0)
    insufficient_evidence_claims: int = Field(ge=0)

    results: List[MatchResult] = Field(default_factory=list)

    summary: str

    @model_validator(mode="after")
    def validate_counts(self):
        if self.total_claims != len(self.results):
            raise ValueError(
                "total_claims must match the number of results."
            )

        status_total = (
            self.supported_claims
            + self.contradicted_claims
            + self.mixed_claims
            + self.insufficient_evidence_claims
        )

        if status_total != self.total_claims:
            raise ValueError(
                "Status counts must add up to total_claims."
            )

        return self