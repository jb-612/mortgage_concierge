import os
import logging
import json
import requests
from pathlib import Path
from google.adk.tools import FunctionTool, ToolContext

logger = logging.getLogger(__name__)

def loan_calculator_tool(amount: float, termYears: int, tool_context: ToolContext) -> dict:
    """
    Tool for a loan calculator.
    
    If LOAN_CALCULATOR_API_URL is set, sends a POST to the external API.
    Otherwise, loads the mock JSON from tests/unit/data/calculator_mock.json.
    
    Args:
        amount (float): The principal loan amount.
        termYears (int): The term of the loan in years.
        tool_context (ToolContext): The ADK tool context.
    
    Returns:
        dict: A dictionary containing either the loan details or an error message.
    """
    # If an external calculator endpoint is configured, call it instead of mock.
    api_url = os.getenv("LOAN_CALCULATOR_API_URL")
    if api_url:
        payload = {"amount": amount, "termYears": termYears}
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {"status": "ok", "data": data}
        except Exception as e:
            logger.exception("External calculator call failed")
            return {"status": "error", "error_message": f"Calculator service error: {e}"}
    # Fallback: load mock JSON from tests/unit/data
    try:
        mock_file = Path(__file__).resolve().parents[2] / "tests" / "unit" / "data" / "calculator_mock.json"
        with open(mock_file, "r") as f:
            data = json.load(f)
        return {"status": "ok", "data": data}
    except Exception as e:
        logger.exception("Failed to load mock JSON")
        return {"status": "error", "error_message": f"Mock data load error: {e}"}

loan_calculator_tool.__name__ = "loan_calculator"
loan_calculator = FunctionTool(loan_calculator_tool)
 
def recalculate_rate_tool(amount: float, termYears: int, overrideRate: float, tool_context: ToolContext) -> dict:
    """
    Tool to recalculate loan payment based on an override interest rate.
    
    If RECALC_RATE_API_URL is set, sends POST with {amount, termYears, overrideRate}.
    Otherwise, loads mock from tests/unit/data/recalc_rate_mock.json.
    """
    api_url = os.getenv("RECALC_RATE_API_URL")
    payload = {"amount": amount, "termYears": termYears, "overrideRate": overrideRate}
    if api_url:
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {"status": "ok", "data": data}
        except Exception as e:
            logger.exception("Recalculate rate call failed")
            return {"status": "error", "error_message": f"Recalculate rate service error: {e}"}
    # Fallback mock
    try:
        mock_file = Path(__file__).resolve().parents[2] / "tests" / "unit" / "data" / "recalc_rate_mock.json"
        with open(mock_file, "r") as f:
            data = json.load(f)
        return {"status": "ok", "data": data}
    except Exception as e:
        logger.exception("Failed to load recalc rate mock JSON")
        return {"status": "error", "error_message": f"Mock data load error: {e}"}

recalculate_rate_tool.__name__ = "recalculate_rate"
recalculate_rate = FunctionTool(recalculate_rate_tool)

def recalculate_term_tool(amount: float, desiredPayment: float, interestRate: float, tool_context: ToolContext) -> dict:
    """
    Tool to recalculate loan term based on desired monthly payment.
    
    If RECALC_TERM_API_URL is set, sends POST with {amount, desiredPayment, interestRate}.
    Otherwise, loads mock from tests/unit/data/recalc_term_mock.json.
    """
    api_url = os.getenv("RECALC_TERM_API_URL")
    payload = {"amount": amount, "desiredPayment": desiredPayment, "interestRate": interestRate}
    if api_url:
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            return {"status": "ok", "data": data}
        except Exception as e:
            logger.exception("Recalculate term call failed")
            return {"status": "error", "error_message": f"Recalculate term service error: {e}"}
    # Fallback mock
    try:
        mock_file = Path(__file__).resolve().parents[2] / "tests" / "unit" / "data" / "recalc_term_mock.json"
        with open(mock_file, "r") as f:
            data = json.load(f)
        return {"status": "ok", "data": data}
    except Exception as e:
        logger.exception("Failed to load recalc term mock JSON")
        return {"status": "error", "error_message": f"Mock data load error: {e}"}

recalculate_term_tool.__name__ = "recalculate_term"
recalculate_term = FunctionTool(recalculate_term_tool)