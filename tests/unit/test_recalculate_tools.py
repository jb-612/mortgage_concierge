import os
import importlib
import pytest
import requests

from pathlib import Path
from mortgage_concierge.tools.loan_calculator import (
    recalculate_rate_tool,
    recalculate_term_tool,
)


class DummyToolContext:
    pass


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("RECALC_RATE_API_URL", raising=False)
    monkeypatch.delenv("RECALC_TERM_API_URL", raising=False)
    yield


def test_recalculate_rate_live_success(monkeypatch):
    fake_data = {"newMonthlyPayment": 1234.56}

    class FakeResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return fake_data

    monkeypatch.setenv("RECALC_RATE_API_URL", "http://fake-rate")
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse())

    result = recalculate_rate_tool(1000, 10, 5.0, DummyToolContext())
    assert result["status"] == "ok"
    assert result["data"] == fake_data


def test_recalculate_rate_live_error(monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.RequestException("rate network error")

    monkeypatch.setenv("RECALC_RATE_API_URL", "http://fake-rate")
    monkeypatch.setattr(requests, "post", fake_post)

    result = recalculate_rate_tool(2000, 15, 4.5, DummyToolContext())
    assert result["status"] == "error"
    assert "Recalculate rate service error" in result["error_message"]


def test_recalculate_rate_fallback(monkeypatch):
    result = recalculate_rate_tool(0, 0, 0, DummyToolContext())
    assert result["status"] == "ok"
    data = result["data"]
    assert data["newMonthlyPayment"] == 3000.0


def test_recalculate_rate_fallback_file_not_found(monkeypatch):
    module = importlib.import_module("mortgage_concierge.tools.loan_calculator")
    fake_path = Path("/nonexistent/recalc_rate_mock.json")
    monkeypatch.setattr(module, "Path", lambda *args, **kwargs: fake_path)

    result = recalculate_rate_tool(0, 0, 0, DummyToolContext())
    assert result["status"] == "error"
    assert "Mock data load error" in result["error_message"]


def test_recalculate_term_live_success(monkeypatch):
    fake_data = {"newTermYears": 12, "monthlyPayment": 2500.0}

    class FakeResponse:
        def raise_for_status(self):
            pass
        def json(self):
            return fake_data

    monkeypatch.setenv("RECALC_TERM_API_URL", "http://fake-term")
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: FakeResponse())

    result = recalculate_term_tool(1000, 800.0, 3.5, DummyToolContext())
    assert result["status"] == "ok"
    assert result["data"] == fake_data


def test_recalculate_term_live_error(monkeypatch):
    def fake_post(*args, **kwargs):
        raise requests.RequestException("term network error")

    monkeypatch.setenv("RECALC_TERM_API_URL", "http://fake-term")
    monkeypatch.setattr(requests, "post", fake_post)

    result = recalculate_term_tool(2000, 1500.0, 4.0, DummyToolContext())
    assert result["status"] == "error"
    assert "Recalculate term service error" in result["error_message"]


def test_recalculate_term_fallback(monkeypatch):
    result = recalculate_term_tool(0, 0, 0, DummyToolContext())
    assert result["status"] == "ok"
    data = result["data"]
    assert data["newTermYears"] == 18


def test_recalculate_term_fallback_file_not_found(monkeypatch):
    module = importlib.import_module("mortgage_concierge.tools.loan_calculator")
    fake_path = Path("/nonexistent/recalc_term_mock.json")
    monkeypatch.setattr(module, "Path", lambda *args, **kwargs: fake_path)

    result = recalculate_term_tool(0, 0, 0, DummyToolContext())
    assert result["status"] == "error"
    assert "Mock data load error" in result["error_message"]