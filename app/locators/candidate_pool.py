from playwright.async_api import Page

from app.locators.locator_generator import LocatorGenerator
from app.locators.locator_ranker import LocatorRanker
from app.locators.locator_validator import LocatorValidator


class CandidatePoolResolver:

    def __init__(
        self,
        generator: LocatorGenerator,
        ranker: LocatorRanker,
        validator: LocatorValidator,
    ):
        self.generator = generator
        self.ranker = ranker
        self.validator = validator

    async def resolve(
        self,
        page: Page,
        element,
    ):
        candidates = self.generator.generate(element)

        candidates = self.ranker.rank(candidates)

        validations = []

        for candidate in candidates:
            validation = await self.validator.validate(
                page,
                candidate,
            )

            validations.append(validation)

        return candidates, validations
