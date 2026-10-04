from app.models.browser import ElementInfo
from app.models.locator import LocatorCandidate
from app.recovery.recovery_ranker import RecoveryRanker


def create_element(
    element_id: str,
    accessible_name: str,
    text: str,
) -> ElementInfo:

    return ElementInfo(
        element_id=element_id,
        tag="button",
        id=element_id,
        class_name="",
        name="",
        role="button",
        aria_label="",
        aria_labelledby="",
        aria_describedby="",
        accessible_name=accessible_name,
        accessible_description="",
        label_text="",
        placeholder="",
        title="",
        text=text,
        inner_text=text,
        value="",
        href="",
        type="button",
        alt="",
        data_testid="",
        data_test="",
        data_cy="",
        visible=True,
        enabled=True,
        bounding_box=None,
        parent_tag="div",
        parent_text="",
        nearby_text="",
        dom_path="",
        attributes={},
    )


def create_candidate(
    element_id: str,
    strategy: str,
    confidence: float,
) -> LocatorCandidate:

    return LocatorCandidate(
        element_id=element_id,
        strategy=strategy,
        value=f"#{element_id}",
        locator_type="css",
        priority=50,
        confidence=confidence,
    )


def test_exact_target_match_is_prioritized():

    elements = [
        create_element(
            "wrong-button",
            "Products",
            "Products",
        ),
        create_element(
            "target-button",
            "Product",
            "Product",
        ),
    ]

    candidates = [
        create_candidate(
            "wrong-button",
            "css",
            1.0,
        ),
        create_candidate(
            "target-button",
            "css",
            0.5,
        ),
    ]

    ranker = RecoveryRanker()

    ranked = ranker.rank(
        candidates,
        elements,
        target="Product",
    )

    assert ranked[0].element_id == ("target-button")


def test_semantic_target_match_beats_unrelated_candidate():

    elements = [
        create_element(
            "unrelated",
            "Add to cart",
            "Add to cart",
        ),
        create_element(
            "target",
            "Product Details",
            "Product Details",
        ),
    ]

    candidates = [
        create_candidate(
            "unrelated",
            "id",
            1.0,
        ),
        create_candidate(
            "target",
            "role",
            0.8,
        ),
    ]

    ranker = RecoveryRanker()

    ranked = ranker.rank(
        candidates,
        elements,
        target="Product",
    )

    assert ranked[0].element_id == "target"


def test_without_target_locator_confidence_is_used():

    elements = [
        create_element(
            "button-1",
            "Product",
            "Product",
        ),
        create_element(
            "button-2",
            "Product Details",
            "Product Details",
        ),
    ]

    candidates = [
        create_candidate(
            "button-1",
            "css",
            0.5,
        ),
        create_candidate(
            "button-2",
            "role",
            0.9,
        ),
    ]

    ranker = RecoveryRanker()

    ranked = ranker.rank(
        candidates,
        elements,
        target=None,
    )

    assert ranked[0].element_id == "button-2"
