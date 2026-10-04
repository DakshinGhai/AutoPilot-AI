import pytest

from app.ai.fallback_client import DeterministicFallbackClient
from app.models.ai import LocatorSelectionRequest
from app.models.candidate_context import CandidateContext


def create_request():

    candidates = [
        CandidateContext(
            candidate_id="low",
            element_id="element-1",
            locator_type="text",
            locator_value="Products",
            strategy="text",
            priority=70,
            visible=True,
            enabled=True,
            match_count=1,
            is_unique=True,
            is_valid=True,
            confidence=0.70,
        ),
        CandidateContext(
            candidate_id="high",
            element_id="element-1",
            locator_type="role",
            locator_value="button:Products",
            strategy="role",
            priority=90,
            visible=True,
            enabled=True,
            match_count=1,
            is_unique=True,
            is_valid=True,
            confidence=0.90,
        ),
    ]

    return LocatorSelectionRequest(
        test_step="Click Products",
        target="Products button",
        candidates=candidates,
    )


@pytest.mark.asyncio
async def test_fallback_selects_highest_ranked_candidate():

    client = DeterministicFallbackClient()

    response = await client.select_locator(create_request())

    assert response.selected_candidate_id == "high"


@pytest.mark.asyncio
async def test_fallback_rejects_empty_candidates():

    client = DeterministicFallbackClient()

    request = LocatorSelectionRequest(
        test_step="Click Products",
        target="Products",
        candidates=[],
    )

    with pytest.raises(ValueError):
        await client.select_locator(request)
