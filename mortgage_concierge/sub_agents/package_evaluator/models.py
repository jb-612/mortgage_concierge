"""
Pydantic models for mortgage package evaluation.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class EvaluationCriteria(BaseModel):
    """User-specific criteria for evaluating mortgage packages."""
    monthly_income: float = Field(..., description="User's monthly income")
    debt_to_income_ratio: Optional[float] = Field(None, description="Current debt-to-income ratio (0-1)")
    risk_tolerance: str = Field("moderate", description="User's risk tolerance (low, moderate, high)")
    desired_term: Optional[int] = Field(None, description="Preferred loan term in years")
    preferred_track_types: Optional[List[str]] = Field(None, description="Preferred interest track types")
    max_monthly_payment: Optional[float] = Field(None, description="Maximum acceptable monthly payment")


class RiskAssessment(BaseModel):
    """Risk assessment for a mortgage package."""
    risk_score: float = Field(..., description="Overall risk score (0-100, lower is better)")
    interest_rate_risk: float = Field(..., description="Risk score for interest rate volatility")
    payment_shock_risk: float = Field(..., description="Risk score for potential payment increases")
    term_risk: float = Field(..., description="Risk score related to loan term length")
    notes: List[str] = Field(..., description="Explanatory notes about risk factors")


class AffordabilityAssessment(BaseModel):
    """Affordability assessment for a mortgage package."""
    affordability_score: float = Field(..., description="Overall affordability score (0-100, higher is better)")
    payment_to_income_ratio: float = Field(..., description="Monthly payment as percentage of income")
    debt_service_ratio: Optional[float] = Field(None, description="Total debt service ratio including this mortgage")
    buffer_percentage: float = Field(..., description="Financial buffer as percentage of income")
    notes: List[str] = Field(..., description="Explanatory notes about affordability")


class CostEfficiencyAssessment(BaseModel):
    """Cost efficiency assessment for a mortgage package."""
    cost_efficiency_score: float = Field(..., description="Overall cost efficiency score (0-100, higher is better)")
    interest_to_principal_ratio: float = Field(..., description="Ratio of total interest to loan amount")
    avg_rate_vs_market: float = Field(..., description="How the rate compares to current market rates")
    early_repayment_potential: float = Field(..., description="Score for potential early repayment benefits")
    notes: List[str] = Field(..., description="Explanatory notes about cost efficiency")


class PackageEvaluation(BaseModel):
    """Complete evaluation results for a mortgage package."""
    package_id: str = Field(..., description="Reference to the evaluated package")
    package_name: str = Field(..., description="Name of the evaluated package")
    evaluation_timestamp: datetime = Field(default_factory=datetime.now, description="When evaluation was performed")
    
    # Scores
    risk_assessment: RiskAssessment = Field(..., description="Detailed risk assessment")
    affordability_assessment: AffordabilityAssessment = Field(..., description="Detailed affordability assessment")
    cost_efficiency_assessment: CostEfficiencyAssessment = Field(..., description="Detailed cost efficiency assessment")
    overall_score: float = Field(..., description="Overall package score (0-100, higher is better)")
    
    # Analysis
    strengths: List[str] = Field(..., description="Key strengths of this package")
    weaknesses: List[str] = Field(..., description="Potential weaknesses or risks")
    recommendations: List[str] = Field(..., description="Personalized recommendations")
    
    # Supporting data
    suitable_for_profiles: List[str] = Field(..., description="Types of borrowers this package suits")
    comparison_notes: Optional[str] = Field(None, description="Notes comparing to other packages")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional evaluation metadata")