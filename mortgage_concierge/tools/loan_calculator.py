import os
import logging
import datetime
import uuid
import requests
from google.adk.tools import FunctionTool, ToolContext

logger = logging.getLogger(__name__)

def loan_calculator_tool(amount: float, termYears: int, tool_context: ToolContext) -> dict:
    """
    Mock tool for a loan calculator.
    
    When called with amount=500000 and termYears=20, returns a fixed result.
    In production you might call the third‑party REST API using requests.
    
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
    # For now, use a fixed mock response.
    if amount == 500000 and termYears == 20:
        mock_response = {
            "loanAmount": 500000,
            "loanTermMonths": 240,
            "loanTermYears": 20,
            "interestType": "fixed",
            "interestRate": 4.25,
            "firstMonthlyPayment": 3096.172345873029,
            "maxMonthlyPayment": 3096.172345873029,
            "totalRepayment": 743081.363009527,
            "totalInterest": 243081.36300952698,
            "effectiveInterestRate": 4.86,
            "amortizationSchedule": [
                {
                    "paymentNumber": 1,
                    "payment": 3096.172345873029,
                    "principal": 1325.3390125396954,
                    "interest": 1770.8333333333335,
                    "remainingBalance": 498674.6609874603
                },
                {
                    "paymentNumber": 2,
                    "payment": 3096.172345873029,
                    "principal": 1330.0329215424404,
                    "interest": 1766.1394243305886,
                    "remainingBalance": 497344.6280659179
                },
                {
                    "paymentNumber": 3,
                    "payment": 3096.172345873029,
                    "principal": 1334.7434548062363,
                    "interest": 1761.4288910667926,
                    "remainingBalance": 496009.88461111166
                },
                {
                    "paymentNumber": 4,
                    "payment": 3096.172345873029,
                    "principal": 1339.470671208675,
                    "interest": 1756.701674664354,
                    "remainingBalance": 494670.41393990297
                },
                {
                    "paymentNumber": 5,
                    "payment": 3096.172345873029,
                    "principal": 1344.2146298358725,
                    "interest": 1751.9577160371564,
                    "remainingBalance": 493326.1993100671
                },
                {
                    "paymentNumber": 6,
                    "payment": 3096.172345873029,
                    "principal": 1348.9753899832078,
                    "interest": 1747.196955889821,
                    "remainingBalance": 491977.2239200839
                },
                {
                    "paymentNumber": 7,
                    "payment": 3096.172345873029,
                    "principal": 1353.753011156065,
                    "interest": 1742.419334716964,
                    "remainingBalance": 490623.47090892785
                },
                {
                    "paymentNumber": 8,
                    "payment": 3096.172345873029,
                    "principal": 1358.547553070576,
                    "interest": 1737.624792802453,
                    "remainingBalance": 489264.92335585726
                },
                {
                    "paymentNumber": 9,
                    "payment": 3096.172345873029,
                    "principal": 1363.3590756543676,
                    "interest": 1732.8132702186613,
                    "remainingBalance": 487901.5642802029
                },
                {
                    "paymentNumber": 10,
                    "payment": 3096.172345873029,
                    "principal": 1368.18763904731,
                    "interest": 1727.9847068257188,
                    "remainingBalance": 486533.37664115557
                },
                {
                    "paymentNumber": 11,
                    "payment": 3096.172345873029,
                    "principal": 1373.0333036022694,
                    "interest": 1723.1390422707595,
                    "remainingBalance": 485160.3433375533
                },
                {
                    "paymentNumber": 12,
                    "payment": 3096.172345873029,
                    "principal": 1377.8961298858608,
                    "interest": 1718.2762159871681,
                    "remainingBalance": 483782.44720766746
                }
            ],
            "timestamp": datetime.datetime.now().isoformat(),
            "guid": str(uuid.uuid4())
        }
        return {"status": "ok", "data": mock_response}
    
    # Otherwise, return an error or consider calling the real service.
    return {"status": "error", "error_message": "No mock configured for the provided parameters."}

loan_calculator_tool.__name__ = "loan_calculator"
loan_calculator = FunctionTool(loan_calculator_tool)