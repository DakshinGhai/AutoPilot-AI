from playwright.async_api import Page


class ActionExecutor:

    def __init__(self, page: Page):
        self.page = page

    async def execute(
        self,
        action: str,
        target: str | None = None,
    ):
        if hasattr(action, "value"):
            action = action.value

        action = str(action).lower()

        if target is not None:
            target = str(target)

        if action == "navigate":
            await self.navigate(target)

        elif action == "click":
            await self.click(target)

        elif action == "search":
            await self.search(target)

        elif action == "fill":
            await self.fill(target)

        elif action == "type":
            await self.type(target)

        elif action == "press":
            await self.press(target)

        elif action == "hover":
            await self.hover(target)

        elif action == "scroll":
            await self.scroll(target)

        else:
            raise ValueError(f"Unsupported action: {action}")

    async def navigate(self, url: str | None):
        if not url:
            raise ValueError("Navigate action requires a URL.")

        url = str(url)

        await self.page.goto(
            url,
            wait_until="domcontentloaded",
        )

    async def click(
        self,
        target: str | None,
    ):

        if not target:
            raise ValueError("Click action requires a target.")

        await self.page.get_by_text(
            target,
            exact=False,
        ).first.click()

    async def search(
        self,
        value: str | None,
    ):
        if not value:
            raise ValueError("Search action requires a value.")

        value = str(value)

        print(f"\n[SEARCH] Searching for: {value}")

        # -----------------------------------------
        # 1. Handle blocking cookie dialog
        # -----------------------------------------

        await self._handle_cookie_banner()

        # -----------------------------------------
        # 2. Semantic searchbox
        # -----------------------------------------

        search_boxes = self.page.get_by_role("searchbox")

        searchbox_count = await search_boxes.count()

        print(f"[SEARCH] searchbox role count: " f"{searchbox_count}")

        for index in range(searchbox_count):

            candidate = search_boxes.nth(index)

            try:
                visible = await candidate.is_visible()
                enabled = await candidate.is_enabled()

                print(
                    f"[SEARCH] searchbox {index}: "
                    f"visible={visible}, "
                    f"enabled={enabled}"
                )

                if visible and enabled:

                    print("[SEARCH] Using role=searchbox")

                    await candidate.fill(value)
                    await candidate.press("Enter")

                    return

            except Exception as error:

                print(f"[SEARCH] Searchbox error: " f"{error}")

        # -----------------------------------------
        # 3. Common search inputs
        # -----------------------------------------

        selectors = [
            'input[type="search"]',
            'input[name="q"]',
            'input[placeholder*="Search" i]',
            'input[aria-label*="Search" i]',
        ]

        for selector in selectors:

            locator = self.page.locator(selector)

            count = await locator.count()

            print(f"[SEARCH] {selector} -> {count}")

            for index in range(count):

                candidate = locator.nth(index)

                try:

                    visible = await candidate.is_visible()
                    enabled = await candidate.is_enabled()

                    print(
                        f"[SEARCH] candidate {index}: "
                        f"visible={visible}, "
                        f"enabled={enabled}"
                    )

                    if visible and enabled:

                        print(f"[SEARCH] Using selector: " f"{selector}")

                        await candidate.fill(value)
                        await candidate.press("Enter")

                        return

                except Exception as error:

                    print(f"[SEARCH] Candidate error: " f"{error}")

        raise RuntimeError("Unable to locate a usable search input.")

    async def _handle_cookie_banner(self):

        cookie_ok = self.page.get_by_role(
            "button",
            name="Ok",
            exact=True,
        )

        count = await cookie_ok.count()

        print(f"[OVERLAY] Cookie OK button count: {count}")

        if count == 0:
            print("[OVERLAY] No cookie banner detected.")
            return

        try:

            button = cookie_ok.first

            visible = await button.is_visible()
            enabled = await button.is_enabled()

            print(f"[OVERLAY] Cookie OK: " f"visible={visible}, " f"enabled={enabled}")

            if visible and enabled:

                print("[OVERLAY] Accepting cookie banner...")

                await button.click()

                # Give IKEA's overlay a moment to disappear.
                await self.page.wait_for_timeout(500)

                print("[OVERLAY] Cookie banner dismissed.")

        except Exception as error:

            print(f"[OVERLAY] Cookie handling failed: " f"{error}")

    async def fill(
        self,
        value: str | None,
    ):

        if not value:
            raise ValueError("Fill action requires a value.")

        inputs = self.page.locator("input").filter(visible=True)

        await inputs.first.fill(value)

    async def type(
        self,
        value: str | None,
    ):

        if not value:
            raise ValueError("Type action requires a value.")

        inputs = self.page.locator("input")

        await inputs.first.fill(value)

    async def press(
        self,
        key: str | None,
    ):

        if not key:
            raise ValueError("Press action requires a key.")

        await self.page.keyboard.press(key)

    async def hover(
        self,
        target: str | None,
    ):

        if not target:
            raise ValueError("Hover action requires a target.")

        await self.page.get_by_text(
            target,
            exact=False,
        ).first.hover()

    async def scroll(
        self,
        target: str | None = None,
    ):

        await self.page.mouse.wheel(
            0,
            800,
        )
