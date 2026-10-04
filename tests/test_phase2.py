import pandas as pd
import pytest

from app.excel.test_parser import TestParser


def test_phase2_test_plan_is_executable():

    dataframe = pd.DataFrame(
        [
            {
                "TestCaseID": "TC001",
                "TestCaseName": "Open IKEA",
                "Description": "Open IKEA homepage",
                "StepNo": 1,
                "Action": "Navigate",
                "TestData": "https://www.ikea.com/in/en/",
                "ExpectedResult": "IKEA homepage displayed",
            }
        ]
    )

    parser = TestParser()

    test_plan = parser.parse(dataframe)

    assert len(test_plan.test_cases) == 1

    test_case = test_plan.test_cases[0]

    assert test_case.steps[0].action.value == "navigate"

    assert test_case.steps[0].target == "https://www.ikea.com/in/en/"
