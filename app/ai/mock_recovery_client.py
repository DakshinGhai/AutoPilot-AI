from app.models.recovery_ai import (
    RecoverySelectionRequest,
    RecoverySelectionResponse,
)


class MockRecoveryAIClient:

    def __init__(
        self,
        selected_candidate_id: str | None = None,
    ):
        self.selected_candidate_id = selected_candidate_id

    async def select_recovery_candidate(
        self,
        request: RecoverySelectionRequest,
    ) -> RecoverySelectionResponse:

        if not request.candidates:
            raise ValueError("No recovery candidates available.")

        candidate_ids = {candidate.candidate_id for candidate in request.candidates}

        if self.selected_candidate_id:

            if self.selected_candidate_id not in candidate_ids:
                raise ValueError("Selected recovery candidate " "does not exist.")

            selected = self.selected_candidate_id

        else:
            selected = request.candidates[0].candidate_id

        return RecoverySelectionResponse(
            selected_candidate_id=selected,
            reason=("Mock recovery AI selected " "an available candidate."),
            confidence=0.90,
        )
