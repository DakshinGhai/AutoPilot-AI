from app.models.candidate_context import CandidateContext
from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)


class RecoveryContextBuilder:

    def build(
        self,
        candidate: LocatorCandidate,
        validation: LocatorValidationResult | None = None,
    ) -> CandidateContext:

        return CandidateContext(
            candidate_id=self._build_candidate_id(candidate),
            element_id=candidate.element_id,
            locator_type=candidate.locator_type,
            locator_value=candidate.value,
            strategy=candidate.strategy,
            priority=candidate.priority,
            semantic_evidence=(candidate.semantic_evidence),
            visible=(validation.is_visible if validation else False),
            enabled=(validation.is_enabled if validation else False),
            match_count=(validation.match_count if validation else None),
            is_unique=(validation.is_unique if validation else candidate.is_unique),
            is_valid=(validation.is_valid if validation else candidate.is_valid),
            confidence=candidate.confidence,
            reason=candidate.reason,
        )

    def build_many(
        self,
        candidates: list[LocatorCandidate],
        validations: list[LocatorValidationResult] | None = None,
    ) -> list[CandidateContext]:

        contexts = []

        for index, candidate in enumerate(candidates):

            validation = None

            if validations is not None:
                if index < len(validations):
                    validation = validations[index]

            contexts.append(
                self.build(
                    candidate,
                    validation,
                )
            )

        return contexts

    @staticmethod
    def _build_candidate_id(
        candidate: LocatorCandidate,
    ) -> str:

        return (
            f"{candidate.element_id}:"
            f"{candidate.locator_type}:"
            f"{candidate.strategy}"
        )
