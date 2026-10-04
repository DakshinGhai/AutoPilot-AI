from playwright.async_api import Page

from app.browser.dom_extractor import DOMExtractor
from app.models.failure import FailureContext
from app.models.trace import LocatorDecisionTrace
from app.recovery.dom_evidence import DOMEvidenceExtractor
from app.recovery.failure_analyzer import FailureAnalyzer


class FailureContextBuilder:

    def __init__(
        self,
        analyzer: FailureAnalyzer | None = None,
        dom_extractor: DOMExtractor | None = None,
        dom_evidence_extractor: DOMEvidenceExtractor | None = None,
    ):
        self.analyzer = analyzer or FailureAnalyzer()
        self.dom_extractor = dom_extractor or DOMExtractor()
        self.dom_evidence_extractor = dom_evidence_extractor or DOMEvidenceExtractor()

    async def build(
        self,
        page: Page,
        test_case_id: str,
        test_case_name: str,
        step: int,
        action: str,
        target: str | None,
        error_message: str,
        locator_decision: LocatorDecisionTrace | None = None,
    ) -> FailureContext:

        evidence = self.analyzer.analyze(
            error_message=error_message,
            action=action,
            target=target,
        )

        evidence.page_url = page.url

        try:
            evidence.page_title = await page.title()
        except Exception:
            evidence.page_title = None

        if locator_decision:
            evidence.locator_type = locator_decision.selected_locator_type
            evidence.locator_value = locator_decision.selected_locator_value
            evidence.match_count = locator_decision.final_match_count
            evidence.is_unique = locator_decision.final_is_unique
            evidence.is_visible = locator_decision.final_is_visible
            evidence.is_enabled = locator_decision.final_is_enabled
            evidence.is_valid = locator_decision.final_is_valid

        # Capture the DOM exactly as it exists at failure time.
        try:
            elements = await self.dom_extractor.extract_elements(page)

            evidence.dom_evidence = self.dom_evidence_extractor.extract(
                elements,
                target=target,
            )

        except Exception:
            # Failure evidence collection must never hide
            # the original test failure.
            evidence.dom_evidence = []

        return FailureContext(
            test_case_id=test_case_id,
            test_case_name=test_case_name,
            step=step,
            action=action,
            target=target,
            evidence=evidence,
        )
