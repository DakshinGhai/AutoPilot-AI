from typing import List

from playwright.async_api import Page

from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)


class LocatorValidator:

    async def validate(
        self,
        page: Page,
        candidate: LocatorCandidate,
    ) -> LocatorValidationResult:

        try:
            locator = self._build_locator(page, candidate)

            match_count = await locator.count()

            if match_count == 0:
                return LocatorValidationResult(
                    element_id=candidate.element_id,
                    strategy=candidate.strategy,
                    value=candidate.value,
                    locator_type=candidate.locator_type,
                    exists=False,
                    match_count=0,
                    is_unique=False,
                    is_visible=False,
                    is_enabled=False,
                    is_valid=False,
                    reason="No matching elements found",
                )

            is_unique = match_count == 1

            target = locator.first

            is_visible = await target.is_visible()

            # Not every HTML element has a meaningful enabled state.
            # Playwright treats non-form elements as enabled.
            is_enabled = await target.is_enabled()

            is_valid = is_unique and is_visible and is_enabled

            if is_valid:
                reason = "Unique, visible and enabled"
            elif not is_unique:
                reason = f"Locator matched {match_count} elements"
            elif not is_visible:
                reason = "Element is not visible"
            elif not is_enabled:
                reason = "Element is disabled"
            else:
                reason = "Locator validation failed"

            return LocatorValidationResult(
                element_id=candidate.element_id,
                strategy=candidate.strategy,
                value=candidate.value,
                locator_type=candidate.locator_type,
                exists=True,
                match_count=match_count,
                is_unique=is_unique,
                is_visible=is_visible,
                is_enabled=is_enabled,
                is_valid=is_valid,
                reason=reason,
            )

        except Exception as exc:
            return LocatorValidationResult(
                element_id=candidate.element_id,
                strategy=candidate.strategy,
                value=candidate.value,
                locator_type=candidate.locator_type,
                exists=False,
                match_count=0,
                is_unique=False,
                is_visible=False,
                is_enabled=False,
                is_valid=False,
                reason=f"Locator error: {exc}",
            )

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
        """
        Expected role format:

            button:Products

        which becomes:

            get_by_role(
                "button",
                name="Products",
                exact=True
            )
        """

        if ":" in value:
            role, name = value.split(":", 1)

            return page.get_by_role(
                role,
                name=name,
                exact=True,
            )

        return page.get_by_role(value)
