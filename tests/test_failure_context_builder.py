from unittest.mock import AsyncMock

import pytest

from app.models.trace import LocatorDecisionTrace
from app.recovery.failure_context_builder import FailureContextBuilder


class FakePage:

    url = "https://www.ikea.com/in/en/search/"

    async def title(self):
        return "Search results - IKEA"


@pytest.mark.asyncio
async def test_failure_context_captures_page_information():

    builder = FailureContextBuilder()

    context = await builder.build(
        page=FakePage(),
        test_case_id="TC001",
        test_case_name="Search Product",
        step=3,
        action="click",
        target="Product",
        error_message="Locator resolved to no matching elements",
    )

    assert context.test_case_id == "TC001"
    assert context.test_case_name == "Search Product"

    assert context.step == 3
    assert context.action == "click"
    assert context.target == "Product"

    assert context.evidence.failure_type == "LOCATOR_FAILURE"
    assert context.evidence.page_url == "https://www.ikea.com/in/en/search/"
    assert context.evidence.page_title == "Search results - IKEA"


@pytest.mark.asyncio
async def test_failure_context_captures_locator_decision():

    builder = FailureContextBuilder()

    locator_decision = LocatorDecisionTrace(
        target="Product",
        candidates_generated=20,
        candidates_valid=3,
        selected_candidate_id="candidate_1",
        selected_locator_type="role",
        selected_locator_value="button:Product",
        ai_confidence=0.91,
        ai_reason="Selected semantic candidate.",
        final_match_count=2,
        final_is_unique=False,
        final_is_visible=True,
        final_is_enabled=True,
        final_is_valid=False,
    )

    context = await builder.build(
        page=FakePage(),
        test_case_id="TC001",
        test_case_name="Search Product",
        step=3,
        action="click",
        target="Product",
        error_message="Strict mode violation: locator resolved to 2 elements",
        locator_decision=locator_decision,
    )

    evidence = context.evidence

    assert evidence.failure_type == "LOCATOR_FAILURE"

    assert evidence.locator_type == "role"
    assert evidence.locator_value == "button:Product"

    assert evidence.match_count == 2
    assert evidence.is_unique is False
    assert evidence.is_visible is True
    assert evidence.is_enabled is True
    assert evidence.is_valid is False


@pytest.mark.asyncio
async def test_failure_context_without_locator_decision():

    builder = FailureContextBuilder()

    context = await builder.build(
        page=FakePage(),
        test_case_id="TC002",
        test_case_name="Navigation Test",
        step=1,
        action="navigate",
        target="https://example.com",
        error_message="page.goto: net::ERR_NETWORK_CHANGED",
    )

    evidence = context.evidence

    assert evidence.failure_type == "NAVIGATION_FAILURE"

    assert evidence.page_url == ("https://www.ikea.com/in/en/search/")

    assert evidence.locator_type is None
    assert evidence.locator_value is None
    assert evidence.match_count is None


@pytest.mark.asyncio
async def test_failure_context_contains_dom_evidence():

    builder = FailureContextBuilder()

    context = await builder.build(
        page=FakePage(),
        test_case_id="TC001",
        test_case_name="Search Product",
        step=3,
        action="click",
        target="Product",
        error_message="Locator resolved to no matching elements",
    )

    assert context.evidence.dom_evidence is not None
