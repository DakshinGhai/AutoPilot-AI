from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)
from app.models.recovery import (
    RecoveryExecutionResult,
)
from app.recovery.ai_recovery_trace_builder import (
    AIRecoveryTraceBuilder,
)


def test_ai_recovery_trace_contains_ai_decision():

    candidate = LocatorCandidate(
        element_id="element-1",
        strategy="role",
        value="button:Products",
        locator_type="role",
        confidence=0.95,
    )

    validation = LocatorValidationResult(
        element_id="element-1",
        strategy="role",
        value="button:Products",
        locator_type="role",
        exists=True,
        match_count=1,
        is_unique=True,
        is_visible=True,
        is_enabled=True,
        is_valid=True,
    )

    result = RecoveryExecutionResult(
        attempted=True,
        success=True,
        action="click",
        selected_candidate=candidate,
        validation=validation,
        retry_attempted=True,
        candidate_count=92,
        valid_candidate_count=92,
        attempt_count=1,
        ai_used=True,
        ai_confidence=0.95,
        ai_reason="Exact semantic match.",
    )

    trace = AIRecoveryTraceBuilder().build(result)

    assert trace.ai_used is True
    assert trace.ai_confidence == 0.95
    assert trace.ai_reason == "Exact semantic match."

    assert trace.selected_candidate_id == "element-1:role:role"

    assert trace.selected_locator_type == "role"

    assert trace.selected_locator_value == "button:Products"

    assert trace.final_match_count == 1
    assert trace.final_is_unique is True
    assert trace.final_is_visible is True
    assert trace.final_is_enabled is True
    assert trace.final_is_valid is True


def test_ai_recovery_trace_preserves_failure():

    result = RecoveryExecutionResult(
        attempted=True,
        success=False,
        action="click",
        original_error="Original timeout",
        recovery_error="Final validation failed",
        retry_attempted=False,
        candidate_count=1,
        valid_candidate_count=0,
        attempt_count=1,
        ai_used=True,
        ai_confidence=0.82,
        ai_reason="Possible semantic match.",
    )

    trace = AIRecoveryTraceBuilder().build(result)

    assert trace.attempted is True
    assert trace.success is False
    assert trace.ai_used is True
    assert trace.ai_confidence == 0.82
    assert trace.original_error == "Original timeout"
    assert trace.recovery_error == "Final validation failed"
    assert trace.retry_attempted is False


def test_non_ai_recovery_trace_is_supported():

    result = RecoveryExecutionResult(
        attempted=True,
        success=True,
        action="click",
        retry_attempted=True,
        candidate_count=2,
        valid_candidate_count=1,
        attempt_count=1,
        ai_used=False,
    )

    trace = AIRecoveryTraceBuilder().build(result)

    assert trace.success is True
    assert trace.ai_used is False
    assert trace.ai_confidence is None
    assert trace.ai_reason is None
