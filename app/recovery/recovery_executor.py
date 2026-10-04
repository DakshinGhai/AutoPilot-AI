from playwright.async_api import Page

from app.models.locator import LocatorCandidate
from app.models.recovery import RecoveryExecutionResult

from app.recovery.recovery_validation_service import (
    RecoveryValidationService,
)


class RecoveryExecutor:

    def __init__(
        self,
        validation_service: RecoveryValidationService | None = None,
    ):
        self.validation_service = validation_service or RecoveryValidationService()

    async def recover_click(
        self,
        page: Page,
        elements,
        original_error: str,
        failed_element_id: str | None = None,
        target: str | None = None,
        attempt_count: int = 0,
    ) -> RecoveryExecutionResult:

        result = RecoveryExecutionResult(
            attempted=True,
            success=False,
            action="click",
            original_error=original_error,
            attempt_count=attempt_count,
        )

        try:

            valid_candidates = await self.validation_service.generate_validate(
                page=page,
                elements=elements,
                failed_element_id=failed_element_id,
                target=target,
            )

            result.valid_candidate_count = len(valid_candidates)

            if not valid_candidates:

                result.recovery_error = "No valid recovery candidates found."

                return result

            selected_candidate, validation = valid_candidates[0]

            result.selected_candidate = selected_candidate

            result.validation = validation

            result.retry_attempted = True

            locator = self._build_locator(
                page,
                selected_candidate,
            )

            await locator.click()

            result.success = True

            return result

        except Exception as exc:

            result.recovery_error = str(exc)

            return result

    def _build_locator(
        self,
        page: Page,
        candidate: LocatorCandidate,
    ):
        locator_type = candidate.locator_type
        value = candidate.value

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

        raise ValueError(f"Unsupported locator type: {locator_type}")

    def _build_role_locator(
        self,
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
