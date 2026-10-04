import pytest
from playwright.async_api import async_playwright

from app.browser.dom_extractor import DOMExtractor
from app.execution.action_executor import ActionExecutor
from app.execution.ai_action_executor import AIActionExecutor


@pytest.mark.asyncio
async def test_ikea_first_chair_product_resolution():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=False)

        page = await browser.new_page(
            viewport={
                "width": 1440,
                "height": 900,
            }
        )

        try:

            await page.goto(
                "https://www.ikea.com/in/en/",
                wait_until="domcontentloaded",
            )

            action_executor = ActionExecutor(page)

            await action_executor.search("chair")

            await page.wait_for_timeout(5000)

            extractor = DOMExtractor()

            elements = await extractor.extract_elements(page)

            resolver = AIActionExecutor(
                page,
                selection_service=None,
            )

            product = resolver._find_first_product_element(
                elements,
                "First chair product",
            )

            assert product is not None

            print("\nFIRST CHAIR PRODUCT:")

            print(f"Element ID: " f"{product.element_id}")

            print(f"Name: " f"{product.accessible_name}")

            print(f"Href: " f"{product.href}")

            assert product.tag == "a"
            assert product.role == "link"
            assert "/p/" in product.href
            assert "chair" in (product.accessible_name or "").lower()

            await page.wait_for_timeout(5000)

        finally:

            await browser.close()
