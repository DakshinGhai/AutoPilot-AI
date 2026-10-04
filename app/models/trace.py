from typing import Optional

from pydantic import BaseModel, Field, model_validator

from app.models.failure import FailureContext


class LocatorDecisionTrace(BaseModel):
    target: str

    candidates_generated: int = 0
    candidates_valid: int = 0

    selected_candidate_id: Optional[str] = None
    selected_locator_type: Optional[str] = None
    selected_locator_value: Optional[str] = None

    ai_confidence: Optional[float] = None
    ai_reason: Optional[str] = None

    final_match_count: Optional[int] = None
    final_is_unique: Optional[bool] = None
    final_is_visible: Optional[bool] = None
    final_is_enabled: Optional[bool] = None
    final_is_valid: Optional[bool] = None


from typing import Optional

from pydantic import BaseModel


class RecoveryTrace(BaseModel):
    attempted: bool = False
    success: bool = False
    attempt_count: int = 0
    policy_allowed: bool = False

    candidate_count: int = 0
    valid_candidate_count: int = 0

    selected_candidate_id: Optional[str] = None
    selected_locator_type: Optional[str] = None
    selected_locator_value: Optional[str] = None
    selected_confidence: Optional[float] = None

    retry_attempted: bool = False

    original_error: Optional[str] = None
    recovery_error: Optional[str] = None

    # AI recovery information
    ai_used: bool = False
    ai_confidence: Optional[float] = None
    ai_reason: Optional[str] = None

    # Final browser validation
    final_match_count: Optional[int] = None
    final_is_unique: Optional[bool] = None
    final_is_visible: Optional[bool] = None
    final_is_enabled: Optional[bool] = None
    final_is_valid: Optional[bool] = None


class ActionExecutionTrace(BaseModel):
    step: int
    action: str
    target: Optional[str] = None
    status: str

    # Canonical field
    locator_decision: Optional[LocatorDecisionTrace] = None

    # Compatibility field
    locator_trace: Optional[LocatorDecisionTrace] = None
    failure_context: Optional[FailureContext] = None
    recovery: Optional[RecoveryTrace] = None
    error: Optional[str] = None

    @model_validator(mode="after")
    def sync_locator_fields(self):
        if self.locator_decision is None and self.locator_trace is not None:
            self.locator_decision = self.locator_trace

        elif self.locator_trace is None and self.locator_decision is not None:
            self.locator_trace = self.locator_decision

        return self


class ExecutionTrace(BaseModel):
    test_case_id: str
    test_case_name: str
    status: str

    actions: list[ActionExecutionTrace] = Field(default_factory=list)

    error: Optional[str] = None
