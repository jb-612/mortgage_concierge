---
id: Pnn/Fnn
parent_id: Pnn
type: design
version: 1
status: draft
dependencies: []
tags: []
created_by: planner
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
---

# Feature Name

## Overview

What this feature adds to the mortgage concierge and why. 1-2 paragraphs.

## Conversation Flow

How this feature fits into the agent's conversation phases.

```
[trigger] ──> [tool call(s)] ──> [agent response] ──> [next phase]
```

- **Entry point**: What user intent or agent phase triggers this
- **Agent behavior**: Tool calls, reasoning, response format
- **Exit point**: Where the conversation goes next

## Dependencies

- **Requires**: existing tools, sub-agents, or state keys
- **External**: APIs, knowledge base docs, OpenAPI specs

## Tool Interface

```python
async def tool_name(
    param: type,
    tool_context: ToolContext = None,
) -> Dict[str, Any]:
    """Purpose and when the agent should call it."""
```

### Return Contract

```python
{"status": "ok", "result_key": { ... }}    # success
{"status": "error", "error_message": "..."}  # error
```

## Session State Contract

| Key | Type | R/W | Lifecycle | Description |
|-----|------|-----|-----------|-------------|
| `key` | `type` | R/W | Phase N+ | Purpose |

## Eval Strategy

### Deterministic behavior (TDD)

| Behavior | Test | Method |
|----------|------|--------|
| Tool returns correct structure | `tests/unit/test_tool.py` | pytest + DummyToolContext |
| State keys populated correctly | `tests/unit/test_tool.py` | Assert on tool_context.state |
| Error cases return status=error | `tests/unit/test_tool.py` | pytest parametrize |

### Agentic behavior (Eval-DD)

| Behavior | Eval entry | Metric | Threshold |
|----------|-----------|--------|-----------|
| Agent calls tool on trigger | `feature.evalset.json` | `tool_trajectory_avg_score` | >= 0.8 |
| Response references tool data | `feature.evalset.json` | `response_match_score` | >= 0.7 |

### Eval baseline requirement

Before any prompt change, capture baseline with `/eval-baseline`.
Store in `eval-baseline.json` within this workitem folder.
Accept only if scores improve or hold; revert if regressed.

## Prompt Changes (if applicable)

Which section of `prompt.py` AGENT_INSTRUCTION changes and why.
All prompt changes are `[Eval-DD]` — require baseline + comparison.

## Sub-Agent Design (if applicable)

- **Name**: agent name
- **Responsibility**: what it evaluates or computes
- **Internal tools**: methods exposed as FunctionTool
- **Parent integration**: wrapped as tool in root agent

## File Structure

```
mortgage_concierge/tools/new_tool.py
tests/unit/test_new_tool.py
tests/eval/data/feature.evalset.json
.workitems/Pnn/Fnn-name/eval-baseline.json
```

## Deliverables

| Artifact | Path | Description |
|----------|------|-------------|
| Tool | `mortgage_concierge/tools/module.py` | Implementation |
| Unit tests | `tests/unit/test_module.py` | TDD coverage |
| Eval cases | `tests/eval/data/feature.evalset.json` | Behavioral coverage |
| Eval baseline | `.workitems/Pnn/Fnn/eval-baseline.json` | Pre-change scores |
| State keys | `shared_libraries/constants.py` | Key declarations |

## Consumers

| Consumer | What it uses | Impact of change |
|----------|-------------|-----------------|
| Root agent | Tool via `agent.py` | Must register tool |
| Prompt | AGENT_INSTRUCTION | Must document tool |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Choice | Why |

## Risks

| Risk | Mitigation |
|------|------------|
| Issue | Fix |
