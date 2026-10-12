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

    reason: str

    @model_validator(mode="after")
    def validate_confidence(self):
        if (
            self.status == "INSUFFICIENT_EVIDENCE"
            and self.confidence is not None
        ):
            raise ValueError(
                "INSUFFICIENT_EVIDENCE must have confidence=None."
            )

        return self
