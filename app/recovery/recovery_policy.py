from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryPolicy:

    enabled: bool = True

    max_attempts_per_step: int = 1

    allowed_actions: tuple[str, ...] = ("click",)

    min_candidate_confidence: float = 0.0

    def can_recover(
        self,
        action: str,
        attempt_count: int,
    ) -> bool:

        if not self.enabled:
            return False

        normalized_action = str(action).lower()

        if normalized_action not in self.allowed_actions:
            return False

        if attempt_count >= (self.max_attempts_per_step):
            return False

        return True
