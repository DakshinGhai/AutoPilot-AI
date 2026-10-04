import pytest

from app.models.candidate_context import CandidateContext
from app.models.trace import LocatorDecisionTrace


def test_locator_decision_trace_contains_ai_decision():

    trace = LocatorDecisionTrace(
        target="Product",
        candidates_generated=8,
        candidates_valid=4,
        selected_candidate_id="candidate_19:css:id",
        selected_locator_type="css",
        selected_locator_value="#product-id",
        ai_confidence=0.95,
        ai_reason="Stable unique ID",
        final_match_count=1,
        final_is_unique=True,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=True,
    )

    assert trace.target == "Product"
    assert trace.candidates_generated == 8
    assert trace.candidates_valid == 4
    assert trace.selected_candidate_id == "candidate_19:css:id"
    assert trace.selected_locator_type == "css"
    assert trace.ai_confidence == 0.95
    assert trace.final_is_valid is True


def test_locator_decision_trace_can_represent_failed_validation():

    trace = LocatorDecisionTrace(
        target="Book Appointment",
        candidates_generated=5,
        candidates_valid=1,
        selected_candidate_id="candidate_7:role",
        selected_locator_type="role",
        selected_locator_value="button:Book Appointment",
        ai_confidence=0.91,
        ai_reason="Semantic button candidate",
        final_match_count=2,
        final_is_unique=False,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=False,
    )

    assert trace.final_match_count == 2
    assert trace.final_is_unique is False
    assert trace.final_is_valid is False


def test_locator_trace_is_attached_to_step_execution():

    from app.models.execution import StepExecutionResult

    trace = LocatorDecisionTrace(
        target="Product",
        candidates_generated=4,
        candidates_valid=2,
        selected_candidate_id="candidate_1:role",
        selected_locator_type="role",
        selected_locator_value="button:Product",
        ai_confidence=0.9,
        ai_reason="Semantic match",
        final_match_count=1,
        final_is_unique=True,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=True,
    )

    step = StepExecutionResult(
        step=3,
        action="click",
        target="Product",
        status="PASS",
        locator_trace=trace,
    )

    assert step.locator_trace is not None
    assert step.locator_trace.target == "Product"
    assert step.locator_trace.final_is_valid is True
