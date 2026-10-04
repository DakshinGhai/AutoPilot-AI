from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.candidate_context import CandidateContext


class LocatorSelectionRequest(BaseModel):
    """
    Input sent to the AI locator-selection layer.
    """

    test_step: str

    target: str

    page_url: Optional[str] = None

    page_title: Optional[str] = None

    candidates: List[CandidateContext] = Field(default_factory=list)


class LocatorSelectionResponse(BaseModel):
    """
    Structured response expected from an AI locator selector.
    """

    selected_candidate_id: str

    reason: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )
