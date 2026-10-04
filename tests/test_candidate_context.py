from app.locators.candidate_context_builder import (
    CandidateContextBuilder,
)

from app.models.locator import LocatorCandidate
from app.models.semantic import SemanticEvidence


def test_candidate_context_without_validation():

    candidate = LocatorCandidate(
        element_id="candidate_1",
        strategy="role",
        value="button:Products",
        locator_type="role",
        priority=5,
        semantic_role="button",
        accessible_name="Products",
        evidence_source="aria-label",
        semantic_evidence=SemanticEvidence(
            role="button",
            accessible_name="Products",
            name_source="aria-label",
            aria_label="Products",
        ),
    )

    builder = CandidateContextBuilder()

    context = builder.build(candidate)

    assert context.candidate_id == ("candidate_1:role:role")

    assert context.element_id == "candidate_1"

    assert context.locator_type == "role"

    assert context.locator_value == ("button:Products")

    assert context.strategy == "role"

    assert context.priority == 5

    assert context.semantic_evidence is not None

    assert context.semantic_evidence.accessible_name == "Products"

    assert context.match_count is None
    assert context.is_valid is None


from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)


def test_candidate_context_with_validation():

    candidate = LocatorCandidate(
        element_id="candidate_2",
        strategy="role",
        value="button:Products",
        locator_type="role",
        priority=5,
    )

    validation = LocatorValidationResult(
        element_id="candidate_2",
        strategy="role",
        value="button:Products",
        locator_type="role",
        exists=True,
        match_count=1,
        is_unique=True,
        is_visible=True,
        is_enabled=True,
        is_valid=True,
        reason="Valid unique visible enabled locator",
    )

    builder = CandidateContextBuilder()

    context = builder.build(
        candidate,
        validation,
    )

    assert context.match_count == 1
    assert context.is_unique is True
    assert context.is_valid is True
    assert context.visible is True
    assert context.enabled is True


def test_candidate_context_preserves_semantic_evidence():

    evidence = SemanticEvidence(
        role="textbox",
        accessible_name="Email Address",
        accessible_description="Enter your email",
        name_source="html-label",
        label_text="Email Address",
        placeholder="Enter email",
    )

    candidate = LocatorCandidate(
        element_id="candidate_3",
        strategy="label",
        value="Email Address",
        locator_type="label",
        priority=6,
        semantic_evidence=evidence,
    )

    builder = CandidateContextBuilder()

    context = builder.build(candidate)

    assert context.semantic_evidence is not None

    assert context.semantic_evidence.role == "textbox"

    assert context.semantic_evidence.accessible_name == "Email Address"

    assert context.semantic_evidence.label_text == "Email Address"

    assert context.semantic_evidence.placeholder == "Enter email"
