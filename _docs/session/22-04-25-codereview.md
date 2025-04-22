mortgage_concierge/bootstrap.py
<source>
"""
Runtime bootstrap for Mortgage Concierge.

This module contains a single public coroutine `init()` that must be called
exactly once during application start‑up (CLI, web server, tests, etc.).  It
performs *expensive, side‑effect‑laden* initialisation such as ingesting bank
policy documents into the in‑memory `MemoryService`.

Placing these operations here – instead of at import‑time – prevents unexpected
cold‑start delays, avoids masking import errors, and keeps unit‑tests fast
(because they can simply choose **not** to call `bootstrap.init()`).
"""
from __future__ import annotations

import asyncio
import logging

from mortgage_concierge.shared_libraries.memory_ingestion import (
    ingest_bank_docs_to_memory,
)

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Public coroutine
# --------------------------------------------------------------------------- #
_initialised: bool = False


async def init() -> None:
    """
    Perform one‑time initialisation for the Mortgage Concierge application.

    This is *idempotent*: calling it multiple times will only run the expensive
    work once.  Subsequent calls return immediately.
    """
    global _initialised
    if _initialised:
        logger.debug("bootstrap.init() already executed – skipping.")
        return

    logger.info("Mortgage Concierge bootstrap: ingesting bank policy documents …")
    # `ingest_bank_docs_to_memory()` does synchronous file‑I/O; run it in a
    # thread so we don't block the event‑loop if the caller is async.
    await asyncio.to_thread(ingest_bank_docs_to_memory)
    _initialised = True
    logger.info("Mortgage Concierge bootstrap completed.")
</source>

mortgage_concierge/agent.py
<source>
import os
from dotenv import load_dotenv

# ADK imports
from google.adk.agents import Agent

# Local imports
from mortgage_concierge.prompt import AGENT_INSTRUCTION
from mortgage_concierge.tools.bank_docs import search_bank_docs
from mortgage_concierge.tools.loan_tracks import list_loan_tracks
from mortgage_concierge.tools.store_state import store_state_tool
from mortgage_concierge.tools.openapi_tools import load_loan_calculator_api_tools

# NOTE:
#   Expensive, I/O‑heavy initialisation (e.g. ingesting bank documents) is **NOT**
#   performed at import‑time.  Call `mortgage_concierge.bootstrap.init()` once
#   from your application entry‑point before the first agent invocation.
#
#   This keeps imports fast and predictable, and avoids masking initialisation
#   errors.  See `mortgage_concierge/bootstrap.py`.

# --------------------------------------------------------------------------- #
# Environment & configuration
# --------------------------------------------------------------------------- #
load_dotenv()

MODEL_ID = os.getenv("MORTGAGE_MODEL", os.getenv("OPENAI_MODEL", "openai/gpt-4.1-nano"))
APP_NAME = os.getenv("APP_NAME", "mortgage_advisor")

# Optional LiteLLM wrapping for external OpenAI models
try:
    from google.adk.models.lite_llm import LiteLlm
except ImportError:
    LiteLlm = None

_LLM_MODEL = (
    LiteLlm(model=MODEL_ID) if LiteLlm is not None and MODEL_ID.startswith("openai/") else MODEL_ID
)

# --------------------------------------------------------------------------- #
# Build tools
# --------------------------------------------------------------------------- #
loan_api_tools = load_loan_calculator_api_tools()

# Augment instruction with a dynamic list of calculator endpoints so the LLM
# understands when to call each generated tool.
if loan_api_tools:
    _tool_listing = "\n\nAvailable calculator endpoints:\n" + "\n".join(
        f"• {t.name} – {getattr(t, 'description', '')}" for t in loan_api_tools
    )
    AGENT_INSTRUCTION_EXTENDED = AGENT_INSTRUCTION + _tool_listing
else:
    AGENT_INSTRUCTION_EXTENDED = AGENT_INSTRUCTION

# --------------------------------------------------------------------------- #
# Root agent – this is what the ADK CLI discovers.
# --------------------------------------------------------------------------- #
root_agent = Agent(
    name=APP_NAME,
    model=_LLM_MODEL,
    description=(
        "A mortgage advisor that provides clear, concise guidance on mortgage "
        "options, eligibility, and application steps."
    ),
    instruction=AGENT_INSTRUCTION_EXTENDED,
    tools=[
        store_state_tool,
        search_bank_docs,
        list_loan_tracks,
        *loan_api_tools,
    ],
    output_key="user:last_advice",
)
</source>

mortgage_concierge/tools/store_state.py
<source>
"""
Tool to update the tool's context state with new key‑value pairs.

It writes borrower profile data under the *namespaced* key defined in
`mortgage_concierge.shared_libraries.constants.PROFILE_KEY` (`user:borrower_profile`)
to avoid clashing with other state entries.
"""
from __future__ import annotations

import logging
import typing

from google.adk.tools import ToolContext, FunctionTool

from mortgage_concierge.shared_libraries.constants import PROFILE_KEY

logger = logging.getLogger(__name__)


def _store_state_tool_impl(
    state: dict[str, typing.Any], tool_context: ToolContext
) -> dict[str, str]:
    """
    Merge the provided dictionary into the existing borrower profile.

    Args:
        state: A dictionary of profile fields gathered from the user.
        tool_context: The ADK ToolContext.

    Returns:
        dict: Standard status wrapper.
    """
    try:
        if not isinstance(state, dict):
            raise TypeError("state must be a JSON object/dict")

        # Retrieve existing profile (or empty) from the session state.
        existing: dict[str, typing.Any] = tool_context.state.get(PROFILE_KEY, {})
        merged = {**existing, **state}

        tool_context.state[PROFILE_KEY] = merged
        return {"status": "success", "result": merged}
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to store state: %s", exc)
        return {"status": "error", "error_message": str(exc)}


_store_state_tool_impl.__name__ = "store_state_tool"
store_state_tool = FunctionTool(_store_state_tool_impl)
</source>

mortgage_concierge/tools/bank_docs.py
<source>
"""
Tool for searching ingested bank policy documents in memory.
"""
from __future__ import annotations

import os

from google.adk.tools import FunctionTool, ToolContext

from mortgage_concierge.shared_libraries.memory_store import memory_service

# ---------------------------------------------------------------------------- #
# Implementation
# ---------------------------------------------------------------------------- #
def _search_bank_docs_impl(query: str, tool_context: ToolContext) -> dict:
    """Search the ingested bank documents in `memory_service`.

    Args:
        query: The search string.
        tool_context: The ADK tool context (unused but kept for parity).

    Returns:
        dict: Standardised response with `status` + (`result` or `error_message`)
    """
    try:
        # Search documents ingested under the 'system' user
        response = memory_service.search_memory(
            app_name="mortgage_advisor",
            user_id="system",
            query=query,
        )
        # Build results from SearchMemoryResponse.memories (MemoryResult items)
        results: list[dict[str, str]] = []
        for mem in getattr(response, "memories", []):
            session_id = getattr(mem, "session_id", "unknown")
            for ev in getattr(mem, "events", []):
                snippet = ""
                if ev.content and ev.content.parts:
                    text = "".join(
                        part.text
                        for part in ev.content.parts
                        if hasattr(part, "text") and part.text
                    )
                    snippet = text[:200]
                results.append({"file": session_id, "snippet": snippet})
        return {"status": "success", "result": results}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error_message": f"Memory search failed: {exc}"}  # noqa: TRY003


_search_bank_docs_impl.__name__ = "search_bank_docs"
search_bank_docs = FunctionTool(_search_bank_docs_impl)
</source>

mortgage_concierge/tools/loan_tracks.py
<source>
"""
Tool for listing available loan track options from a JSON file.
"""
from __future__ import annotations

import json
import os

from google.adk.tools import FunctionTool, ToolContext

# Path to the loan tracks JSON file (configurable via env)
LOAN_TRACKS_PATH = os.getenv(
    "LOAN_TRACKS_PATH",
    os.path.join(os.getcwd(), "_knowledge_base", "loan_tracks.json"),
)


def _list_loan_tracks_impl(tool_context: ToolContext) -> dict:
    """
    Return the list of loan tracks as a status‑wrapped dictionary.
    """
    try:
        if not os.path.isfile(LOAN_TRACKS_PATH):
            raise FileNotFoundError(f"Loan tracks file not found: {LOAN_TRACKS_PATH}")

        with open(LOAN_TRACKS_PATH, encoding="utf-8") as fp:
            data = json.load(fp)

        return {"status": "success", "result": data}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error_message": str(exc)}


_list_loan_tracks_impl.__name__ = "list_loan_tracks"
list_loan_tracks = FunctionTool(_list_loan_tracks_impl)
</source>

mortgage_concierge/tools/loan_calculator.py
<source>
import os
import logging
import json
import requests
from pathlib import Path
from google.adk.tools import FunctionTool, ToolContext

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Helper
# --------------------------------------------------------------------------- #
def _wrap_success(payload: dict | list | str | float | int) -> dict:
    return {"status": "success", "result": payload}


def _wrap_error(exc: Exception | str) -> dict:
    return {"status": "error", "error_message": str(exc)}


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #
def _loan_calculator_impl(amount: float, termYears: int, tool_context: ToolContext) -> dict:
    """
    Calculate loan details.

    Returns:
        dict: {"status": "success", "result": <calculation dict>} or
              {"status": "error", "error_message": <msg>}
    """
    api_url = os.getenv("LOAN_CALCULATOR_API_URL")
    if api_url:
        payload = {"amount": amount, "termYears": termYears}
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            return _wrap_success(response.json())
        except Exception as exc:  # noqa: BLE001
            logger.exception("External calculator call failed")
            return _wrap_error(f"Calculator service error: {exc}")

    # Fallback: load mock JSON
    try:
        mock_file = Path(__file__).resolve().parents[2] / "tests" / "unit" / "data" / "calculator_mock.json"
        with open(mock_file, "r") as fp:
            data = json.load(fp)
        return _wrap_success(data)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to load mock JSON")
        return _wrap_error(f"Mock data load error: {exc}")


_loan_calculator_impl.__name__ = "loan_calculator"
loan_calculator = FunctionTool(_loan_calculator_impl)


def _recalculate_rate_impl(amount: float, termYears: int, overrideRate: float, tool_context: ToolContext) -> dict:
    """
    Recalculate loan payment based on an override interest rate.
    """
    api_url = os.getenv("RECALC_RATE_API_URL")
    payload = {"amount": amount, "termYears": termYears, "overrideRate": overrideRate}
    if api_url:
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            return _wrap_success(response.json())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Recalculate rate call failed")
            return _wrap_error(f"Recalculate rate service error: {exc}")

    try:
        mock_file = Path(__file__).resolve().parents[2] / "tests" / "unit" / "data" / "recalc_rate_mock.json"
        with open(mock_file, "r") as fp:
            data = json.load(fp)
        return _wrap_success(data)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to load recalc rate mock JSON")
        return _wrap_error(f"Mock data load error: {exc}")


_recalculate_rate_impl.__name__ = "recalculate_rate"
recalculate_rate = FunctionTool(_recalculate_rate_impl)


def _recalculate_term_impl(amount: float, desiredPayment: float, interestRate: float, tool_context: ToolContext) -> dict:
    """
    Recalculate loan term based on desired monthly payment.
    """
    api_url = os.getenv("RECALC_TERM_API_URL")
    payload = {"amount": amount, "desiredPayment": desiredPayment, "interestRate": interestRate}
    if api_url:
        try:
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            return _wrap_success(response.json())
        except Exception as exc:  # noqa: BLE001
            logger.exception("Recalculate term call failed")
            return _wrap_error(f"Recalculate term service error: {exc}")

    try:
        mock_file = Path(__file__).resolve().parents[2] / "tests" / "unit" / "data" / "recalc_term_mock.json"
        with open(mock_file, "r") as fp:
            data = json.load(fp)
        return _wrap_success(data)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Failed to load recalc term mock JSON")
        return _wrap_error(f"Mock data load error: {exc}")


_recalculate_term_impl.__name__ = "recalculate_term"
recalculate_term = FunctionTool(_recalculate_term_impl)
</source>

mortgage_concierge/shared_libraries/constants.py
<source>
"""
Constants for state keys and other shared values.
"""

# Namespaced key for the borrower profile stored in session.state
PROFILE_KEY = "user:borrower_profile"
"""
Key under which the BorrowerProfile is stored in session.state.
"""
</source>

mortgage_concierge/prompt.py
<source>
"""
Instruction template for the Mortgage Advisor Agent (Phase 1: Borrower Profiling).
"""
from mortgage_concierge.shared_libraries.constants import PROFILE_KEY

AGENT_INSTRUCTION = f"""
You are a professional mortgage advisor.

Phase 1: Collect borrower profile information step by step.
Persist all collected fields under the namespaced key "{PROFILE_KEY}" in session state.

Ask the user for the following details in order:
  1. Estimated property value
  2. Planned down payment amount
  3. Gross annual income
  4. Total monthly debt payments
  5. Credit score range (poor, fair, good, very_good, excellent)
  6. Risk tolerance (low, medium, high)

After each answer, call the 'store_state_tool' tool with:
    {{ "state": {{ "<field_name>": <value> }} }}

Examples:
    store_state_tool(state={{"estimated_property_value": 750000}})
    store_state_tool(state={{"risk_tolerance": "medium"}})

When you need factual details about the bank's lending policies or requirements,
call:
  • search_bank_docs(query) — returns matching snippets from policy documents.

When you want to present the user with available loan repayment tracks and options,
call:
  • list_loan_tracks() — returns the full list of loan track configurations.

Use these tools to ground your responses in actual bank documentation and
available loan products.

Only proceed to Phase 2 (loan eligibility & options) after all profile fields
are confirmed with the user.
"""
</source>

mortgage_concierge/tools/openapi_tools.py
<source>
"""
Generate RestApiTool instances from the mortgage calculator OpenAPI spec.
"""
from __future__ import annotations

import os
from pathlib import Path

import yaml
from google.adk.tools.openapi_tool.openapi_spec_parser.openapi_toolset import OpenAPIToolset


def load_loan_calculator_api_tools():
    """
    Return a list of RestApiTool instances generated from the loan calculator
    OpenAPI specification.
    """
    spec_file = Path(__file__).resolve().parents[1] / "openapi" / "loan_calculator.yaml"
    if not spec_file.exists():
        raise FileNotFoundError(
            f"OpenAPI spec not found at {spec_file}. Ensure the file exists."
        )

    with open(spec_file, "r", encoding="utf-8") as fp:
        spec_dict = yaml.safe_load(fp)

    # Optionally override *all* server URLs via env var without assuming
    # the structure of `servers`.
    base_url = os.getenv("LOAN_CALCULATOR_API_BASE_URL")
    if base_url:
        for server in spec_dict.get("servers", []):
            server["url"] = base_url

    # Create the toolset from a dict (preferred path per ADK docs)
    toolset = OpenAPIToolset(spec_dict=spec_dict)

    return toolset.get_tools()
</source>
