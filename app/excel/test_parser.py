import re
from typing import Optional

import pandas as pd

from app.models.test_plan import (
    ActionType,
    ExpectedResult,
    TestCase,
    TestData,
    TestPlan,
    TestStep,
)


class TestParser:

    ACTION_ALIASES = {
        "navigate": ActionType.NAVIGATE,
        "open": ActionType.NAVIGATE,
        "go to": ActionType.NAVIGATE,

        "click": ActionType.CLICK,

        "search": ActionType.SEARCH,

        "fill": ActionType.FILL,
        "enter": ActionType.FILL,

        "type": ActionType.TYPE,

        "select": ActionType.SELECT,

        "check": ActionType.CHECK,

        "uncheck": ActionType.UNCHECK,

        "hover": ActionType.HOVER,

        "press": ActionType.PRESS,

        "scroll": ActionType.SCROLL,

        "wait": ActionType.WAIT,

        "assert text": ActionType.ASSERT_TEXT,
        "verify text": ActionType.ASSERT_TEXT,

        "assert visible": ActionType.ASSERT_VISIBLE,
        "verify visible": ActionType.ASSERT_VISIBLE,

        "assert url": ActionType.ASSERT_URL,
        "verify url": ActionType.ASSERT_URL,

        "assert value": ActionType.ASSERT_VALUE,

        "assert count": ActionType.ASSERT_COUNT,
    }

    def parse(self, dataframe: pd.DataFrame) -> TestPlan:
        test_cases = []

        grouped = dataframe.groupby(
            "TestCaseID",
            sort=False
        )

        for test_case_id, group in grouped:

            first_row = group.iloc[0]

            name = self._clean_value(
                first_row["TestCaseName"]
            )

            description = self._clean_value(
                first_row["Description"]
            )

            steps = []

            group = group.sort_values(
                by="StepNo"
            )

            for _, row in group.iterrows():

                raw_action = self._clean_value(
                    row["Action"]
                )

                action, target = self._normalize_action(
                    raw_action,
                    row["TestData"]
                )

                test_data = self._clean_value(
                    row["TestData"]
                )

                expected_result = self._clean_value(
                    row["ExpectedResult"]
                )

                step = TestStep(
                    step=int(row["StepNo"]),
                    action=action,
                    target=target,
                    test_data=TestData(
                        value=test_data
                    ),
                    expected_result=ExpectedResult(
                        value=expected_result
                    ),
                    raw_action=raw_action,
                )

                steps.append(step)

            test_case = TestCase(
                test_case_id=str(test_case_id).strip(),
                name=name or f"Test Case {test_case_id}",
                description=description,
                steps=steps,
            )

            test_cases.append(test_case)

        return TestPlan(
            test_cases=test_cases
        )

    def _normalize_action(
        self,
        raw_action: str,
        test_data,
    ):
        if not raw_action:
            raise ValueError(
                "Action cannot be empty."
            )

        normalized = raw_action.strip().lower()

        # Exact match first
        if normalized in self.ACTION_ALIASES:
            action = self.ACTION_ALIASES[normalized]

            target = self._clean_value(test_data)

            return action, target

        # Natural language matching
        for alias, action_type in self.ACTION_ALIASES.items():

            pattern = rf"^\s*{re.escape(alias)}\b"

            if re.search(pattern, normalized):
                remaining = normalized[
                    len(alias):
                ].strip()

                remaining = re.sub(
                    r"^(on|to|the)\s+",
                    "",
                    remaining,
                )

                target = (
                    remaining
                    if remaining
                    else self._clean_value(test_data)
                )

                return action_type, target

        raise ValueError(
            f"Unsupported action: '{raw_action}'"
        )

    @staticmethod
    def _clean_value(value) -> Optional[str]:

        if pd.isna(value):
            return None

        value = str(value).strip()

        if not value:
            return None

        return value