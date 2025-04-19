import os
from dotenv import load_dotenv

# ADK imports
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

# No direct Runner or session service here; ADK CLI bootstraps runner

# Local imports
from mortgage_concierge.prompt import AGENT_INSTRUCTION

# Load environment variables
load_dotenv()

# Configuration
MODEL_ID = os.getenv("MORTGAGE_MODEL", os.getenv("OPENAI_MODEL", "openai/gpt-4.1-nano"))
APP_NAME = os.getenv("APP_NAME", "mortgage_advisor")

# Define the root ADK agent; ADK CLI will wrap this into a runner
root_agent = Agent(
    name=APP_NAME,
    model=LiteLlm(model=MODEL_ID),
    description="A mortgage advisor that provides clear, concise guidance on mortgage options, eligibility, and application steps.",
    instruction=AGENT_INSTRUCTION,
    tools=[],  # Memory tool to be added in Phase 1
    output_key="last_advice",
)