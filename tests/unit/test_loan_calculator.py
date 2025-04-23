import os
import json
import pytest
import importlib
import requests
import uuid

from pathlib import Path
from mortgage_concierge.tools.loan_calculator import (
    loan_calculator_tool,
    recalculate_rate_tool,
    recalculate_term_tool
)


class DummyToolContext:
    def __init__(self):
        self.state = {}


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # Ensure calculator URLs are unset for fallback tests
    monkeypatch.delenv("LOAN_CALCULATOR_API_URL", raising=False)
    monkeypatch.delenv("RECALC_RATE_API_URL", raising=False)
    monkeypatch.delenv("RECALC_TERM_API_URL", raising=False)
    yield


def test_live_mode_success(monkeypatch):
    # Simulate a successful external API call
    test_guid = str(uuid.uuid4())
    fake_data = {
        "guid": test_guid,
        "loanAmount": 123.45,
        "loanTermYears": 5
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return fake_data

    monkeypatch.setenv("LOAN_CALCULATOR_API_URL", "http://fake")
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse())

    tool_context = DummyToolContext()
    result = loan_calculator_tool(123.45, 5, tool_context)
    
    assert result["status"] == "ok"
    assert result["data"] == fake_data
    assert tool_context.state["loan_calculation_guid"] == test_guid
    assert tool_context.state["loan_initial_results"] == fake_data


def test_live_mode_error(monkeypatch):
    # Simulate a network error
    def fake_post(*args, **kwargs):
        raise requests.RequestException("network error")

    monkeypatch.setenv("LOAN_CALCULATOR_API_URL", "http://fake")
    monkeypatch.setattr(requests, "post", fake_post)

    result = loan_calculator_tool(1000, 10, DummyToolContext())
    assert result["status"] == "error"
    assert "Calculator service error" in result["error_message"]


def test_fallback_mode_loads_file():
    # With no URL, should load mock JSON from tests/unit/data
    tool_context = DummyToolContext()
    result = loan_calculator_tool(500000, 20, tool_context)
    
    assert result["status"] == "ok"
    assert isinstance(result["data"], dict)
    assert result["data"]["loanAmount"] == 500000
    assert tool_context.state["loan_calculation_guid"] == "00000000-0000-0000-0000-000000000000"
    assert tool_context.state["loan_initial_results"] == result["data"]


def test_fallback_mode_file_not_found(monkeypatch):
    # Override Path resolution to point to a non-existent file
    module = importlib.import_module("mortgage_concierge.tools.loan_calculator")
    fake_path = Path("/nonexistent/calculator_mock.json")
    monkeypatch.setattr(module, "Path", lambda *args, **kwargs: fake_path)

    result = loan_calculator_tool(0, 0, DummyToolContext())
    assert result["status"] == "error"
    assert "Mock data load error" in result["error_message"]


def test_recalculate_rate_tool_success(monkeypatch):
    # Simulate a successful rate recalculation
    test_guid = "test-guid-123"
    new_rate = 4.5
    fake_data = {
        "guid": test_guid,
        "newRate": new_rate,
        "newMonthlyPayment": 2500.75
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return fake_data

    monkeypatch.setenv("RECALC_RATE_API_URL", "http://fake")
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse())

    tool_context = DummyToolContext()
    result = recalculate_rate_tool(test_guid, new_rate, tool_context)
    
    assert result["status"] == "ok"
    assert result["data"] == fake_data
    assert tool_context.state["loan_custom_rate"] == new_rate


def test_recalculate_term_tool_success(monkeypatch):
    # Simulate a successful term recalculation
    test_guid = "test-guid-456"
    new_term = 15
    fake_data = {
        "guid": test_guid,
        "newTermYears": new_term,
        "newMonthlyPayment": 3200.50
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return fake_data

    monkeypatch.setenv("RECALC_TERM_API_URL", "http://fake")
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse())

    tool_context = DummyToolContext()
    result = recalculate_term_tool(test_guid, new_term, tool_context)
    
    assert result["status"] == "ok"
    assert result["data"] == fake_data
    assert tool_context.state["loan_custom_term"] == new_term


def test_recalculate_tools_fallback_mode():
    # Test fallback to mock JSON for recalculation tools
    tool_context = DummyToolContext()
    
    # Test rate recalculation fallback
    rate_result = recalculate_rate_tool("test-guid", 3.5, tool_context)
    assert rate_result["status"] == "ok"
    assert "overrideRate" in rate_result["data"]
    assert tool_context.state["loan_custom_rate"] == 3.5
    
    # Test term recalculation fallback
    term_result = recalculate_term_tool("test-guid", 18, tool_context)
    assert term_result["status"] == "ok"
    assert "newTermYears" in term_result["data"]
    assert tool_context.state["loan_custom_term"] == 18