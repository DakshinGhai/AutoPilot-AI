import pytest

from playwright.async_api import async_playwright


@pytest.mark.asyncio
async def test_inspect_ikea_targets():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True,
            channel="chrome",
        )

        page = await browser.new_page()

        try:

            await page.goto(
                "https://www.ikea.com/in/en/",
                wait_until="domcontentloaded",
                timeout=60000,
            )

            await page.wait_for_timeout(3000)

            buttons = page.locator("button")

            count = await buttons.count()

            print(f"\nTotal buttons: {count}")

            for index in range(min(count, 30)):

                button = buttons.nth(index)

                try:

                    if not await button.is_visible():
                        continue

                    text = (await button.inner_text()).strip()

                    aria_label = await button.get_attribute("aria-label")

                    title = await button.get_attribute("title")

                    button_id = await button.get_attribute("id")

                    classes = await button.get_attribute("class")

                    print(f"\nBUTTON {index}")
                    print(f"  text       = {text!r}")
                    print(f"  aria-label = {aria_label!r}")
                    print(f"  title      = {title!r}")
                    print(f"  id         = {button_id!r}")
                    print(f"  class      = {classes!r}")

                except Exception as exc:

                    print(f"Button {index} error: {exc}")

        finally:

            await browser.close()
