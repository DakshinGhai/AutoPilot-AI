from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    SEARCH = "search"
    FILL = "fill"
    TYPE = "type"
    SELECT = "select"
    CHECK = "check"
    UNCHECK = "uncheck"
    HOVER = "hover"
    PRESS = "press"
    SCROLL = "scroll"
    WAIT = "wait"
    ASSERT_TEXT = "assert_text"
    ASSERT_VISIBLE = "assert_visible"
    ASSERT_URL = "assert_url"
    ASSERT_VALUE = "assert_value"
    ASSERT_COUNT = "assert_count"


class TestData(BaseModel):
    value: Optional[str] = None


class ExpectedResult(BaseModel):
    value: Optional[str] = None


class TestStep(BaseModel):
    step: int = Field(ge=1)
    action: ActionType
    target: Optional[str] = None
    test_data: Optional[TestData] = None
    expected_result: Optional[ExpectedResult] = None
    raw_action: Optional[str] = None


class TestCase(BaseModel):
    test_case_id: str
    name: str
    description: Optional[str] = None
    steps: List[TestStep]


class TestPlan(BaseModel):
    test_cases: List[TestCase]