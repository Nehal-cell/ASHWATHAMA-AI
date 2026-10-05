from typing import Optional

from pydantic import BaseModel


class MatchResult(BaseModel):
    claim_id: str
    evidence_id: Optional[str] = None

    status: str
    confidence: Optional[float] = None

    reason: str