---
name: add-tool
description: Scaffold a new ADK function tool with TDD lifecycle and eval case addition
argument-hint: "<tool-name> <description>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Add New ADK Tool

Create tool: $ARGUMENTS

## Step 1 — Design
Define:
- Function name (snake_case)
- Parameters (with types, including `tool_context: ToolContext`)
- Return type: `Dict[str, Any]` with `status` field
- New state keys (if any) → add to `mortgage_concierge/shared_libraries/constants.py`
- Docstring: purpose, usage context, return format

## Step 2 — Write Tests First (TDD Red)
Create `tests/unit/test_<tool_name>.py`:
- Import `DummyToolContext` (from conftest.py or define inline)
- Test success case, error case, edge cases
- Use `@pytest.mark.asyncio` if async
- Verify tests FAIL (tool doesn't exist yet)

## Step 3 — Implement
Create `mortgage_concierge/tools/<tool_name>.py`:
- Follow pattern from existing tools (e.g., `store_state.py` for sync, `simulation_tools.py` for async)
- Override `__name__`: `func.__name__ = "<tool_name>"`
- Wrap: `tool = FunctionTool(func)`
- Verify tests PASS

## Step 4 — Register
- Import in `mortgage_concierge/agent.py`
- Add to `tools=[]` list
- Add tool description to `AGENT_INSTRUCTION` in `prompt.py`

## Step 5 — Add Eval Cases
- Add at least one entry to appropriate evalset in `tests/eval/data/`
- Include `query`, `expected_tool_use`, `reference`

## Step 6 — Verify No Regression
Run full eval suite and compare against baseline.

## Reference Files
- Sync pattern: `mortgage_concierge/tools/store_state.py`
- Async pattern: `mortgage_concierge/tools/simulation_tools.py`
- Test pattern: `tests/unit/test_loan_calculator.py`
- Agent registration: `mortgage_concierge/agent.py`
