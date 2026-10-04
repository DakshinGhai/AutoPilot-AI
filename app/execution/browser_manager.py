from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)


class BrowserManager:

    def __init__(
        self,
        headless: bool = False,
        timeout: int = 30000,
    ):
        self.headless = headless
        self.timeout = timeout

        self.playwright: Playwright | None = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def start(self) -> Page:

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless, channel="chrome"
        )

        self.context = await self.browser.new_context()

        self.page = await self.context.new_page()

        self.page.set_default_timeout(self.timeout)

        return self.page

    async def close(self):

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None
