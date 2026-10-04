from typing import Protocol

from app.models.recovery_ai import (
    RecoverySelectionRequest,
    RecoverySelectionResponse,
)


class RecoveryAIClient(Protocol):

    async def select_recovery_candidate(
        self,
        request: RecoverySelectionRequest,
    ) -> RecoverySelectionResponse: ...
