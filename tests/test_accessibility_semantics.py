import pytest

from app.browser.dom_extractor import DOMExtractor
from app.execution.browser_manager import BrowserManager
from app.locators.locator_generator import LocatorGenerator


@pytest.mark.asyncio
async def test_accessible_name_resolution():

    browser = BrowserManager(headless=True)

    page = await browser.start()

    try:

        await page.set_content("""
            <html>
                <body>

                    <button
                        id="products"
                        aria-label="Products"
                    >
                        Product Menu
                    </button>

                    <button id="rooms">
                        Rooms
                    </button>

                    <form
                        id="search-form"
                        role="search"
                    >
                        <button>
                            Clear
                        </button>

                        <button>
                            Search
                        </button>
                    </form>

                    <span id="postal-label">
                        Postal code
                    </span>

                    <button
                        id="postal"
                        aria-labelledby="postal-label"
                    >
                        Enter
                    </button>

                </body>
            </html>
            """)

        extractor = DOMExtractor()

        elements = await extractor.extract_elements(page)

        assert len(elements) > 0

        products = next(element for element in elements if element.id == "products")

        assert products.accessible_name == "Products"

        rooms = next(element for element in elements if element.id == "rooms")

        assert rooms.accessible_name == "Rooms"

        search_form = next(
            element for element in elements if element.id == "search-form"
        )

        assert search_form.accessible_name == ""

        postal = next(element for element in elements if element.id == "postal")

        assert postal.accessible_name == "Postal code"

        generator = LocatorGenerator()

        product_candidates = generator.generate(products)

        role_candidates = [
            candidate
            for candidate in product_candidates
            if candidate.strategy == "role"
        ]

        assert len(role_candidates) == 1

        assert role_candidates[0].value == "button:Products"

    finally:

        await browser.close()
