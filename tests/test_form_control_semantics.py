import pytest

from app.execution.browser_manager import BrowserManager
from app.browser.dom_extractor import DOMExtractor
from app.locators.locator_generator import LocatorGenerator
from app.locators.locator_validator import LocatorValidator


@pytest.mark.asyncio
async def test_form_control_semantics():

    browser = BrowserManager(headless=True)

    page = await browser.start()

    try:

        await page.set_content("""
            <html>
                <body>

                    <form>

                        <label for="username">
                            Username
                        </label>

                        <input
                            id="username"
                            type="text"
                        />

                        <label for="description">
                            Description
                        </label>

                        <textarea
                            id="description"
                        ></textarea>

                        <label>
                            Remember me
                            <input
                                id="remember"
                                type="checkbox"
                            />
                        </label>

                        <label>
                            Male
                            <input
                                id="male"
                                type="radio"
                                name="gender"
                            />
                        </label>

                        <label for="country">
                            Country
                        </label>

                        <select id="country">
                            <option value="india">
                                India
                            </option>
                            <option value="usa">
                                USA
                            </option>
                        </select>

                        <label for="countries">
                            Countries
                        </label>

                        <select
                            id="countries"
                            multiple
                        >
                            <option value="india">
                                India
                            </option>
                            <option value="usa">
                                USA
                            </option>
                        </select>

                        <label for="price">
                            Price
                        </label>

                        <input
                            id="price"
                            type="range"
                        />

                    </form>

                </body>
            </html>
            """)

        extractor = DOMExtractor()

        elements = await extractor.extract_elements(page)

        username = next(element for element in elements if element.id == "username")

        description = next(
            element for element in elements if element.id == "description"
        )

        remember = next(element for element in elements if element.id == "remember")

        male = next(element for element in elements if element.id == "male")

        country = next(element for element in elements if element.id == "country")

        countries = next(element for element in elements if element.id == "countries")

        price = next(element for element in elements if element.id == "price")

        # --------------------------------------------------
        # Semantic role extraction
        # --------------------------------------------------

        assert username.role == "textbox"

        assert description.role == "textbox"

        assert remember.role == "checkbox"

        assert male.role == "radio"

        assert country.role == "combobox"

        assert countries.role == "listbox"

        assert price.role == "slider"

        # --------------------------------------------------
        # Accessible names
        # --------------------------------------------------

        assert username.accessible_name == "Username"

        assert description.accessible_name == "Description"

        assert remember.accessible_name == "Remember me"

        assert male.accessible_name == "Male"

        assert country.accessible_name == "Country"

        assert countries.accessible_name == "Countries"

        assert price.accessible_name == "Price"

        # --------------------------------------------------
        # Locator generation
        # --------------------------------------------------

        generator = LocatorGenerator()

        controls = [
            username,
            description,
            remember,
            male,
            country,
            countries,
            price,
        ]

        for control in controls:

            candidates = generator.generate(control)

            role_candidates = [
                candidate for candidate in candidates if candidate.strategy == "role"
            ]

            assert len(role_candidates) == 1

            role_candidate = role_candidates[0]

            assert role_candidate.locator_type == "role"

            assert role_candidate.value == (
                f"{control.role}:" f"{control.accessible_name}"
            )

        # --------------------------------------------------
        # Locator validation
        # --------------------------------------------------

        validator = LocatorValidator()

        for control in controls:

            candidates = generator.generate(control)

            role_candidate = next(
                candidate for candidate in candidates if candidate.strategy == "role"
            )

            result = await validator.validate(
                page,
                role_candidate,
            )

            assert result.exists is True

            assert result.match_count == 1

            assert result.is_unique is True

            assert result.is_visible is True

            assert result.is_enabled is True

            assert result.is_valid is True

    finally:

        await browser.close()
