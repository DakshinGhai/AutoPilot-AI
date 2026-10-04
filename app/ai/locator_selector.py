from app.ai.client import AIClient
from app.models.ai import (
    LocatorSelectionRequest,
    LocatorSelectionResponse,
)
from app.models.candidate_context import CandidateContext


class LocatorSelectionService:

    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def select(
        self,
        request: LocatorSelectionRequest,
    ) -> tuple[
        LocatorSelectionResponse,
        CandidateContext,
    ]:

        if not request.candidates:
            raise ValueError("Cannot select locator without candidates")

        response = await self.ai_client.select_locator(request)

        selected = next(
            (
                candidate
                for candidate in request.candidates
                if candidate.candidate_id == response.selected_candidate_id
            ),
            None,
        )

        if selected is None:
            raise ValueError("AI selected an unknown candidate")

        return response, selected
