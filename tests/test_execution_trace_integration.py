from app.models.execution import AIExecutionResult
from app.models.trace import (
    ActionExecutionTrace,
    ExecutionTrace,
    LocatorDecisionTrace,
)


def test_locator_decision_trace():

    trace = LocatorDecisionTrace(
        target="Search IKEA products",
        candidates_generated=5,
        candidates_valid=3,
        selected_candidate_id="candidate_1:role:role",
        selected_locator_type="role",
        selected_locator_value="button:Search IKEA products",
        ai_confidence=0.95,
        ai_reason="Semantic role is stable",
        final_match_count=1,
        final_is_unique=True,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=True,
    )

    assert trace.target == "Search IKEA products"
    assert trace.candidates_generated == 5
    assert trace.candidates_valid == 3
    assert trace.selected_locator_type == "role"
    assert trace.final_is_valid is True


def test_action_execution_trace_contains_locator_decision():

    locator_trace = LocatorDecisionTrace(
        target="Search",
        candidates_generated=4,
        candidates_valid=2,
        selected_candidate_id="candidate-1",
        selected_locator_type="css",
        selected_locator_value="#search",
        ai_confidence=0.9,
        ai_reason="Stable ID",
        final_match_count=1,
        final_is_unique=True,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=True,
    )

    action_trace = ActionExecutionTrace(
        step=1,
        action="click",
        target="Search",
        status="PASS",
        locator_decision=locator_trace,
    )

    assert action_trace.status == "PASS"
    assert action_trace.locator_decision is not None
    assert action_trace.locator_decision.selected_locator_type == "css"


def test_execution_trace_contains_actions():

    action_trace = ActionExecutionTrace(
        step=1,
        action="click",
        target="Search",
        status="PASS",
    )

    execution_trace = ExecutionTrace(
        test_case_id="TC001",
        test_case_name="IKEA Search",
        status="PASS",
        actions=[action_trace],
    )

    assert execution_trace.test_case_id == "TC001"
    assert execution_trace.status == "PASS"
    assert len(execution_trace.actions) == 1
    assert execution_trace.actions[0].action == "click"


def test_ai_execution_result_supports_locator_decision():

    locator_trace = LocatorDecisionTrace(
        target="Search",
        candidates_generated=3,
        candidates_valid=2,
        selected_candidate_id="candidate-1",
        selected_locator_type="css",
        selected_locator_value="#search",
        ai_confidence=1.0,
        ai_reason="Stable locator",
        final_match_count=1,
        final_is_unique=True,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=True,
    )

    result = AIExecutionResult(
        success=True,
        candidate_id="candidate-1",
        locator_type="css",
        locator_value="#search",
        action="click",
        ai_confidence=1.0,
        ai_reason="Stable locator",
        locator_decision=locator_trace,
        final_match_count=1,
        final_is_unique=True,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=True,
    )

    assert result.success is True
    assert result.locator_decision is not None
    assert result.final_is_valid is True
