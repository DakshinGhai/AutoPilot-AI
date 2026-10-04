from app.locators.locator_generator import LocatorGenerator
from app.models.browser import ElementInfo


def test_role_candidate_contains_semantic_metadata():

    element = ElementInfo(
        element_id="candidate_1",
        tag="button",
        role="button",
        aria_label="Products",
        accessible_name="Products",
        label_text="",
        text="",
    )

    generator = LocatorGenerator()

    candidates = generator.generate(element)

    role_candidate = next(
        candidate for candidate in candidates if candidate.locator_type == "role"
    )

    assert role_candidate.semantic_role == "button"
    assert role_candidate.accessible_name == "Products"
    assert role_candidate.evidence_source == "aria-label"


def test_label_candidate_contains_semantic_metadata():

    element = ElementInfo(
        element_id="candidate_2",
        tag="input",
        role="textbox",
        label_text="Email Address",
        accessible_name="Email Address",
    )

    generator = LocatorGenerator()

    candidates = generator.generate(element)

    label_candidate = next(
        candidate for candidate in candidates if candidate.strategy == "label"
    )

    assert label_candidate.semantic_role == "textbox"
    assert label_candidate.accessible_name == "Email Address"
    assert label_candidate.evidence_source == "html-label"


def test_role_candidate_tracks_aria_labelledby():

    element = ElementInfo(
        element_id="candidate_3",
        tag="button",
        role="button",
        aria_labelledby="button-name",
        accessible_name="Book Appointment",
    )

    generator = LocatorGenerator()

    candidates = generator.generate(element)

    role_candidate = next(
        candidate for candidate in candidates if candidate.locator_type == "role"
    )

    assert role_candidate.semantic_role == "button"
    assert role_candidate.accessible_name == "Book Appointment"
    assert role_candidate.evidence_source == "aria-labelledby"
