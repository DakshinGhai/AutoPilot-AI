import asyncio
import json

from app.execution.browser_manager import (
    BrowserManager,
)
from app.browser.page_inspector import (
    PageInspector,
)


async def main():

    browser = BrowserManager(headless=False)

    page = await browser.start()

    try:

        await page.goto(
            "https://www.ikea.com/in/en/",
            wait_until="domcontentloaded",
        )

        inspector = PageInspector()

        page_info = await inspector.inspect(page)

        print("\nURL:")

        print(page_info.url)

        print("\nTITLE:")

        print(page_info.title)

        print("\nELEMENT COUNT:")

        print(len(page_info.elements))

        print("\nBUTTONS:")

        for button in page_info.buttons[:10]:

            print(
                json.dumps(
                    button.model_dump(mode="json"),
                    indent=2,
                )
            )

    finally:

        await browser.close()


if __name__ == "__main__":

    asyncio.run(main())
