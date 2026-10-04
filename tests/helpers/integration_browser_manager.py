from playwright.async_api import async_playwright


class IntegrationBrowserManager:

    def __init__(self):
        self.page = None
        self.started = False
        self.closed = False

    async def start(self):

        self.started = True

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=True,
            channel="chrome",
        )

        self.page = await self.browser.new_page()

        return self.page

    async def close(self):

        self.closed = True

        await self.browser.close()

        await self.playwright.stop()
