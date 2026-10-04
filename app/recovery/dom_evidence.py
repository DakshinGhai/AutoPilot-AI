from app.models.browser import ElementInfo
from app.models.failure import DOMEvidence


class DOMEvidenceExtractor:

    def __init__(self, max_elements: int = 30):
        self.max_elements = max_elements

    def extract(
        self,
        elements: list[ElementInfo],
        target: str | None = None,
    ) -> list[DOMEvidence]:

        ranked_elements = self._rank_elements(
            elements,
            target,
        )

        return [
            self._to_evidence(element)
            for element in ranked_elements[: self.max_elements]
        ]

    def _rank_elements(
        self,
        elements: list[ElementInfo],
        target: str | None,
    ) -> list[ElementInfo]:

        if not target or not target.strip():
            return elements

        normalized_target = target.strip().lower()

        scored = [
            (
                self._score_element(
                    element,
                    normalized_target,
                ),
                index,
                element,
            )
            for index, element in enumerate(elements)
        ]

        scored.sort(key=lambda item: (-item[0], item[1]))

        return [element for _, _, element in scored]

    def _score_element(
        self,
        element: ElementInfo,
        target: str,
    ) -> int:

        score = 0

        accessible_name = (element.accessible_name or "").strip().lower()

        text = (element.text or "").strip().lower()

        label_text = (element.label_text or "").strip().lower()

        placeholder = (element.placeholder or "").strip().lower()

        aria_label = (element.aria_label or "").strip().lower()

        nearby_text = (element.nearby_text or "").strip().lower()

        # Strongest semantic match.
        if accessible_name == target:
            score += 100

        elif target in accessible_name:
            score += 70

        # Explicit ARIA label.
        if aria_label == target:
            score += 90

        elif target in aria_label:
            score += 60

        # Associated HTML label.
        if label_text == target:
            score += 85

        elif target in label_text:
            score += 55

        # Visible text.
        if text == target:
            score += 80

        elif target in text:
            score += 50

        # Placeholder.
        if placeholder == target:
            score += 75

        elif target in placeholder:
            score += 45

        # Nearby contextual text.
        if target in nearby_text:
            score += 20

        # Prefer elements that are actually usable.
        if element.visible:
            score += 5

        if element.enabled:
            score += 5

        return score

    def _to_evidence(
        self,
        element: ElementInfo,
    ) -> DOMEvidence:

        return DOMEvidence(
            element_id=element.element_id,
            tag=element.tag,
            role=element.role,
            accessible_name=element.accessible_name,
            text=element.text,
            label_text=element.label_text,
            placeholder=element.placeholder,
            element_id_attribute=element.id,
            name=element.name,
            visible=element.visible,
            enabled=element.enabled,
            dom_path=element.dom_path,
        )
