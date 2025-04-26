"""
Tools for working with loan simulation sub-agents.

This module provides function tools that wrap the LoanSimulationAgent
to enable easy access from the main agent.
"""
import logging
from typing import List, Dict, Any, Optional

from google.adk.tools import FunctionTool, ToolContext

from mortgage_concierge.sub_agents.loan_simulation.agent import LoanSimulationAgent
from mortgage_concierge.sub_agents.loan_simulation.models import LoanTrackSpecification

logger = logging.getLogger(__name__)

async def simulate_loan_tracks_tool(
    track_specifications: List[Dict[str, Any]],
    package_name: str,
    tool_context: ToolContext,
    save_amortization_artifacts: bool = True
) -> Dict[str, Any]:
    """
    Simulates multiple loan tracks and creates a mortgage package.
    
    This tool creates a LoanSimulationAgent to simulate multiple mortgage tracks
    based on the provided specifications. The agent will calculate each track and
    compile the results into a unified MortgagePackage.
    
    Args:
        track_specifications: List of loan track specifications, each containing:
            - amount: The loan amount for this track
            - term_years: The loan term in years
            - track_type: Type of track (e.g., 'prime', 'fixed')
            - custom_rate: (Optional) Custom interest rate for this track
            - loan_name: (Optional) Friendly name for this track
        package_name: User-friendly name for the mortgage package
        tool_context: The ADK tool context
        save_amortization_artifacts: Whether to store amortization schedules as artifacts
    
    Returns:
        Dictionary with status and either the mortgage package or an error message
    """
    try:
        # Convert dict specs to LoanTrackSpecification objects
        track_specs = [
            LoanTrackSpecification(**spec) for spec in track_specifications
        ]
        
        # Create simulation agent
        simulation_agent = LoanSimulationAgent()
        
        # Run the simulation
        result = await simulation_agent.simulate_loan_tracks(
            track_specifications=track_specs,
            tool_context=tool_context,
            save_artifacts=save_amortization_artifacts
        )
        
        return result
    except Exception as e:
        logger.exception("Error in simulate_loan_tracks_tool")
        return {
            "status": "error",
            "error_message": f"Failed to simulate loan tracks: {str(e)}"
        }

simulate_loan_tracks_tool.__name__ = "simulate_loan_tracks"
simulate_loan_tracks = FunctionTool(simulate_loan_tracks_tool)