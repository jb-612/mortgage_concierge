---
name: conversation-designer
description: Design conversation flows and state transitions for the mortgage concierge phases
argument-hint: "[phase-name | 'full']"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Conversation Flow Designer

Design flows for: $ARGUMENTS

## Process

1. Read `mortgage_concierge/prompt.py` to understand current 4-phase flow:
   - Phase 1: Borrower Profiling → store_state_tool
   - Phase 2: Loan Calculation → calculateLoan → recalculate*
   - Phase 3: Multi-Track Simulation → list_loan_tracks → simulate_loan_tracks
   - Phase 4: Package Evaluation → evaluate_mortgage_package_tool

2. Map state transitions per phase:
   - Which state keys are SET at each phase
   - Which state keys are READ at each phase
   - Prerequisites: which keys must exist before entering a phase

3. Design conversation paths:
   - **Happy path**: User provides info in order
   - **Correction path**: User changes earlier info mid-flow
   - **Skip-ahead path**: User jumps phases
   - **Error recovery path**: Tool failures, missing data

4. Create evalset entries testing each path type in `tests/eval/data/`

5. Validate prompt supports all designed paths
