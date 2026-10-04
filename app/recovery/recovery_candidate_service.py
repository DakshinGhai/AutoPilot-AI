from app.locators.locator_ranker import LocatorRanker
from app.models.locator import LocatorCandidate
from app.recovery.recovery_candidate_generator import (
    RecoveryCandidateGenerator,
)


class RecoveryCandidateService:

    def __init__(
        self,
        generator: RecoveryCandidateGenerator | None = None,
        ranker: LocatorRanker | None = None,
    ):
        self.generator = generator or RecoveryCandidateGenerator()
        self.ranker = ranker or LocatorRanker()

    def generate_and_rank(
        self,
        elements,
        failed_element_id: str | None = None,
    ) -> list[LocatorCandidate]:

        candidates = self.generator.generate(
            elements,
            failed_element_id=failed_element_id,
        )

        return self.ranker.rank(candidates)
