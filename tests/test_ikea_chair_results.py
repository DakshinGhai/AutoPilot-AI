import pytest
from playwright.async_api import async_playwright

from app.browser.dom_extractor import DOMExtractor
from app.execution.action_executor import ActionExecutor


@pytest.mark.asyncio
async def test_ikea_chair_results():

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=False)

        page = await browser.new_page(
            viewport={
                "width": 1440,
                "height": 900,
            }
        )

        try:

            print("\n======================================")
            print(" IKEA CHAIR RESULT INSPECTION")
            print("======================================")

            print("\n[1] Opening IKEA...")

            await page.goto(
                "https://www.ikea.com/in/en/",
                wait_until="domcontentloaded",
            )

            await page.wait_for_timeout(3000)

            action_executor = ActionExecutor(page)

            print("\n[2] Searching for chair...")

            await action_executor.search("chair")

            # Give IKEA search results time to render.
            await page.wait_for_timeout(5000)

            print("\n[3] Current URL:")
            print(page.url)

            print("\n[4] Page title:")
            print(await page.title())

            print("\n[5] Extracting DOM...")

            extractor = DOMExtractor()

            elements = await extractor.extract_elements(page)

            print(f"\nTotal DOM elements: {len(elements)}")

            # -------------------------------------------------
            # Look for elements containing "chair"
            # -------------------------------------------------

            matching = []

            for element in elements:

                searchable = [
                    element.accessible_name,
                    element.text,
                    element.inner_text,
                    element.aria_label,
                    element.title,
                    element.nearby_text,
                ]

                combined = " ".join(str(value) for value in searchable if value).strip()

                if "chair" in combined.lower():

                    matching.append(
                        (
                            element,
                            combined,
                        )
                    )

            print(f"\nElements containing 'chair': " f"{len(matching)}")

            # -------------------------------------------------
            # Print first 30 matches
            # -------------------------------------------------

            for index, (
                element,
                combined,
            ) in enumerate(
                matching[:30],
                start=1,
            ):

                print("\n--------------------------------------")

                print(f"CHAIR MATCH #{index}")

                print(f"Element ID      : " f"{element.element_id}")

                print(f"Tag             : " f"{element.tag}")

                print(f"Role            : " f"{element.role}")

                print(f"ID              : " f"{element.id}")

                print(f"Class           : " f"{element.class_name}")

                print(f"Accessible Name : " f"{element.accessible_name}")

                print(f"Text            : " f"{element.text}")

                print(f"Inner Text      : " f"{element.inner_text}")

                print(f"Href            : " f"{element.href}")

                print(f"Nearby Text     : " f"{element.nearby_text}")

                print(f"DOM Path        : " f"{element.dom_path}")

                print(f"Visible         : " f"{element.visible}")

                print(f"Enabled         : " f"{element.enabled}")

            print("\n======================================")

            print("Keeping browser open for inspection.")

            await page.wait_for_timeout(10000)

        finally:

            await browser.close()
