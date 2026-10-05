from datetime import datetime
from typing import Optional

from pydantic import BaseModel, model_validator


class Claim(BaseModel):
    claim_id: str
    statement_id: str

    subject: str
    action: str

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    location: Optional[str] = None
    object: Optional[str] = None

    expected: Optional[bool] = None
    description: str

    @model_validator(mode="after")
    def validate_claim(self):
        if not self.subject.strip():
            raise ValueError("Claim subject cannot be empty.")

        if not self.action.strip():
            raise ValueError("Claim action cannot be empty.")

        if not self.description.strip():
            raise ValueError("Claim description cannot be empty.")

        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time < self.start_time
        ):
            raise ValueError(
                "Claim end_time cannot be earlier than start_time."
            )

        return self