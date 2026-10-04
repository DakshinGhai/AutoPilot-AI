from playwright.async_api import Page

from app.ai.locator_executor import AILocatorExecutor
from app.ai.locator_selector import LocatorSelectionService
from app.browser.dom_extractor import DOMExtractor
from app.locators.candidate_context_builder import CandidateContextBuilder
from app.locators.locator_generator import LocatorGenerator
from app.locators.locator_ranker import LocatorRanker
from app.locators.locator_validator import LocatorValidator
from app.models.ai import LocatorSelectionRequest
from app.models.trace import LocatorDecisionTrace


class AIActionExecutor:

    def __init__(
        self,
        page: Page,
        selection_service: LocatorSelectionService,
    ):
        self.page = page
        self.selection_service = selection_service

        self.dom_extractor = DOMExtractor()
        self.locator_generator = LocatorGenerator()
        self.locator_ranker = LocatorRanker()
        self.locator_validator = LocatorValidator()
        self.context_builder = CandidateContextBuilder()

        self.ai_locator_executor = AILocatorExecutor(self.locator_validator)

    async def execute(
        self,
        action: str,
        target: str | None = None,
        value: str | None = None,
    ):
        action = action.lower()

        if action == "navigate":
            return await self._navigate(target)

        if action == "click":
            return await self._click(target)

        raise ValueError(f"AI execution does not support action: {action}")

    async def _navigate(
        self,
        target: str | None,
    ):
        if not target:
            raise ValueError("Navigate action requires a URL.")

        await self.page.goto(
            target,
            wait_until="domcontentloaded",
        )

        return None

    async def _click(self, target):
        if not target:
            raise ValueError("Click action requires a target.")

        elements = await self.dom_extractor.extract_elements(self.page)

        # ---------------------------------------------------------
        # SPECIAL TARGET: FIRST PRODUCT FROM SEARCH RESULTS
        # ---------------------------------------------------------

        if self._is_first_product_target(target):

            product_element = self._find_first_product_element(
                elements,
                target,
            )

            if product_element is None:
                raise ValueError(f"No product element found for target: {target}")

            matched_elements = [product_element]

            print("\n[PRODUCT RESOLUTION]")

            print(f"Target: {target}")

            print(f"First product element: " f"{product_element.element_id}")

            print(f"Tag: {product_element.tag}")

            print(f"Role: {product_element.role}")

            print(f"Accessible name: " f"{product_element.accessible_name}")

            print(f"Text: " f"{product_element.text}")

            print(f"DOM path: " f"{product_element.dom_path}")

        else:

            # -----------------------------------------------------
            # NORMAL SEMANTIC TARGET MATCHING
            # -----------------------------------------------------

            matched_elements = [
                element
                for element in elements
                if self._element_matches_target(
                    element,
                    target,
                )
            ]

        if not matched_elements:
            raise ValueError(f"No DOM element matched target: {target}")

        contexts = []

        candidates_generated = 0
        candidates_valid = 0

        for element in matched_elements:

            candidates = self.locator_generator.generate(element)

            candidates_generated += len(candidates)

            ranked_candidates = self.locator_ranker.rank(candidates)

            for candidate in ranked_candidates:

                validation = await self.locator_validator.validate(
                    self.page,
                    candidate,
                )

                if not validation.is_valid:
                    continue

                candidates_valid += 1

                context = self.context_builder.build(
                    candidate,
                    validation,
                )

                contexts.append(context)

        if not contexts:
            raise ValueError(
                f"No valid locator candidates found " f"for target: {target}"
            )

        print(f"\n[LOCATOR] Candidates generated: " f"{candidates_generated}")

        print(f"[LOCATOR] Valid candidates: " f"{candidates_valid}")

        request = LocatorSelectionRequest(
            test_step=f"click {target}",
            target=target,
            page_url=self.page.url,
            page_title=await self.page.title(),
            candidates=contexts,
        )

        print("\n[AI] Selecting locator...")

        ai_response, selected = await self.selection_service.select(request)

        print(f"[AI] Selected candidate: " f"{selected.candidate_id}")

        print(f"[AI] Locator type: " f"{selected.locator_type}")

        print(f"[AI] Locator value: " f"{selected.locator_value}")

        print(f"[AI] Confidence: " f"{ai_response.confidence}")

        print(f"[AI] Reason: " f"{ai_response.reason}")

        # ---------------------------------------------------------
        # FINAL VALIDATION + CLICK
        # ---------------------------------------------------------

        print("\n[CLICK] Executing selected locator...")

        result = await self.ai_locator_executor.execute_click(
            self.page,
            selected,
            ai_response,
        )

        result.locator_decision = LocatorDecisionTrace(
            target=target,
            candidates_generated=candidates_generated,
            candidates_valid=candidates_valid,
            selected_candidate_id=selected.candidate_id,
            selected_locator_type=selected.locator_type,
            selected_locator_value=selected.locator_value,
            ai_confidence=ai_response.confidence,
            ai_reason=ai_response.reason,
            final_match_count=result.final_match_count,
            final_is_unique=result.final_is_unique,
            final_is_visible=result.final_is_visible,
            final_is_enabled=result.final_is_enabled,
            final_is_valid=result.final_is_valid,
        )

        if not result.success:
            raise RuntimeError(result.error or "AI click execution failed.")

        print("[CLICK] Success")

        return result

    @staticmethod
    def _element_matches_target(
        element,
        target: str,
    ) -> bool:

        target_lower = target.strip().lower()

        if not target_lower:
            return False

        searchable_values = [
            element.accessible_name,
            element.label_text,
            element.text,
            element.inner_text,
            element.aria_label,
            element.placeholder,
            element.title,
        ]

        for value in searchable_values:

            if not value:
                continue

            if target_lower in value.strip().lower():
                return True

        return False

    @staticmethod
    def _is_first_product_target(
        target: str,
    ) -> bool:

        normalized = target.strip().lower()

        return normalized.startswith("first ") and "product" in normalized

    def _find_first_product_element(
        self,
        elements,
        target: str,
    ):
        target_lower = target.strip().lower()

        # Remove "first" and "product" to obtain
        # the actual product search term.
        search_term = (
            target_lower.replace("first", "", 1).replace("product", "", 1).strip()
        )

        if not search_term:
            search_term = "product"

        print(
            f"[PRODUCT RESOLUTION] "
            f"Searching for first product containing: "
            f"'{search_term}'"
        )

        candidates = []

        for element in elements:

            # We only want elements that can reasonably
            # represent a product/card.
            if not self._looks_like_product_element(element):
                continue

            searchable_values = [
                element.accessible_name,
                element.text,
                element.inner_text,
                element.aria_label,
                element.title,
                element.nearby_text,
            ]

            combined_text = " ".join(
                str(value) for value in searchable_values if value
            ).lower()

            if search_term in combined_text:
                candidates.append(element)

        print(
            f"[PRODUCT RESOLUTION] " f"Matching product elements: " f"{len(candidates)}"
        )

        if not candidates:
            return None

        # DOMExtractor preserves the page traversal order.
        # Therefore the first candidate is the first
        # matching product encountered in the DOM.
        return candidates[0]

    @staticmethod
    def _looks_like_product_element(
        element,
    ) -> bool:

        tag = (element.tag or "").lower()

        role = (element.role or "").lower()

        class_name = (element.class_name or "").lower()

        # Links and buttons can represent product cards.
        if tag in {"a", "button"}:
            return True

        if role in {
            "link",
            "button",
            "article",
            "listitem",
        }:
            return True

        # IKEA product cards commonly contain
        # product/card-related class names.
        if any(
            keyword in class_name
            for keyword in [
                "product",
                "card",
                "item",
            ]
        ):
            return True

        return False

    @staticmethod
    def _is_first_product_target(target: str) -> bool:
        normalized = target.strip().lower()

        return normalized.startswith("first ") and "product" in normalized

    def _find_first_product_element(
        self,
        elements,
        target: str,
    ):
        """
        Find the first actual clickable product link
        matching the requested product term.

        IKEA search result structure observed:

            section#product-list
                product card
                    ...
                    h3 -> product name
                    a.plp-price-module__product-link -> product link

        We intentionally select the <a>, not the <h3>.
        """

        target_lower = target.strip().lower()

        # Example:
        #
        # "First chair product"
        #
        # becomes:
        #
        # "chair"
        #
        search_term = target_lower

        search_term = search_term.replace(
            "first",
            "",
            1,
        )

        search_term = search_term.replace(
            "product",
            "",
            1,
        )

        search_term = search_term.strip()

        if not search_term:
            search_term = "product"

        print("\n[PRODUCT RESOLUTION]")

        print(f"[PRODUCT RESOLUTION] " f"Search term: {search_term}")

        product_links = []

        for element in elements:

            # We specifically want clickable
            # product links.
            if element.tag != "a":
                continue

            if element.role != "link":
                continue

            href = element.href or ""

            if "/p/" not in href:
                continue

            # IKEA product links have the
            # plp product-link class.
            class_name = (element.class_name or "").lower()

            if "plp-price-module__product-link" not in class_name:
                continue

            searchable_values = [
                element.accessible_name,
                element.text,
                element.inner_text,
                element.href,
            ]

            combined_text = " ".join(
                str(value) for value in searchable_values if value
            ).lower()

            if search_term not in combined_text:
                continue

            if not element.visible:
                continue

            if not element.enabled:
                continue

            product_links.append(element)

        print(
            f"[PRODUCT RESOLUTION] " f"Matching product links: " f"{len(product_links)}"
        )

        if not product_links:
            return None

        first_product = product_links[0]

        print("\n[FIRST PRODUCT]")

        print(f"Element ID      : " f"{first_product.element_id}")

        print(f"Product         : " f"{first_product.accessible_name}")

        print(f"Tag             : " f"{first_product.tag}")

        print(f"Role            : " f"{first_product.role}")

        print(f"Href            : " f"{first_product.href}")

        print(f"DOM Path        : " f"{first_product.dom_path}")

        return first_product
