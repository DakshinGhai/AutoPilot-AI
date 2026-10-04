from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.candidate_context import CandidateContext


class RecoverySelectionRequest(BaseModel):
    test_step: str
    target: str
    original_error: str

    page_url: Optional[str] = None
    page_title: Optional[str] = None

    candidates: List[CandidateContext] = Field(default_factory=list)


class RecoverySelectionResponse(BaseModel):
    selected_candidate_id: str

    reason: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
