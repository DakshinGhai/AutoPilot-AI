import pytest

from playwright.async_api import async_playwright

from app.models.candidate_context import (
    CandidateContext,
)

from app.recovery.ai_recovery_validator import (
    AIRecoveryValidator,
)


def create_candidate(
    candidate_id: str,
    locator_value: str,
) -> CandidateContext:

    return CandidateContext(
        candidate_id=candidate_id,
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
        reason="Recovery candidate",
    )


@pytest.mark.asyncio
async def test_ai_selected_candidate_is_revalidated():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button id="product">
                Product
            </button>
            """)

        candidate = create_candidate(
            "candidate-1",
            "button:Product",
        )

        validator = AIRecoveryValidator()

        result = await validator.validate_selected_candidate(
            page,
            candidate,
        )

        assert result.exists is True
        assert result.match_count == 1
        assert result.is_unique is True
        assert result.is_visible is True
        assert result.is_enabled is True
        assert result.is_valid is True

        await browser.close()


@pytest.mark.asyncio
async def test_ai_selected_candidate_is_rejected_when_dom_changed():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button id="different">
                Different Product
            </button>
            """)

        candidate = create_candidate(
            "candidate-1",
            "button:Product",
        )

        validator = AIRecoveryValidator()

        result = await validator.validate_selected_candidate(
            page,
            candidate,
        )

        assert result.exists is False
        assert result.match_count == 0
        assert result.is_valid is False

        await browser.close()


@pytest.mark.asyncio
async def test_ai_selected_candidate_is_rejected_when_not_unique():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button>Product</button>
            <button>Product</button>
            """)

        candidate = create_candidate(
            "candidate-1",
            "button:Product",
        )

        validator = AIRecoveryValidator()

        result = await validator.validate_selected_candidate(
            page,
            candidate,
        )

        assert result.match_count == 2
        assert result.is_unique is False
        assert result.is_valid is False

        await browser.close()
