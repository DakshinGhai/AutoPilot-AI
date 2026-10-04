import pytest

from app.ai.locator_executor import AILocatorExecutor
from app.models.ai import LocatorSelectionResponse
from app.models.candidate_context import CandidateContext
from app.models.locator import LocatorCandidate
from app.locators.locator_validator import (
    LocatorValidator,
)


def create_candidate_context(
    locator_type="css",
    locator_value="#products-button",
):
    return CandidateContext(
        candidate_id="candidate-1",
        element_id="element-1",
        locator_type=locator_type,
        locator_value=locator_value,
        strategy="id",
        priority=100,
        visible=True,
        enabled=True,
        match_count=1,
        is_unique=True,
        is_valid=True,
        confidence=0.95,
        reason="Stable ID",
    )


def create_ai_response():

    return LocatorSelectionResponse(
        selected_candidate_id="candidate-1",
        reason="Stable and unique locator",
        confidence=0.95,
    )


@pytest.mark.asyncio
async def test_build_css_locator():

    executor = AILocatorExecutor(LocatorValidator())

    class FakePage:

        def locator(self, value):
            return "css:" + value

    candidate = create_candidate_context()

    locator = executor._build_locator(
        FakePage(),
        candidate,
    )

    assert locator == ("css:#products-button")


@pytest.mark.asyncio
async def test_build_xpath_locator():

    executor = AILocatorExecutor(LocatorValidator())

    class FakePage:

        def locator(self, value):
            return value

    candidate = create_candidate_context(
        locator_type="xpath",
        locator_value=("//button[@id='products-button']"),
    )

    locator = executor._build_locator(
        FakePage(),
        candidate,
    )

    assert locator == ("xpath=//button[@id='products-button']")


@pytest.mark.asyncio
async def test_build_role_locator():

    executor = AILocatorExecutor(LocatorValidator())

    class FakePage:

        def get_by_role(
            self,
            role,
            name=None,
            exact=False,
        ):
            return (
                role,
                name,
                exact,
            )

    candidate = create_candidate_context(
        locator_type="role",
        locator_value="button:Products",
    )

    locator = executor._build_locator(
        FakePage(),
        candidate,
    )

    assert locator == (
        "button",
        "Products",
        True,
    )


@pytest.mark.asyncio
async def test_build_label_locator():

    executor = AILocatorExecutor(LocatorValidator())

    class FakePage:

        def get_by_label(
            self,
            value,
            exact=False,
        ):
            return (
                value,
                exact,
            )

    candidate = create_candidate_context(
        locator_type="label",
        locator_value="Email",
    )

    locator = executor._build_locator(
        FakePage(),
        candidate,
    )

    assert locator == (
        "Email",
        True,
    )


def test_unsupported_locator_type():

    executor = AILocatorExecutor(LocatorValidator())

    class FakePage:
        pass

    candidate = create_candidate_context(
        locator_type="unsupported",
        locator_value="something",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported locator type",
    ):
        executor._build_locator(
            FakePage(),
            candidate,
        )


def test_context_to_candidate():

    executor = AILocatorExecutor(LocatorValidator())

    context = create_candidate_context()

    candidate = executor._candidate_from_context(context)

    assert isinstance(
        candidate,
        LocatorCandidate,
    )

    assert candidate.value == "#products-button"

    assert candidate.locator_type == "css"

    assert candidate.is_valid is True
