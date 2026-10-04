from app.models.browser import ElementInfo
from app.models.locator import (
    LocatorCandidate,
    LocatorResolutionResult,
    LocatorValidationResult,
)
from app.locators.locator_generator import LocatorGenerator
from app.locators.locator_ranker import LocatorRanker
from app.locators.locator_validator import LocatorValidator


class LocatorResolver:

    def __init__(self):
        self.generator = LocatorGenerator()
        self.ranker = LocatorRanker()
        self.validator = LocatorValidator()

    async def resolve(
        self,
        page,
        element: ElementInfo,
    ) -> LocatorResolutionResult:

        # -----------------------------------------
        # 1. Generate candidates
        # -----------------------------------------

        candidates = self.generator.generate(element)

        if not candidates:
            return LocatorResolutionResult(
                element_id=element.element_id,
                success=False,
                reason="No locator candidates generated",
            )

        # -----------------------------------------
        # 2. Rank candidates
        # -----------------------------------------

        ranked_candidates = self.ranker.rank(candidates)

        validations = []

        # -----------------------------------------
        # 3. Validate in ranked order
        # -----------------------------------------

        for candidate in ranked_candidates:

            validation = await self.validator.validate(
                page,
                candidate,
            )

            validations.append(validation)

            # Store validation information
            # back on the candidate.
            candidate.is_valid = validation.is_valid
            candidate.is_unique = validation.is_unique
            candidate.reason = validation.reason

            # -------------------------------------
            # First valid candidate wins
            # -------------------------------------

            if validation.is_valid:

                return LocatorResolutionResult(
                    element_id=element.element_id,
                    selected_locator=candidate,
                    candidates=ranked_candidates,
                    validations=validations,
                    success=True,
                    reason="Valid locator found",
                )

        # -----------------------------------------
        # No candidate survived validation
        # -----------------------------------------

        return LocatorResolutionResult(
            element_id=element.element_id,
            selected_locator=None,
            candidates=ranked_candidates,
            validations=validations,
            success=False,
            reason="No valid locator found",
        )
