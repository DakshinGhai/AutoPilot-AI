from typing import Optional

from pydantic import BaseModel, Field

from app.models.semantic import SemanticEvidence


class CandidateContext(BaseModel):
    """
    Compact representation of a locator candidate.

    This model is designed to be consumed by:
    - deterministic ranking
    - debugging
    - future AI locator selection
    """

    candidate_id: str

    element_id: str

    locator_type: str
    locator_value: str
    strategy: str

    priority: int

    semantic_evidence: Optional[SemanticEvidence] = None

    visible: bool = False
    enabled: bool = False

    match_count: Optional[int] = None
    is_unique: Optional[bool] = None
    is_valid: Optional[bool] = None

    confidence: Optional[float] = None

    reason: Optional[str] = None
