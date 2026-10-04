from app.models.browser import ElementInfo
from app.recovery.recovery_candidate_generator import (
    RecoveryCandidateGenerator,
)

from app.recovery.recovery_candidate_service import (
    RecoveryCandidateService,
)


def create_button(
    element_id: str,
    text: str,
) -> ElementInfo:

    return ElementInfo(
        element_id=element_id,
        tag="button",
        id=element_id,
        class_name="product-button",
        name="",
        role="button",
        aria_label="",
        aria_labelledby="",
        aria_describedby="",
        accessible_name=text,
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
        dom_path=f"/html/body/button[@id='{element_id}']",
        attributes={},
    )


def test_recovery_candidates_are_generated():

    elements = [
        create_button("product-1", "Product"),
        create_button("product-2", "Product Details"),
    ]

    generator = RecoveryCandidateGenerator()

    candidates = generator.generate(elements)

    assert len(candidates) > 0

    assert all(
        candidate.element_id in {"product-1", "product-2"} for candidate in candidates
    )


def test_failed_element_is_excluded():

    elements = [
        create_button("failed-product", "Product"),
        create_button("alternative-product", "Product Details"),
    ]

    generator = RecoveryCandidateGenerator()

    candidates = generator.generate(
        elements,
        failed_element_id="failed-product",
    )

    assert len(candidates) > 0

    assert all(candidate.element_id != "failed-product" for candidate in candidates)


def test_recovery_candidates_are_deduplicated():

    elements = [
        create_button("product-1", "Product"),
        create_button("product-1", "Product"),
    ]

    generator = RecoveryCandidateGenerator()

    candidates = generator.generate(elements)

    keys = [
        (
            candidate.element_id,
            candidate.locator_type,
            candidate.value,
        )
        for candidate in candidates
    ]

    assert len(keys) == len(set(keys))


def test_recovery_candidates_are_ranked():

    elements = [
        create_button("product-1", "Product"),
        create_button("product-2", "Product Details"),
    ]

    service = RecoveryCandidateService()

    candidates = service.generate_and_rank(elements)

    assert len(candidates) > 0

    confidences = [candidate.confidence for candidate in candidates]

    assert confidences == sorted(
        confidences,
        reverse=True,
    )
