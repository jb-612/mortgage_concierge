---
name: design-agent
description: Design and implement a new ADK sub-agent with tools, state contracts, and eval cases
argument-hint: "<agent-name> <description>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Design New Sub-Agent

Create sub-agent: $ARGUMENTS

## Step 1 — Define Responsibilities
- What tasks does this agent handle?
- What it does NOT handle (boundary with existing agents)?
- Input/output contract

## Step 2 — Design State Contract
- State keys this agent reads (from parent session)
- State keys this agent writes (to parent session)
- Add all new keys to `mortgage_concierge/shared_libraries/constants.py`

## Step 3 — Design Internal Tools
- List methods the agent uses internally
- Each wraps as `FunctionTool(self._method)`

## Step 4 — Write Agent Prompt
Follow pattern from `LoanSimulationAgent` or `PackageEvaluatorAgent`:
- TOOL INSTRUCTIONS section
- OUTPUT FORMAT section
- Domain-specific guidelines

## Step 5 — Create Pydantic Models
- Input models (specifications, criteria)
- Output models (results, assessments)
- Place in `mortgage_concierge/sub_agents/<name>/models.py`

## Step 6 — Create Eval Cases
- Add evalset JSON in `tests/eval/data/`
- Queries that trigger the agent's wrapper tool

## Step 7 — Implement
- `mortgage_concierge/sub_agents/<name>/__init__.py`
- `mortgage_concierge/sub_agents/<name>/agent.py`
- `mortgage_concierge/sub_agents/<name>/models.py`
- `mortgage_concierge/tools/<name>_tools.py` (wrapper)
- Register in `agent.py` and `prompt.py`

## Step 8 — Write Tests
- Unit tests for agent methods and wrapper tool
- Integration tests for full flow

## Reference
- Canonical pattern: `mortgage_concierge/sub_agents/loan_simulation/agent.py`
- Wrapper pattern: `mortgage_concierge/tools/simulation_tools.py`
