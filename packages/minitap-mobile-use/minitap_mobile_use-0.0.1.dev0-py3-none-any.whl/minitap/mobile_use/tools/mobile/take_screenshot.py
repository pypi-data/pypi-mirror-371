from typing import Optional

from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_core.tools.base import InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from minitap.mobile_use.context import MobileUseContext
from minitap.mobile_use.controllers.mobile_command_controller import (
    take_screenshot as take_screenshot_controller,
)
from minitap.mobile_use.graph.state import State
from minitap.mobile_use.tools.tool_wrapper import ExecutorMetadata, ToolWrapper
from minitap.mobile_use.utils.media import compress_base64_jpeg
from typing_extensions import Annotated


def get_take_screenshot_tool(ctx: MobileUseContext):
    @tool
    def take_screenshot(
        tool_call_id: Annotated[str, InjectedToolCallId],
        state: Annotated[State, InjectedState],
        agent_thought: str,
        executor_metadata: Optional[ExecutorMetadata],
    ):
        """
        Take a screenshot of the device.
        """
        compressed_image_base64 = None
        has_failed = False

        try:
            output = take_screenshot_controller(ctx=ctx)
            compressed_image_base64 = compress_base64_jpeg(output)
        except Exception as e:
            output = str(e)
            has_failed = True

        tool_message = ToolMessage(
            tool_call_id=tool_call_id,
            content=take_screenshot_wrapper.on_failure_fn()
            if has_failed
            else take_screenshot_wrapper.on_success_fn(),
            additional_kwargs={"error": output} if has_failed else {},
        )
        updates = {
            "agents_thoughts": [agent_thought],
            "messages": [tool_message],
        }
        if compressed_image_base64:
            updates["latest_screenshot_base64"] = compressed_image_base64
        return Command(
            update=take_screenshot_wrapper.handle_executor_state_fields(
                ctx=ctx,
                state=state,
                executor_metadata=executor_metadata,
                tool_message=tool_message,
                is_failure=has_failed,
                updates=updates,
            ),
        )

    return take_screenshot


take_screenshot_wrapper = ToolWrapper(
    tool_fn_getter=get_take_screenshot_tool,
    on_success_fn=lambda: "Screenshot taken successfully.",
    on_failure_fn=lambda: "Failed to take screenshot.",
)
