from playwright.async_api import Page

from app.locators.locator_validator import LocatorValidator
from app.models.ai import LocatorSelectionResponse
from app.models.candidate_context import CandidateContext
from app.models.execution import AIExecutionResult


class AILocatorExecutor:

    def __init__(
        self,
        validator: LocatorValidator,
    ):
        self.validator = validator

    async def execute_click(
        self,
        page: Page,
        selected: CandidateContext,
        ai_response: LocatorSelectionResponse,
    ) -> AIExecutionResult:

        try:
            locator = self._build_locator(page, selected)

            validation_candidate = self._candidate_from_context(selected)

            validation = await self.validator.validate(
                page,
                validation_candidate,
            )

            if not validation.is_valid:
                return AIExecutionResult(
                    success=False,
                    candidate_id=selected.candidate_id,
                    locator_type=selected.locator_type,
                    locator_value=selected.locator_value,
                    action="click",
                    ai_confidence=ai_response.confidence,
                    ai_reason=ai_response.reason,
                    final_match_count=validation.match_count,
                    final_is_unique=validation.is_unique,
                    final_is_visible=validation.is_visible,
                    final_is_enabled=validation.is_enabled,
                    final_is_valid=validation.is_valid,
                    error=("Final locator validation failed: " f"{validation.reason}"),
                )

            await locator.click()

            return AIExecutionResult(
                success=True,
                candidate_id=selected.candidate_id,
                locator_type=selected.locator_type,
                locator_value=selected.locator_value,
                action="click",
                ai_confidence=ai_response.confidence,
                ai_reason=ai_response.reason,
                final_match_count=validation.match_count,
                final_is_unique=validation.is_unique,
                final_is_visible=validation.is_visible,
                final_is_enabled=validation.is_enabled,
                final_is_valid=validation.is_valid,
            )

        except Exception as exc:
            return AIExecutionResult(
                success=False,
                candidate_id=selected.candidate_id,
                locator_type=selected.locator_type,
                locator_value=selected.locator_value,
                action="click",
                ai_confidence=ai_response.confidence,
                ai_reason=ai_response.reason,
                error=str(exc),
            )

    def _build_locator(
        self,
        page: Page,
        candidate: CandidateContext,
    ):

        locator_type = candidate.locator_type
        value = candidate.locator_value

        if locator_type == "css":
            return page.locator(value)

        if locator_type == "xpath":
            return page.locator(f"xpath={value}")

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
            return self._build_role_locator(
                page,
                value,
            )

        raise ValueError(f"Unsupported locator type: " f"{locator_type}")

    @staticmethod
    def _build_role_locator(
        page: Page,
        value: str,
    ):

        if ":" in value:

            role, name = value.split(
                ":",
                1,
            )

            return page.get_by_role(
                role,
                name=name,
                exact=True,
            )

        return page.get_by_role(value)

    @staticmethod
    def _candidate_from_context(
        context: CandidateContext,
    ):
        from app.models.locator import (
            LocatorCandidate,
        )

        return LocatorCandidate(
            element_id=context.element_id,
            strategy=context.strategy,
            value=context.locator_value,
            locator_type=context.locator_type,
            priority=context.priority,
            confidence=context.confidence,
            is_unique=context.is_unique,
            is_valid=context.is_valid,
            reason=context.reason,
            semantic_evidence=(context.semantic_evidence),
        )
