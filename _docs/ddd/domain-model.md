# Domain Model

## Model Hierarchy

```
BorrowerProfile (shared_libraries/types.py)
├── annual_income: float
├── credit_score: int
├── monthly_debts: float
├── down_payment: float
├── property_value: float
└── loan_amount: float

LoanTrackSpecification (loan_simulation/models.py)
├── track_name: str
├── interest_rate: float
├── term_months: int
├── allocation_percentage: float
└── track_type: str

MortgageTrack (loan_simulation/models.py)
├── track_specification: LoanTrackSpecification
├── monthly_payment: float
├── total_interest: float
├── total_cost: float
└── amortization_summary: dict

MortgagePackage (loan_simulation/models.py)
├── package_id: str
├── package_name: str
├── tracks: List[MortgageTrack]
├── combined_monthly_payment: float
├── combined_total_interest: float
├── combined_total_cost: float
└── weighted_average_rate: float

EvaluationCriteria (package_evaluator/models.py)
├── risk_tolerance: str
├── priority: str
└── market_rate_benchmark: float

PackageEvaluation (package_evaluator/models.py)
├── evaluation_id: str
├── package_id: str
├── risk_assessment: RiskAssessment
├── affordability_assessment: AffordabilityAssessment
├── cost_efficiency_assessment: CostEfficiencyAssessment
├── overall_score: float
├── recommendation: str
├── strengths: List[str]
└── weaknesses: List[str]
```

## State Flow Diagram

```
Phase 1              Phase 2                  Phase 3                    Phase 4
[BorrowerProfile] → [LoanCalculation] → [MortgagePackage] → [PackageEvaluation]
     ↓                    ↓                      ↓                       ↓
 user_profile     loan_calculation_guid    proposed_packages    package_evaluations
                  loan_initial_results     amortization_artifacts
```
