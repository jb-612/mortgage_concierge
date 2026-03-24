---
name: prompt-tune
description: Iterative prompt engineering with hypothesis, edit, eval, compare, accept/revert
argument-hint: "<hypothesis>"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Prompt Tuning Loop

Hypothesis: $ARGUMENTS

## Iterative Process

### Step 1 — Capture Baseline
Run `/eval-baseline` or read existing `.workitems/<current>/eval-baseline.json`.

### Step 2 — Make the Edit
Modify one of:
- `mortgage_concierge/prompt.py` (AGENT_INSTRUCTION)
- `mortgage_concierge/sub_agents/loan_simulation/agent.py` (instruction string)
- `mortgage_concierge/sub_agents/package_evaluator/agent.py` (instruction string)

### Step 3 — Run Evals
```
adk eval mortgage_concierge tests/eval/data/<evalset>.evalset.json \
  --config_file_path=tests/eval/data/test_config.json \
  --print_detailed_results
```

### Step 4 — Compare
Present table:
```
| Metric                    | Before | After | Delta  |
|---------------------------|--------|-------|--------|
| tool_trajectory_avg_score | 0.85   | 0.88  | +0.03  |
| response_match_score      | 0.72   | 0.75  | +0.03  |
```

### Step 5 — Decision
- **All metrics >= baseline**: Accept. Update eval-baseline.json with new scores.
- **Any metric regressed**: Revert with `git checkout -- <file>`. Try different approach.
- **Mixed results**: Present tradeoffs, ask user to decide.

### Step 6 — Log
Append to `.workitems/<current>/prompt-tuning-log.md`:
- Hypothesis
- Change made
- Before/after scores
- Decision (accept/revert)
