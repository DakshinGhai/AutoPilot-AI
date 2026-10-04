from app.models.ai import (
    LocatorSelectionRequest,
    LocatorSelectionResponse,
)


class MockAIClient:

    def __init__(
        self,
        selected_candidate_id: str | None = None,
    ):
        self.selected_candidate_id = selected_candidate_id

    async def select_locator(
        self,
        request: LocatorSelectionRequest,
    ) -> LocatorSelectionResponse:

        if not request.candidates:
            raise ValueError("No locator candidates available")

        if self.selected_candidate_id:

            candidate_ids = {candidate.candidate_id for candidate in request.candidates}

            if self.selected_candidate_id not in candidate_ids:
                raise ValueError("Selected candidate does not exist")

            selected = self.selected_candidate_id

        else:

            # Deterministic fallback used only
            # for testing the AI boundary.
            selected = request.candidates[0].candidate_id

        return LocatorSelectionResponse(
            selected_candidate_id=selected,
            reason=("Mock AI selected an available " "browser-backed candidate."),
            confidence=0.90,
        )
