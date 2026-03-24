# Bounded Contexts

## 1. Borrower Context
- **Entities**: BorrowerProfile
- **State**: user_profile
- **Owner**: store_state_tool, root agent Phase 1

## 2. Loan Calculation Context
- **Entities**: LoanCalculationResult, AmortizationPayment
- **State**: loan_calculation_guid, loan_initial_results, loan_selected_track, loan_custom_rate, loan_custom_term
- **Owner**: OpenAPI tools (calculateLoan, recalculateWithNewRate, recalculateWithNewTerm)

## 3. Simulation Context
- **Entities**: LoanTrackSpecification, MortgageTrack, MortgagePackage
- **State**: proposed_packages, amortization_artifacts
- **Owner**: LoanSimulationAgent, simulate_loan_tracks wrapper tool

## 4. Evaluation Context
- **Entities**: EvaluationCriteria, RiskAssessment, AffordabilityAssessment, CostEfficiencyAssessment, PackageEvaluation
- **State**: package_evaluations
- **Owner**: PackageEvaluatorAgent, evaluate_mortgage_package wrapper tool

## 5. Knowledge Context
- **Entities**: BankDocument, MemoryResult
- **State**: Managed by InMemoryMemoryService (not session state)
- **Owner**: bootstrap.py, memory_ingestion.py, search_bank_docs tool
