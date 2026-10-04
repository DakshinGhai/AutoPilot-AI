import pytest

from app.execution.browser_manager import BrowserManager
from app.locators.locator_validator import LocatorValidator
from app.models.locator import LocatorCandidate


@pytest.mark.asyncio
async def test_locator_validation():

    browser = BrowserManager(headless=True)

    await browser.start()

    try:
        page = browser.page

        await page.set_content("""
            <html>
                <body>

                    <button
                        id="products-button"
                        aria-label="Products"
                    >
                        Products
                    </button>

                    <button>
                        Duplicate
                    </button>

                    <button>
                        Duplicate
                    </button>

                    <button
                        id="hidden-button"
                        style="display:none;"
                    >
                        Hidden
                    </button>

                </body>
            </html>
            """)

        validator = LocatorValidator()

        # -----------------------------------------
        # 1. Unique + visible + enabled
        # -----------------------------------------

        candidate = LocatorCandidate(
            element_id="candidate_1",
            strategy="id",
            value="#products-button",
            locator_type="css",
        )

        result = await validator.validate(
            page,
            candidate,
        )

        assert result.exists is True
        assert result.match_count == 1
        assert result.is_unique is True
        assert result.is_visible is True
        assert result.is_enabled is True
        assert result.is_valid is True

        # -----------------------------------------
        # 2. Duplicate locator
        # -----------------------------------------

        duplicate_candidate = LocatorCandidate(
            element_id="candidate_2",
            strategy="text",
            value="Duplicate",
            locator_type="text",
        )

        duplicate_result = await validator.validate(
            page,
            duplicate_candidate,
        )

        assert duplicate_result.exists is True
        assert duplicate_result.match_count == 2
        assert duplicate_result.is_unique is False
        assert duplicate_result.is_valid is False

        # -----------------------------------------
        # 3. Hidden element
        # -----------------------------------------

        hidden_candidate = LocatorCandidate(
            element_id="candidate_3",
            strategy="id",
            value="#hidden-button",
            locator_type="css",
        )

        hidden_result = await validator.validate(
            page,
            hidden_candidate,
        )

        assert hidden_result.exists is True
        assert hidden_result.match_count == 1
        assert hidden_result.is_unique is True
        assert hidden_result.is_visible is False
        assert hidden_result.is_valid is False

        aria_candidate = LocatorCandidate(
            element_id="candidate_4",
            strategy="aria-label",
            value="Products",
            locator_type="aria-label",
        )

        aria_result = await validator.validate(
            page,
            aria_candidate,
        )

        assert aria_result.exists is True
        assert aria_result.match_count == 1
        assert aria_result.is_unique is True
        assert aria_result.is_visible is True
        assert aria_result.is_enabled is True
        assert aria_result.is_valid is True

    finally:
        await browser.close()
