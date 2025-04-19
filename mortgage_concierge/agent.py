import os
from dotenv import load_dotenv

# ADK imports
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.services import InMemorySessionService
from google.adk.runners import Runner

# Local imports
from prompt import AGENT_INSTRUCTION

# Load environment variables
load_dotenv()

# Configuration
MODEL_ID = os.getenv("MORTGAGE_MODEL", os.getenv("OPENAI_MODEL", "openai/gpt-4.1-nano"))
APP_NAME = os.getenv("APP_NAME", "mortgage_advisor")

# Initialize session service, agent, and runner
session_service = InMemorySessionService()
agent = Agent(
    name=APP_NAME,
    model=LiteLlm(model=MODEL_ID),
    description="A mortgage advisor that provides clear, concise guidance on mortgage options, eligibility, and application steps.",
    instruction=AGENT_INSTRUCTION,
    tools=[],  # Add memory tool in Phase 1
    output_key="last_advice",
)
runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)