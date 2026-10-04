from app.locators.locator_generator import LocatorGenerator
from app.models.browser import ElementInfo
from app.models.locator import LocatorCandidate


class RecoveryCandidateGenerator:

    def __init__(
        self,
        locator_generator: LocatorGenerator | None = None,
    ):
        self.locator_generator = locator_generator or LocatorGenerator()

    def generate(
        self,
        elements: list[ElementInfo],
        failed_element_id: str | None = None,
    ) -> list[LocatorCandidate]:

        candidates: list[LocatorCandidate] = []

        for element in elements:

            if failed_element_id and element.element_id == failed_element_id:
                continue

            # LocatorGenerator.generate() expects
            # one ElementInfo, not a list.
            generated = self.locator_generator.generate(element)

            candidates.extend(generated)

        return self._deduplicate(candidates)

    def _deduplicate(
        self,
        candidates: list[LocatorCandidate],
    ) -> list[LocatorCandidate]:

        seen: set[tuple[str, str, str]] = set()
        result: list[LocatorCandidate] = []

        for candidate in candidates:

            key = (
                candidate.element_id,
                candidate.locator_type,
                candidate.value,
            )

            if key in seen:
                continue

            seen.add(key)
            result.append(candidate)

        return result
