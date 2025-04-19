import os
from dotenv import load_dotenv

# ADK imports
from google.adk.agents import Agent
# The Agent can accept a model ID string directly; we avoid LiteLlm dependency

# No direct Runner or session service here; ADK CLI bootstraps runner

# Local imports
from mortgage_concierge.prompt import AGENT_INSTRUCTION

# Load environment variables
load_dotenv()

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
from mortgage_concierge.tools.bank_docs import search_bank_docs
from mortgage_concierge.tools.loan_tracks import list_loan_tracks

root_agent = Agent(
    name=APP_NAME,
    model=_LLM_MODEL,
    description="A mortgage advisor that provides clear, concise guidance on mortgage options, eligibility, and application steps.",
    instruction=AGENT_INSTRUCTION,
    tools=[
        search_bank_docs,
        list_loan_tracks,
    ],  # Tools for factual grounding and loan track listing
    output_key="last_advice",
)