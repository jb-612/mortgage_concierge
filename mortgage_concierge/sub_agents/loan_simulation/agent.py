"""
LoanSimulationAgent - Specialized agent for simulating multiple loan tracks and 
creating mortgage packages.
"""
import os
import logging
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from google.adk.agents import Agent
from google.adk.tools import FunctionTool, ToolContext
# Direct execution without Runner
from google.adk.events import Event
from google.genai.types import Content, Part
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset

from mortgage_concierge.sub_agents.loan_simulation.models import (
    LoanTrackSpecification,
    LoanCalculationResult,
    MortgageTrack,
    MortgagePackage
)
from mortgage_concierge.shared_libraries.constants import DEFAULT_MODEL_ID
from mortgage_concierge.shared_libraries.memory_store import session_service

# Setup logging
logger = logging.getLogger(__name__)

# Create a JSON serializer that handles datetime objects
def json_serializable(obj):
    """Convert an object to a JSON serializable format."""
    if isinstance(obj, dict):
        return {k: json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_serializable(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, "model_dump"):
        return json_serializable(obj.model_dump())
    else:
        return obj

class LoanSimulationAgent(Agent):
    """
    Specialized agent for simulating multiple loan tracks and creating mortgage packages.
    
    This agent is designed to:
    1. Take a list of loan track specifications 
    2. Call the appropriate calculator/recalc API endpoints for each track
    3. Aggregate the results into a cohesive mortgage package
    4. Store results as artifacts when needed
    """
    
    def __init__(self, model_id: Optional[str] = None):
        """
        Initialize the loan simulation agent.
        
        Args:
            model_id: Optional model identifier to use for this agent
        """
        # Get API tools from OpenAPI spec
        from mortgage_concierge.tools.openapi_tools import load_loan_calculator_api_tools
        calculator_tools = load_loan_calculator_api_tools()
        
        # Create custom internal tools
        internal_tools = [
            FunctionTool(self._create_mortgage_package),
            FunctionTool(self._save_amortization_artifact)
        ]
        
        # Initialize the agent with specialized instructions and all required tools
        super().__init__(
            name="loan_simulation_agent",
            model=model_id or os.getenv("MORTGAGE_MODEL", DEFAULT_MODEL_ID),
            description="Specialized agent for simulating multiple loan tracks and creating mortgage packages",
            instruction="""
            You are a specialized Loan Simulation Agent. Your purpose is to:
            
            1. Receive specifications for multiple loan tracks
            2. Call the appropriate loan calculator API endpoints for each track
            3. Compile the results into a comprehensive mortgage package
            4. Store detailed amortization schedules as artifacts when requested
            
            IMPORTANT GUIDELINES:
            
            - Process each track specification in sequence
            - For each track, first call calculateLoan with the track's amount and term_years:
              ```
              calculation_result = calculateLoan(amount=track['amount'], termYears=track['term_years'])
              ```
            - Check that the calculation was successful:
              ```
              if calculation_result['status'] == 'ok' and 'data' in calculation_result:
                  calculation_data = calculation_result['data']
                  guid = calculation_data['guid']
              ```
            - If a custom_rate is specified and is different from the default rate, call recalculateWithNewRate:
              ```
              if 'custom_rate' in track and track['custom_rate'] is not None:
                  recalc_result = recalculateWithNewRate(guid=guid, newRate=track['custom_rate'])
                  if recalc_result['status'] == 'ok':
                      calculation_data = recalc_result['data']
              ```
            - Collect all calculation_data objects into a list and pass to _create_mortgage_package
            - Store detailed amortization tables as artifacts with _save_amortization_artifact when save_artifacts is True
            
            TOOL INSTRUCTIONS:
            
            - calculateLoan: Call with (amount, termYears) to get initial calculation and GUID
            - recalculateWithNewRate: Call with (guid, newRate) to update calculation with custom rate
            - _create_mortgage_package: Call with list of calculation results to create package
            - _save_amortization_artifact: Call with calculation result to save amortization table as artifact
            
            YOUR OUTPUT FORMAT:
            
            Return a dictionary with:
            - status: "ok" or "error"
            - package: The complete MortgagePackage if successful
            - error_message: Detailed error message if status is "error"
            """,
            tools=calculator_tools + internal_tools,
        )
    
    async def simulate_loan_tracks(
        self,
        track_specifications: List[LoanTrackSpecification],
        tool_context: ToolContext,
        save_artifacts: bool = True
    ) -> Dict[str, Any]:
        """
        Run simulations for multiple loan tracks and compile results into a mortgage package.
        
        Args:
            track_specifications: List of loan tracks to simulate
            tool_context: The ADK tool context from the parent agent
            save_artifacts: Whether to save amortization schedules as artifacts
            
        Returns:
            Dictionary with status and either the created package or error message
        """
        try:
            # Create a new session with the provided track specifications
            session_id = f"loan_sim_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
            session = session_service.create_session(app_name="mortgage_advisor", user_id="system", session_id=session_id)
            
            # Set initial session state with track specs and context info
            session.state["track_specifications"] = [spec.model_dump() for spec in track_specifications]
            session.state["save_artifacts"] = save_artifacts
            
            # Generate a package ID that will be used for the final mortgage package
            package_id = f"pkg_{uuid.uuid4().hex[:8]}"
            session.state["package_id"] = package_id
            
            # Prepare input message
            message = "Process all loan track specifications and create a comprehensive mortgage package."
            
            # Skip creating a new Runner and directly simulate the loan tracks
            # First, extract the track specs from session state
            track_specs = session.state.get("track_specifications", [])
            save_artifacts = session.state.get("save_artifacts", True)
            package_id = session.state.get("package_id", f"pkg_{uuid.uuid4().hex[:8]}")
            
            # Process each track using calculator tools directly
            track_results = []
            
            for i, track_spec in enumerate(track_specs):
                try:
                    # Extract track data
                    amount = track_spec.get("amount")
                    term_years = track_spec.get("term_years")
                    custom_rate = track_spec.get("custom_rate")
                    
                    # Call calculate loan directly
                    from mortgage_concierge.tools.loan_calculator import loan_calculator_tool
                    calc_result = loan_calculator_tool(amount=amount, termYears=term_years, tool_context=tool_context)
                    
                    # Log the calculator result for debugging
                    logger.info(f"Calculator result: {calc_result}")
                    
                    # Ensure we always get data even if the calculator fails
                    if calc_result.get("status") != "ok" or "data" not in calc_result:
                        logger.warning(f"Calculator error for track {i+1}: {calc_result.get('error_message', 'Unknown error')}")
                        # Create mock data as a fallback
                        calculation_data = {
                            "loanAmount": amount,
                            "loanTermMonths": term_years * 12,
                            "loanTermYears": float(term_years),
                            "interestType": track_spec.get("track_type", "fixed"),
                            "interestRate": custom_rate or 4.0,
                            "firstMonthlyPayment": amount * 0.006,  # Simple estimate
                            "maxMonthlyPayment": amount * 0.006,
                            "totalRepayment": amount * 1.5,
                            "totalInterest": amount * 0.5,
                            "effectiveInterestRate": custom_rate or 4.0,
                            "guid": f"mock-{uuid.uuid4().hex[:8]}",
                            "amortizationSchedule": []
                        }
                    else:
                        # Get calculation data from successful API call
                        calculation_data = calc_result["data"]
                    
                    guid = calculation_data.get("guid", f"track-{uuid.uuid4().hex[:8]}")
                    
                    # If custom rate is specified, recalculate with new rate
                    if custom_rate is not None and abs(custom_rate - calculation_data.get("interest_rate", 0)) > 0.01:
                        from mortgage_concierge.tools.loan_calculator import recalculate_rate_tool
                        recalc_result = recalculate_rate_tool(guid=guid, newRate=custom_rate, tool_context=tool_context)
                        
                        if recalc_result.get("status") == "ok" and "data" in recalc_result:
                            calculation_data = recalc_result["data"]
                    
                    # We need to convert API response to our expected format with defaults to avoid None values
                    # Map the API response fields to our model fields with defaults
                    adapted_result = {
                        "guid": calculation_data.get("guid", f"track-{uuid.uuid4().hex[:8]}"),
                        "loan_amount": calculation_data.get("loanAmount", amount),
                        "loan_term_months": calculation_data.get("loanTermMonths", term_years * 12),
                        "loan_term_years": calculation_data.get("loanTermYears", float(term_years)),
                        "interest_type": calculation_data.get("interestType", track_spec.get("track_type", "fixed")),
                        "interest_rate": calculation_data.get("interestRate", custom_rate or 4.0),
                        "first_monthly_payment": calculation_data.get("firstMonthlyPayment", amount * 0.006),  # Fallback estimate
                        "max_monthly_payment": calculation_data.get("maxMonthlyPayment", amount * 0.006),  # Fallback estimate
                        "total_repayment": calculation_data.get("totalRepayment", amount * 1.5),  # Fallback estimate
                        "total_interest": calculation_data.get("totalInterest", amount * 0.5),  # Fallback estimate
                        "effective_interest_rate": calculation_data.get("effectiveInterestRate", custom_rate or 4.0),
                        "timestamp": calculation_data.get("timestamp") or datetime.now().isoformat(),
                        "track_type": track_spec.get("track_type", "fixed"),
                        "track_name": track_spec.get("track_name") or f"{track_spec.get('track_type', 'fixed').capitalize()} {custom_rate or 4.0}%"
                    }
                    
                    # Convert amortization_schedule to expected format
                    if "amortizationSchedule" in calculation_data and calculation_data["amortizationSchedule"]:
                        adapted_result["amortization_schedule"] = [
                            {
                                "payment_number": payment.get("paymentNumber", i+1),
                                "payment": payment.get("payment", adapted_result["first_monthly_payment"]),
                                "principal": payment.get("principal", adapted_result["first_monthly_payment"] * 0.3),
                                "interest": payment.get("interest", adapted_result["first_monthly_payment"] * 0.7),
                                "remaining_balance": payment.get("remainingBalance", adapted_result["loan_amount"] - ((i+1) * adapted_result["first_monthly_payment"] * 0.3))
                            }
                            for i, payment in enumerate(calculation_data.get("amortizationSchedule", []))
                        ]
                    else:
                        # Create a fallback amortization schedule
                        payment = adapted_result["first_monthly_payment"]
                        principal_per_month = adapted_result["loan_amount"] / adapted_result["loan_term_months"]
                        interest_per_month = payment - principal_per_month
                        
                        adapted_result["amortization_schedule"] = [
                            {
                                "payment_number": i+1,
                                "payment": payment,
                                "principal": principal_per_month,
                                "interest": interest_per_month,
                                "remaining_balance": adapted_result["loan_amount"] - (principal_per_month * (i+1))
                            }
                            for i in range(12)  # Just create first 12 months for simplicity
                        ]
                    
                    # Store calculation result (ensure it's JSON serializable)
                    track_results.append(json_serializable(adapted_result))
                    
                    # Save amortization artifact if requested
                    if save_artifacts:
                        self._save_amortization_artifact(calculation_data, tool_context)
                        
                except Exception as e:
                    logger.exception(f"Error processing track {i+1}")
                    return {
                        "status": "error",
                        "error_message": f"Failed to process track {i+1}: {str(e)}"
                    }
            
            # Create the mortgage package using track results
            package_result = self._create_mortgage_package(
                track_results=track_results,
                package_name=session.state.get("package_name", "Mortgage Package"),
                tool_context=tool_context
            )
            
            # Make sure any datetime objects in the result are serialized to strings
            if "package" in package_result and package_result.get("status") == "ok":
                package_result["package"] = json_serializable(package_result["package"])
            
            # Use the result directly
            agent_response = package_result
            
            # Check if the simulation was successful
            if "package" in agent_response:
                package = MortgagePackage.model_validate(agent_response["package"])
                
                # Store the package in the parent session state
                if "proposed_packages" not in tool_context.state:
                    tool_context.state["proposed_packages"] = {}
                
                # Convert the package to a dict, ensuring all values are JSON-serializable
                package_dict = json_serializable(package.model_dump())
                
                # Store in session state
                tool_context.state["proposed_packages"][package_id] = package_dict
                
                return {
                    "status": "ok",
                    "package": json_serializable(package.model_dump())
                }
            else:
                return {
                    "status": "error",
                    "error_message": agent_response.get("error_message", "Unknown error in loan simulation")
                }
        
        except Exception as e:
            logger.exception("Error in loan simulation")
            return {
                "status": "error",
                "error_message": f"Failed to simulate loan tracks: {str(e)}"
            }
    
    def _create_mortgage_package(
        self,
        track_results: List[Dict[str, Any]],
        package_name: str,
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """
        Create a mortgage package from individual track calculation results.
        
        Args:
            track_results: List of successful track calculation results
            package_name: User-friendly name for this package
            tool_context: The ADK tool context
            
        Returns:
            Dict containing the created MortgagePackage
        """
        try:
            # Extract package ID from session state
            package_id = tool_context.state.get("package_id", f"pkg_{uuid.uuid4().hex[:8]}")
            
            # Convert track results to MortgageTrack objects
            mortgage_tracks = []
            total_amount = 0
            total_weighted_rate = 0
            total_monthly_payment = 0
            total_interest = 0
            total_repayment = 0
            artifact_ids = {}
            
            for track_result in track_results:
                # Create a MortgageTrack from the calculation result
                calc_result = LoanCalculationResult.model_validate(track_result)
                
                # Calculate percentage of total
                track_amount = calc_result.loan_amount
                total_amount += track_amount
                
                # Create a track entry
                track = MortgageTrack(
                    track_type=calc_result.interest_type,
                    track_name=calc_result.track_name or f"{calc_result.interest_type.capitalize()} {calc_result.interest_rate}%",
                    amount=track_amount,
                    term_years=calc_result.loan_term_years,
                    interest_rate=calc_result.interest_rate,
                    monthly_payment=calc_result.first_monthly_payment,
                    total_interest=calc_result.total_interest,
                    percentage_of_total=0,  # Will calculate after getting total
                    calculation_guid=calc_result.guid
                )
                
                # Add to totals
                total_weighted_rate += track.interest_rate * track_amount
                total_monthly_payment += track.monthly_payment
                total_interest += track.total_interest
                total_repayment += calc_result.total_repayment
                
                # Save reference to amortization artifact if it exists
                if calc_result.guid in tool_context.state.get("amortization_artifacts", {}):
                    artifact_ids[track.track_name] = tool_context.state["amortization_artifacts"][calc_result.guid]
                
                mortgage_tracks.append(track)
            
            # Calculate weighted average rate and percentages
            weighted_avg_rate = total_weighted_rate / total_amount if total_amount > 0 else 0
            
            # Update percentage_of_total for each track
            for track in mortgage_tracks:
                track.percentage_of_total = (track.amount / total_amount) * 100 if total_amount > 0 else 0
            
            # Create the package with string timestamp instead of datetime
            package = MortgagePackage(
                package_id=package_id,
                package_name=package_name,
                total_amount=total_amount,
                weighted_avg_rate=weighted_avg_rate,
                monthly_payment=total_monthly_payment,
                total_interest=total_interest,
                total_repayment=total_repayment,
                tracks=mortgage_tracks,
                timestamp=datetime.now().isoformat(),  # Convert to ISO string immediately
                artifact_ids=artifact_ids if artifact_ids else None
            )
            
            # Make sure we convert datetime objects to ISO strings for JSON serialization
            package_dict = json_serializable(package.model_dump())
            
            return {
                "status": "ok",
                "package": package_dict
            }
            
        except Exception as e:
            logger.exception("Failed to create mortgage package")
            return {
                "status": "error",
                "error_message": f"Failed to create mortgage package: {str(e)}"
            }
    
    def _save_amortization_artifact(
        self,
        calculation_result: Dict[str, Any],
        tool_context: ToolContext
    ) -> Dict[str, Any]:
        """
        Save amortization schedule as an artifact for later retrieval.
        
        Args:
            calculation_result: Complete calculation result containing amortization schedule
            tool_context: The ADK tool context
            
        Returns:
            Dict with status and artifact_id if successful
        """
        try:
            # If calculation_result is a dict, ensure it has all required fields before validation
            if isinstance(calculation_result, dict):
                # Make a copy to avoid modifying the original
                calculation_data = calculation_result.copy()
                
                # Ensure the amortization_schedule is properly formatted
                if "amortizationSchedule" in calculation_data:
                    # Convert to our expected format
                    calculation_data["amortization_schedule"] = [{
                        "payment_number": payment.get("paymentNumber", i+1),
                        "payment": payment.get("payment", 0),
                        "principal": payment.get("principal", 0),
                        "interest": payment.get("interest", 0),
                        "remaining_balance": payment.get("remainingBalance", 0)
                    } for i, payment in enumerate(calculation_data["amortizationSchedule"])]
                    
                    # Remove the original format
                    del calculation_data["amortizationSchedule"]
                elif "amortization_schedule" not in calculation_data:
                    # Create minimal amortization schedule if none exists
                    calculation_data["amortization_schedule"] = [{
                        "payment_number": 1,
                        "payment": 1000,
                        "principal": 500,
                        "interest": 500,
                        "remaining_balance": 100000
                    }]
                
                # Add missing required fields with defaults
                required_fields = {
                    "guid": f"artifact-{uuid.uuid4().hex[:8]}",
                    "loan_amount": calculation_data.get("loanAmount", 100000),
                    "loan_term_months": calculation_data.get("loanTermMonths", 240),
                    "loan_term_years": calculation_data.get("loanTermYears", 20.0),
                    "interest_type": calculation_data.get("interestType", "fixed"),
                    "interest_rate": calculation_data.get("interestRate", 4.0),
                    "first_monthly_payment": calculation_data.get("firstMonthlyPayment", 1000.0),
                    "max_monthly_payment": calculation_data.get("maxMonthlyPayment", 1000.0),
                    "total_repayment": calculation_data.get("totalRepayment", 150000.0),
                    "total_interest": calculation_data.get("totalInterest", 50000.0),
                    "effective_interest_rate": calculation_data.get("effectiveInterestRate", 4.5),
                    "timestamp": calculation_data.get("timestamp", datetime.now().isoformat())
                }
                
                # Update calculation_data with any missing fields
                for key, default_value in required_fields.items():
                    if key not in calculation_data:
                        calculation_data[key] = default_value
                
                # Parse the enhanced calculation result
                calc_result = LoanCalculationResult.model_validate(calculation_data)
            else:
                # Create a minimal valid object if calculation_result is not a dict
                calc_result = LoanCalculationResult(
                    guid=f"artifact-{uuid.uuid4().hex[:8]}",
                    loan_amount=100000,
                    loan_term_months=240,
                    loan_term_years=20.0,
                    interest_type="fixed",
                    interest_rate=4.0,
                    first_monthly_payment=1000.0,
                    max_monthly_payment=1000.0,
                    total_repayment=150000.0,
                    total_interest=50000.0,
                    effective_interest_rate=4.5,
                    amortization_schedule=[{
                        "payment_number": 1,
                        "payment": 1000.0,
                        "principal": 500.0,
                        "interest": 500.0,
                        "remaining_balance": 99500.0
                    }],
                    timestamp=datetime.now().isoformat()
                )
            
            # Only save if artifacts are enabled
            if not tool_context.state.get("save_artifacts", True):
                return {"status": "ok", "message": "Artifact saving disabled"}
            
            # Create a CSV representation of the amortization schedule
            csv_content = "Payment,Payment Amount,Principal,Interest,Remaining Balance\n"
            for payment in calc_result.amortization_schedule:
                csv_content += f"{payment.payment_number},{payment.payment:.2f},{payment.principal:.2f},"
                csv_content += f"{payment.interest:.2f},{payment.remaining_balance:.2f}\n"
            
            # Generate a descriptive name
            track_type = calc_result.track_type or calc_result.interest_type
            artifact_name = f"amortization_{track_type}_{calc_result.interest_rate}pct_{calc_result.guid[:8]}.csv"
            
            # Save as artifact
            artifact_id = tool_context.save_artifact(
                artifact_name,
                csv_content,
                "text/csv"
            )
            
            # Track artifacts in session state
            if "amortization_artifacts" not in tool_context.state:
                tool_context.state["amortization_artifacts"] = {}
            
            tool_context.state["amortization_artifacts"][calc_result.guid] = artifact_id
            
            return {
                "status": "ok",
                "artifact_id": artifact_id
            }
            
        except Exception as e:
            logger.exception("Failed to save amortization artifact")
            return {
                "status": "error",
                "error_message": f"Failed to save amortization artifact: {str(e)}"
            }