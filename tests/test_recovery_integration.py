import pytest

from playwright.async_api import async_playwright

from app.browser.page_inspector import PageInspector
from app.models.browser import ElementInfo
from app.recovery.recovery_executor import RecoveryExecutor


@pytest.mark.asyncio
async def test_recovery_can_execute_after_failed_click():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=True)

        page = await browser.new_page()

        await page.set_content("""
            <button
                id="product"
                onclick="
                    document.body.dataset.clicked='true'
                "
            >
                Product
            </button>
            """)

        inspector = PageInspector()

        page_info = await inspector.inspect(page)

        assert len(page_info.elements) > 0

        executor = RecoveryExecutor()

        result = await executor.recover_click(
            page=page,
            elements=page_info.elements,
            original_error=("Locator click failed."),
        )

        assert result.attempted is True
        assert result.success is True
        assert result.retry_attempted is True

        assert result.selected_candidate is not None

        assert result.validation is not None
        assert result.validation.is_valid is True

        clicked = await page.locator("body").get_attribute("data-clicked")

        assert clicked == "true"

        await browser.close()
