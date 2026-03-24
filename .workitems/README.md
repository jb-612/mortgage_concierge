# Work Items

Structured planning artifacts for the mortgage concierge agent.

## Naming Convention

Two-level hierarchy: `PNN/FNN-<snake_case_name>/`
- `PNN/` = Phase directory (P01 = Core, P02 = Quality, P03 = Hardening, P04 = Features)
- `FNN-name/` = Feature folder within phase

Examples: `P01/F01-borrower_profiling/`, `P04/F02-package_comparison/`

## Files Per Feature

| File | Purpose | Created By |
|------|---------|------------|
| `design.md` | Conversation flow, tool interface, state contract, eval strategy | Planner |
| `user_stories.md` | Borrower scenarios with eval mapping per criterion | Planner |
| `tasks.md` | Atomic tasks tagged `[TDD]` or `[Eval-DD]` | Planner |
| `eval-baseline.json` | ADK eval scores captured before implementation | `/eval-baseline` |

## Dual Testing Strategy

Agentic systems require two testing approaches:

### TDD — Deterministic Code
- Tool functions, Pydantic models, state helpers, data transformations
- Tested with `pytest` using `DummyToolContext`
- RED-GREEN-REFACTOR with 3-agent role separation

### Eval-DD — Agentic Behavior
- Prompt instructions, tool selection, response quality, conversation flow
- Tested with ADK `AgentEvaluator` and evalset JSON files
- Baseline captured before changes, scores compared after
- Thresholds: `tool_trajectory_avg_score >= 0.8`, `response_match_score >= 0.7`

### When to use which

| Change type | Testing method | Artifact |
|-------------|---------------|----------|
| New tool function | TDD | `tests/unit/test_*.py` |
| Tool return format | TDD | `tests/unit/test_*.py` |
| State helper logic | TDD | `tests/unit/test_*.py` |
| Prompt instruction edit | Eval-DD | `tests/eval/data/*.evalset.json` |
| Tool selection behavior | Eval-DD | `tests/eval/data/*.evalset.json` |
| Response quality | Eval-DD | `tests/eval/data/*.evalset.json` |
| New conversation phase | Both | Unit tests + eval cases |

## Templates

```bash
mkdir -p .workitems/PNN/FNN-name
cp .workitems/_templates/*.md .workitems/PNN/FNN-name/
```

The `/feature-spec` skill handles this automatically.

## Rules

1. **Plan before code** — workitem must exist before implementation
2. **Design verdict required** — `status: approved` before coding
3. **Tasks are atomic** — each < 2 hours, one testable behavior
4. **TDD for tools** — deterministic logic tested with pytest
5. **Eval-DD for behavior** — prompt/routing tested with ADK evals
6. **Eval baseline required** — capture before any prompt change
7. **No threshold regression** — eval scores must not drop below baseline
8. **State keys declared** — new keys added to `constants.py`
