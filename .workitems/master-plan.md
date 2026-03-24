# Mortgage Concierge Master Plan

ADK-based conversational mortgage advisor. Guides borrowers through profiling, loan calculation, multi-track simulation, and package evaluation.

## Phase Index

| Phase | Description | Features | Done | Gate |
|-------|-------------|----------|------|------|
| P01 | Core Agent — conversation phases 1-4 | 6 | 6/6 | PASSED |
| P02 | Quality & Coverage — evals, refactoring | 5 | 0/5 | — |
| P03 | Adversarial Hardening — safety & edge cases | 3 | 0/3 | — |
| P04 | New Features — refinancing, comparison | 2 | 0/2 | — |

## P01 — Core Agent (Complete)

- [x] P01/F01-borrower_profiling — Collect borrower profile via conversation
- [x] P01/F02-loan_calculation — Calculate loan with OpenAPI tools
- [x] P01/F03-recalculation — Recalculate with new rate or term
- [x] P01/F04-loan_tracks — List and explain available loan tracks
- [x] P01/F05-multi_track_simulation — Simulate multi-track mortgage packages
- [x] P01/F06-package_evaluation — Evaluate packages for risk/affordability/cost

## P02 — Quality & Coverage (In Progress)

- [ ] P02/F01-eval_coverage_phase3 — Evalset for simulate_loan_tracks
- [ ] P02/F02-eval_coverage_phase4 — Evalset for evaluate_mortgage_package
- [ ] P02/F03-state_key_cleanup — Declare undeclared state keys in constants.py
- [ ] P02/F04-cc_refactoring — Refactor functions with CC > 5
- [ ] P02/F05-test_consolidation — Consolidate DummyToolContext into conftest.py

## P03 — Adversarial Hardening (Planned)

- [ ] P03/F01-prompt_injection_defense — Harden against prompt injection
- [ ] P03/F02-edge_case_handling — Handle extreme borrower profiles
- [ ] P03/F03-hallucination_prevention — Prevent fabrication of products/rates

## P04 — New Features (Planned)

- [ ] P04/F01-refinancing_advisor — Refinancing recommendation engine
- [ ] P04/F02-package_comparison — Side-by-side package comparison tool
