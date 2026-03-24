---
paths:
  - "mortgage_concierge/**/*.py"
---

# ADK Pattern Rules

## Tool Implementation

1. All tools MUST return `dict` with a `status` field: `{"status": "ok", ...}` or `{"status": "error", "error_message": "..."}`
2. Tools accessing session state MUST accept `tool_context: ToolContext` parameter
3. Use `tool_context.state["key"] = value` for writes, `tool_context.state.get("key", default)` for reads
4. All state keys MUST be declared in `mortgage_concierge/shared_libraries/constants.py` before use
5. Use helper functions from `state_helpers.py` for common state operations
6. Override `__name__` for ADK: `my_func.__name__ = "my_tool"` then `my_tool = FunctionTool(my_func)`
7. Every tool function MUST have a docstring: purpose, usage context, return format

## Sub-Agent Design

8. Sub-agents inherit from ADK's `Agent` class
9. Internal methods used as tools: `FunctionTool(self._method)`
10. Sub-agents exposed to root agent as function tools via wrappers in `mortgage_concierge/tools/`
11. Sub-agents create own sessions via `session_service.create_session()`
12. Write results to parent's `tool_context.state` for cross-agent data sharing

## Bootstrap and Initialization

13. No import-time side effects — use `bootstrap.init()` for initialization
14. Use `@lru_cache` for expensive one-time operations

## Models

15. All data contracts use Pydantic `BaseModel` with `Field(description=...)`
16. Use `model_dump()` for dict conversion; handle datetime via `json_serializable()` helper

## Configuration

17. Model ID from env `MORTGAGE_MODEL` with fallback (see `constants.py`)
18. Root agent prompt in `prompt.py`; sub-agent prompts inline in their `__init__`
