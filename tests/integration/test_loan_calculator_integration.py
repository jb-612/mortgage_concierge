"""
Integration tests for loan calculator functionality.
Tests the full flow from initial calculation to recalculation using OpenAPI tools.
"""
import os
import json
import pytest
import requests
from unittest.mock import patch, MagicMock

from google.adk.tools import ToolContext
from google.adk.sessions import Session
from google.adk.sessions.state import State

# Import the tools
from mortgage_concierge.tools.loan_calculator import (
    loan_calculator_tool,
    recalculate_rate_tool,
    recalculate_term_tool
)


@pytest.fixture
def mock_session():
    """Create a mock session with an empty state dictionary."""
    session = MagicMock(spec=Session)
    session.state = State({}, {})
    return session


@pytest.fixture
def tool_context(mock_session):
    """Create a tool context with a mock session."""
    context = MagicMock(spec=ToolContext)
    context.session = mock_session
    context.state = mock_session.state
    return context


class TestLoanCalculatorIntegration:
    """Integration tests for the loan calculator functionality."""

    def test_full_calculation_flow(self, tool_context, monkeypatch):
        """
        Test the full loan calculation flow:
        1. Initial calculation with loan_calculator_tool
        2. Store GUID in session state
        3. Recalculate with new rate using recalculate_rate_tool
        4. Recalculate with new term using recalculate_term_tool
        """
        # Setup mock responses for all API calls
        initial_calc_data = {
            "guid": "test-guid-12345",
            "loanAmount": 400000,
            "loanTermYears": 30,
            "loanTermMonths": 360,
            "interestRate": 4.5,
            "firstMonthlyPayment": 2026.74,
            "totalRepayment": 729626.40,
            "totalInterest": 329626.40
        }

        rate_recalc_data = {
            "guid": "test-guid-12345",
            "loanAmount": 400000,
            "loanTermYears": 30,
            "loanTermMonths": 360,
            "interestRate": 4.0,  # New rate
            "firstMonthlyPayment": 1909.66,  # Lower due to new rate
            "totalRepayment": 687478.60,
            "totalInterest": 287478.60
        }

        term_recalc_data = {
            "guid": "test-guid-12345",
            "loanAmount": 400000,
            "loanTermYears": 20,  # New term
            "loanTermMonths": 240,
            "interestRate": 4.5,
            "firstMonthlyPayment": 2532.49,  # Higher due to shorter term
            "totalRepayment": 607797.60,
            "totalInterest": 207797.60
        }

        # Mock API responses
        class MockResponse:
            def __init__(self, json_data):
                self.json_data = json_data
            
            def raise_for_status(self):
                pass
            
            def json(self):
                return self.json_data

        # Mock the requests.post call based on URL
        def mock_post(url, json=None, timeout=None):
            if "calculate-loan" in url:
                return MockResponse(initial_calc_data)
            elif "recalculate-rate" in url:
                return MockResponse(rate_recalc_data)
            elif "recalculate-term" in url:
                return MockResponse(term_recalc_data)
            return MockResponse({})

        # Set up environment variables
        monkeypatch.setenv("LOAN_CALCULATOR_API_URL", "http://fake-api/calculate-loan")
        monkeypatch.setenv("RECALC_RATE_API_URL", "http://fake-api/recalculate-rate")
        monkeypatch.setenv("RECALC_TERM_API_URL", "http://fake-api/recalculate-term")
        
        # Mock requests.post
        monkeypatch.setattr(requests, "post", mock_post)

        # Step 1: Initial calculation
        result = loan_calculator_tool(400000, 30, tool_context)
        
        # Verify successful result
        assert result["status"] == "ok"
        assert result["data"] == initial_calc_data
        
        # Verify state was stored
        assert tool_context.state.get("loan_calculation_guid") == "test-guid-12345"
        assert tool_context.state.get("loan_initial_results") == initial_calc_data

        # Step 2: Recalculate with new rate
        rate_result = recalculate_rate_tool("test-guid-12345", 4.0, tool_context)
        
        # Verify successful result
        assert rate_result["status"] == "ok"
        assert rate_result["data"] == rate_recalc_data
        
        # Verify custom rate was stored
        assert tool_context.state.get("loan_custom_rate") == 4.0

        # Step 3: Recalculate with new term
        term_result = recalculate_term_tool("test-guid-12345", 20, tool_context)
        
        # Verify successful result
        assert term_result["status"] == "ok"
        assert term_result["data"] == term_recalc_data
        
        # Verify custom term was stored
        assert tool_context.state.get("loan_custom_term") == 20

    def test_full_calculation_with_fallback(self, tool_context, monkeypatch):
        """
        Test the full loan calculation flow with fallback to mock data:
        1. Initial calculation with loan_calculator_tool (fallback)
        2. Store GUID in session state
        3. Recalculate with new rate using recalculate_rate_tool (fallback)
        4. Recalculate with new term using recalculate_term_tool (fallback)
        """
        # Ensure environment variables are not set (to trigger fallback)
        monkeypatch.delenv("LOAN_CALCULATOR_API_URL", raising=False)
        monkeypatch.delenv("RECALC_RATE_API_URL", raising=False)
        monkeypatch.delenv("RECALC_TERM_API_URL", raising=False)

        # Step 1: Initial calculation with fallback
        result = loan_calculator_tool(500000, 20, tool_context)
        
        # Verify successful result
        assert result["status"] == "ok"
        assert "guid" in result["data"]
        
        # Store GUID for later use
        guid = result["data"]["guid"]
        
        # Verify state was stored
        assert tool_context.state.get("loan_calculation_guid") == guid
        assert tool_context.state.get("loan_initial_results") == result["data"]

        # Step 2: Recalculate with new rate
        rate_result = recalculate_rate_tool(guid, 3.5, tool_context)
        
        # Verify successful result
        assert rate_result["status"] == "ok"
        assert "newMonthlyPayment" in rate_result["data"]
        
        # Verify custom rate was stored
        assert tool_context.state.get("loan_custom_rate") == 3.5

        # Step 3: Recalculate with new term
        term_result = recalculate_term_tool(guid, 15, tool_context)
        
        # Verify successful result
        assert term_result["status"] == "ok"
        assert "newTermYears" in term_result["data"]
        
        # Verify custom term was stored
        assert tool_context.state.get("loan_custom_term") == 15

    @pytest.mark.skip("Requires ADK API Server - run manually with ADK server running")
    def test_agent_with_adk_server(self):
        """
        Integration test using the ADK API server.
        
        To run this test:
        1. Start ADK API server: adk api_server
        2. Run this test: pytest tests/integration/test_loan_calculator_integration.py::TestLoanCalculatorIntegration::test_agent_with_adk_server -v
        """
        base_url = "http://0.0.0.0:8765"  # Default ADK server
        app_name = "mortgage_concierge"
        user_id = "test_user_123"
        session_id = "test_session_123"
        
        # Step 1: Create a new session
        session_url = f"{base_url}/apps/{app_name}/users/{user_id}/sessions/{session_id}"
        session_payload = {
            "state": {
                "user_profile": {
                    "property_value": 700000,
                    "down_payment": 200000,
                    "annual_income": 120000,
                    "monthly_debt": 1500,
                    "credit_score": "excellent",
                    "risk_tolerance": "medium"
                }
            }
        }
        
        session_response = requests.post(session_url, json=session_payload)
        assert session_response.status_code == 200
        
        # Step 2: Send a query to calculate a loan
        run_url = f"{base_url}/run"
        query_payload = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{
                    "text": "I want to know how much my monthly payment would be for a 30-year mortgage"
                }]
            }
        }
        
        response = requests.post(run_url, json=query_payload)
        assert response.status_code == 200
        
        # Parse events to find the LoanCalculation tool call and response
        events = response.json()
        assert len(events) > 0
        
        # Step 3: Request to see different interest rate
        rate_query_payload = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{
                    "text": "What if I got a 4% interest rate?"
                }]
            }
        }
        
        rate_response = requests.post(run_url, json=rate_query_payload)
        assert rate_response.status_code == 200
        
        # Step 4: Request to see different term
        term_query_payload = {
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "new_message": {
                "role": "user",
                "parts": [{
                    "text": "How about a 15-year mortgage instead?"
                }]
            }
        }
        
        term_response = requests.post(run_url, json=term_query_payload)
        assert term_response.status_code == 200