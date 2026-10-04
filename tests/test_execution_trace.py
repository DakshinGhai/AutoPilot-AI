from app.models.trace import (
    ActionExecutionTrace,
    LocatorDecisionTrace,
    ExecutionTrace,
)


def test_locator_decision_trace():

    trace = LocatorDecisionTrace(
        target="Product",
        candidates_generated=8,
        candidates_valid=5,
        selected_candidate_id="candidate_19:role",
        selected_locator_type="role",
        selected_locator_value="link:Product",
        ai_confidence=0.94,
        ai_reason="Accessible name matched the requested target.",
        final_match_count=1,
        final_is_unique=True,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=True,
    )

    assert trace.target == "Product"
    assert trace.candidates_generated == 8
    assert trace.candidates_valid == 5
    assert trace.selected_locator_type == "role"
    assert trace.ai_confidence == 0.94
    assert trace.final_is_valid is True


def test_action_execution_trace():

    locator_trace = LocatorDecisionTrace(
        target="Product",
        candidates_generated=4,
        candidates_valid=3,
        selected_candidate_id="candidate_1",
        selected_locator_type="css",
        selected_locator_value="#product",
        ai_confidence=0.90,
        ai_reason="Stable CSS locator selected.",
        final_match_count=1,
        final_is_unique=True,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=True,
    )

    trace = ActionExecutionTrace(
        step=3,
        action="click",
        target="Product",
        status="PASS",
        locator_trace=locator_trace,
    )

    assert trace.step == 3
    assert trace.action == "click"
    assert trace.target == "Product"
    assert trace.status == "PASS"
    assert trace.locator_decision is not None


def test_test_execution_trace():

    trace = ExecutionTrace(
        test_case_id="TC001",
        test_case_name="Search Product",
        status="PASS",
    )

    assert trace.test_case_id == "TC001"
    assert trace.test_case_name == "Search Product"
    assert trace.status == "PASS"
    assert trace.actions == []
