import re

from playwright.async_api import Page, expect


class AssertionEngine:

    def __init__(self, page: Page):
        self.page = page

    async def validate(
        self,
        expected_result: str | None,
    ):
        if not expected_result:
            return

        expected = expected_result.strip()
        normalized = expected.lower()

        # -----------------------------------------
        # Homepage assertion
        # -----------------------------------------
        if "homepage displayed" in normalized:
            await expect(
                self.page
            ).to_have_url(
                re.compile(r".*ikea\.com.*")
            )
            return

        # -----------------------------------------
        # Search results assertion
        # -----------------------------------------
        if "search results displayed" in normalized:
            # Verify that we are on an IKEA search-results page.
            await expect(
                self.page
            ).to_have_url(
                re.compile(r".*/search/.*")
            )

            # Verify that the search-results heading is visible.
            await expect(
                self.page.get_by_role(
                    "heading",
                    name=re.compile(
                        r"Showing results for",
                        re.IGNORECASE
                    )
                )
            ).to_be_visible()

            return

        # -----------------------------------------
        # Generic page assertion
        # -----------------------------------------
        if "page displayed" in normalized:
            title = await self.page.title()

            if not title.strip():
                raise AssertionError(
                    "Expected page title to be displayed, "
                    "but the page title is empty."
                )

            return

        # -----------------------------------------
        # Generic text assertion
        # -----------------------------------------
        await self.assert_text(expected)

    async def assert_text(
        self,
        expected_text: str,
    ):
        await expect(
            self.page.locator("body")
        ).to_contain_text(
            expected_text
        )