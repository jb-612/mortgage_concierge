"""
Tools for evaluating mortgage packages using the PackageEvaluatorAgent.
"""
import logging
from typing import Dict, Any, Optional, List, Union

from google.adk.tools import FunctionTool, ToolContext
from pydantic import BaseModel, Field

from mortgage_concierge.sub_agents.package_evaluator import PackageEvaluatorAgent
from mortgage_concierge.sub_agents.package_evaluator.models import EvaluationCriteria
from mortgage_concierge.sub_agents.loan_simulation.models import MortgagePackage
from mortgage_concierge.shared_libraries.state_helpers import (
    get_proposed_packages,
    ensure_session_state,
    get_package_evaluation_results
)

# Setup logging
logger = logging.getLogger(__name__)


async def evaluate_mortgage_package_tool(
    package_id: str,
    monthly_income: float,
    debt_to_income_ratio: Optional[float] = None,
    risk_tolerance: str = "moderate",
    desired_term: Optional[int] = None,
    preferred_track_types: Optional[List[str]] = None,
    max_monthly_payment: Optional[float] = None,
    market_rate_benchmark: Optional[float] = None,
    tool_context: ToolContext = None
) -> Dict[str, Any]:
    """
    Evaluate a mortgage package based on user-specific criteria.
    
    Args:
        package_id: ID of the package to evaluate (from package simulation results)
        monthly_income: User's monthly income for affordability calculation
        debt_to_income_ratio: Optional current debt-to-income ratio (0-1)
        risk_tolerance: User's risk tolerance level (low, moderate, high)
        desired_term: Optional preferred loan term in years
        preferred_track_types: Optional list of preferred interest track types
        max_monthly_payment: Optional maximum acceptable monthly payment
        market_rate_benchmark: Optional current market rate for comparison
        tool_context: Tool context for accessing session state
        
    Returns:
        Dictionary with evaluation results including risk, affordability, and cost analyses
    """
    try:
        # Validate inputs
        if not package_id:
            return {
                "status": "error",
                "error_message": "Package ID is required"
            }
            
        if monthly_income <= 0:
            return {
                "status": "error",
                "error_message": "Monthly income must be greater than zero"
            }
            
        if debt_to_income_ratio is not None and (debt_to_income_ratio < 0 or debt_to_income_ratio > 1):
            return {
                "status": "error",
                "error_message": "Debt-to-income ratio must be between 0 and 1"
            }
            
        if risk_tolerance not in ["low", "moderate", "high"]:
            return {
                "status": "error",
                "error_message": "Risk tolerance must be 'low', 'moderate', or 'high'"
            }
        
        # Get the mortgage package from session state using our helper function
        packages = get_proposed_packages(tool_context)
        if not packages:
            return {
                "status": "error",
                "error_message": "No mortgage packages found in session state"
            }
            
        package_data = packages.get(package_id)
        if not package_data:
            logger.warning(f"Package '{package_id}' not found in state. Available packages: {list(packages.keys())}")
            return {
                "status": "error",
                "error_message": f"Package with ID '{package_id}' not found in session state"
            }
            
        logger.info(f"Retrieved package '{package_id}' from session state for evaluation")
            
        # Convert to MortgagePackage object
        package = MortgagePackage.model_validate(package_data)
        
        # Create evaluation criteria
        criteria = EvaluationCriteria(
            monthly_income=monthly_income,
            debt_to_income_ratio=debt_to_income_ratio,
            risk_tolerance=risk_tolerance,
            desired_term=desired_term,
            preferred_track_types=preferred_track_types,
            max_monthly_payment=max_monthly_payment
        )
        
        # Create and run the evaluator agent
        evaluator = PackageEvaluatorAgent()
        evaluation_result = await evaluator.evaluate_package(
            mortgage_package=package,
            evaluation_criteria=criteria,
            tool_context=tool_context,
            market_rate_benchmark=market_rate_benchmark
        )
        
        # If successful, store the evaluation in session state
        if evaluation_result.get("status") == "ok" and "evaluation" in evaluation_result:
            evaluation_data = evaluation_result["evaluation"]
            evaluations = get_package_evaluation_results(tool_context)
            evaluations[f"eval_{package_id}"] = evaluation_data
            tool_context.state["package_evaluations"] = evaluations
            logger.info(f"Saved evaluation for package '{package_id}' to session state")
        
        # Return the evaluation results
        return evaluation_result
        
    except Exception as e:
        logger.exception("Error evaluating mortgage package")
        return {
            "status": "error",
            "error_message": f"Failed to evaluate mortgage package: {str(e)}"
        }

# Export the tool
evaluate_mortgage_package_tool.__name__ = "evaluate_mortgage_package"
evaluate_mortgage_package = FunctionTool(evaluate_mortgage_package_tool)