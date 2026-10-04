import pytest

from app.ai.locator_selector import (
    LocatorSelectionService,
)

from app.ai.mock_client import (
    MockAIClient,
)

from app.models.ai import (
    LocatorSelectionRequest,
)

from app.models.candidate_context import (
    CandidateContext,
)


@pytest.mark.asyncio
async def test_ai_selects_existing_candidate():

    candidates = [
        CandidateContext(
            candidate_id="candidate_1:role:role",
            element_id="candidate_1",
            locator_type="role",
            locator_value="button:Products",
            strategy="role",
            priority=5,
            visible=True,
            enabled=True,
            match_count=1,
            is_unique=True,
            is_valid=True,
        ),
        CandidateContext(
            candidate_id="candidate_1:css:css",
            element_id="candidate_1",
            locator_type="css",
            locator_value="button.products",
            strategy="css",
            priority=9,
            visible=True,
            enabled=True,
            match_count=1,
            is_unique=True,
            is_valid=True,
        ),
    ]

    request = LocatorSelectionRequest(
        test_step="Click Products",
        target="Products",
        page_url="https://example.com",
        page_title="Example",
        candidates=candidates,
    )

    client = MockAIClient(selected_candidate_id=("candidate_1:role:role"))

    service = LocatorSelectionService(client)

    response, selected = await service.select(request)

    assert response.selected_candidate_id == "candidate_1:role:role"

    assert selected.locator_type == "role"

    assert selected.locator_value == "button:Products"


@pytest.mark.asyncio
async def test_ai_cannot_select_unknown_candidate():

    candidates = [
        CandidateContext(
            candidate_id="candidate_1:role:role",
            element_id="candidate_1",
            locator_type="role",
            locator_value="button:Products",
            strategy="role",
            priority=5,
        )
    ]

    request = LocatorSelectionRequest(
        test_step="Click Products",
        target="Products",
        candidates=candidates,
    )

    client = MockAIClient(selected_candidate_id="fake-candidate")

    service = LocatorSelectionService(client)

    with pytest.raises(ValueError):
        await service.select(request)


@pytest.mark.asyncio
async def test_ai_selection_requires_candidates():

    request = LocatorSelectionRequest(
        test_step="Click Products",
        target="Products",
        candidates=[],
    )

    client = MockAIClient()

    service = LocatorSelectionService(client)

    with pytest.raises(ValueError):
        await service.select(request)


from pydantic import ValidationError

from app.models.ai import (
    LocatorSelectionResponse,
)


def test_ai_response_confidence_must_be_valid():

    response = LocatorSelectionResponse(
        selected_candidate_id="candidate_1",
        reason="Semantic locator",
        confidence=0.95,
    )

    assert response.confidence == 0.95


def test_ai_response_rejects_invalid_confidence():

    with pytest.raises(ValidationError):

        LocatorSelectionResponse(
            selected_candidate_id="candidate_1",
            reason="Invalid",
            confidence=2.0,
        )
