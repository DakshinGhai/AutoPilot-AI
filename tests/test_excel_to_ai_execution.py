import pytest

from app.excel.excel_reader import ExcelReader
from app.excel.test_parser import TestParser

from app.execution.executor import TestExecutor as FrameworkExecutor

from app.ai.mock_client import MockAIClient
from app.ai.locator_selector import LocatorSelectionService
from tests.helpers.integration_browser_manager import IntegrationBrowserManager

EXCEL_PATH = "test_data/ikea_test_cases.xlsx"


@pytest.mark.asyncio
async def test_excel_to_ai_playwright_execution():

    # -----------------------------------------
    # 1. Read Excel
    # -----------------------------------------

    reader = ExcelReader()

    dataframe = reader.read(EXCEL_PATH)

    assert dataframe is not None
    assert len(dataframe) > 0

    # -----------------------------------------
    # 2. Convert Excel → TestPlan
    # -----------------------------------------

    parser = TestParser()

    test_plan = parser.parse(dataframe)

    assert test_plan is not None
    assert len(test_plan.test_cases) > 0

    print(f"\nLoaded {len(test_plan.test_cases)} test case(s) from Excel")

    for test_case in test_plan.test_cases:

        print(f"\nTest Case: {test_case.test_case_id}")

        print(f"Steps: {len(test_case.steps)}")

        for step in test_case.steps:

            print(
                f"  Step {step.step}: "
                f"action={step.action}, "
                f"target={step.target}, "
                f"data={step.test_data}"
            )
    # -----------------------------------------
    # 3. AI Selection Service
    # -----------------------------------------

    ai_client = MockAIClient()

    selection_service = LocatorSelectionService(ai_client)

    # -----------------------------------------
    # 4. Browser Manager
    # -----------------------------------------
    #
    # For this integration test we use the
    # existing FakeBrowserManager from the
    # previous test.
    #
    # Import it from your test module if it
    # already exists there.
    # -----------------------------------------

    from tests.helpers.integration_browser_manager import IntegrationBrowserManager

    browser_manager = IntegrationBrowserManager()

    # -----------------------------------------
    # 5. Real TestExecutor
    # -----------------------------------------

    executor = FrameworkExecutor(
        browser_manager=browser_manager,
        ai_selection_service=selection_service,
    )

    # -----------------------------------------
    # 6. Execute Excel-generated TestPlan
    # -----------------------------------------

    results = await executor.execute(test_plan, test_case_id="TC001")

    # -----------------------------------------
    # 7. Validate execution
    # -----------------------------------------

    assert browser_manager.started is True
    assert browser_manager.closed is True

    assert len(results) > 0

    for result in results:

        print(f"\n{result.test_case_id}: " f"{result.status}")

        print(f"Test error: {result.error}")

        for step in result.steps:

            print(f"  Step {step.step}: " f"{step.status}")

            print(f"  Action: {step.action}")

            print(f"  Target: {step.target}")

            print(f"  Error: {step.error}")

        assert result.status == "PASS"

        for step in result.steps:
            assert step.status == "PASS"

        for step in result.steps:
            assert step.status == "PASS"
