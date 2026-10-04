import pytest

from playwright.async_api import async_playwright

from app.models.candidate_context import CandidateContext
from app.recovery.ai_recovery_executor import (
    AIRecoveryExecutor,
)


def create_candidate(
    locator_value: str = "button:Product",
) -> CandidateContext:

    return CandidateContext(
        candidate_id="candidate-1",
        element_id="product-1",
        locator_type="role",
        locator_value=locator_value,
        strategy="role",
        priority=90,
        visible=True,
        enabled=True,
        match_count=1,
        is_unique=True,
        is_valid=True,
        confidence=0.90,
        reason="AI recovery candidate",
    )


@pytest.mark.asyncio
async def test_ai_recovery_executor_clicks_valid_candidate():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button id="product">
                Product
            </button>
            """)

        candidate = create_candidate()

        executor = AIRecoveryExecutor()

        result = await executor.execute(
            page=page,
            candidate=candidate,
            action="click",
        )

        assert result.attempted is True
        assert result.success is True
        assert result.retry_attempted is True
        assert result.selected_candidate is not None
        assert result.validation is not None
        assert result.validation.is_valid is True

        await browser.close()


@pytest.mark.asyncio
async def test_ai_recovery_executor_rejects_stale_candidate():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button id="different">
                Different
            </button>
            """)

        candidate = create_candidate()

        executor = AIRecoveryExecutor()

        result = await executor.execute(
            page=page,
            candidate=candidate,
            action="click",
            original_error="Original locator failed",
        )

        assert result.attempted is True
        assert result.success is False
        assert result.retry_attempted is False
        assert result.validation is not None
        assert result.validation.is_valid is False
        assert result.recovery_error is not None

        await browser.close()


@pytest.mark.asyncio
async def test_ai_recovery_executor_rejects_unsupported_action():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button>
                Product
            </button>
            """)

        candidate = create_candidate()

        executor = AIRecoveryExecutor()

        result = await executor.execute(
            page=page,
            candidate=candidate,
            action="navigate",
        )

        assert result.attempted is True
        assert result.success is False
        assert result.retry_attempted is True
        assert result.recovery_error is not None

        await browser.close()
