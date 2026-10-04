import pytest

from app.execution.browser_manager import BrowserManager
from app.browser.dom_extractor import DOMExtractor
from app.locators.locator_generator import LocatorGenerator


@pytest.mark.asyncio
async def test_role_locator_requires_accessible_name():

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

                </body>
            </html>
            """)

        extractor = DOMExtractor()

        elements = await extractor.extract_elements(page)

        products = next(element for element in elements if element.id == "products")

        search_form = next(
            element for element in elements if element.id == "search-form"
        )

        # Product button should have semantic information.
        assert products.role == "button"
        assert products.accessible_name == "Products"

        # Search container intentionally has no accessible name.
        assert search_form.role == "search"
        assert search_form.accessible_name == ""

        generator = LocatorGenerator()

        product_candidates = generator.generate(products)

        search_candidates = generator.generate(search_form)

        product_role_candidates = [
            candidate
            for candidate in product_candidates
            if candidate.strategy == "role"
        ]

        search_role_candidates = [
            candidate for candidate in search_candidates if candidate.strategy == "role"
        ]

        # Semantic button locator must be generated.
        assert len(product_role_candidates) == 1

        assert product_role_candidates[0].value == "button:Products"

        # Do not invent a role locator from descendant text.
        assert len(search_role_candidates) == 0

    finally:

        await browser.close()
