"""
Tool to update the tool's context state with new key-value pairs.
Useful for persisting data across tool calls within an agent session.
"""

import logging
import typing
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

def store_state_tool(
    state: dict[str, typing.Any], tool_context: ToolContext
) -> dict[str, str]:
    """
    Merges the provided state dictionary into the existing tool_context.state.

    Args:
        state: A dictionary containing state data to store.
        tool_context: The ToolContext object which holds the current state.

    Returns:
        A dictionary indicating the status and any error message if applicable.
    """
    logger.info("store_state_tool called with state: %s", state)
    try:
        tool_context.state.update(state)
        return {"status": "ok"}
    except Exception as exc:
        logger.exception("Failed to store state: %s", exc)
        return {"status": "error", "error_message": str(exc)}