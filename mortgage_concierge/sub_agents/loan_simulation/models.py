"""
Pydantic models for loan simulation and mortgage packages.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class LoanTrackSpecification(BaseModel):
    """Specification for a loan track to be simulated."""
    amount: float = Field(..., description="The principal loan amount")
    term_years: int = Field(..., description="The term of the loan in years")
    track_type: str = Field(..., description="The type of interest track (e.g., 'prime', 'fixed')")
    custom_rate: Optional[float] = Field(None, description="Optional custom interest rate")
    loan_name: Optional[str] = Field(None, description="Optional friendly name for this loan")


class AmortizationPayment(BaseModel):
    """Single payment in an amortization schedule."""
    payment_number: int = Field(..., description="Payment sequence number")
    payment: float = Field(..., description="Total payment amount")
    principal: float = Field(..., description="Amount of principal paid")
    interest: float = Field(..., description="Amount of interest paid")
    remaining_balance: float = Field(..., description="Remaining loan balance after payment")


class LoanCalculationResult(BaseModel):
    """Results of a loan calculation, matches API response format."""
    guid: str = Field(..., description="Unique identifier for the calculation")
    loan_amount: float = Field(..., description="Original loan amount")
    loan_term_months: int = Field(..., description="Loan term in months")
    loan_term_years: float = Field(..., description="Loan term in years")
    interest_type: str = Field(..., description="Type of interest (fixed, variable)")
    interest_rate: float = Field(..., description="Interest rate in percentage")
    first_monthly_payment: float = Field(..., description="Amount of the first monthly payment")
    max_monthly_payment: float = Field(..., description="Maximum monthly payment amount")
    total_repayment: float = Field(..., description="Total amount to be repaid over the loan term")
    total_interest: float = Field(..., description="Total interest to be paid over the loan term")
    effective_interest_rate: float = Field(..., description="Effective annual interest rate as a percentage")
    amortization_schedule: List[AmortizationPayment] = Field(..., description="Payment schedule")
    timestamp: datetime = Field(..., description="Timestamp of calculation")
    track_type: Optional[str] = Field(None, description="The type of interest track used")
    track_name: Optional[str] = Field(None, description="Friendly name for this loan track")


class MortgageTrack(BaseModel):
    """A single mortgage track within a package."""
    track_type: str = Field(..., description="Type of track (e.g., 'prime', 'fixed')")
    track_name: str = Field(..., description="Friendly name for this track")
    amount: float = Field(..., description="Amount allocated to this track")
    term_years: float = Field(..., description="Term in years")
    interest_rate: float = Field(..., description="Current interest rate")
    monthly_payment: float = Field(..., description="Monthly payment for this track")
    total_interest: float = Field(..., description="Total interest over the term")
    percentage_of_total: float = Field(..., description="Percentage of total mortgage amount")
    calculation_guid: str = Field(..., description="Reference to full calculation details")


class MortgagePackage(BaseModel):
    """A complete mortgage package, potentially with multiple tracks."""
    package_id: str = Field(..., description="Unique identifier for this package")
    package_name: str = Field(..., description="User-friendly name for this package")
    total_amount: float = Field(..., description="Total mortgage amount")
    weighted_avg_rate: float = Field(..., description="Weighted average interest rate")
    monthly_payment: float = Field(..., description="Total monthly payment")
    total_interest: float = Field(..., description="Total interest over all tracks")
    total_repayment: float = Field(..., description="Total amount to be repaid")
    tracks: List[MortgageTrack] = Field(..., description="Individual mortgage tracks")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this package was created")
    artifact_ids: Optional[Dict[str, str]] = Field(default=None, description="IDs of related artifacts")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional package metadata")


class PackageEvaluation(BaseModel):
    """Evaluation results for a mortgage package."""
    package_id: str = Field(..., description="Reference to the evaluated package")
    risk_score: float = Field(..., description="Risk assessment score (0-100, lower is better)")
    affordability_score: float = Field(..., description="Affordability score (0-100, higher is better)")
    cost_efficiency_score: float = Field(..., description="Cost efficiency score (0-100, higher is better)")
    overall_score: float = Field(..., description="Overall package score (0-100, higher is better)")
    strengths: List[str] = Field(..., description="Key strengths of this package")
    weaknesses: List[str] = Field(..., description="Potential weaknesses or risks")
    recommendations: List[str] = Field(..., description="Personalized recommendations")