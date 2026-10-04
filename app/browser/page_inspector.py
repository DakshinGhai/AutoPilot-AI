from playwright.async_api import Page

from app.browser.dom_extractor import DOMExtractor
from app.models.browser import PageInfo


class PageInspector:

    def __init__(self):
        self.dom_extractor = DOMExtractor()

    async def inspect(self, page: Page) -> PageInfo:

        print("\n[PAGE INSPECTOR] Starting inspection")

        print(f"[PAGE INSPECTOR] URL: {page.url}")

        title = await page.title()

        print(f"[PAGE INSPECTOR] Title: {title}")

        print("[PAGE INSPECTOR] Waiting for page...")

        try:
            await page.wait_for_load_state("domcontentloaded")
        except Exception as error:
            print(f"[PAGE INSPECTOR] " f"Load-state warning: {error}")

        print("[PAGE INSPECTOR] Running DOM extraction...")

        elements = await self.dom_extractor.extract_elements(page)

        page_info = PageInfo(
            url=page.url,
            title=title,
            elements=elements,
        )

        self._categorize_elements(page_info)

        print(f"[PAGE INSPECTOR] " f"Extracted elements: " f"{len(page_info.elements)}")

        return page_info

    def _categorize_elements(
        self,
        page_info: PageInfo,
    ):

        for element in page_info.elements:

            tag = element.tag.lower()

            role = element.role.lower() if element.role else None

            if tag in {
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6",
            }:
                page_info.headings.append(element)

            if tag == "button" or role == "button":
                page_info.buttons.append(element)

            if tag == "a":
                page_info.links.append(element)

            if tag == "input":
                page_info.inputs.append(element)

                input_type = element.type.lower() if element.type else "text"

                if input_type == "checkbox":
                    page_info.checkboxes.append(element)

                elif input_type == "radio":
                    page_info.radio_buttons.append(element)

            if tag == "textarea":
                page_info.textareas.append(element)

            if tag == "select":
                page_info.selects.append(element)

            if tag == "form":
                page_info.forms.append(element)

            if role == "dialog":
                page_info.dialogs.append(element)

            if role == "menu":
                page_info.menus.append(element)

            if role in {
                "tab",
                "tablist",
            }:
                page_info.tabs.append(element)
