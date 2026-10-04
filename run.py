import argparse
import asyncio
import json
from pathlib import Path

from app.excel.excel_reader import ExcelReader
from app.excel.test_parser import TestParser
from app.execution.browser_manager import BrowserManager
from app.execution.executor import TestExecutor
from app.ai.gemini_client import GeminiAIClient
from app.ai.gemini_client import GeminiAIClient
from app.ai.locator_selector import LocatorSelectionService


def parse_arguments():

    parser = argparse.ArgumentParser(description="AI Test Automation Framework")

    parser.add_argument(
        "--excel",
        required=True,
        help="Path to Excel test plan",
    )

    parser.add_argument(
        "--list-tests",
        action="store_true",
        help="List available test cases",
    )

    parser.add_argument(
        "--validate-plan",
        action="store_true",
        help="Generate TestPlan JSON only",
    )

    parser.add_argument(
        "--test-case",
        help="Execute only a specific test case",
    )

    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed mode",
    )

    return parser.parse_args()


def build_test_plan(excel_path):

    reader = ExcelReader()

    dataframe = reader.read(excel_path)

    parser = TestParser()

    return parser.parse(dataframe)


def save_test_plan(test_plan):

    output_directory = Path("output")

    output_directory.mkdir(exist_ok=True)

    output_file = output_directory / "test_plan.json"

    with output_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            test_plan.model_dump(mode="json"),
            file,
            indent=2,
            ensure_ascii=False,
        )

    return output_file


async def execute_tests(test_plan, headed, test_case_id=None):
    browser_manager = BrowserManager(
        headless=not headed,
        timeout=30000,
    )

    ai_client = GeminiAIClient()
    ai_selection_service = LocatorSelectionService(ai_client)

    executor = TestExecutor(
        browser_manager,
        ai_selection_service=ai_selection_service,
    )

    return await executor.execute(
        test_plan,
        test_case_id=test_case_id,
    )


async def async_main():

    args = parse_arguments()

    print("\n===================================")
    print(" AI Test Automation Framework")
    print(" Phase 2 - Browser Execution")
    print("===================================\n")

    print(f"Reading Excel: {args.excel}")

    test_plan = build_test_plan(args.excel)

    print(f"Test cases loaded: " f"{len(test_plan.test_cases)}")

    if args.list_tests:

        print("\nAvailable Test Cases:\n")

        for test_case in test_plan.test_cases:

            print(f"{test_case.test_case_id}" f" - " f"{test_case.name}")

        return

    output_file = save_test_plan(test_plan)

    print(f"TestPlan saved to: " f"{output_file}")

    if args.validate_plan:

        print("\nTestPlan validation successful.")

        return

    print("\nStarting Playwright...")

    results = await execute_tests(
        test_plan,
        headed=args.headed,
        test_case_id=args.test_case,
    )

    print("\n===================================")
    print(" Execution Results")
    print("===================================\n")

    for result in results:

        print(f"{result.test_case_id} " f"- " f"{result.test_case_name}")

        print(f"Status: {result.status}")

        for step in result.steps:

            print(f"  Step {step.step}: " f"{step.action}" f" -> " f"{step.status}")

            if step.error:

                print(f"    Error: " f"{step.error}")

        print()


def main():

    asyncio.run(async_main())


if __name__ == "__main__":
    main()
