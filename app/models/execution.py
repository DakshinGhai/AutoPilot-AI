from typing import List, Optional

from pydantic import BaseModel


from app.models.failure import FailureContext
from app.models.trace import (
    LocatorDecisionTrace,
    ExecutionTrace,
    RecoveryTrace,
)


class AIExecutionResult(BaseModel):
    success: bool = False

    candidate_id: str
    locator_type: str
    locator_value: str

    action: str

    ai_confidence: Optional[float] = None
    ai_reason: Optional[str] = None

    locator_decision: Optional[LocatorDecisionTrace] = None

    final_match_count: Optional[int] = None
    final_is_unique: Optional[bool] = None
    final_is_visible: Optional[bool] = None
    final_is_enabled: Optional[bool] = None
    final_is_valid: Optional[bool] = None

    error: Optional[str] = None


class StepExecutionResult(BaseModel):
    step: int
    action: str
    target: Optional[str] = None
    status: str

    locator_trace: Optional[LocatorDecisionTrace] = None
    failure_context: Optional[FailureContext] = None
    recovery: Optional[RecoveryTrace] = None
    error: Optional[str] = None


class TestExecutionResult(BaseModel):
    test_case_id: str
    test_case_name: str
    status: str

    steps: List[StepExecutionResult]

    trace: Optional[ExecutionTrace] = None

    error: Optional[str] = None
