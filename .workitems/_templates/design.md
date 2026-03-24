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
[trigger] ──> [tool call(s)] ──> [agent response] ──> [next phase or user turn]
```

- **Entry point**: What user intent or agent phase triggers this feature
- **Agent behavior**: What the agent does (tool calls, reasoning, response)
- **Exit point**: Where the conversation goes next

## Dependencies

- **Requires**: existing tools, sub-agents, or state keys this depends on
- **External**: third-party APIs, knowledge base docs, OpenAPI specs

## Tool Interface

```python
async def tool_name(
    param: type,
    tool_context: ToolContext = None,
) -> Dict[str, Any]:
    """Purpose of this tool and when the agent should call it."""
```

### Return Contract

```python
# Success
{"status": "ok", "result_key": { ... }}

# Error
{"status": "error", "error_message": "..."}
```

## Session State Contract

| Key | Type | Read/Write | Lifecycle | Description |
|-----|------|------------|-----------|-------------|
| `key_name` | `type` | R/W | Phase N+ | Purpose |

## Sub-Agent Design (if applicable)

- **Name**: agent name
- **Responsibility**: what it evaluates or computes
- **Internal tools**: methods exposed as FunctionTool
- **Parent integration**: how it's wrapped as a tool in root agent

## Prompt Changes (if applicable)

Which section of `prompt.py` AGENT_INSTRUCTION changes and why.
Mark as `[Eval-DD]` — prompt changes require eval baseline + comparison.

## File Structure

```
mortgage_concierge/tools/new_tool.py
mortgage_concierge/sub_agents/new_agent/  (if applicable)
tests/unit/test_new_tool.py
tests/eval/data/feature.evalset.json      (if Eval-DD tasks)
```

## Deliverables

| Artifact | Path | Description |
|----------|------|-------------|
| Tool | `mortgage_concierge/tools/module.py` | Tool implementation |
| Tests | `tests/unit/test_module.py` | Unit tests (TDD) |
| Eval cases | `tests/eval/data/feature.evalset.json` | Behavioral coverage |
| State keys | `shared_libraries/constants.py` | New state key declarations |

## Consumers

| Consumer | What it uses | Impact of change |
|----------|-------------|-----------------|
| Root agent | Tool via `agent.py` tools list | Must register tool |
| Prompt | AGENT_INSTRUCTION reference | Must update tool docs |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Choice made | Why this approach was chosen |

## Risks

| Risk | Mitigation |
|------|------------|
| Potential issue | How to address it |

## Open Questions

- Any unresolved decisions (remove when answered)
