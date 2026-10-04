from app.models.report import ExecutionSummary
from app.models.trace import ExecutionTrace


class ExecutionReportGenerator:

    def generate(
        self,
        trace: ExecutionTrace,
    ) -> ExecutionSummary:

        total_steps = len(trace.actions)

        passed_steps = sum(
            1 for action in trace.actions if action.status.upper() == "PASS"
        )

        failed_steps = sum(
            1 for action in trace.actions if action.status.upper() == "FAIL"
        )

        decisions = [
            action.locator_decision
            for action in trace.actions
            if action.locator_decision is not None
        ]

        successful_decisions = [
            decision for decision in decisions if decision.final_is_valid is True
        ]

        confidences = [
            decision.ai_confidence
            for decision in decisions
            if decision.ai_confidence is not None
        ]

        average_confidence = (
            sum(confidences) / len(confidences) if confidences else None
        )

        return ExecutionSummary(
            test_case_id=trace.test_case_id,
            test_case_name=trace.test_case_name,
            status=trace.status,
            total_steps=total_steps,
            passed_steps=passed_steps,
            failed_steps=failed_steps,
            ai_locator_decisions=len(decisions),
            successful_locator_decisions=len(successful_decisions),
            average_ai_confidence=average_confidence,
        )
