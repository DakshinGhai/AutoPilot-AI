from playwright.async_api import Page

from app.locators.locator_validator import (
    LocatorValidator,
)

from app.models.candidate_context import (
    CandidateContext,
)

from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)


class AIRecoveryValidator:

    def __init__(
        self,
        validator: LocatorValidator | None = None,
    ):
        self.validator = validator or LocatorValidator()

    async def validate_selected_candidate(
        self,
        page: Page,
        candidate: CandidateContext,
    ) -> LocatorValidationResult:

        locator_candidate = self._candidate_from_context(candidate)

        return await self.validator.validate(
            page,
            locator_candidate,
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
            semantic_evidence=(candidate.semantic_evidence),
            is_unique=candidate.is_unique,
            is_valid=candidate.is_valid,
        )
