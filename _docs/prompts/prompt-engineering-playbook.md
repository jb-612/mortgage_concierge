# Prompt Engineering Playbook

## Current Prompt Architecture

The root agent prompt lives in `mortgage_concierge/prompt.py` as `AGENT_INSTRUCTION`.
It defines a 4-phase conversation flow:

1. **Phase 1: Borrower Profiling** — Collect 6 fields, store via `store_state_tool`
2. **Phase 2: Loan Calculation** — Use OpenAPI tools for calculate/recalculate
3. **Phase 3: Multi-Track Simulation** — List tracks, configure packages, simulate
4. **Phase 4: Package Evaluation** — Set criteria, evaluate, recommend

Sub-agent prompts are inline in their `__init__` methods:
- `loan_simulation/agent.py` — Simulation-specific tool instructions
- `package_evaluator/agent.py` — Evaluation criteria and scoring guidelines

## Eval-Driven Development (Eval-DD) Workflow

### Before Making Changes
1. Run `/eval-baseline` to capture current scores
2. Document your hypothesis: "Changing X should improve Y because Z"

### Making Changes
1. Edit the relevant prompt file
2. Make ONE change at a time (isolate variables)
3. Keep changes small and focused

### After Making Changes
1. Run evals: `adk eval mortgage_concierge tests/eval/data/<evalset>.evalset.json --config_file_path=tests/eval/data/test_config.json --print_detailed_results`
2. Compare scores against baseline
3. If improved: accept, update baseline
4. If regressed: revert with `git checkout -- <file>`
5. Log results in `.workitems/<current>/prompt-tuning-log.md`

## Common Pitfalls

- **Tool call ordering**: The prompt must clearly specify when to use each tool. Ambiguous instructions lead to wrong tool selection.
- **Parameter formatting**: If the LLM passes wrong parameter types, add explicit format examples in the tool instructions.
- **Phase transitions**: Users may skip phases. The prompt should handle graceful degradation.
- **State assumptions**: Don't assume state keys exist. Tools should check for missing state gracefully.

## Adding a New Phase

1. Define the phase in `AGENT_INSTRUCTION` with clear boundaries
2. List the tools available in this phase
3. Define state prerequisites (what must exist before entering)
4. Define state outputs (what gets stored)
5. Add eval cases covering the new phase
6. Run `/eval-baseline` before and after to measure impact
