---
id: Pnn/Fnn
parent_id: Pnn
type: tasks
version: 1
status: draft
estimated_hours: 0
dependencies: []
tags: []
created_by: planner
created_at: "YYYY-MM-DDTHH:MM:SSZ"
updated_at: "YYYY-MM-DDTHH:MM:SSZ"
---

# Tasks: Feature Name

## Progress

- Started: YYYY-MM-DD
- Tasks Complete: 0/N
- Percentage: 0%
- Status: NOT_STARTED

## Dependency Graph

```
T01 ──> T02 ──> T06
T03 ──> T04 ──> T06
T05 ──────────> T06
```

## Tasks

### T01: Pydantic model and state keys [TDD]
- [ ] Estimate: 30min
- [ ] Tests: tests/unit/test_models.py
- [ ] Dependencies: None
- [ ] Notes: Define data contracts, declare keys in constants.py

### T02: Core tool implementation [TDD]
- [ ] Estimate: 1hr
- [ ] Tests: tests/unit/test_tool.py
- [ ] Dependencies: T01
- [ ] Notes: Tool returns dict with status field, uses tool_context.state

### T03: State helper functions [TDD]
- [ ] Estimate: 30min
- [ ] Tests: tests/unit/test_state_helpers.py
- [ ] Dependencies: T01
- [ ] Notes: Add getters/setters to state_helpers.py

### T04: Eval cases for tool selection [Eval-DD]
- [ ] Estimate: 30min
- [ ] Eval: tests/eval/data/feature.evalset.json
- [ ] Baseline: .workitems/Pnn/Fnn/eval-baseline.json
- [ ] Thresholds: tool_trajectory >= 0.8, response_match >= 0.7
- [ ] Dependencies: T02, T03
- [ ] Notes: Write evalset entries before prompt changes

### T05: Prompt instruction update [Eval-DD]
- [ ] Estimate: 30min
- [ ] Eval: tests/eval/data/feature.evalset.json
- [ ] Baseline: captured in T04
- [ ] Thresholds: scores must not regress below T04 baseline
- [ ] Dependencies: T04
- [ ] Notes: Capture baseline, edit prompt.py, compare, accept/revert

### T06: Integration and agent registration [TDD]
- [ ] Estimate: 30min
- [ ] Tests: tests/integration/test_feature.py
- [ ] Dependencies: T02, T03, T05
- [ ] Notes: Register tool in agent.py, verify end-to-end

## Summary

| Phase | Tasks | Type | Est. Hours |
|-------|-------|------|------------|
| Data contracts | T01, T03 | TDD | Xhr |
| Tool logic | T02 | TDD | Xhr |
| Eval coverage | T04 | Eval-DD | Xhr |
| Agent behavior | T05 | Eval-DD | Xhr |
| Integration | T06 | TDD | Xhr |
| **Total** | **N tasks** | | **Xhr** |

## Deliverables Checklist

- [ ] All source files from design.md Deliverables table exist
- [ ] Tool registered in `agent.py` tools list
- [ ] Tool documented in `prompt.py` AGENT_INSTRUCTION
- [ ] State keys declared in `constants.py`
- [ ] Unit tests pass (`pytest tests/unit/`)
- [ ] Eval baseline captured in workitem folder (`eval-baseline.json`)
- [ ] Eval cases added to evalset (`tests/eval/data/`)
- [ ] Eval scores at or above baseline (`adk eval`)
- [ ] No eval threshold regressions below: tool >= 0.8, response >= 0.7
- [ ] Consumer impact assessed (see design.md Consumers table)
