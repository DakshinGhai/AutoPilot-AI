from playwright.async_api import Page

from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)

from app.recovery.recovery_candidate_service import (
    RecoveryCandidateService,
)

from app.recovery.recovery_candidate_validator import (
    RecoveryCandidateValidator,
)

from app.recovery.recovery_ranker import (
    RecoveryRanker,
)


class RecoveryValidationService:

    def __init__(
        self,
        candidate_service: RecoveryCandidateService | None = None,
        candidate_validator: RecoveryCandidateValidator | None = None,
        recovery_ranker: RecoveryRanker | None = None,
    ):
        self.candidate_service = candidate_service or RecoveryCandidateService()

        self.candidate_validator = candidate_validator or RecoveryCandidateValidator()

        self.recovery_ranker = recovery_ranker or RecoveryRanker()

    async def generate_validate(
        self,
        page: Page,
        elements,
        failed_element_id: str | None = None,
        target: str | None = None,
    ) -> list[
        tuple[
            LocatorCandidate,
            LocatorValidationResult,
        ]
    ]:

        candidates = self.candidate_service.generate_and_rank(
            elements,
            failed_element_id=failed_element_id,
        )

        candidates = self.recovery_ranker.rank(
            candidates,
            elements,
            target=target,
        )

        valid_candidates = await self.candidate_validator.validate_and_filter(
            page,
            candidates,
        )

        return valid_candidates
