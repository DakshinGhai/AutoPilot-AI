from pathlib import Path

from app.excel.excel_reader import ExcelReader
from app.excel.test_parser import TestParser

EXCEL_PATH = Path("test_data/ikea_test_cases.xlsx")


def test_excel_produces_structured_test_plan():
    reader = ExcelReader()
    dataframe = reader.read(EXCEL_PATH)

    parser = TestParser()
    test_plan = parser.parse(dataframe)

    assert test_plan is not None
    assert len(test_plan.test_cases) > 0

    test_case = test_plan.test_cases[0]

    assert test_case.test_case_id
    assert test_case.name
    assert len(test_case.steps) > 0

    for step in test_case.steps:
        assert step.action is not None
        assert step.target is not None
