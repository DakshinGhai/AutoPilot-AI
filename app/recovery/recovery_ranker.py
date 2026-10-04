from app.models.browser import ElementInfo
from app.models.locator import LocatorCandidate


class RecoveryRanker:

    def rank(
        self,
        candidates: list[LocatorCandidate],
        elements: list[ElementInfo],
        target: str | None = None,
    ) -> list[LocatorCandidate]:

        if not target or not target.strip():
            return sorted(
                candidates,
                key=lambda candidate: (candidate.confidence or 0.0),
                reverse=True,
            )

        normalized_target = target.strip().lower()

        element_map = {element.element_id: element for element in elements}

        scored = []

        for index, candidate in enumerate(candidates):

            element = element_map.get(candidate.element_id)

            relevance = 0

            if element:
                relevance = self._target_relevance(
                    element,
                    normalized_target,
                )

            locator_score = candidate.confidence or 0.0

            total_score = relevance * 0.7 + locator_score * 0.3

            scored.append(
                (
                    total_score,
                    index,
                    candidate,
                )
            )

        scored.sort(
            key=lambda item: (
                -item[0],
                item[1],
            )
        )

        return [candidate for _, _, candidate in scored]

    def _target_relevance(
        self,
        element: ElementInfo,
        target: str,
    ) -> float:

        accessible_name = (element.accessible_name or "").strip().lower()

        aria_label = (element.aria_label or "").strip().lower()

        label_text = (element.label_text or "").strip().lower()

        visible_text = (element.text or "").strip().lower()

        placeholder = (element.placeholder or "").strip().lower()

        nearby_text = (element.nearby_text or "").strip().lower()

        # Exact semantic matches get highest relevance.
        if accessible_name == target:
            return 1.0

        if aria_label == target:
            return 0.95

        if label_text == target:
            return 0.90

        if visible_text == target:
            return 0.85

        if placeholder == target:
            return 0.80

        # Partial semantic matches.
        if target in accessible_name:
            return 0.75

        if target in aria_label:
            return 0.70

        if target in label_text:
            return 0.65

        if target in visible_text:
            return 0.60

        if target in placeholder:
            return 0.55

        if target in nearby_text:
            return 0.40

        return 0.0
