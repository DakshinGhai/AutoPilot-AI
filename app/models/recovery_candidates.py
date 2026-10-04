from pydantic import BaseModel

from app.models.locator import (
    LocatorCandidate,
    LocatorValidationResult,
)


class RecoveryCandidateResult(BaseModel):

    candidates: list[LocatorCandidate] = []
    valid_candidates: list[
        tuple[
            LocatorCandidate,
            LocatorValidationResult,
        ]
    ] = []
