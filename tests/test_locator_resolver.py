import pytest

from app.execution.browser_manager import BrowserManager
from app.browser.page_inspector import PageInspector
from app.locators.locator_resolver import LocatorResolver


@pytest.mark.asyncio
async def test_locator_resolver():

    browser = BrowserManager(headless=True)

    await browser.start()

    try:
        page = browser.page

        await page.set_content("""
            <html>
                <body>

                    <nav>
                        <button id="products-button">
                            Products
                        </button>
                    </nav>

                </body>
            </html>
            """)

        inspector = PageInspector()

        page_info = await inspector.inspect(page)

        products = None

        for element in page_info.elements:

            if element.text == "Products":
                products = element
                break

        assert products is not None

        resolver = LocatorResolver()

        result = await resolver.resolve(
            page,
            products,
        )

        assert result.success is True
        assert result.selected_locator is not None

        print(
            "\nSelected locator:",
            result.selected_locator.strategy,
            result.selected_locator.value,
        )

        print("\nCandidate validation:")

        for validation in result.validations:
            print(
                validation.strategy,
                validation.value,
                "=>",
                validation.is_valid,
                validation.reason,
            )

    finally:
        await browser.close()
