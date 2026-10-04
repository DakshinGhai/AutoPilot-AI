from typing import Optional

from playwright.async_api import Page

from app.ai.locator_selector import LocatorSelectionService
from app.locators.candidate_context_builder import CandidateContextBuilder
from app.locators.locator_resolver import LocatorResolver
from app.models.ai import LocatorSelectionRequest
from app.models.candidate_context import CandidateContext
from app.models.locator import LocatorCandidate


class AILocatorPipeline:

    def __init__(
        self,
        locator_resolver: LocatorResolver,
        selection_service: LocatorSelectionService,
        candidate_context_builder: CandidateContextBuilder,
    ):
        self.locator_resolver = locator_resolver
        self.selection_service = selection_service
        self.candidate_context_builder = candidate_context_builder

    async def select_locator(
        self,
        page: Page,
        test_step: str,
        target: str,
    ):

        resolution = await self.locator_resolver.resolve(page)

        if not resolution.candidates:
            raise ValueError("No locator candidates were generated")

        contexts: list[CandidateContext] = []

        for candidate in resolution.candidates:

            validation = next(
                (
                    item
                    for item in resolution.validations
                    if (
                        item.element_id == candidate.element_id
                        and item.strategy == candidate.strategy
                    )
                ),
                None,
            )

            context = self.candidate_context_builder.build(
                candidate,
                validation,
            )

            contexts.append(context)

        request = LocatorSelectionRequest(
            test_step=test_step,
            target=target,
            page_url=page.url,
            page_title=await page.title(),
            candidates=contexts,
        )

        response, selected = await self.selection_service.select(request)

        return response, selected
