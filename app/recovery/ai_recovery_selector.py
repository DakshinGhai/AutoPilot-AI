from app.ai.recovery_client import RecoveryAIClient

from app.models.candidate_context import (
    CandidateContext,
)

from app.models.recovery_ai import (
    RecoverySelectionRequest,
    RecoverySelectionResponse,
)


class AIRecoverySelector:

    def __init__(
        self,
        ai_client: RecoveryAIClient,
    ):
        self.ai_client = ai_client

    async def select(
        self,
        test_step: str,
        target: str,
        original_error: str,
        candidates: list[CandidateContext],
        page_url: str | None = None,
        page_title: str | None = None,
    ) -> tuple[
        RecoverySelectionResponse,
        CandidateContext,
    ]:

        if not candidates:
            raise ValueError("Cannot select recovery candidate " "without candidates.")

        request = RecoverySelectionRequest(
            test_step=test_step,
            target=target,
            original_error=original_error,
            page_url=page_url,
            page_title=page_title,
            candidates=candidates,
        )

        response = await self.ai_client.select_recovery_candidate(request)

        selected = next(
            (
                candidate
                for candidate in candidates
                if candidate.candidate_id == response.selected_candidate_id
            ),
            None,
        )

        if selected is None:
            raise ValueError("AI selected an unknown recovery " "candidate.")

        return response, selected
