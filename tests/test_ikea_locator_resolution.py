import pytest

from app.execution.browser_manager import BrowserManager
from app.browser.page_inspector import PageInspector
from app.locators.locator_resolver import LocatorResolver

IKEA_URL = "https://www.ikea.com/in/en/"


@pytest.mark.asyncio
async def test_ikea_locator_resolution():

    browser = BrowserManager(headless=False)

    await browser.start()

    try:
        page = browser.page

        print("\nOpening IKEA...")

        await page.goto(
            IKEA_URL,
            wait_until="domcontentloaded",
        )

        await page.wait_for_timeout(3000)

        inspector = PageInspector()

        print("Inspecting IKEA DOM...")

        page_info = await inspector.inspect(page)

        print(f"\nURL: {page_info.url}")

        print(f"Title: {page_info.title}")

        print(f"Elements extracted: " f"{len(page_info.elements)}")

        resolver = LocatorResolver()

        target_texts = [
            "Products",
            "Rooms",
            "Offers",
            "Inspiration",
            "Enter postal code",
            "Search",
        ]

        for target_text in target_texts:

            print("\n" + "=" * 70)
            print(f"TARGET: {target_text}")
            print("=" * 70)

            matching_elements = [
                element
                for element in page_info.elements
                if element.text and target_text.lower() in element.text.strip().lower()
            ]

            print(f"Matching extracted elements: " f"{len(matching_elements)}")

            if not matching_elements:
                print(f"Could not find '{target_text}' " "in extracted DOM.")
                continue

            for element_index, element in enumerate(
                matching_elements[:5],
                start=1,
            ):

                print(f"\n--- Matching element #{element_index} ---")

                print(f"Element ID : {element.element_id}")

                print(f"Tag        : {element.tag}")

                print(f"Role       : {element.role}")

                print(f"ID         : {element.id}")

                print(f"Text       : {element.text}")

                print(f"Placeholder: {element.placeholder}")

                print(f"ARIA label : {element.aria_label}")

                print(f"Test ID    : {element.data_testid}")

                print(f"Visible    : {element.visible}")

                print(f"Enabled    : {element.enabled}")

                print("\nResolving locator...")

                result = await resolver.resolve(
                    page,
                    element,
                )

                print("\nCandidates:")

                for index, candidate in enumerate(
                    result.candidates,
                    start=1,
                ):
                    print(
                        f"  {index}. "
                        f"{candidate.strategy:<12} "
                        f"{candidate.value:<60} "
                        f"confidence="
                        f"{candidate.confidence}"
                    )

                print("\nValidation:")

                for validation in result.validations:

                    print(
                        f"  {validation.strategy:<12} "
                        f"{validation.value:<60} "
                        f"matches="
                        f"{validation.match_count} "
                        f"visible="
                        f"{validation.is_visible} "
                        f"enabled="
                        f"{validation.is_enabled} "
                        f"valid="
                        f"{validation.is_valid}"
                    )

                    print(f"      reason: " f"{validation.reason}")

                print("\nResult:")

                if result.success:

                    selected = result.selected_locator

                    print(f"  SELECTED: " f"{selected.strategy} " f"→ {selected.value}")

                    print(f"  Confidence: " f"{selected.confidence}")

                else:

                    print("  NO VALID LOCATOR FOUND")

        print("\nKeeping browser open for inspection.")

        await page.wait_for_timeout(5000)

    finally:
        await browser.close()
