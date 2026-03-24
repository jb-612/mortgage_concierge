---
name: task-breakdown
description: Break a feature into atomic TDD or Eval-DD tasks ordered by dependency
argument-hint: "<workitem-path>"
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Task Breakdown

Break down the feature at $ARGUMENTS into atomic tasks.

## Prerequisites
- Read `design.md` from the workitem path
- Verify Design Status is `APPROVED` — if not, stop and suggest `/design-review` first

## Process

1. Analyze the proposed solution and identify atomic units of testable behavior
2. Classify each task:
   - **[TDD]**: Deterministic code — tools, models, helpers, state management
   - **[Eval-DD]**: Agentic behavior — prompt changes, tool selection, response quality
3. Order by dependency (infrastructure first, then core logic, then integration)
4. Write each task using this template:

```
### TNN: <description>
- Type: [TDD] | [Eval-DD]
- Files: <source files to create/modify>
- Tests: <test file> | <evalset file>
- Depends: <task IDs or "none">
- Criteria: <single testable assertion>
- Status: [ ]
```

5. Keep tasks.md under 100 lines (split feature if > 15 tasks)
6. Flag any task likely to produce functions with CC > 5

## Output
Updated `.workitems/<path>/tasks.md` with ordered task list.
