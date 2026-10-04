import os

import pytest
from playwright.async_api import async_playwright

from app.ai.gemini_recovery_client import (
    GeminiRecoveryAIClient,
)
from app.locators.locator_generator import (
    LocatorGenerator,
)
from app.locators.locator_ranker import (
    LocatorRanker,
)
from app.locators.locator_validator import (
    LocatorValidator,
)
from app.models.recovery_ai import (
    RecoverySelectionRequest,
)
from app.recovery.ai_recovery_executor import (
    AIRecoveryExecutor,
)
from app.recovery.ai_recovery_selector import (
    AIRecoverySelector,
)
from app.recovery.recovery_context_builder import (
    RecoveryContextBuilder,
)
from app.browser.dom_extractor import (
    DOMExtractor,
)

IKEA_URL = "https://www.ikea.com/in/en/"


@pytest.mark.asyncio
async def test_live_ikea_ai_recovery():

    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not configured.")

    async with async_playwright() as playwright:

        browser = await playwright.chromium.launch(headless=False)

        page = await browser.new_page()
        await page.wait_for_timeout(1000)
        # -------------------------------------------------
        # 1. Open IKEA
        # -------------------------------------------------

        await page.goto(
            IKEA_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        await page.wait_for_timeout(3000)

        print(
            "\nIKEA page loaded:",
            page.url,
        )

        # -------------------------------------------------
        # 2. Extract DOM
        # -------------------------------------------------

        extractor = DOMExtractor()

        elements = await extractor.extract_elements(page)

        print(
            "DOM elements:",
            len(elements),
        )

        assert elements

        # -------------------------------------------------
        # 3. Generate recovery candidates
        # -------------------------------------------------

        generator = LocatorGenerator()
        ranker = LocatorRanker()

        all_candidates = []

        for element in elements:

            generated = generator.generate(element)

            all_candidates.extend(generated)

        all_candidates = ranker.rank(all_candidates)

        print(
            "Generated candidates:",
            len(all_candidates),
        )

        assert all_candidates

        # -------------------------------------------------
        # 4. Validate candidates
        # -------------------------------------------------

        validator = LocatorValidator()

        validated_candidates = []

        for candidate in all_candidates:

            result = await validator.validate(
                page,
                candidate,
            )

            if result.is_valid:

                validated_candidates.append(
                    (
                        candidate,
                        result,
                    )
                )

        print(
            "Valid candidates:",
            len(validated_candidates),
        )

        assert validated_candidates

        # -------------------------------------------------
        # 5. Find a Product-related candidate
        # -------------------------------------------------

        target = "Product"

        target_candidates = []

        for candidate, validation in validated_candidates:

            semantic = candidate.semantic_evidence

            searchable = " ".join(
                filter(
                    None,
                    [
                        candidate.value,
                        candidate.reason,
                        (semantic.accessible_name if semantic else ""),
                        (semantic.visible_text if semantic else ""),
                        (semantic.label_text if semantic else ""),
                    ],
                )
            ).lower()

            if "product" in searchable:

                target_candidates.append(
                    (
                        candidate,
                        validation,
                    )
                )

        print(
            "Target candidates:",
            len(target_candidates),
        )

        # IKEA may change its DOM, so don't assume
        # a specific candidate ID.
        assert target_candidates

        # -------------------------------------------------
        # 6. Build AI context
        # -------------------------------------------------

        context_builder = RecoveryContextBuilder()

        contexts = [
            context_builder.build(
                candidate,
                validation,
            )
            for candidate, validation in target_candidates[:10]
        ]

        assert contexts

        print("\nCandidates sent to Gemini:")

        for context in contexts:

            print(
                f"  {context.candidate_id} "
                f"→ {context.locator_type}:"
                f"{context.locator_value}"
            )

        # -------------------------------------------------
        # 7. Ask Gemini to select
        # -------------------------------------------------

        client = GeminiRecoveryAIClient()

        selector = AIRecoverySelector(client)

        response, selected_context = await selector.select(
            test_step="Recover failed Product click",
            target=target,
            original_error=("Original Product locator failed"),
            candidates=contexts,
            page_url=page.url,
            page_title=await page.title(),
        )

        print("\nGemini selection:")

        print(
            "Candidate:",
            response.selected_candidate_id,
        )

        print(
            "Reason:",
            response.reason,
        )

        print(
            "Confidence:",
            response.confidence,
        )

        assert selected_context is not None

        # -------------------------------------------------
        # 8. Final browser validation + execution
        # -------------------------------------------------

        executor = AIRecoveryExecutor()

        execution_result = await executor.execute(
            page=page,
            candidate=selected_context,
            action="click",
            original_error=("Original Product locator failed"),
        )

        print("\nRecovery execution:")

        print(
            "Success:",
            execution_result.success,
        )

        print(
            "Retry attempted:",
            execution_result.retry_attempted,
        )

        if execution_result.recovery_error:
            print(
                "Recovery error:",
                execution_result.recovery_error,
            )

        assert execution_result.validation is not None

        assert execution_result.validation.is_valid

        assert execution_result.success

        await browser.close()
