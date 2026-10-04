import pytest

from app.execution.browser_manager import BrowserManager
from app.browser.page_inspector import PageInspector


@pytest.mark.asyncio
async def test_dom_extraction():

    browser = BrowserManager(headless=True)

    page = await browser.start()

    try:

        await page.goto(
            "https://www.ikea.com/in/en/",
            wait_until="domcontentloaded",
        )

        inspector = PageInspector()

        page_info = await inspector.inspect(page)

        # Basic page information
        assert page_info.url
        assert page_info.title

        # DOM extraction must return elements
        assert len(page_info.elements) > 0

        # Inspect first extracted element
        element = page_info.elements[0]

        assert element.element_id
        assert element.tag

        # Locator intelligence fields
        assert hasattr(element, "text")
        assert hasattr(element, "role")
        assert hasattr(element, "aria_label")
        assert hasattr(element, "visible")
        assert hasattr(element, "enabled")
        assert hasattr(element, "dom_path")
        assert hasattr(element, "attributes")

    finally:

        await browser.close()
