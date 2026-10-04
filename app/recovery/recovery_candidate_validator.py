from playwright.async_api import Page

from app.locators.locator_validator import LocatorValidator
from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)


class RecoveryCandidateValidator:

    def __init__(
        self,
        validator: LocatorValidator | None = None,
    ):
        self.validator = validator or LocatorValidator()

    async def validate(
        self,
        page: Page,
        candidates: list[LocatorCandidate],
    ) -> list[LocatorValidationResult]:

        validations: list[LocatorValidationResult] = []

        for candidate in candidates:

            validation = await self.validator.validate(
                page,
                candidate,
            )

            validations.append(validation)

        return validations

    async def validate_and_filter(
        self,
        page: Page,
        candidates: list[LocatorCandidate],
    ) -> list[
        tuple[
            LocatorCandidate,
            LocatorValidationResult,
        ]
    ]:

        results = await self.validate(
            page,
            candidates,
        )

        candidate_results = []

        for candidate, validation in zip(
            candidates,
            results,
        ):
            if validation.is_valid:
                candidate_results.append(
                    (
                        candidate,
                        validation,
                    )
                )

        return candidate_results
