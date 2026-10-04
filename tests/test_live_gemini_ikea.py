import os

import pytest
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from app.ai.locator_executor import (
    AILocatorExecutor,
)
from app.ai.gemini_client import GeminiAIClient
from app.ai.locator_selector import LocatorSelectionService
from app.browser.dom_extractor import DOMExtractor
from app.locators.candidate_context_builder import (
    CandidateContextBuilder,
)
from app.locators.locator_generator import LocatorGenerator
from app.locators.locator_ranker import LocatorRanker
from app.locators.locator_validator import LocatorValidator
from app.models.ai import LocatorSelectionRequest

load_dotenv()


@pytest.mark.asyncio
async def test_live_gemini_ikea_locator_selection():

    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY is not configured")

    if not os.getenv("GEMINI_MODEL"):
        pytest.skip("GEMINI_MODEL is not configured")

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

            # -------------------------------------------------
            # 1. Extract the actual browser DOM
            # -------------------------------------------------

            extractor = DOMExtractor()

            elements = await extractor.extract_elements(page)

            print(f"\nDOM elements extracted: " f"{len(elements)}")

            assert elements, "DOMExtractor returned no elements"

            target = next(
                (
                    element
                    for element in elements
                    if element.id == "search-box-visual-search-icon"
                ),
                None,
            )

            assert target is not None, (
                "Could not find " "search-box-visual-search-icon " "in extracted DOM"
            )

            print("\nTarget ElementInfo:")
            print(
                "  element_id:",
                target.element_id,
            )
            print(
                "  tag:",
                target.tag,
            )
            print(
                "  id:",
                target.id,
            )
            print(
                "  role:",
                target.role,
            )
            print(
                "  accessible_name:",
                target.accessible_name,
            )
            print(
                "  aria_label:",
                target.aria_label,
            )
            print(
                "  text:",
                target.text,
            )
            print(
                "  visible:",
                target.visible,
            )

            # -------------------------------------------------
            # 3. Generate locator candidates
            # -------------------------------------------------

            generator = LocatorGenerator()

            candidates = generator.generate(target)

            assert candidates, "No locator candidates generated"

            # -------------------------------------------------
            # 4. Rank candidates
            # -------------------------------------------------

            ranker = LocatorRanker()

            ranked_candidates = ranker.rank(candidates)

            print(f"\nGenerated candidates: " f"{len(ranked_candidates)}")

            # -------------------------------------------------
            # 5. Validate candidates against REAL browser
            # -------------------------------------------------

            validator = LocatorValidator()

            context_builder = CandidateContextBuilder()

            contexts = []

            for candidate in ranked_candidates:

                print("\n--- VALIDATING CANDIDATE ---")

                print(
                    "Strategy:",
                    candidate.strategy,
                )

                print(
                    "Locator type:",
                    candidate.locator_type,
                )

                print(
                    "Value:",
                    repr(candidate.value),
                )

                print(
                    "Priority:",
                    candidate.priority,
                )

                validation = await validator.validate(
                    page,
                    candidate,
                )

                print(
                    "  Exists:",
                    validation.exists,
                )

                print(
                    "  Match count:",
                    validation.match_count,
                )

                print(
                    "  Unique:",
                    validation.is_unique,
                )

                print(
                    "  Visible:",
                    validation.is_visible,
                )

                print(
                    "  Enabled:",
                    validation.is_enabled,
                )

                print(
                    "  Valid:",
                    validation.is_valid,
                )

                print(
                    "  Reason:",
                    validation.reason,
                )

                context = context_builder.build(
                    candidate,
                    validation,
                )

                contexts.append(context)

            # -------------------------------------------------
            # 6. Only validated candidates go to Gemini
            # -------------------------------------------------

            valid_contexts = [context for context in contexts if context.is_valid]

            print(f"\nValid candidates sent to Gemini: " f"{len(valid_contexts)}")

            assert valid_contexts, "No valid browser-backed " "locator candidates found"

            # -------------------------------------------------
            # 7. Build AI request
            # -------------------------------------------------

            request = LocatorSelectionRequest(
                test_step=(
                    "Click the visual search button "
                    "for searching IKEA products using "
                    "a photo"
                ),
                target=("Search IKEA products using a photo"),
                page_url=page.url,
                page_title=await page.title(),
                candidates=valid_contexts,
            )

            print(
                "\nAI request candidate count:",
                len(request.candidates),
            )

            # -------------------------------------------------
            # 8. REAL GEMINI
            # -------------------------------------------------

            gemini_client = GeminiAIClient()

            selection_service = LocatorSelectionService(gemini_client)

            response, selected = await selection_service.select(request)
            executor = AILocatorExecutor(LocatorValidator())

            execution_result = await executor.execute_click(
                page,
                selected,
                response,
            )

            print("\n==============================")
            print("AI LOCATOR EXECUTION")
            print("==============================")

            print(
                "Success:",
                execution_result.success,
            )

            print(
                "Candidate ID:",
                execution_result.candidate_id,
            )

            print(
                "Locator Type:",
                execution_result.locator_type,
            )

            print(
                "Locator Value:",
                execution_result.locator_value,
            )

            print(
                "Action:",
                execution_result.action,
            )

            print(
                "AI Confidence:",
                execution_result.ai_confidence,
            )

            print(
                "AI Reason:",
                execution_result.ai_reason,
            )

            print(
                "Error:",
                execution_result.error,
            )

            assert execution_result.success is True

            # -------------------------------------------------
            # 9. Print Gemini result
            # -------------------------------------------------

            print("\n==============================")
            print("GEMINI SELECTION")
            print("==============================")

            print(
                "Candidate ID:",
                response.selected_candidate_id,
            )

            print(
                "Locator Type:",
                selected.locator_type,
            )

            print(
                "Locator Value:",
                selected.locator_value,
            )

            print(
                "Strategy:",
                selected.strategy,
            )

            print(
                "Confidence:",
                response.confidence,
            )

            print(
                "Reason:",
                response.reason,
            )

            # -------------------------------------------------
            # 10. Safety assertions
            # -------------------------------------------------

            valid_candidate_ids = {
                candidate.candidate_id for candidate in valid_contexts
            }

            assert response.selected_candidate_id in valid_candidate_ids, (
                "Gemini selected a candidate " "that was not supplied"
            )

            assert selected.is_valid is True

            assert 0.0 <= response.confidence <= 1.0

            print("\nLIVE GEMINI LOCATOR TEST PASSED")

        finally:
            await browser.close()
