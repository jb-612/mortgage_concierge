"""
PackageEvaluatorAgent - Specialized agent for evaluating mortgage packages based on
risk, affordability, and overall cost efficiency.
"""
import os
import logging
import uuid
from typing import List, Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.tools import FunctionTool, ToolContext

from mortgage_concierge.sub_agents.loan_simulation.models import MortgagePackage
from mortgage_concierge.sub_agents.package_evaluator.models import (
    EvaluationCriteria,
    RiskAssessment,
    AffordabilityAssessment,
    CostEfficiencyAssessment,
    PackageEvaluation
)
from mortgage_concierge.shared_libraries.constants import DEFAULT_MODEL_ID

# Setup logging
logger = logging.getLogger(__name__)

class PackageEvaluatorAgent(Agent):
    """
    Specialized agent for evaluating mortgage packages based on risk, affordability,
    and overall cost efficiency.
    
    This agent is designed to:
    1. Analyze a mortgage package
    2. Assess risk factors based on interest types and rates
    3. Evaluate affordability based on user financial profile
    4. Measure cost efficiency over the loan term
    5. Generate personalized recommendations
    """
    
    def __init__(self, model_id: Optional[str] = None):
        """
        Initialize the package evaluator agent.
        
        Args:
            model_id: Optional model identifier to use for this agent
        """
        # Create custom internal tools for evaluation steps
        internal_tools = [
            FunctionTool(self._evaluate_risk),
            FunctionTool(self._evaluate_affordability),
            FunctionTool(self._evaluate_cost_efficiency),
            FunctionTool(self._create_package_evaluation)
        ]
        
        # Initialize the agent with specialized instructions and required tools
        super().__init__(
            name="package_evaluator_agent",
            model=model_id or os.getenv("MORTGAGE_MODEL", DEFAULT_MODEL_ID),
            description="Specialized agent for evaluating mortgage packages",
            instruction="""
            You are a specialized Package Evaluator Agent. Your purpose is to:
            
            1. Analyze mortgage packages that contain one or more loan tracks
            2. Evaluate risk factors based on interest rate types, volatility, and term length
            3. Assess affordability based on the user's financial profile
            4. Measure cost efficiency over the loan term
            5. Generate an overall score and personalized recommendations
            
            IMPORTANT GUIDELINES:
            
            - Carefully analyze each track within the mortgage package
            - For variable/adjustable rate tracks, assign higher risk scores
            - Consider the user's risk tolerance when making recommendations
            - Analyze payment-to-income ratios to assess affordability
            - Identify key strengths and weaknesses of each package
            - Provide actionable recommendations specific to the user's situation
            - When comparing multiple packages, highlight tradeoffs between them
            
            TOOL INSTRUCTIONS:
            
            - _evaluate_risk: Analyze risk factors of the package
            - _evaluate_affordability: Assess if the package is affordable for the user
            - _evaluate_cost_efficiency: Measure overall cost efficiency
            - _create_package_evaluation: Create the final evaluation with scores and recommendations
            
            YOUR OUTPUT FORMAT:
            
            Return a dictionary with:
            - status: "ok" or "error"
            - evaluation: The complete PackageEvaluation if successful
            - error_message: Detailed error message if status is "error"
            """,
            tools=internal_tools,
        )
    
    async def evaluate_package(
        self,
        mortgage_package: MortgagePackage,
        evaluation_criteria: EvaluationCriteria,
        tool_context: ToolContext,
        market_rate_benchmark: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a mortgage package based on risk, affordability, and cost efficiency.
        
        Args:
            mortgage_package: The complete mortgage package to evaluate
            evaluation_criteria: User-specific criteria for evaluation
            tool_context: The ADK tool context from the parent agent
            market_rate_benchmark: Optional current market average rate for comparison
            
        Returns:
            Dictionary with status and either the evaluation or error message
        """
        try:
            # Create a new session for this evaluation
            session = await self.create_session()
            
            # Set initial session state with package and criteria
            session.state["mortgage_package"] = mortgage_package.model_dump()
            session.state["evaluation_criteria"] = evaluation_criteria.model_dump()
            session.state["parent_session_id"] = tool_context.session_id
            session.state["market_rate_benchmark"] = market_rate_benchmark
            
            # Generate an evaluation ID
            evaluation_id = f"eval_{uuid.uuid4().hex[:8]}"
            session.state["evaluation_id"] = evaluation_id
            
            # Run the agent to evaluate the package
            response = await session.send_message(
                "Evaluate this mortgage package based on risk, affordability, and cost efficiency."
            )
            
            # Extract the agent's response
            agent_response = response.message.content
            
            # Check if the evaluation was successful
            if "evaluation" in agent_response:
                evaluation = PackageEvaluation.model_validate(agent_response["evaluation"])
                
                # Store the evaluation in the parent session state
                if "package_evaluations" not in tool_context.state:
                    tool_context.state["package_evaluations"] = {}
                
                tool_context.state["package_evaluations"][evaluation_id] = evaluation.model_dump()
                
                return {
                    "status": "ok",
                    "evaluation": evaluation.model_dump()
                }
            else:
                return {
                    "status": "error",
                    "error_message": agent_response.get("error_message", "Unknown error in package evaluation")
                }
        
        except Exception as e:
            logger.exception("Error in package evaluation")
            return {
                "status": "error",
                "error_message": f"Failed to evaluate mortgage package: {str(e)}"
            }
    
    def _evaluate_risk(
        self,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """
        Evaluate the risk factors of a mortgage package.
        
        Args:
            tool_context: The ADK tool context
            
        Returns:
            Dict containing RiskAssessment details
        """
        try:
            # Get package and criteria from session state
            package_data = tool_context.state.get("mortgage_package", {})
            criteria_data = tool_context.state.get("evaluation_criteria", {})
            
            # Convert to objects
            package = MortgagePackage.model_validate(package_data)
            criteria = EvaluationCriteria.model_validate(criteria_data)
            
            # Initialize risk scores
            interest_rate_risk = 0.0
            payment_shock_risk = 0.0
            term_risk = 0.0
            notes = []
            
            # Risk weighting based on user risk tolerance
            risk_weights = {
                "low": {"variable": 80, "fixed": 20, "long_term": 30, "short_term": 60},
                "moderate": {"variable": 50, "fixed": 30, "long_term": 40, "short_term": 40},
                "high": {"variable": 30, "fixed": 40, "long_term": 50, "short_term": 30}
            }
            
            # Get appropriate risk weights
            weights = risk_weights.get(criteria.risk_tolerance.lower(), risk_weights["moderate"])
            
            # Calculate weighted term risk
            avg_term = sum(track.term_years * track.percentage_of_total / 100 for track in package.tracks)
            if avg_term > 20:
                term_risk = weights["long_term"]
                notes.append(f"Longer term of {avg_term:.1f} years increases sensitivity to rate changes over time")
            else:
                term_risk = weights["short_term"]
                notes.append(f"Moderate term of {avg_term:.1f} years balances flexibility with stability")
                
            # Analyze each track for interest rate risk
            variable_percentage = sum(
                track.percentage_of_total for track in package.tracks 
                if track.track_type.lower() in ["variable", "adjustable", "prime", "libor", "euribor"]
            )
            
            fixed_percentage = 100 - variable_percentage
            
            # Calculate interest rate risk
            interest_rate_risk = (variable_percentage / 100 * weights["variable"] + 
                                 fixed_percentage / 100 * weights["fixed"])
            
            if variable_percentage > 70:
                notes.append(f"High proportion of variable rate tracks ({variable_percentage:.1f}%) increases interest rate risk")
                payment_shock_risk = 70 + (variable_percentage - 70) * 0.5
            elif variable_percentage > 30:
                notes.append(f"Moderate proportion of variable rate tracks ({variable_percentage:.1f}%) presents balanced risk")
                payment_shock_risk = 30 + (variable_percentage - 30)
            else:
                notes.append(f"Low proportion of variable rate tracks ({variable_percentage:.1f}%) minimizes interest rate risk")
                payment_shock_risk = variable_percentage
            
            # Adjust payment shock risk based on buffer
            monthly_income = criteria.monthly_income
            monthly_payment = package.monthly_payment
            payment_ratio = monthly_payment / monthly_income * 100 if monthly_income > 0 else 0
            
            if payment_ratio > 40:
                payment_shock_risk += 20
                notes.append(f"High payment-to-income ratio ({payment_ratio:.1f}%) increases vulnerability to payment shocks")
            elif payment_ratio > 30:
                payment_shock_risk += 10
                notes.append(f"Moderate payment-to-income ratio ({payment_ratio:.1f}%) presents some vulnerability")
            else:
                notes.append(f"Low payment-to-income ratio ({payment_ratio:.1f}%) provides good buffer against payment shocks")
            
            # Calculate overall risk score (lower is better)
            risk_score = (interest_rate_risk * 0.4 + payment_shock_risk * 0.4 + term_risk * 0.2)
            
            # Create the risk assessment
            risk_assessment = RiskAssessment(
                risk_score=risk_score,
                interest_rate_risk=interest_rate_risk,
                payment_shock_risk=payment_shock_risk,
                term_risk=term_risk,
                notes=notes
            )
            
            return {
                "status": "ok",
                "risk_assessment": risk_assessment.model_dump()
            }
            
        except Exception as e:
            logger.exception("Failed to evaluate risk")
            return {
                "status": "error",
                "error_message": f"Failed to evaluate risk: {str(e)}"
            }
    
    def _evaluate_affordability(
        self,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """
        Evaluate the affordability of a mortgage package.
        
        Args:
            tool_context: The ADK tool context
            
        Returns:
            Dict containing AffordabilityAssessment details
        """
        try:
            # Get package and criteria from session state
            package_data = tool_context.state.get("mortgage_package", {})
            criteria_data = tool_context.state.get("evaluation_criteria", {})
            
            # Convert to objects
            package = MortgagePackage.model_validate(package_data)
            criteria = EvaluationCriteria.model_validate(criteria_data)
            
            # Calculate affordability metrics
            monthly_income = criteria.monthly_income
            monthly_payment = package.monthly_payment
            
            # Calculate payment to income ratio
            payment_to_income_ratio = monthly_payment / monthly_income if monthly_income > 0 else 1
            
            # Calculate buffer percentage (percentage of income not used for mortgage)
            buffer_percentage = (1 - payment_to_income_ratio) * 100
            
            # Calculate debt service ratio if debt_to_income_ratio is provided
            debt_service_ratio = None
            if criteria.debt_to_income_ratio is not None:
                debt_service_ratio = criteria.debt_to_income_ratio + payment_to_income_ratio
            
            # Generate notes
            notes = []
            
            # Analyze payment to income ratio
            if payment_to_income_ratio > 0.45:
                notes.append(f"Monthly payment is {payment_to_income_ratio*100:.1f}% of income, which exceeds recommended maximum (45%)")
                affordability_score = 30
            elif payment_to_income_ratio > 0.35:
                notes.append(f"Monthly payment is {payment_to_income_ratio*100:.1f}% of income, which is high but potentially manageable")
                affordability_score = 50
            elif payment_to_income_ratio > 0.25:
                notes.append(f"Monthly payment is {payment_to_income_ratio*100:.1f}% of income, which is within recommended range")
                affordability_score = 75
            else:
                notes.append(f"Monthly payment is {payment_to_income_ratio*100:.1f}% of income, which is comfortably affordable")
                affordability_score = 90
            
            # Analyze debt service ratio if available
            if debt_service_ratio is not None:
                if debt_service_ratio > 0.55:
                    notes.append(f"Total debt service ratio of {debt_service_ratio*100:.1f}% exceeds recommended maximum (55%)")
                    affordability_score -= 20
                elif debt_service_ratio > 0.45:
                    notes.append(f"Total debt service ratio of {debt_service_ratio*100:.1f}% is high")
                    affordability_score -= 10
                else:
                    notes.append(f"Total debt service ratio of {debt_service_ratio*100:.1f}% is within healthy limits")
            
            # Analyze buffer
            if buffer_percentage < 30:
                notes.append(f"Limited financial buffer ({buffer_percentage:.1f}% of income) leaves little room for unexpected expenses")
            else:
                notes.append(f"Good financial buffer ({buffer_percentage:.1f}% of income) provides flexibility for unexpected expenses")
            
            # Check max monthly payment if specified
            if criteria.max_monthly_payment is not None:
                if monthly_payment > criteria.max_monthly_payment:
                    notes.append(f"Monthly payment (${monthly_payment:.2f}) exceeds specified maximum (${criteria.max_monthly_payment:.2f})")
                    affordability_score -= 15
                else:
                    notes.append(f"Monthly payment (${monthly_payment:.2f}) is within specified maximum (${criteria.max_monthly_payment:.2f})")
            
            # Ensure score is within range
            affordability_score = max(0, min(100, affordability_score))
            
            # Create affordability assessment
            affordability_assessment = AffordabilityAssessment(
                affordability_score=affordability_score,
                payment_to_income_ratio=payment_to_income_ratio * 100,  # Convert to percentage
                debt_service_ratio=debt_service_ratio * 100 if debt_service_ratio is not None else None,  # Convert to percentage
                buffer_percentage=buffer_percentage,
                notes=notes
            )
            
            return {
                "status": "ok",
                "affordability_assessment": affordability_assessment.model_dump()
            }
            
        except Exception as e:
            logger.exception("Failed to evaluate affordability")
            return {
                "status": "error",
                "error_message": f"Failed to evaluate affordability: {str(e)}"
            }
    
    def _evaluate_cost_efficiency(
        self,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """
        Evaluate the cost efficiency of a mortgage package.
        
        Args:
            tool_context: The ADK tool context
            
        Returns:
            Dict containing CostEfficiencyAssessment details
        """
        try:
            # Get package, criteria, and market rates from session state
            package_data = tool_context.state.get("mortgage_package", {})
            criteria_data = tool_context.state.get("evaluation_criteria", {})
            market_rate_benchmark = tool_context.state.get("market_rate_benchmark")
            
            # Convert to objects
            package = MortgagePackage.model_validate(package_data)
            criteria = EvaluationCriteria.model_validate(criteria_data)
            
            # Calculate cost efficiency metrics
            total_interest = package.total_interest
            total_amount = package.total_amount
            
            # Calculate interest to principal ratio
            interest_to_principal_ratio = total_interest / total_amount if total_amount > 0 else 0
            
            # Generate notes
            notes = []
            
            # Analyze interest to principal ratio
            if interest_to_principal_ratio > 0.7:
                notes.append(f"High interest-to-principal ratio ({interest_to_principal_ratio:.2f}) means paying substantially more in interest")
                efficiency_score = 40
            elif interest_to_principal_ratio > 0.5:
                notes.append(f"Moderate interest-to-principal ratio ({interest_to_principal_ratio:.2f})")
                efficiency_score = 60
            else:
                notes.append(f"Low interest-to-principal ratio ({interest_to_principal_ratio:.2f}) indicates good cost efficiency")
                efficiency_score = 80
            
            # Compare weighted average rate to market benchmark
            avg_rate_vs_market = 0
            if market_rate_benchmark is not None:
                rate_difference = market_rate_benchmark - package.weighted_avg_rate
                avg_rate_vs_market = rate_difference
                
                if rate_difference > 0.5:
                    notes.append(f"Rate is {abs(rate_difference):.2f}% below market average, which is excellent")
                    efficiency_score += 15
                elif rate_difference > 0:
                    notes.append(f"Rate is {abs(rate_difference):.2f}% below market average, which is good")
                    efficiency_score += 10
                elif rate_difference > -0.5:
                    notes.append(f"Rate is {abs(rate_difference):.2f}% above market average, which is acceptable")
                    efficiency_score -= 5
                else:
                    notes.append(f"Rate is {abs(rate_difference):.2f}% above market average, which is poor")
                    efficiency_score -= 15
            else:
                # If no market benchmark, use weighted average rate directly
                if package.weighted_avg_rate < 4.0:
                    notes.append(f"Weighted average rate of {package.weighted_avg_rate:.2f}% is very competitive")
                    efficiency_score += 10
                elif package.weighted_avg_rate < 5.0:
                    notes.append(f"Weighted average rate of {package.weighted_avg_rate:.2f}% is reasonable")
                elif package.weighted_avg_rate < 6.0:
                    notes.append(f"Weighted average rate of {package.weighted_avg_rate:.2f}% is moderately high")
                    efficiency_score -= 5
                else:
                    notes.append(f"Weighted average rate of {package.weighted_avg_rate:.2f}% is high")
                    efficiency_score -= 10
            
            # Evaluate early repayment potential based on track types
            fixed_percentage = sum(
                track.percentage_of_total for track in package.tracks 
                if track.track_type.lower() in ["fixed"]
            )
            
            # Fixed rate tracks typically have prepayment penalties
            if fixed_percentage > 70:
                early_repayment_potential = 40
                notes.append(f"High proportion of fixed rate tracks ({fixed_percentage:.1f}%) may limit early repayment flexibility")
            elif fixed_percentage > 30:
                early_repayment_potential = 60
                notes.append(f"Balanced mix of fixed and variable tracks provides moderate early repayment flexibility")
            else:
                early_repayment_potential = 80
                notes.append(f"Low proportion of fixed rate tracks provides good early repayment flexibility")
            
            # Term alignment with user preference
            if criteria.desired_term is not None:
                avg_term = sum(track.term_years * track.percentage_of_total / 100 for track in package.tracks)
                term_difference = abs(avg_term - criteria.desired_term)
                
                if term_difference <= 2:
                    notes.append(f"Term length ({avg_term:.1f} years) aligns well with desired term ({criteria.desired_term} years)")
                    efficiency_score += 5
                elif term_difference <= 5:
                    notes.append(f"Term length ({avg_term:.1f} years) is reasonably close to desired term ({criteria.desired_term} years)")
                else:
                    notes.append(f"Term length ({avg_term:.1f} years) differs significantly from desired term ({criteria.desired_term} years)")
                    efficiency_score -= 5
            
            # Ensure score is within range
            efficiency_score = max(0, min(100, efficiency_score))
            
            # Create cost efficiency assessment
            cost_efficiency_assessment = CostEfficiencyAssessment(
                cost_efficiency_score=efficiency_score,
                interest_to_principal_ratio=interest_to_principal_ratio,
                avg_rate_vs_market=avg_rate_vs_market,
                early_repayment_potential=early_repayment_potential,
                notes=notes
            )
            
            return {
                "status": "ok",
                "cost_efficiency_assessment": cost_efficiency_assessment.model_dump()
            }
            
        except Exception as e:
            logger.exception("Failed to evaluate cost efficiency")
            return {
                "status": "error",
                "error_message": f"Failed to evaluate cost efficiency: {str(e)}"
            }
    
    def _create_package_evaluation(
        self,
        risk_assessment: Dict[str, Any],
        affordability_assessment: Dict[str, Any],
        cost_efficiency_assessment: Dict[str, Any],
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """
        Create the final package evaluation with overall score and recommendations.
        
        Args:
            risk_assessment: Risk assessment details
            affordability_assessment: Affordability assessment details
            cost_efficiency_assessment: Cost efficiency assessment details
            tool_context: The ADK tool context
            
        Returns:
            Dict containing the final PackageEvaluation
        """
        try:
            # Get package and criteria from session state
            package_data = tool_context.state.get("mortgage_package", {})
            criteria_data = tool_context.state.get("evaluation_criteria", {})
            
            # Convert to objects
            package = MortgagePackage.model_validate(package_data)
            criteria = EvaluationCriteria.model_validate(criteria_data)
            
            # Convert assessments to objects
            risk = RiskAssessment.model_validate(risk_assessment)
            affordability = AffordabilityAssessment.model_validate(affordability_assessment)
            cost_efficiency = CostEfficiencyAssessment.model_validate(cost_efficiency_assessment)
            
            # Calculate overall score (weighted average based on user risk tolerance)
            risk_weight = {
                "low": 0.4,
                "moderate": 0.3,
                "high": 0.2
            }.get(criteria.risk_tolerance.lower(), 0.3)
            
            affordability_weight = 0.4
            cost_efficiency_weight = 1 - risk_weight - affordability_weight
            
            # For risk, lower is better, so invert the score (100 - score)
            risk_component = (100 - risk.risk_score) * risk_weight
            affordability_component = affordability.affordability_score * affordability_weight
            cost_efficiency_component = cost_efficiency.cost_efficiency_score * cost_efficiency_weight
            
            overall_score = risk_component + affordability_component + cost_efficiency_component
            
            # Identify strengths (high scores in specific areas)
            strengths = []
            weaknesses = []
            
            # Risk strengths/weaknesses
            if risk.risk_score < 40:
                strengths.append("Low overall risk profile suitable for risk-averse borrowers")
            elif risk.risk_score > 70:
                weaknesses.append("High risk profile due to variable rate exposure and potential payment shocks")
            
            if risk.interest_rate_risk < 40:
                strengths.append("Good protection against interest rate fluctuations")
            elif risk.interest_rate_risk > 70:
                weaknesses.append("High exposure to interest rate fluctuations")
            
            # Affordability strengths/weaknesses
            if affordability.affordability_score > 70:
                strengths.append("Comfortably affordable for your income level")
            elif affordability.affordability_score < 40:
                weaknesses.append("Stretches your budget and leaves limited financial buffer")
            
            if affordability.payment_to_income_ratio < 30:
                strengths.append(f"Low payment-to-income ratio ({affordability.payment_to_income_ratio:.1f}%) provides financial flexibility")
            elif affordability.payment_to_income_ratio > 45:
                weaknesses.append(f"High payment-to-income ratio ({affordability.payment_to_income_ratio:.1f}%) exceeds recommended guidelines")
            
            # Cost efficiency strengths/weaknesses
            if cost_efficiency.cost_efficiency_score > 70:
                strengths.append("Excellent cost efficiency with favorable rates and terms")
            elif cost_efficiency.cost_efficiency_score < 40:
                weaknesses.append("Below average cost efficiency with higher relative interest costs")
            
            if cost_efficiency.interest_to_principal_ratio < 0.5:
                strengths.append(f"Relatively low interest-to-principal ratio ({cost_efficiency.interest_to_principal_ratio:.2f})")
            elif cost_efficiency.interest_to_principal_ratio > 0.7:
                weaknesses.append(f"High interest-to-principal ratio ({cost_efficiency.interest_to_principal_ratio:.2f})")
            
            # Track mix strengths/weaknesses
            fixed_percentage = sum(
                track.percentage_of_total for track in package.tracks 
                if track.track_type.lower() in ["fixed"]
            )
            
            variable_percentage = 100 - fixed_percentage
            
            if fixed_percentage > 0 and variable_percentage > 0:
                strengths.append(f"Balanced mix of fixed ({fixed_percentage:.1f}%) and variable ({variable_percentage:.1f}%) tracks")
            elif fixed_percentage > 80:
                strengths.append(f"High proportion of fixed rate tracks ({fixed_percentage:.1f}%) provides stability")
                if criteria.risk_tolerance.lower() == "high":
                    weaknesses.append("Limited variable rate exposure may miss opportunities for lower rates")
            elif variable_percentage > 80:
                if criteria.risk_tolerance.lower() != "high":
                    weaknesses.append(f"High proportion of variable rate tracks ({variable_percentage:.1f}%) increases risk")
                else:
                    strengths.append(f"High proportion of variable rate tracks ({variable_percentage:.1f}%) maximizes rate flexibility")
            
            # Generate suitable profiles
            suitable_for_profiles = []
            
            if risk.risk_score < 50:
                suitable_for_profiles.append("Risk-averse borrowers")
            if risk.risk_score > 60:
                suitable_for_profiles.append("Risk-tolerant borrowers")
            if affordability.affordability_score > 70:
                suitable_for_profiles.append("Borrowers prioritizing budget comfort")
            if cost_efficiency.cost_efficiency_score > 70:
                suitable_for_profiles.append("Cost-conscious borrowers")
            if fixed_percentage > 70:
                suitable_for_profiles.append("Borrowers seeking payment stability")
            if variable_percentage > 70:
                suitable_for_profiles.append("Borrowers seeking lowest possible rates")
            if package.total_amount < 500000:
                suitable_for_profiles.append("First-time homebuyers")
            
            # Generate personalized recommendations
            recommendations = []
            
            # Risk recommendations
            if risk.risk_score > 60 and criteria.risk_tolerance.lower() != "high":
                recommendations.append("Consider increasing the fixed-rate portion to reduce interest rate risk")
            
            if risk.payment_shock_risk > 60:
                recommendations.append("Build a larger emergency fund to protect against potential payment increases")
            
            # Affordability recommendations
            if affordability.affordability_score < 50:
                if package.total_amount > 300000:
                    recommendations.append("Consider reducing loan amount to improve affordability")
                recommendations.append("Explore options to increase down payment to reduce monthly payments")
            
            # Cost efficiency recommendations
            if cost_efficiency.cost_efficiency_score < 60:
                recommendations.append("Shop around for better interest rates on the variable portion")
                if package.weighted_avg_rate > 5.0:
                    recommendations.append("Consider refinancing if rates drop by 0.5% or more")
            
            # Term recommendations
            avg_term = sum(track.term_years * track.percentage_of_total / 100 for track in package.tracks)
            if criteria.desired_term is not None and abs(avg_term - criteria.desired_term) > 5:
                if avg_term > criteria.desired_term:
                    recommendations.append(f"Consider shorter term options closer to your preferred {criteria.desired_term} years")
                else:
                    recommendations.append(f"Consider slightly longer term options closer to your preferred {criteria.desired_term} years")
            
            # Ensure we have at least 3 recommendations
            if len(recommendations) < 3:
                if "Consider making extra payments when possible to reduce total interest" not in recommendations:
                    recommendations.append("Consider making extra payments when possible to reduce total interest")
                if "Review your mortgage terms annually to identify refinancing opportunities" not in recommendations:
                    recommendations.append("Review your mortgage terms annually to identify refinancing opportunities")
                if "Consider mortgage insurance to protect against payment difficulties" not in recommendations and affordability.affordability_score < 70:
                    recommendations.append("Consider mortgage insurance to protect against payment difficulties")
            
            # Create the package evaluation
            package_evaluation = PackageEvaluation(
                package_id=package.package_id,
                package_name=package.package_name,
                risk_assessment=risk,
                affordability_assessment=affordability,
                cost_efficiency_assessment=cost_efficiency,
                overall_score=overall_score,
                strengths=strengths,
                weaknesses=weaknesses,
                recommendations=recommendations,
                suitable_for_profiles=suitable_for_profiles
            )
            
            return {
                "status": "ok",
                "evaluation": package_evaluation.model_dump()
            }
            
        except Exception as e:
            logger.exception("Failed to create package evaluation")
            return {
                "status": "error",
                "error_message": f"Failed to create package evaluation: {str(e)}"
            }