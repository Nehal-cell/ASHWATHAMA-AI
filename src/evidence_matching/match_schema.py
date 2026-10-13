
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class MatchResult(BaseModel):
    claim_id: str
    evidence_id: Optional[str] = None

    status: Literal[
        "SUPPORTED",
        "CONTRADICTED",
        "MIXED",
        "INSUFFICIENT_EVIDENCE",
    ]

    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    supporting_reliability: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    contradicting_reliability: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )

    reason: str

    @model_validator(mode="after")
    def validate_confidence(self):
        if (
            self.status in ("INSUFFICIENT_EVIDENCE", "MIXED")
            and self.confidence is not None
        ):
            raise ValueError(
                f"{self.status} must have confidence=None."
            )

        if self.status == "MIXED":
            if self.supporting_reliability is None:
                raise ValueError(
                    "MIXED results must include supporting_reliability."
                )

            if self.contradicting_reliability is None:
                raise ValueError(
                    "MIXED results must include contradicting_reliability."
                )

        elif (
            self.supporting_reliability is not None
            or self.contradicting_reliability is not None
        ):
            raise ValueError(
                "Separate reliability scores are only for MIXED results."
            )

        return self