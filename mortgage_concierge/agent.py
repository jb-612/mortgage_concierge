import os
from dotenv import load_dotenv

# ADK imports
from google.adk.agents import Agent

# Local imports
from mortgage_concierge.prompt import AGENT_INSTRUCTION

# Load environment variables early
load_dotenv()

# Configuration
MODEL_ID = os.getenv("MORTGAGE_MODEL", os.getenv("OPENAI_MODEL", "openai/gpt-4.1-nano"))
APP_NAME = os.getenv("APP_NAME", "mortgage_advisor")

# Optional LiteLLM wrapping for external OpenAI models
try:
    from google.adk.models.lite_llm import LiteLlm
except ImportError:  # LiteLLM not installed – fall back to raw model string
    LiteLlm = None

# Determine model argument: wrap with LiteLlm if specifying an OpenAI provider
_LLM_MODEL = MODEL_ID
if LiteLlm is not None and isinstance(MODEL_ID, str) and MODEL_ID.startswith("openai/"):
    _LLM_MODEL = LiteLlm(model=MODEL_ID)

# Tools
from mortgage_concierge.tools.bank_docs import search_bank_docs
from mortgage_concierge.tools.loan_tracks import list_loan_tracks
from mortgage_concierge.tools.store_state import store_state_tool
from mortgage_concierge.tools.openapi_tools import load_loan_calculator_api_tools

# Generate OpenAPI-based tools for loan calculator endpoints
loan_api_tools = load_loan_calculator_api_tools()

# Root ADK agent (imported by ADK CLI / frameworks)
root_agent = Agent(
    name=APP_NAME,
    model=_LLM_MODEL,
    description=(
        "A mortgage advisor that provides clear, concise guidance on mortgage "
        "options, eligibility, and application steps."
    ),
    instruction=AGENT_INSTRUCTION,
    tools=[
        store_state_tool,
        search_bank_docs,   # Tool for searching bank policy documents
        list_loan_tracks,
        *loan_api_tools,    # OpenAPI-generated REST API tools
    ],
    output_key="last_advice",
)
