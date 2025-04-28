"""
Unit tests for the mortgage package evaluation tools.
"""
import pytest
import json
from datetime import datetime
from unittest.mock import MagicMock, patch

from mortgage_concierge.sub_agents.loan_simulation.models import (
    MortgagePackage,
    MortgageTrack
)
from mortgage_concierge.sub_agents.package_evaluator.models import (
    EvaluationCriteria, 
    PackageEvaluation,
    RiskAssessment,
    AffordabilityAssessment,
    CostEfficiencyAssessment
)
from mortgage_concierge.tools.evaluation_tools import evaluate_mortgage_package_tool


class MockToolContext:
    def __init__(self, state=None):
        self.state = state or {}
        self.session_id = "test-session-id"
        
    def save_artifact(self, name, content, mime_type):
        return f"artifact-{name}"


# Sample mortgage package for testing
@pytest.fixture
def sample_mortgage_package():
    return MortgagePackage(
        package_id="pkg_12345678",
        package_name="Test 60/40 Split Package",
        total_amount=500000.0,
        weighted_avg_rate=4.05,
        monthly_payment=2653.47,
        total_interest=295020.60,
        total_repayment=795020.60,
        tracks=[
            MortgageTrack(
                track_type="fixed",
                track_name="Fixed 4.25%",
                amount=300000.0,
                term_years=25,
                interest_rate=4.25,
                monthly_payment=1617.88,
                total_interest=185363.64,
                percentage_of_total=60.0,
                calculation_guid="calc_fixed_12345"
            ),
            MortgageTrack(
                track_type="variable",
                track_name="Variable 3.75%",
                amount=200000.0,
                term_years=25,
                interest_rate=3.75,
                monthly_payment=1035.59,
                total_interest=110676.96,
                percentage_of_total=40.0,
                calculation_guid="calc_variable_67890"
            )
        ],
        timestamp=datetime.now()
    )


# Test evaluation criteria for testing
@pytest.fixture
def evaluation_criteria():
    return EvaluationCriteria(
        monthly_income=8000.0,
        debt_to_income_ratio=0.2,
        risk_tolerance="moderate",
        desired_term=25,
        max_monthly_payment=3000.0
    )


# Mock evaluation result for testing
@pytest.fixture
def mock_evaluation_result():
    return PackageEvaluation(
        package_id="pkg_12345678",
        package_name="Test 60/40 Split Package",
        evaluation_timestamp=datetime.now(),
        risk_assessment=RiskAssessment(
            risk_score=45.0,
            interest_rate_risk=42.0,
            payment_shock_risk=50.0,
            term_risk=40.0,
            notes=["Moderate risk profile with balanced fixed/variable mix"]
        ),
        affordability_assessment=AffordabilityAssessment(
            affordability_score=75.0,
            payment_to_income_ratio=33.17,
            debt_service_ratio=53.17,
            buffer_percentage=66.83,
            notes=["Payment is within recommended guidelines"]
        ),
        cost_efficiency_assessment=CostEfficiencyAssessment(
            cost_efficiency_score=70.0,
            interest_to_principal_ratio=0.59,
            avg_rate_vs_market=0.2,
            early_repayment_potential=60.0,
            notes=["Good overall cost efficiency"]
        ),
        overall_score=72.5,
        strengths=[
            "Balanced mix of fixed (60.0%) and variable (40.0%) tracks",
            "Good protection against interest rate fluctuations", 
            "Monthly payment within recommended range"
        ],
        weaknesses=[
            "Total debt service ratio is high at 53.17%"
        ],
        recommendations=[
            "Consider increasing down payment to improve affordability",
            "Build an emergency fund to protect against payment increases",
            "Review mortgage terms annually to identify refinancing opportunities"
        ],
        suitable_for_profiles=[
            "Borrowers with moderate risk tolerance",
            "First-time homebuyers"
        ]
    )


@pytest.mark.asyncio
async def test_evaluate_mortgage_package_success(sample_mortgage_package, evaluation_criteria, mock_evaluation_result):
    """Test successful mortgage package evaluation."""
    # Set up mock context with sample package in state
    context = MockToolContext(state={
        "proposed_packages": {
            "pkg_12345678": sample_mortgage_package.model_dump()
        }
    })
    
    # Create an async mock that will be awaited
    async def mock_evaluate_package(*args, **kwargs):
        return {
            "status": "ok",
            "evaluation": mock_evaluation_result.model_dump()
        }
    
    # Mock the PackageEvaluatorAgent.evaluate_package method
    with patch("mortgage_concierge.tools.evaluation_tools.PackageEvaluatorAgent") as MockAgent:
        # Set up the mock
        mock_agent_instance = MagicMock()
        MockAgent.return_value = mock_agent_instance
        mock_agent_instance.evaluate_package = mock_evaluate_package
        
        # Call the tool
        result = await evaluate_mortgage_package_tool(
            package_id="pkg_12345678",
            monthly_income=8000.0,
            debt_to_income_ratio=0.2,
            risk_tolerance="moderate",
            desired_term=25,
            max_monthly_payment=3000.0,
            tool_context=context
        )
        
        # Verify the result
        assert result["status"] == "ok"
        assert result["evaluation"]["package_id"] == "pkg_12345678"
        assert result["evaluation"]["overall_score"] == 72.5
        assert len(result["evaluation"]["strengths"]) == 3
        assert len(result["evaluation"]["recommendations"]) == 3


@pytest.mark.asyncio
async def test_evaluate_mortgage_package_invalid_package_id():
    """Test evaluation with invalid package ID."""
    context = MockToolContext(state={"proposed_packages": {}})
    
    # We don't need to mock the agent for this test as it will fail before reaching that point
    result = await evaluate_mortgage_package_tool(
        package_id="non_existent_package",
        monthly_income=8000.0,
        risk_tolerance="moderate",
        tool_context=context
    )
    
    assert result["status"] == "error"
    assert "not found" in result["error_message"]


@pytest.mark.asyncio
async def test_evaluate_mortgage_package_invalid_input():
    """Test evaluation with invalid input."""
    context = MockToolContext()
    
    # We don't need to mock the agent for this test as it will fail during input validation
    
    # Test with invalid monthly income
    result = await evaluate_mortgage_package_tool(
        package_id="pkg_12345678",
        monthly_income=-1000.0,  # Invalid negative income
        risk_tolerance="moderate",
        tool_context=context
    )
    
    assert result["status"] == "error"
    assert "income" in result["error_message"]
    
    # Test with invalid risk tolerance
    result = await evaluate_mortgage_package_tool(
        package_id="pkg_12345678",
        monthly_income=8000.0,
        risk_tolerance="invalid_value",  # Invalid risk tolerance
        tool_context=context
    )
    
    assert result["status"] == "error"
    assert "tolerance" in result["error_message"]