---
name: design-review
description: Review a feature design for completeness, architecture alignment, and ADK patterns compliance
argument-hint: "<workitem-path>"
allowed-tools: Read, Glob, Grep, Bash
---

# Design Review

Review the design at $ARGUMENTS.

## Three Review Checks

### Check 1 — Design Completeness
- All required sections present: Problem Statement, Proposed Solution, Architecture Impact, State Contract, ADK Patterns, Acceptance Criteria
- State Contract keys follow naming conventions from `mortgage_concierge/shared_libraries/constants.py`
- Acceptance criteria are testable (can be asserted in a test or eval)
- File is under 100 lines

### Check 2 — Architecture Alignment
Read `_docs/hld.md` (if exists) and check:
- Agent/tool separation: tools contain business logic, agents contain orchestration
- State contracts don't conflict with existing keys in `constants.py`
- Sub-agent responsibilities are clearly bounded (no overlap with existing agents)
- No cross-layer imports (tools should not import from agent.py)

### Check 3 — ADK Patterns Compliance
- Tools return `dict` with `status` field
- Tools use `tool_context: ToolContext` parameter
- State access via `tool_context.state`
- Sub-agents wrapped as `FunctionTool`
- Bootstrap pattern respected (no import-time side effects)
- Pydantic models for data contracts

## Verdict
- **APPROVED**: No blocking issues. Update design.md status to `APPROVED` with date.
- **CHANGES_REQUIRED**: List specific issues. Update status to `CHANGES_REQUIRED` with findings.

## Output
Update the design.md file's `Design Status` line with verdict and date.
