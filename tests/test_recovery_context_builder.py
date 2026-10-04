from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)

from app.models.semantic import (
    SemanticEvidence,
)

from app.recovery.recovery_context_builder import (
    RecoveryContextBuilder,
)


def create_candidate():

    return LocatorCandidate(
        element_id="product-1",
        strategy="role",
        value="button:Product",
        locator_type="role",
        priority=90,
        confidence=0.90,
        reason="Semantic role with accessible name",
        semantic_evidence=SemanticEvidence(
            role="button",
            accessible_name="Product",
            accessible_description="",
            name_source="native-element-text",
            aria_label=None,
            aria_labelledby=None,
            aria_describedby=None,
            label_text="",
            placeholder=None,
            visible_text="Product",
        ),
    )


def create_validation():

    return LocatorValidationResult(
        element_id="product-1",
        strategy="role",
        value="button:Product",
        locator_type="role",
        exists=True,
        match_count=1,
        is_unique=True,
        is_visible=True,
        is_enabled=True,
        is_valid=True,
        reason="Unique visible enabled element",
    )


def test_recovery_context_contains_candidate_data():

    builder = RecoveryContextBuilder()

    context = builder.build(
        create_candidate(),
        create_validation(),
    )

    assert context.candidate_id == "product-1:role:role"

    assert context.element_id == "product-1"
    assert context.locator_type == "role"
    assert context.locator_value == ("button:Product")

    assert context.strategy == "role"
    assert context.priority == 90

    assert context.visible is True
    assert context.enabled is True
    assert context.match_count == 1
    assert context.is_unique is True
    assert context.is_valid is True

    assert context.confidence == 0.90


def test_recovery_context_preserves_semantic_evidence():

    builder = RecoveryContextBuilder()

    context = builder.build(
        create_candidate(),
        create_validation(),
    )

    assert context.semantic_evidence is not None

    assert context.semantic_evidence.role == "button"

    assert context.semantic_evidence.accessible_name == "Product"


def test_recovery_context_without_validation():

    builder = RecoveryContextBuilder()

    candidate = create_candidate()

    context = builder.build(candidate)

    assert context.candidate_id == ("product-1:role:role")

    assert context.visible is False
    assert context.enabled is False
    assert context.match_count is None

    assert context.confidence == 0.90


def test_build_many_creates_all_contexts():

    builder = RecoveryContextBuilder()

    candidate_one = create_candidate()

    candidate_two = LocatorCandidate(
        element_id="product-2",
        strategy="id",
        value="#product-2",
        locator_type="css",
        priority=100,
        confidence=1.0,
    )

    validation_one = create_validation()

    validation_two = LocatorValidationResult(
        element_id="product-2",
        strategy="id",
        value="#product-2",
        locator_type="css",
        exists=True,
        match_count=1,
        is_unique=True,
        is_visible=True,
        is_enabled=True,
        is_valid=True,
    )

    contexts = builder.build_many(
        [candidate_one, candidate_two],
        [validation_one, validation_two],
    )

    assert len(contexts) == 2

    assert contexts[0].candidate_id == ("product-1:role:role")

    assert contexts[1].candidate_id == ("product-2:css:id")

    assert contexts[0].is_valid is True
    assert contexts[1].is_valid is True
