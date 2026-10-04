from app.models.trace import RecoveryTrace


def test_successful_recovery_trace():

    trace = RecoveryTrace(
        attempted=True,
        success=True,
        attempt_count=1,
        policy_allowed=True,
        selected_candidate_id=("candidate_1:role:role"),
        selected_locator_type="role",
        selected_locator_value=("button:Product"),
        selected_confidence=0.90,
        retry_attempted=True,
        original_error=("Original locator failed."),
        recovery_error=None,
        candidate_count=10,
        valid_candidate_count=3,
    )

    assert trace.attempted is True
    assert trace.success is True
    assert trace.policy_allowed is True
    assert trace.attempt_count == 1
    assert trace.retry_attempted is True

    assert trace.selected_locator_type == "role"

    assert trace.valid_candidate_count == 3


def test_failed_recovery_trace():

    trace = RecoveryTrace(
        attempted=True,
        success=False,
        attempt_count=1,
        policy_allowed=True,
        retry_attempted=False,
        original_error=("Original locator failed."),
        recovery_error=("No valid recovery candidates found."),
        candidate_count=5,
        valid_candidate_count=0,
    )

    assert trace.attempted is True
    assert trace.success is False
    assert trace.policy_allowed is True
    assert trace.attempt_count == 1
    assert trace.retry_attempted is False
    assert trace.valid_candidate_count == 0
