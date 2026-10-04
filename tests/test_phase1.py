import pandas as pd

from app.excel.test_parser import TestParser


def test_excel_to_test_plan():

    dataframe = pd.DataFrame(
        [
            {
                "TestCaseID": "TC001",
                "TestCaseName": "Search Product",
                "Description": "Search IKEA product",
                "StepNo": 1,
                "Action": "Navigate",
                "TestData": "https://www.ikea.com/in/en/",
                "ExpectedResult": "IKEA homepage displayed",
            },
            {
                "TestCaseID": "TC001",
                "TestCaseName": "Search Product",
                "Description": "Search IKEA product",
                "StepNo": 2,
                "Action": "Search",
                "TestData": "chair",
                "ExpectedResult": "Search results displayed",
            },
            {
                "TestCaseID": "TC001",
                "TestCaseName": "Search Product",
                "Description": "Search IKEA product",
                "StepNo": 3,
                "Action": "Click",
                "TestData": "Product",
                "ExpectedResult": "Product page displayed",
            },
        ]
    )

    parser = TestParser()

    plan = parser.parse(dataframe)

    assert len(plan.test_cases) == 1

    test_case = plan.test_cases[0]

    assert test_case.test_case_id == "TC001"

    assert test_case.name == "Search Product"

    assert len(test_case.steps) == 3

    assert test_case.steps[0].action.value == "navigate"

    assert test_case.steps[1].action.value == "search"

    assert test_case.steps[2].action.value == "click"

    assert test_case.steps[2].target == "Product"


def test_natural_language_action():

    dataframe = pd.DataFrame(
        [
            {
                "TestCaseID": "TC002",
                "TestCaseName": "Interior Design",
                "Description": "Booking flow",
                "StepNo": 1,
                "Action": "Click on Interior Design",
                "TestData": None,
                "ExpectedResult": "Interior Design page displayed",
            }
        ]
    )

    parser = TestParser()

    plan = parser.parse(dataframe)

    step = plan.test_cases[0].steps[0]

    assert step.action.value == "click"

    assert step.target == "interior design"
