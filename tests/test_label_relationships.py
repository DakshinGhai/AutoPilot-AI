import pytest

from app.execution.browser_manager import BrowserManager
from app.browser.dom_extractor import DOMExtractor
from app.locators.locator_generator import LocatorGenerator
from app.locators.locator_validator import LocatorValidator


@pytest.mark.asyncio
async def test_label_relationships():
    browser = BrowserManager(headless=True)

    page = await browser.start()

    try:

        await page.set_content("""
            <html>
                <body>

                    <form>

                        <label for="email">
                            Email Address
                        </label>

                        <input
                            id="email"
                            type="text"
                        />

                        <label>
                            Password
                            <input
                                id="password"
                                type="password"
                            />
                        </label>

                        <input
                            id="search"
                            type="text"
                            placeholder="Search products"
                        />

                    </form>

                </body>
            </html>
            """)

        extractor = DOMExtractor()

        elements = await extractor.extract_elements(page)

        email = next(element for element in elements if element.id == "email")

        password = next(element for element in elements if element.id == "password")

        search = next(element for element in elements if element.id == "search")

        # --------------------------------------------
        # Explicit label
        # --------------------------------------------

        assert email.label_text == "Email Address"

        assert email.accessible_name == ("Email Address")

        # --------------------------------------------
        # Wrapped label
        # --------------------------------------------

        assert password.label_text == "Password"

        assert password.accessible_name == ("Password")

        # --------------------------------------------
        # No HTML label
        # --------------------------------------------

        assert search.label_text == ""

        # --------------------------------------------
        # Locator generation
        # --------------------------------------------

        generator = LocatorGenerator()

        email_candidates = generator.generate(email)

        password_candidates = generator.generate(password)

        search_candidates = generator.generate(search)

        email_label = [
            candidate for candidate in email_candidates if candidate.strategy == "label"
        ]

        password_label = [
            candidate
            for candidate in password_candidates
            if candidate.strategy == "label"
        ]

        search_label = [
            candidate
            for candidate in search_candidates
            if candidate.strategy == "label"
        ]

        assert len(email_label) == 1
        assert email_label[0].value == "Email Address"
        assert email_label[0].locator_type == "label"

        assert len(password_label) == 1
        assert password_label[0].value == "Password"
        assert password_label[0].locator_type == "label"

        assert len(search_label) == 0

        # --------------------------------------------
        # Validate with Playwright
        # --------------------------------------------

        validator = LocatorValidator()

        email_result = await validator.validate(
            page,
            email_label[0],
        )

        password_result = await validator.validate(
            page,
            password_label[0],
        )

        assert email_result.is_valid is True
        assert email_result.is_unique is True
        assert email_result.is_visible is True
        assert email_result.is_enabled is True

        assert password_result.is_valid is True
        assert password_result.is_unique is True
        assert password_result.is_visible is True
        assert password_result.is_enabled is True

    finally:

        await browser.close()
