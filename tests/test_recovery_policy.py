from app.recovery.recovery_policy import (
    RecoveryPolicy,
)


def test_recovery_is_allowed_for_click():

    policy = RecoveryPolicy()

    assert policy.can_recover(
        action="click",
        attempt_count=0,
    )


def test_recovery_is_blocked_after_one_attempt():

    policy = RecoveryPolicy()

    assert not policy.can_recover(
        action="click",
        attempt_count=1,
    )


def test_recovery_is_blocked_for_unsupported_action():

    policy = RecoveryPolicy()

    assert not policy.can_recover(
        action="navigate",
        attempt_count=0,
    )


def test_recovery_can_be_disabled():

    policy = RecoveryPolicy(enabled=False)

    assert not policy.can_recover(
        action="click",
        attempt_count=0,
    )
