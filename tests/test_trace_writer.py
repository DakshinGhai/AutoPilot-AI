import json

from app.models.trace import (
    ActionExecutionTrace,
    ExecutionTrace,
    LocatorDecisionTrace,
)
from app.reporting.trace_writer import ExecutionTraceWriter


def test_execution_trace_is_written_to_json(tmp_path):
    trace = ExecutionTrace(
        test_case_id="TC001",
        test_case_name="Search IKEA Product",
        status="PASS",
        actions=[
            ActionExecutionTrace(
                step=2,
                action="click",
                target="Search",
                status="PASS",
                locator_decision=LocatorDecisionTrace(
                    target="Search",
                    candidates_generated=4,
                    candidates_valid=4,
                    selected_candidate_id="candidate_1",
                    selected_locator_type="role",
                    selected_locator_value="button:Search",
                    ai_confidence=0.98,
                    ai_reason="Selected the unique accessible button.",
                    final_match_count=1,
                    final_is_unique=True,
                    final_is_visible=True,
                    final_is_enabled=True,
                    final_is_valid=True,
                ),
            )
        ],
    )

    output_path = tmp_path / "execution_trace.json"

    writer = ExecutionTraceWriter()
    result = writer.save(trace, output_path)

    assert result == output_path
    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["test_case_id"] == "TC001"
    assert data["test_case_name"] == "Search IKEA Product"
    assert data["status"] == "PASS"

    assert len(data["actions"]) == 1

    action = data["actions"][0]

    assert action["action"] == "click"
    assert action["target"] == "Search"
    assert action["status"] == "PASS"

    decision = action["locator_decision"]

    assert decision["candidates_generated"] == 4
    assert decision["candidates_valid"] == 4
    assert decision["selected_locator_type"] == "role"
    assert decision["selected_locator_value"] == "button:Search"
    assert decision["ai_confidence"] == 0.98
    assert decision["final_match_count"] == 1
    assert decision["final_is_valid"] is True


def test_trace_writer_creates_parent_directories(tmp_path):
    trace = ExecutionTrace(
        test_case_id="TC002",
        test_case_name="Example",
        status="PASS",
    )

    output_path = tmp_path / "nested" / "reports" / "execution_trace.json"

    writer = ExecutionTraceWriter()
    writer.save(trace, output_path)

    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data["test_case_id"] == "TC002"
