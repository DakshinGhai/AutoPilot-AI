from app.locators.locator_ranker import LocatorRanker
from app.models.locator import LocatorCandidate


def test_locator_ranking():

    candidates = [
        LocatorCandidate(
            element_id="candidate_1",
            strategy="dom-path",
            value="//div/button[1]",
            locator_type="xpath",
        ),
        LocatorCandidate(
            element_id="candidate_1",
            strategy="text",
            value="Products",
            locator_type="text",
        ),
        LocatorCandidate(
            element_id="candidate_1",
            strategy="role",
            value="Products",
            locator_type="role",
        ),
        LocatorCandidate(
            element_id="candidate_1",
            strategy="id",
            value="#section-products",
            locator_type="css",
        ),
    ]

    ranker = LocatorRanker()

    ranked = ranker.rank(candidates)

    assert len(ranked) == 4

    assert ranked[0].strategy == "id"

    assert ranked[1].strategy == "role"

    assert ranked[-1].strategy == "dom-path"

    assert ranked[0].confidence >= ranked[1].confidence

    assert ranked[1].confidence >= ranked[2].confidence

    assert ranked[2].confidence >= ranked[3].confidence
