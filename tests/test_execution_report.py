from app.models.trace import (
    ActionExecutionTrace,
    ExecutionTrace,
    LocatorDecisionTrace,
)
from app.reporting.execution_report import ExecutionReportGenerator


def test_execution_report_generates_summary():

    trace = ExecutionTrace(
        test_case_id="TC001",
        test_case_name="Search Product",
        status="PASS",
        actions=[
            ActionExecutionTrace(
                step=1,
                action="navigate",
                target="https://www.ikea.com/in/en/",
                status="PASS",
            ),
            ActionExecutionTrace(
                step=2,
                action="search",
                target="chair",
                status="PASS",
            ),
            ActionExecutionTrace(
                step=3,
                action="click",
                target="Product",
                status="PASS",
                locator_decision=LocatorDecisionTrace(
                    target="Product",
                    candidates_generated=516,
                    candidates_valid=102,
                    selected_candidate_id="candidate_7:role:role",
                    selected_locator_type="role",
                    selected_locator_value="button:Product",
                    ai_confidence=0.90,
                    ai_reason="Selected an available candidate.",
                    final_match_count=1,
                    final_is_unique=True,
                    final_is_visible=True,
                    final_is_enabled=True,
                    final_is_valid=True,
                ),
            ),
        ],
    )

    generator = ExecutionReportGenerator()

    summary = generator.generate(trace)

    assert summary.test_case_id == "TC001"
    assert summary.test_case_name == "Search Product"
    assert summary.status == "PASS"

    assert summary.total_steps == 3
    assert summary.passed_steps == 3
    assert summary.failed_steps == 0

    assert summary.ai_locator_decisions == 1
    assert summary.successful_locator_decisions == 1

    assert summary.average_ai_confidence == 0.90


def test_execution_report_handles_no_ai_decisions():

    trace = ExecutionTrace(
        test_case_id="TC002",
        test_case_name="Interior Design Booking",
        status="PASS",
        actions=[
            ActionExecutionTrace(
                step=1,
                action="navigate",
                target="https://www.ikea.com/in/en/",
                status="PASS",
            )
        ],
    )

    generator = ExecutionReportGenerator()

    summary = generator.generate(trace)

    assert summary.total_steps == 1
    assert summary.passed_steps == 1
    assert summary.failed_steps == 0

    assert summary.ai_locator_decisions == 0
    assert summary.successful_locator_decisions == 0
    assert summary.average_ai_confidence is None
