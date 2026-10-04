import pytest

from app.execution.browser_manager import BrowserManager
from app.browser.dom_extractor import DOMExtractor
from app.locators.locator_generator import LocatorGenerator
from app.locators.locator_validator import LocatorValidator


@pytest.mark.asyncio
async def test_aria_relationships():

    browser = BrowserManager(headless=True)

    page = await browser.start()

    try:

        await page.set_content("""
            <html>
                <body>

                    <span id="email-label">
                        Email Address
                    </span>

                    <span id="email-help">
                        Enter your work email
                    </span>

                    <input
                        id="email"
                        type="text"
                        aria-labelledby="email-label"
                        aria-describedby="email-help"
                    />


                    <span id="password-label">
                        Password
                    </span>

                    <span id="password-help">
                        Minimum 8 characters
                    </span>

                    <span id="password-error">
                        Password is required
                    </span>

                    <input
                        id="password"
                        type="password"
                        aria-labelledby="password-label"
                        aria-describedby="
                            password-help
                            password-error
                        "
                    />


                    <span id="first-name">
                        First
                    </span>

                    <span id="last-name">
                        Name
                    </span>

                    <button
                        id="submit"
                        aria-labelledby="
                            first-name
                            last-name
                        "
                    >
                        Submit
                    </button>


                    <span id="broken-label">
                        Broken Example
                    </span>

                    <button
                        id="broken"
                        aria-labelledby="
                            missing-label
                            broken-label
                        "
                    >
                        Click
                    </button>

                </body>
            </html>
            """)

        extractor = DOMExtractor()

        elements = await extractor.extract_elements(page)

        assert len(elements) > 0

        # --------------------------------------------------
        # aria-labelledby + aria-describedby
        # --------------------------------------------------

        email = next(element for element in elements if element.id == "email")

        assert email.role == "textbox"

        assert email.aria_labelledby == "email-label"

        assert email.aria_describedby == "email-help"

        assert email.accessible_name == "Email Address"

        assert email.accessible_description == "Enter your work email"

        # --------------------------------------------------
        # Multiple aria-describedby references
        # --------------------------------------------------

        password = next(element for element in elements if element.id == "password")

        assert password.role == "textbox"

        assert password.accessible_name == "Password"

        assert password.accessible_description == (
            "Minimum 8 characters " "Password is required"
        )

        # --------------------------------------------------
        # Multiple aria-labelledby references
        # --------------------------------------------------

        submit = next(element for element in elements if element.id == "submit")

        assert submit.role == "button"

        assert submit.accessible_name == "First Name"

        # --------------------------------------------------
        # Broken reference should not break extraction
        # --------------------------------------------------

        broken = next(element for element in elements if element.id == "broken")

        assert broken.accessible_name == "Broken Example"

        # --------------------------------------------------
        # Role locator must use resolved accessible name
        # --------------------------------------------------

        generator = LocatorGenerator()

        email_candidates = generator.generate(email)

        email_role_candidates = [
            candidate for candidate in email_candidates if candidate.strategy == "role"
        ]

        assert len(email_role_candidates) == 1

        assert email_role_candidates[0].value == "textbox:Email Address"

        # --------------------------------------------------
        # Validate role locator through Playwright
        # --------------------------------------------------

        validator = LocatorValidator()

        result = await validator.validate(page, email_role_candidates[0])

        assert result.exists is True
        assert result.match_count == 1
        assert result.is_unique is True
        assert result.is_visible is True
        assert result.is_enabled is True
        assert result.is_valid is True

    finally:

        await browser.close()
