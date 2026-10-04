from typing import Optional

from pydantic import BaseModel


class ExecutionSummary(BaseModel):
    test_case_id: str
    test_case_name: str
    status: str

    total_steps: int = 0
    passed_steps: int = 0
    failed_steps: int = 0

    ai_locator_decisions: int = 0
    successful_locator_decisions: int = 0

    average_ai_confidence: Optional[float] = None
