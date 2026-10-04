from typing import Optional

from pydantic import BaseModel

from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)


class RecoveryExecutionResult(BaseModel):

    attempted: bool = False
    success: bool = False

    action: str

    original_error: Optional[str] = None
    recovery_error: Optional[str] = None

    selected_candidate: Optional[LocatorCandidate] = None

    validation: Optional[LocatorValidationResult] = None

    retry_attempted: bool = False

    candidate_count: int = 0
    valid_candidate_count: int = 0

    attempt_count: int = 0

    ai_used: bool = False
    ai_confidence: Optional[float] = None
    ai_reason: Optional[str] = None
