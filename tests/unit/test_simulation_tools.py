"""
Unit tests for loan simulation tools and sub-agent.
"""
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import pytest

from mortgage_concierge.tools.simulation_tools import simulate_loan_tracks_tool
from mortgage_concierge.sub_agents.loan_simulation.models import (
    LoanTrackSpecification,
    MortgagePackage
)

class DummyToolContext:
    """Mock tool context for testing."""
    def __init__(self):
        self.state = {}
        self.session_id = "test-session-123"
        self.save_artifact = MagicMock(return_value="artifact-123")


@pytest.mark.asyncio
async def test_simulate_loan_tracks_tool():
    """Test the simulate_loan_tracks_tool function."""
    # Create mock LoanSimulationAgent
    mock_agent = AsyncMock()
    mock_agent.simulate_loan_tracks.return_value = {
        "status": "ok",
        "package": {
            "package_id": "pkg_12345678",
            "package_name": "Test Package",
            "total_amount": 500000,
            "weighted_avg_rate": 4.25,
            "monthly_payment": 2400.75,
            "total_interest": 150000,
            "total_repayment": 650000,
            "tracks": [
                {
                    "track_type": "fixed",
                    "track_name": "Fixed 4.25%",
                    "amount": 500000,
                    "term_years": 25,
                    "interest_rate": 4.25,
                    "monthly_payment": 2400.75,
                    "total_interest": 150000,
                    "percentage_of_total": 100.0,
                    "calculation_guid": "test-guid-123"
                }
            ],
            "timestamp": "2025-04-25T12:00:00",
            "artifact_ids": None,
            "metadata": None
        }
    }
    
    # Prepare test data
    track_specs = [
        {
            "amount": 500000,
            "term_years": 25,
            "track_type": "fixed",
            "custom_rate": 4.25
        }
    ]
    
    tool_context = DummyToolContext()
    
    # Test with mocked agent
    with patch('mortgage_concierge.tools.simulation_tools.LoanSimulationAgent', 
              return_value=mock_agent):
        result = await simulate_loan_tracks_tool(
            track_specifications=track_specs,
            package_name="Test Package",
            tool_context=tool_context
        )
    
    # Verify result
    assert result["status"] == "ok"
    assert result["package"]["package_id"] == "pkg_12345678"
    assert result["package"]["total_amount"] == 500000
    
    # Verify agent was called correctly
    mock_agent.simulate_loan_tracks.assert_called_once()
    
    # First argument should be a list of LoanTrackSpecification objects
    call_args = mock_agent.simulate_loan_tracks.call_args[1]
    assert isinstance(call_args["track_specifications"][0], LoanTrackSpecification)
    assert call_args["track_specifications"][0].amount == 500000
    assert call_args["track_specifications"][0].term_years == 25
    assert call_args["track_specifications"][0].track_type == "fixed"
    assert call_args["track_specifications"][0].custom_rate == 4.25
    
    # Verify tool_context was passed correctly
    assert call_args["tool_context"] == tool_context


@pytest.mark.asyncio
async def test_simulate_loan_tracks_tool_error_handling():
    """Test error handling in simulate_loan_tracks_tool."""
    # Create mock agent that raises an exception
    mock_agent = AsyncMock()
    mock_agent.simulate_loan_tracks.side_effect = ValueError("Test error")
    
    # Prepare test data
    track_specs = [
        {
            "amount": 500000,
            "term_years": 25,
            "track_type": "fixed"
        }
    ]
    
    tool_context = DummyToolContext()
    
    # Test with mocked agent
    with patch('mortgage_concierge.tools.simulation_tools.LoanSimulationAgent', 
              return_value=mock_agent):
        result = await simulate_loan_tracks_tool(
            track_specifications=track_specs,
            package_name="Test Package",
            tool_context=tool_context
        )
    
    # Verify error handling
    assert result["status"] == "error"
    assert "error_message" in result
    assert "Test error" in result["error_message"]