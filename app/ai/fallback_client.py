from app.models.ai import (
    LocatorSelectionRequest,
    LocatorSelectionResponse,
)


class DeterministicFallbackClient:

    async def select_locator(
        self,
        request: LocatorSelectionRequest,
    ) -> LocatorSelectionResponse:

        if not request.candidates:
            raise ValueError("Cannot select locator without candidates")

        valid_candidates = [
            candidate for candidate in request.candidates if candidate.is_valid is True
        ]

        candidates = valid_candidates if valid_candidates else request.candidates

        selected = sorted(
            candidates,
            key=lambda candidate: (
                candidate.priority,
                candidate.confidence or 0.0,
            ),
            reverse=True,
        )[0]

        return LocatorSelectionResponse(
            selected_candidate_id=selected.candidate_id,
            reason=(
                "Deterministic fallback selected the "
                "highest-ranked available candidate."
            ),
            confidence=selected.confidence or 0.50,
        )
