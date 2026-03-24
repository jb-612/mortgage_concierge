---
name: state-architect
description: Audit session state keys, design new contracts, verify cross-agent compatibility
argument-hint: "[audit|design|verify]"
allowed-tools: Read, Glob, Grep, Bash
---

# State Architecture

Mode: $ARGUMENTS

## Mode: audit
1. Read `mortgage_concierge/shared_libraries/constants.py` for declared keys
2. Grep all `tool_context.state` and `session.state` access across codebase
3. Cross-reference: find keys used but not in constants, and keys declared but unused
4. Report state key inventory with read/write locations

Known undeclared keys (from exploration):
- `"package_evaluations"`, `"amortization_artifacts"`, `"save_artifacts"`
- `"package_id"`, `"mortgage_package"`, `"evaluation_criteria"`
- `"market_rate_benchmark"`, `"evaluation_id"`

## Mode: design
1. Propose new keys following naming conventions
2. Add to `constants.py`
3. Create helper functions in `state_helpers.py`

## Mode: verify
1. Trace state flow: root agent → LoanSimulationAgent → PackageEvaluatorAgent
2. Verify keys written by one agent are correctly read by another
3. Identify potential state conflicts or race conditions
