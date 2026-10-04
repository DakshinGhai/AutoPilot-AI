from pathlib import Path

from app.browser.page_inspector import PageInspector
from app.execution.action_executor import ActionExecutor
from app.execution.ai_action_executor import AIActionExecutor
from app.execution.assertion_engine import AssertionEngine
from app.execution.browser_manager import BrowserManager

from app.recovery.recovery_executor import RecoveryExecutor
from app.recovery.failure_context_builder import FailureContextBuilder

from app.reporting.trace_writer import ExecutionTraceWriter

from app.models.execution import (
    StepExecutionResult,
    TestExecutionResult,
)
from app.recovery.recovery_policy import (
    RecoveryPolicy,
)

from app.models.test_plan import TestPlan

from app.models.trace import (
    ActionExecutionTrace,
    ExecutionTrace,
    RecoveryTrace,
)
class TestExecutor:

    def __init__(
        self,
        browser_manager: BrowserManager,
        ai_selection_service=None,
    ):
        self.trace_writer = ExecutionTraceWriter()

        self.browser_manager = browser_manager

        self.page_inspector = PageInspector()
        self.failure_context_builder = FailureContextBuilder()
        self.recovery_executor = RecoveryExecutor()
        self.recovery_policy = RecoveryPolicy()
        # AI service is injected.
        # This keeps Gemini/Mock AI outside the executor.
        self.ai_selection_service = (
            ai_selection_service
        )

    async def execute(
        self,
        test_plan: TestPlan,
        test_case_id: str | None = None,
    ):

        page = await self.browser_manager.start()

        results = []

        try:

            for test_case in test_plan.test_cases:

                if (
                    test_case_id
                    and test_case.test_case_id != test_case_id
                ):
                    continue

                test_result = (
                    await self._execute_test_case(
                        page,
                        test_case,
                    )
                )

                results.append(test_result)

        finally:

            await self.browser_manager.close()

        return results

    async def _execute_test_case(self, page, test_case):

        action_executor = ActionExecutor(page)
        assertion_engine = AssertionEngine(page)

        ai_action_executor = None

        if self.ai_selection_service:
            ai_action_executor = AIActionExecutor(
                page,
                self.ai_selection_service,
            )

        step_results = []
        action_traces = []

        for step in test_case.steps:

            action = (
                step.action.value
                if hasattr(step.action, "value")
                else str(step.action)
            )

            target = (
                str(step.target)
                if step.target is not None
                else None
            )

            ai_result = None

            try:

                print(
                    f"\n[STEP {step.step}] "
                    f"Action={action}, Target={target}"
                )

                if action == "navigate":

                    print(
                        f"[EXECUTION] Navigating to: {target}"
                    )

                    await action_executor.execute(
                        action=action,
                        target=target,
                    )

                elif ai_action_executor and action == "click":

                    print(
                        f"\n[AI EXECUTION] Click target: {target}"
                    )

                    ai_result = await ai_action_executor.execute(
                        action=action,
                        target=target,
                        value=(
                            step.test_data.value
                            if step.test_data
                            else None
                        ),
                    )

                    if not ai_result.success:
                        raise RuntimeError(
                            ai_result.error
                            or "AI action execution failed"
                        )

                else:

                    await action_executor.execute(
                        action=action,
                        target=target,
                    )

                if (
                    step.expected_result
                    and step.expected_result.value
                    and step.expected_result.value.strip()
                ):

                    print(
                        f"[ASSERTION] Step {step.step} "
                        f"Expected={step.expected_result.value}"
                    )

                    await assertion_engine.validate(
                        step.expected_result.value
                    )

                    print(
                        f"[ASSERTION] Step {step.step} PASSED"
                    )

                step_result = StepExecutionResult(
                    step=step.step,
                    action=action,
                    target=target,
                    status="PASS",
                    locator_trace=(
                        ai_result.locator_decision
                        if ai_result
                        else None
                    ),
                    error=None,
                )

                step_results.append(step_result)

                action_traces.append(
                    ActionExecutionTrace(
                        step=step.step,
                        action=action,
                        target=target,
                        status="PASS",
                        locator_decision=(
                            ai_result.locator_decision
                            if ai_result
                            else None
                        ),
                        error=None,
                    )
                )

            except Exception as error:

                print(
                    f"\n[STEP FAILED] "
                    f"Step {step.step}: {error}"
                )

                original_error = str(error)

                recovery_trace = None
                recovery_result = None

                # -----------------------------------------
                # ATTEMPT RECOVERY
                # -----------------------------------------
                recovery_allowed = (
                    self.recovery_policy.can_recover(
                        action=action,
                        attempt_count=0,
                    )
                )

                if recovery_allowed:

                    try:

                        print(
                            f"[RECOVERY] Attempting recovery "
                            f"for step {step.step}"
                        )

                        page_info = await self.page_inspector.inspect(
                            page
                        )

                        recovery_result = (
                            await self.recovery_executor.recover_click(
                                page=page,
                                elements=page_info.elements,
                                original_error=original_error,
                                target=target,
                                attempt_count=1,
                            )
                        )

                        selected_candidate = (
                            recovery_result.selected_candidate
                        )

                        recovery_trace = RecoveryTrace(
                            attempted=recovery_result.attempted,

                            success=recovery_result.success,
                            attempt_count=(
                                recovery_result.attempt_count
                            ),
                            policy_allowed=recovery_allowed,
                            selected_candidate_id=(
                                selected_candidate.candidate_id
                                if selected_candidate
                                else None
                            ),

                            selected_locator_type=(
                                selected_candidate.locator_type
                                if selected_candidate
                                else None
                            ),

                            selected_locator_value=(
                                selected_candidate.value
                                if selected_candidate
                                else None
                            ),
                            selected_confidence=(
                                selected_candidate.confidence
                                if selected_candidate
                                else None
                            ),

                            retry_attempted=(
                                recovery_result.retry_attempted
                            ),

                            original_error=(
                                recovery_result.original_error
                            ),

                            recovery_error=(
                                recovery_result.recovery_error
                            ),
                            candidate_count=(
                                recovery_result.candidate_count
                            ),

                            valid_candidate_count=(
                                recovery_result.valid_candidate_count
                            ),
                        )

                    except Exception as recovery_error:

                        print(
                            f"[RECOVERY FAILED] "
                            f"{recovery_error}"
                        )

                        recovery_trace = RecoveryTrace(
                            attempted=True,
                            success=False,
                            retry_attempted=False,
                            original_error=original_error,
                            recovery_error=str(
                                recovery_error
                            ),
                        )

                # -----------------------------------------
                # RECOVERY SUCCEEDED
                # -----------------------------------------

                if (
                    recovery_result
                    and recovery_result.success
                ):

                    print(
                        f"[RECOVERY] Step {step.step} "
                        f"recovered successfully"
                    )

                    step_result = StepExecutionResult(
                        step=step.step,
                        action=action,
                        target=target,
                        status="RECOVERED",

                        locator_trace=(
                            ai_result.locator_trace
                            if ai_result
                            else None
                        ),

                        recovery=recovery_trace,

                        failure_context=None,

                        error=None,
                    )

                    step_results.append(
                        step_result
                    )

                    action_traces.append(
                        ActionExecutionTrace(
                            step=step.step,
                            action=action,
                            target=target,
                            status="RECOVERED",

                            locator_trace=(
                                ai_result.locator_trace
                                if ai_result
                                else None
                            ),

                            recovery=recovery_trace,

                            failure_context=None,

                            error=None,
                        )
                    )

                    continue

                # -----------------------------------------
                # RECOVERY FAILED
                # -----------------------------------------

                failure_context = (
                    await self.failure_context_builder.build(
                        page=page,
                        test_case_id=test_case.test_case_id,
                        test_case_name=test_case.name,
                        step=step.step,
                        action=action,
                        target=target,
                        error_message=original_error,

                        locator_decision=(
                            ai_result.locator_trace
                            if ai_result
                            else None
                        ),
                    )
                )

                step_result = StepExecutionResult(
                    step=step.step,
                    action=action,
                    target=target,
                    status="FAIL",

                    locator_trace=(
                        ai_result.locator_trace
                        if ai_result
                        else None
                    ),

                    recovery=recovery_trace,

                    failure_context=failure_context,

                    error=original_error,
                )

                step_results.append(
                    step_result
                )

                action_traces.append(
                    ActionExecutionTrace(
                        step=step.step,
                        action=action,
                        target=target,
                        status="FAIL",

                        locator_trace=(
                            ai_result.locator_trace
                            if ai_result
                            else None
                        ),

                        recovery=recovery_trace,

                        failure_context=failure_context,

                        error=original_error,
                    )
                )

                execution_trace = ExecutionTrace(
                    test_case_id=test_case.test_case_id,
                    test_case_name=test_case.name,
                    status="FAIL",
                    actions=action_traces,
                    error=original_error,
                )

                self.trace_writer.save(
                    execution_trace,
                    Path("output")
                    / f"{test_case.test_case_id}_execution_trace.json",
                )

                return TestExecutionResult(
                    test_case_id=test_case.test_case_id,
                    test_case_name=test_case.name,
                    status="FAIL",
                    steps=step_results,
                    trace=execution_trace,
                    error=original_error,
                )

        execution_trace = ExecutionTrace(
            test_case_id=test_case.test_case_id,
            test_case_name=test_case.name,
            status="PASS",
            actions=action_traces,
            error=None,
        )
        self.trace_writer.save(
            execution_trace,
            Path("output") / f"{test_case.test_case_id}_execution_trace.json",
        )

        return TestExecutionResult(
            test_case_id=test_case.test_case_id,
            test_case_name=test_case.name,
            status="PASS",
            steps=step_results,
            trace=execution_trace,
            error=None,
        )