import os
from dotenv import load_dotenv

# ADK imports
from google.adk.agents import Agent

# The Agent can accept a model ID string directly; we avoid LiteLlm dependency

# No direct Runner or session service here; ADK CLI bootstraps runner

# Local imports
from mortgage_concierge.prompt import AGENT_INSTRUCTION
from mortgage_concierge.shared_libraries.memory_ingestion import ingest_bank_docs_to_memory


# Load environment variables
load_dotenv()

# Ingest bank documents at agent startup
ingest_bank_docs_to_memory()

# Configuration
MODEL_ID = os.getenv("MORTGAGE_MODEL", os.getenv("OPENAI_MODEL", "openai/gpt-4.1-nano"))
APP_NAME = os.getenv("APP_NAME", "mortgage_advisor")

# Optional LiteLLM wrapping for external OpenAI models
try:
    from google.adk.models.lite_llm import LiteLlm
except ImportError:
    LiteLlm = None

# Determine model argument: wrap with LiteLlm if specifying an OpenAI provider
_LLM_MODEL = MODEL_ID
if LiteLlm is not None and isinstance(MODEL_ID, str) and MODEL_ID.startswith("openai/"):
    _LLM_MODEL = LiteLlm(model=MODEL_ID)

# Define the root ADK agent; ADK CLI will wrap this into a runner
# from mortgage_concierge.tools.bank_docs_simple_txt import search_bank_docs_txt # simple text search
from mortgage_concierge.tools.bank_docs import search_bank_docs
from mortgage_concierge.tools.loan_tracks import list_loan_tracks
from mortgage_concierge.tools.store_state import store_state_tool
from mortgage_concierge.tools.loan_calculator import loan_calculator



root_agent = Agent(
    name=APP_NAME,
    model=_LLM_MODEL,
    description="A mortgage advisor that provides clear, concise guidance on mortgage options, eligibility, and application steps.",
    instruction=AGENT_INSTRUCTION,
    tools=[
        store_state_tool,  
        search_bank_docs,   # Tool for searching bank policy documents
        list_loan_tracks,
        loan_calculator,    # Tool for loan calculations
    ],  # Tools for factual grounding and loan track listing
    output_key="last_advice",
)