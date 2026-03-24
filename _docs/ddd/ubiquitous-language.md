# Ubiquitous Language — Mortgage Concierge

## Core Terms

| Term | Definition | Code Reference |
|------|-----------|----------------|
| **Borrower Profile** | Collected financial information about the user (income, credit score, DTI, etc.) | `BorrowerProfile` in `shared_libraries/types.py` |
| **Track** | A specific loan product type (e.g., fixed 30yr, ARM 5/1) with associated interest rate | `LoanTrackSpecification` in `loan_simulation/models.py` |
| **Package** | A combination of one or more loan tracks simulated together (e.g., 60/40 split) | `MortgagePackage` in `loan_simulation/models.py` |
| **Simulation** | The process of calculating combined metrics for a multi-track mortgage package | `LoanSimulationAgent.simulate_loan_tracks()` |
| **Evaluation** | Analysis of a package for risk, affordability, and cost efficiency | `PackageEvaluatorAgent._create_package_evaluation()` |
| **GUID** | Calculator-assigned identifier for a loan calculation, required for recalculations | `loan_calculation_guid` state key |
| **Amortization Schedule** | Month-by-month breakdown of principal and interest payments | Returned by calculator API, stored as artifact |
| **Recalculation** | Re-running a calculation with modified rate or term, using existing GUID | `recalculateWithNewRate`, `recalculateWithNewTerm` tools |
| **Bootstrap** | One-time initialization that ingests bank docs into memory service | `bootstrap.init()` with `@lru_cache` |
| **Knowledge Base** | Bank policy documents and loan track definitions in `_knowledge_base/` | Ingested via `memory_ingestion.py` |

## Phase Names

| Phase | Name | Description |
|-------|------|-------------|
| P1 | Borrower Profiling | Collect financial information, store in session state |
| P2 | Loan Calculation | Initial calculation, track selection, recalculation |
| P3 | Multi-Track Simulation | Create complex multi-track mortgage packages |
| P4 | Package Evaluation | Analyze packages for risk, affordability, cost |
