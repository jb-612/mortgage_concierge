# Mortgage Concierge — Capability Map

## Capability Matrix

| Capability | Tool/Agent | State Keys | Eval Coverage | Phase |
|-----------|-----------|------------|---------------|-------|
| Borrower profiling | store_state_tool | user_profile | loan_calculator.evalset | P1 |
| Bank policy search | search_bank_docs | — | loan_calculator.evalset | P1 |
| Loan track listing | list_loan_tracks | — | — (gap) | P2 |
| Initial calculation | calculateLoan (OpenAPI) | loan_calculation_guid, loan_initial_results | loan_calculator.evalset | P2 |
| Rate recalculation | recalculateWithNewRate (OpenAPI) | loan_custom_rate | loan_calculator.evalset | P2 |
| Term recalculation | recalculateWithNewTerm (OpenAPI) | loan_custom_term | loan_calculator.evalset | P2 |
| Multi-track simulation | simulate_loan_tracks → LoanSimulationAgent | proposed_packages, amortization_artifacts | — (gap) | P3 |
| Package evaluation | evaluate_mortgage_package → PackageEvaluatorAgent | package_evaluations | — (gap) | P4 |

## Coverage Gaps
- Phase 3 (Multi-track simulation) has no dedicated evalset
- Phase 4 (Package evaluation) has no dedicated evalset
- Adversarial testing not yet captured
- list_loan_tracks has no eval coverage

## Sub-Agent State Contracts

### LoanSimulationAgent
- **Reads**: track_specifications (input param)
- **Writes**: proposed_packages[<package_id>], amortization_artifacts[<guid>]

### PackageEvaluatorAgent
- **Reads**: proposed_packages[<package_id>], mortgage_package, evaluation_criteria
- **Writes**: package_evaluations[<eval_id>]
