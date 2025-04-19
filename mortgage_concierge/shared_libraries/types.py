"""
Pydantic data models for the Mortgage Advisor.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field

class BorrowerProfile(BaseModel):
    """Information gathered about the borrower during profiling."""
    estimated_property_value: Optional[float] = Field(
        default=None, description="Estimated value of the property.")
    down_payment_amount: Optional[float] = Field(
        default=None, description="Amount the borrower plans to pay as down payment.")
    gross_annual_income: Optional[float] = Field(
        default=None, description="Borrower's gross annual income before taxes.")
    total_monthly_debt_payments: Optional[float] = Field(
        default=None, description="Borrower's existing monthly debt obligations.")
    credit_score_range: Optional[Literal[
        "poor", "fair", "good", "very_good", "excellent"
    ]] = Field(default=None, description="Borrower's credit score category.")
    risk_tolerance: Optional[Literal["low", "medium", "high"]] = Field(
        default="medium", description="Borrower's comfort level with interest rate fluctuations.")
    # Additional fields (e.g., desired_loan_amount) will be added in later phases.