import pytest

from playwright.async_api import async_playwright

from app.models.browser import ElementInfo

from app.recovery.recovery_executor import (
    RecoveryExecutor,
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
async def test_recovery_executor_clicks_valid_candidate():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button id="product-1"
                    onclick="document.body.dataset.clicked='true'">
                Product
            </button>
            """)

        elements = [
            create_button(
                "product-1",
                "Product",
            )
        ]

        executor = RecoveryExecutor()

        result = await executor.recover_click(
            page=page,
            elements=elements,
            original_error=("Original locator failed."),
            target="Product",
        )

        assert result.attempted is True
        assert result.success is True
        assert result.retry_attempted is True

        assert result.selected_candidate is not None
        assert result.validation is not None
        assert result.validation.is_valid is True

        assert result.original_error == ("Original locator failed.")

        clicked = await page.locator("body").get_attribute("data-clicked")

        assert clicked == "true"

        await browser.close()


@pytest.mark.asyncio
async def test_recovery_executor_fails_when_no_candidate_is_valid():

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

        executor = RecoveryExecutor()

        result = await executor.recover_click(
            page=page,
            elements=elements,
            original_error=("Original locator failed."),
        )

        assert result.attempted is True
        assert result.success is False
        assert result.retry_attempted is False

        assert result.selected_candidate is None
        assert result.validation is None

        assert result.recovery_error == ("No valid recovery candidates found.")

        await browser.close()


@pytest.mark.asyncio
async def test_recovery_executor_excludes_failed_element():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button id="failed-product">
                Product
            </button>

            <button id="alternative-product"
                    onclick="document.body.dataset.clicked='true'">
                Product Details
            </button>
            """)

        elements = [
            create_button(
                "failed-product",
                "Product",
            ),
            create_button(
                "alternative-product",
                "Product Details",
            ),
        ]

        executor = RecoveryExecutor()

        result = await executor.recover_click(
            page=page,
            elements=elements,
            original_error=("Original locator failed."),
            failed_element_id="failed-product",
        )

        assert result.success is True
        assert result.selected_candidate is not None

        assert result.selected_candidate.element_id != "failed-product"

        clicked = await page.locator("body").get_attribute("data-clicked")

        assert clicked == "true"

        await browser.close()
