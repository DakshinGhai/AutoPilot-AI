from playwright.async_api import async_playwright


class FakeBrowserManager:

    def __init__(self):
        self.page = None
        self.started = False
        self.closed = False
        self.result_text = None

    async def start(self):

        self.started = True

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=True,
            channel="chrome",
        )

        self.page = await self.browser.new_page()

        await self.page.set_content("""
            <!DOCTYPE html>
            <html>
            <body>

                <button
                    id="products-button"
                    aria-label="Products"
                    onclick="
                        document.getElementById('result').innerText =
                        'Products opened'
                    "
                >
                    Products
                </button>

                <div id="result">Waiting</div>

            </body>
            </html>
            """)

        return self.page

    async def close(self):
        self.closed = True

        await self.browser.close()
        await self.playwright.stop()
