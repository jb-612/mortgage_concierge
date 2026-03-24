---
name: feature-spec
description: Create a new feature workitem folder with design.md and tasks.md templates
argument-hint: "<epic-number> <feature-number> <feature-name> [description]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Feature Specification Creator

Create a workitem for feature $ARGUMENTS.

## Steps

1. Parse arguments: extract PNN (epic), FNN (feature), feature name, optional description
2. Read `_docs/prd.md` and `_docs/capability-map.md` (if they exist) to understand existing capabilities
3. Create folder: `.workitems/PNN-FNN-<snake_case_name>/`
4. Generate `design.md` (max 100 lines) with this template:

```
# PNN-FNN: <Feature Name>

## Problem Statement
<What problem does this solve?>

## Proposed Solution
<High-level approach>

## Architecture Impact
- Agent changes: <none | root agent | new sub-agent>
- Tool changes: <new tools | modified tools>
- State changes: <new state keys | modified keys>
- Model changes: <new Pydantic models | modified models>

## State Contract
| Key | Type | Read By | Written By |
|-----|------|---------|------------|

## ADK Patterns
- Tools to add/modify: <list>
- Prompt changes needed: <yes/no, which agent>
- Eval cases needed: <list of scenarios>

## Acceptance Criteria
- [ ] <Criterion 1>
- [ ] <Criterion 2>

## Design Status: PENDING_REVIEW
```

5. Generate `tasks.md` stub (max 100 lines):

```
# PNN-FNN: <Feature Name> — Tasks

## Status: [ ] Complete

### T01: <first task>
- Type: [TDD] | [Eval-DD]
- Files: <source files to create/modify>
- Tests: <test file path> | <evalset file path>
- Depends: none
- Criteria: <testable assertion>
- Status: [ ]
```

6. Verify both files are under 100 lines
7. Report: workitem path created, next step is `/design-review`
