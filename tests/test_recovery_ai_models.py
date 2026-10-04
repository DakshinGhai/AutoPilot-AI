import pytest
from pydantic import ValidationError

from app.models.candidate_context import CandidateContext
from app.models.recovery_ai import (
    RecoverySelectionRequest,
    RecoverySelectionResponse,
)


def create_candidate(
    candidate_id: str = "candidate-1",
) -> CandidateContext:

    return CandidateContext(
        candidate_id=candidate_id,
        element_id="product-1",
        locator_type="role",
        locator_value="button:Product",
        strategy="role",
        priority=90,
        visible=True,
        enabled=True,
        match_count=1,
        is_unique=True,
        is_valid=True,
        confidence=0.90,
        reason="Semantic role with accessible name",
    )


def test_recovery_selection_request():

    candidate = create_candidate()

    request = RecoverySelectionRequest(
        test_step="Click Product",
        target="Product",
        original_error="Locator click failed.",
        page_url="https://www.ikea.com/in/en/",
        page_title="IKEA",
        candidates=[candidate],
    )

    assert request.test_step == "Click Product"
    assert request.target == "Product"
    assert request.original_error == ("Locator click failed.")

    assert len(request.candidates) == 1

    assert request.candidates[0].candidate_id == "candidate-1"


def test_recovery_selection_request_defaults():

    request = RecoverySelectionRequest(
        test_step="Click Product",
        target="Product",
        original_error="Locator failed.",
    )

    assert request.page_url is None
    assert request.page_title is None
    assert request.candidates == []


def test_recovery_selection_response():

    response = RecoverySelectionResponse(
        selected_candidate_id=("candidate-1"),
        reason=("Candidate matches the target."),
        confidence=0.94,
    )

    assert response.selected_candidate_id == "candidate-1"

    assert response.reason == ("Candidate matches the target.")

    assert response.confidence == 0.94


def test_recovery_selection_response_rejects_invalid_confidence():

    with pytest.raises(ValidationError):

        RecoverySelectionResponse(
            selected_candidate_id="candidate-1",
            reason="Invalid confidence.",
            confidence=1.5,
        )


def test_recovery_selection_response_rejects_negative_confidence():

    with pytest.raises(ValidationError):

        RecoverySelectionResponse(
            selected_candidate_id="candidate-1",
            reason="Invalid confidence.",
            confidence=-0.1,
        )
