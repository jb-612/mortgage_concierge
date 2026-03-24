# Mortgage Concierge Development Plan

## Phase 1 — Core Agent (Complete)
- [x] P01-F01-borrower-profiling — Borrower profile collection and state storage
- [x] P01-F02-loan-calculation — Initial loan calculation with OpenAPI tools
- [x] P01-F03-recalculation — Rate and term recalculation with GUID
- [x] P01-F04-loan-tracks — Loan track listing and selection
- [x] P01-F05-multi-track-simulation — Multi-track loan simulation sub-agent
- [x] P01-F06-package-evaluation — Package evaluation sub-agent

## Phase 2 — Quality & Coverage (In Progress)
- [ ] P02-F01-eval-coverage-phase3 — Add evalset coverage for simulate_loan_tracks
- [ ] P02-F02-eval-coverage-phase4 — Add evalset coverage for evaluate_mortgage_package
- [ ] P02-F03-state-key-cleanup — Declare all undeclared state keys in constants.py
- [ ] P02-F04-cc-refactoring — Refactor functions exceeding CC > 5 (simulate_loan_tracks, _create_package_evaluation)
- [ ] P02-F05-test-consolidation — Consolidate DummyToolContext into tests/conftest.py

## Phase 3 — Adversarial Hardening (Planned)
- [ ] P03-F01-prompt-injection-defense — Harden agent against prompt injection attacks
- [ ] P03-F02-edge-case-handling — Handle extreme borrower profiles gracefully
- [ ] P03-F03-hallucination-prevention — Prevent fabrication of non-existent products/rates

## Phase 4 — Future Features (Planned)
- [ ] P04-F01-refinancing-advisor — Refinancing recommendation engine
- [ ] P04-F02-comparison-tool — Side-by-side package comparison
