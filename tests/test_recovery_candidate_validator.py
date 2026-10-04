import pytest
from playwright.async_api import async_playwright

from app.models.browser import ElementInfo
from app.recovery.recovery_candidate_service import (
    RecoveryCandidateService,
)
from app.recovery.recovery_candidate_validator import (
    RecoveryCandidateValidator,
)
from app.recovery.recovery_validation_service import (
    RecoveryValidationService,
)


def create_button(
    element_id: str,
    text: str,
) -> ElementInfo:

    return ElementInfo(
        element_id=element_id,
        tag="button",
        id=element_id,
        class_name="product-button",
        name="",
        role="button",
        aria_label="",
        aria_labelledby="",
        aria_describedby="",
        accessible_name=text,
        accessible_description="",
        label_text="",
        placeholder="",
        title="",
        text=text,
        inner_text=text,
        value="",
        href="",
        type="button",
        alt="",
        data_testid="",
        data_test="",
        data_cy="",
        visible=True,
        enabled=True,
        bounding_box=None,
        parent_tag="div",
        parent_text="",
        nearby_text="",
        dom_path=(f"/html/body/button[@id='{element_id}']"),
        attributes={},
    )


@pytest.mark.asyncio
async def test_recovery_candidate_is_validated():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(
            headless=True,
            channel="chrome",
        )

        page = await browser.new_page()

        await page.set_content("""
            <button id="product-1">
                Product
            </button>
            """)

        elements = [
            create_button(
                "product-1",
                "Product",
            )
        ]

        candidate_service = RecoveryCandidateService()

        candidates = candidate_service.generate_and_rank(elements)

        validator = RecoveryCandidateValidator()

        results = await validator.validate(
            page,
            candidates,
        )

        assert len(results) > 0

        valid_results = [result for result in results if result.is_valid]

        assert len(valid_results) > 0

        assert all(result.match_count == 1 for result in valid_results)

        assert all(result.is_unique for result in valid_results)

        assert all(result.is_visible for result in valid_results)

        assert all(result.is_enabled for result in valid_results)

        await browser.close()


@pytest.mark.asyncio
async def test_invalid_recovery_candidate_is_rejected():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button id="real-product">
                Product
            </button>
            """)

        elements = [
            create_button(
                "missing-product",
                "Missing Product",
            )
        ]

        candidate_service = RecoveryCandidateService()

        candidates = candidate_service.generate_and_rank(elements)

        validator = RecoveryCandidateValidator()

        results = await validator.validate(
            page,
            candidates,
        )

        assert len(results) > 0

        assert all(not result.is_valid for result in results)

        assert any(result.match_count == 0 for result in results)

        await browser.close()


@pytest.mark.asyncio
async def test_validate_and_filter_returns_only_valid_candidates():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button id="product-1">
                Product
            </button>

            <button id="product-2">
                Product Details
            </button>
            """)

        elements = [
            create_button(
                "product-1",
                "Product",
            ),
            create_button(
                "missing-product",
                "Missing Product",
            ),
        ]

        candidate_service = RecoveryCandidateService()

        candidates = candidate_service.generate_and_rank(elements)

        validator = RecoveryCandidateValidator()

        valid_candidates = await validator.validate_and_filter(
            page,
            candidates,
        )

        assert len(valid_candidates) > 0

        for candidate, validation in valid_candidates:

            assert validation.is_valid

            assert validation.match_count == 1

            assert validation.is_unique

            assert validation.is_visible

            assert validation.is_enabled

            assert candidate.element_id != ("missing-product")

        await browser.close()


@pytest.mark.asyncio
async def test_recovery_validation_service_runs_full_pipeline():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button id="product-1">
                Product
            </button>
            """)

        elements = [
            create_button(
                "product-1",
                "Product",
            )
        ]

        service = RecoveryValidationService()

        results = await service.generate_validate(
            page,
            elements,
        )

        assert len(results) > 0

        assert any(validation.is_valid for _, validation in results)

        await browser.close()
