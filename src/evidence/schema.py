from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class EvidenceRecord(BaseModel):
    case_id: str
    evidence_id: str
    source_device: str
    artifact_type: str
    event_time: datetime
    description: str
    source_tool: str
    reliability: Optional[float] = Field(default=None, ge=0, le=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    source_reference: Optional[str] = None
    collected_at: Optional[datetime] = None
    collection_method: Optional[str] = None