from app.models.recovery import RecoveryExecutionResult
from app.models.trace import RecoveryTrace


class AIRecoveryTraceBuilder:

    def build(
        self,
        result: RecoveryExecutionResult,
    ) -> RecoveryTrace:

        candidate = result.selected_candidate
        validation = result.validation

        return RecoveryTrace(
            attempted=result.attempted,
            success=result.success,
            attempt_count=result.attempt_count,
            candidate_count=result.candidate_count,
            valid_candidate_count=(result.valid_candidate_count),
            selected_candidate_id=(self._candidate_id(candidate)),
            selected_locator_type=(candidate.locator_type if candidate else None),
            selected_locator_value=(candidate.value if candidate else None),
            retry_attempted=result.retry_attempted,
            original_error=result.original_error,
            recovery_error=result.recovery_error,
            ai_used=result.ai_used,
            ai_confidence=result.ai_confidence,
            ai_reason=result.ai_reason,
            final_match_count=(validation.match_count if validation else None),
            final_is_unique=(validation.is_unique if validation else None),
            final_is_visible=(validation.is_visible if validation else None),
            final_is_enabled=(validation.is_enabled if validation else None),
            final_is_valid=(validation.is_valid if validation else None),
        )

    @staticmethod
    def _candidate_id(candidate):

        if candidate is None:
            return None

        return (
            f"{candidate.element_id}:"
            f"{candidate.locator_type}:"
            f"{candidate.strategy}"
        )
