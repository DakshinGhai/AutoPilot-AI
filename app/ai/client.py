from typing import Protocol

from app.models.ai import (
    LocatorSelectionRequest,
    LocatorSelectionResponse,
)


class AIClient(Protocol):

    async def select_locator(
        self,
        request: LocatorSelectionRequest,
    ) -> LocatorSelectionResponse: ...
