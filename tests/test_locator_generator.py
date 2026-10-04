from app.locators.locator_generator import LocatorGenerator
from app.models.browser import ElementInfo


def test_locator_generation():

    element = ElementInfo(
        element_id="candidate_1",
        tag="button",
        id="section-products",
        class_name="hnf-menu__entrypoint",
        name=None,
        role="button",
        accessible_name="Products",
        aria_label=None,
        aria_labelledby=None,
        placeholder=None,
        title=None,
        text="Products",
        inner_text="Products",
        value=None,
        href="/in/en/cat/products-products/",
        type="button",
        alt=None,
        data_testid=None,
        data_test=None,
        data_cy=None,
        visible=True,
        enabled=True,
        bounding_box=None,
        parent_tag="nav",
        parent_text="Products",
        nearby_text="Products",
        dom_path="a#section-products",
        attributes={
            "id": "section-products",
            "role": "button",
        },
    )

    generator = LocatorGenerator()

    candidates = generator.generate(element)

    assert len(candidates) > 0

    strategies = {candidate.strategy for candidate in candidates}

    assert "id" in strategies
    assert "role" in strategies
    assert "text" in strategies
    assert "dom-path" in strategies
    role_candidates = [
        candidate for candidate in candidates if candidate.strategy == "role"
    ]

    assert len(role_candidates) > 0

    assert any(candidate.value == "button:Products" for candidate in role_candidates)


def test_aria_label_locator_generation():

    element = ElementInfo(
        element_id="candidate_aria",
        tag="button",
        id=None,
        class_name=None,
        name=None,
        role="button",
        aria_label="Enter postal code",
        aria_labelledby=None,
        placeholder=None,
        title=None,
        text="Enter postal code",
        inner_text="Enter postal code",
        value=None,
        href=None,
        type="button",
        alt=None,
        data_testid=None,
        data_test=None,
        data_cy=None,
        visible=True,
        enabled=True,
        bounding_box=None,
        parent_tag="div",
        parent_text=None,
        nearby_text=None,
        dom_path="button",
        attributes={
            "aria-label": "Enter postal code",
        },
    )

    generator = LocatorGenerator()

    candidates = generator.generate(element)

    aria_candidates = [
        candidate for candidate in candidates if candidate.strategy == "aria-label"
    ]

    assert len(aria_candidates) == 1
    assert aria_candidates[0].value == "Enter postal code"
    assert aria_candidates[0].locator_type == "aria-label"
