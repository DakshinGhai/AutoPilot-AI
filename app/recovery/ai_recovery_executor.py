from playwright.async_api import Page

from app.models.candidate_context import CandidateContext
from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)
from app.models.recovery import RecoveryExecutionResult
from app.recovery.ai_recovery_validator import (
    AIRecoveryValidator,
)


class AIRecoveryExecutor:

    def __init__(
        self,
        validator: AIRecoveryValidator | None = None,
    ):
        self.validator = validator or AIRecoveryValidator()

    async def execute(
        self,
        page: Page,
        candidate: CandidateContext,
        action: str,
        original_error: str | None = None,
        ai_confidence: float | None = None,
        ai_reason: str | None = None,
    ) -> RecoveryExecutionResult:

        validation = await self.validator.validate_selected_candidate(
            page,
            candidate,
        )

        if not validation.is_valid:
            return RecoveryExecutionResult(
                attempted=True,
                success=False,
                action=action,
                original_error=original_error,
                recovery_error=(
                    "AI-selected recovery candidate " "failed final browser validation."
                ),
                selected_candidate=(self._candidate_from_context(candidate)),
                validation=validation,
                retry_attempted=False,
                candidate_count=1,
                valid_candidate_count=0,
                attempt_count=1,
            )

        locator_candidate = self._candidate_from_context(candidate)

        try:
            locator = self._build_locator(
                page,
                locator_candidate,
            )

            await self._execute_action(
                locator,
                action,
            )

            return RecoveryExecutionResult(
                attempted=True,
                success=True,
                action=action,
                original_error=original_error,
                selected_candidate=locator_candidate,
                validation=validation,
                retry_attempted=True,
                candidate_count=1,
                valid_candidate_count=1,
                attempt_count=1,
                ai_used=True,
                ai_confidence=ai_confidence,
                ai_reason=ai_reason,
            )

        except Exception as exc:

            return RecoveryExecutionResult(
                attempted=True,
                success=False,
                action=action,
                original_error=original_error,
                recovery_error=str(exc),
                selected_candidate=locator_candidate,
                validation=validation,
                retry_attempted=True,
                candidate_count=1,
                valid_candidate_count=1,
                attempt_count=1,
                ai_used=True,
                ai_confidence=ai_confidence,
                ai_reason=ai_reason,
            )

    @staticmethod
    def _candidate_from_context(
        candidate: CandidateContext,
    ) -> LocatorCandidate:

        return LocatorCandidate(
            element_id=candidate.element_id,
            strategy=candidate.strategy,
            value=candidate.locator_value,
            locator_type=candidate.locator_type,
            priority=candidate.priority,
            confidence=candidate.confidence,
            reason=candidate.reason,
            semantic_evidence=candidate.semantic_evidence,
            is_unique=candidate.is_unique,
            is_valid=candidate.is_valid,
        )

    @staticmethod
    def _build_locator(
        page: Page,
        candidate: LocatorCandidate,
    ):
        locator_type = candidate.locator_type
        value = candidate.value

        if locator_type == "css":
            return page.locator(value)

        if locator_type == "xpath":
            return page.locator(value)

        if locator_type == "text":
            return page.get_by_text(
                value,
                exact=True,
            )

        if locator_type == "placeholder":
            return page.get_by_placeholder(
                value,
                exact=True,
            )

        if locator_type == "testid":
            return page.get_by_test_id(value)

        if locator_type == "aria-label":
            return page.locator(f'[aria-label="{value}"]')

        if locator_type == "label":
            return page.get_by_label(
                value,
                exact=True,
            )

        if locator_type == "role":

            if ":" not in value:
                raise ValueError("Invalid role locator format.")

            role, name = value.split(
                ":",
                1,
            )

            return page.get_by_role(
                role,
                name=name,
                exact=True,
            )

        raise ValueError(f"Unsupported locator type: {locator_type}")

    @staticmethod
    async def _execute_action(
        locator,
        action: str,
    ):

        normalized_action = str(action).lower().strip()

        if normalized_action == "click":
            await locator.click()
            return

        raise ValueError(f"Unsupported recovery action: {action}")
