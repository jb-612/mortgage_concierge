import os
import json
import pytest
import importlib
import requests

from pathlib import Path
from mortgage_concierge.tools.loan_calculator import loan_calculator_tool


class DummyToolContext:
    pass


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # Ensure calculator URL is unset for fallback tests
    monkeypatch.delenv("LOAN_CALCULATOR_API_URL", raising=False)
    yield


def test_live_mode_success(monkeypatch):
    # Simulate a successful external API call
    fake_data = {"foo": "bar"}

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return fake_data

    monkeypatch.setenv("LOAN_CALCULATOR_API_URL", "http://fake")
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse())

    result = loan_calculator_tool(123.45, 5, DummyToolContext())
    assert result["status"] == "ok"
    assert result["data"] == fake_data


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
    result = loan_calculator_tool(500000, 20, DummyToolContext())
    assert result["status"] == "ok"
    assert isinstance(result["data"], dict)
    assert result["data"]["loanAmount"] == 500000


def test_fallback_mode_file_not_found(monkeypatch):
    # Override Path resolution to point to a non-existent file
    module = importlib.import_module("mortgage_concierge.tools.loan_calculator")
    fake_path = Path("/nonexistent/calculator_mock.json")
    monkeypatch.setattr(module, "Path", lambda *args, **kwargs: fake_path)

    result = loan_calculator_tool(0, 0, DummyToolContext())
    assert result["status"] == "error"
    assert "Mock data load error" in result["error_message"]