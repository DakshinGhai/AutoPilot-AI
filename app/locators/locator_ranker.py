from typing import List

from app.models.locator import LocatorCandidate


class LocatorRanker:

    STRATEGY_SCORES = {
        "id": 100,
        "testid": 98,
        "data-test": 96,
        "data-cy": 94,
        "role": 90,
        "aria-label": 88,
        "placeholder": 85,
        "text": 70,
        "css": 50,
        "dom-path": 20,
    }

    def rank(
        self,
        candidates: List[LocatorCandidate],
    ) -> List[LocatorCandidate]:

        ranked_candidates = []

        for candidate in candidates:

            score = self._calculate_score(candidate)

            candidate.confidence = score / 100.0

            ranked_candidates.append(candidate)

        ranked_candidates.sort(
            key=lambda candidate: (candidate.confidence or 0.0),
            reverse=True,
        )

        return ranked_candidates

    def _calculate_score(
        self,
        candidate: LocatorCandidate,
    ) -> float:

        score = self.STRATEGY_SCORES.get(
            candidate.strategy,
            10,
        )

        return float(
            max(
                0,
                min(
                    100,
                    score,
                ),
            )
        )
