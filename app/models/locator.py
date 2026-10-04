from typing import Optional

from pydantic import BaseModel, Field


from app.models.semantic import SemanticEvidence


class LocatorCandidate(BaseModel):
    element_id: str
    strategy: str
    value: str
    locator_type: str
    priority: int = Field(default=0)
    source: str = "deterministic"
    confidence: Optional[float] = None
    is_unique: Optional[bool] = None
    is_valid: Optional[bool] = None
    reason: Optional[str] = None
    semantic_role: Optional[str] = None
    accessible_name: Optional[str] = None
    evidence_source: Optional[str] = None
    semantic_evidence: Optional[SemanticEvidence] = None


class LocatorValidationResult(BaseModel):
    element_id: str
    strategy: str
    value: str
    locator_type: str

    exists: bool = False
    match_count: int = 0
    is_unique: bool = False
    is_visible: bool = False
    is_enabled: bool = False

    is_valid: bool = False
    reason: Optional[str] = None


class LocatorResolutionResult(BaseModel):
    element_id: str

    selected_locator: Optional[LocatorCandidate] = None

    candidates: list[LocatorCandidate] = Field(default_factory=list)

    validations: list[LocatorValidationResult] = Field(default_factory=list)

    success: bool = False
    reason: Optional[str] = None
