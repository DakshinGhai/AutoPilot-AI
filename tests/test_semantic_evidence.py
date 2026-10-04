from app.locators.locator_generator import LocatorGenerator
from app.models.browser import ElementInfo


def test_role_candidate_contains_structured_semantic_evidence():

    element = ElementInfo(
        element_id="candidate_1",
        tag="button",
        role="button",
        aria_label="Products",
        aria_labelledby="product-label",
        aria_describedby="product-description",
        accessible_name="Products",
        accessible_description="Open product menu",
        label_text="",
        placeholder=None,
        inner_text="",
        text="",
    )

    generator = LocatorGenerator()

    candidates = generator.generate(element)

    role_candidate = next(
        candidate for candidate in candidates if candidate.locator_type == "role"
    )

    evidence = role_candidate.semantic_evidence

    assert evidence is not None

    assert evidence.role == "button"
    assert evidence.accessible_name == "Products"
    assert evidence.accessible_description == "Open product menu"

    assert evidence.aria_label == "Products"
    assert evidence.aria_labelledby == "product-label"
    assert evidence.aria_describedby == "product-description"

    assert evidence.name_source == "aria-label"


def test_label_candidate_contains_structured_semantic_evidence():

    element = ElementInfo(
        element_id="candidate_2",
        tag="input",
        role="textbox",
        label_text="Email Address",
        accessible_name="Email Address",
        accessible_description="Enter your email",
        placeholder="Enter email",
        inner_text="",
        text="",
    )

    generator = LocatorGenerator()

    candidates = generator.generate(element)

    label_candidate = next(
        candidate for candidate in candidates if candidate.strategy == "label"
    )

    evidence = label_candidate.semantic_evidence

    assert evidence is not None

    assert evidence.role == "textbox"
    assert evidence.accessible_name == "Email Address"
    assert evidence.accessible_description == "Enter your email"
    assert evidence.label_text == "Email Address"
    assert evidence.placeholder == "Enter email"

    assert evidence.name_source == "html-label"


def test_aria_labelledby_is_preserved_as_evidence():

    element = ElementInfo(
        element_id="candidate_3",
        tag="button",
        role="button",
        aria_labelledby="appointment-title",
        accessible_name="Book Appointment",
        label_text="",
        inner_text="",
        text="",
    )

    generator = LocatorGenerator()

    candidates = generator.generate(element)

    role_candidate = next(
        candidate for candidate in candidates if candidate.locator_type == "role"
    )

    evidence = role_candidate.semantic_evidence

    assert evidence is not None

    assert evidence.role == "button"
    assert evidence.accessible_name == "Book Appointment"
    assert evidence.aria_labelledby == "appointment-title"

    assert evidence.name_source == "aria-labelledby"
