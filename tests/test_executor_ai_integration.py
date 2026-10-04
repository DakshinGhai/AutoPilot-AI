import pytest

from app.ai.locator_selector import LocatorSelectionService
from app.ai.mock_client import MockAIClient
from app.execution.executor import TestExecutor as FrameworkExecutor


class FakeBrowserManager:

    def __init__(self, page):
        self.page = page
        self.started = False
        self.closed = False

    async def start(self):
        self.started = True
        return self.page

    async def close(self):
        self.closed = True


class FakePage:

    url = "https://example.com"

    async def title(self):
        return "Example"


@pytest.mark.asyncio
async def test_executor_accepts_ai_selection_service():

    ai_client = MockAIClient()

    selection_service = LocatorSelectionService(ai_client)

    page = FakePage()

    browser_manager = FakeBrowserManager(page)

    executor = FrameworkExecutor(
        browser_manager=browser_manager,
        ai_selection_service=selection_service,
    )

    assert executor.ai_selection_service is (selection_service)

    assert browser_manager.started is False
    assert browser_manager.closed is False
