import pytest

from app.execution.ai_action_executor import (
    AIActionExecutor,
)


@pytest.mark.asyncio
async def test_navigate_requires_target():

    class FakePage:
        pass

    executor = AIActionExecutor(
        FakePage(),
        None,
    )

    with pytest.raises(
        ValueError,
        match="Navigate action requires a URL",
    ):
        await executor.execute(
            action="navigate",
            target=None,
        )


@pytest.mark.asyncio
async def test_click_requires_target():

    class FakePage:
        pass

    executor = AIActionExecutor(
        FakePage(),
        None,
    )

    with pytest.raises(
        ValueError,
        match="Click action requires a target",
    ):
        await executor.execute(
            action="click",
            target=None,
        )


@pytest.mark.asyncio
async def test_unsupported_ai_action():

    class FakePage:
        pass

    executor = AIActionExecutor(
        FakePage(),
        None,
    )

    with pytest.raises(
        ValueError,
        match="AI execution does not support action",
    ):
        await executor.execute(
            action="fill",
            target="Email",
        )
