---
# Unconditional — always loaded
---

# TDD and Eval-DD Discipline

## Three Laws of TDD (Deterministic Code)

1. Do not write production code unless it makes a failing test pass
2. Do not write more of a test than is sufficient to fail
3. Do not write more production code than is sufficient to pass the failing test

## When to Use TDD vs Eval-DD

### TDD — for deterministic, testable code:
- Tool functions in `mortgage_concierge/tools/`
- Pydantic models in `*/models.py`
- Helper functions in `shared_libraries/`
- State management logic
- Data transformation and calculation logic

**Test with:** `pytest` unit tests using `DummyToolContext`/`MockToolContext`

### Eval-DD — for agentic, non-deterministic behavior:
- Agent instruction prompts (`prompt.py`)
- Sub-agent instruction strings
- Tool selection and routing behavior
- Response generation quality
- Multi-turn conversation flow

**Test with:** ADK `AgentEvaluator` with evalset JSON files

## Three-Agent Role Separation

During TDD sessions (when `/tmp/mc-tdd-markers/<hash>` exists):

| Agent | Phase | Can Edit | Cannot Edit |
|-------|-------|----------|-------------|
| tdd-test-writer | RED | `test_*.py`, `*_test.py` | production `.py` |
| tdd-code-writer | GREEN | production `.py` | test files |
| tdd-refactorer | REFACTOR | both | — (no new behavior) |
| lead | coordination | no `.py` files | all `.py` |

## Complexity Rule

- CC <= 5: Acceptable
- CC 6-7: Must refactor before commit
- CC > 7: Blocked by check-complexity.sh hook

## Write Tests Before Implementation

Per global CLAUDE.md: before implementing any new behavior or bug fix, write tests for it first.
