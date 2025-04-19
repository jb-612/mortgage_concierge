Okay, let's convert the Google Colab notebook into a well-structured, multi-file VS Code project following clean code best practices.

**Project Structure:**

```
weather-bot-adk/
├── .vscode/
│   └── settings.json        # Optional: VSCode specific settings
├── agents/
│   ├── __init__.py
│   ├── base_models.py       # Define model constants here
│   ├── farewell_agent.py
│   ├── greeting_agent.py
│   ├── root_agent.py
│   └── weather_agent.py
├── callbacks/
│   ├── __init__.py
│   └── guardrails.py        # Contains both before_model and before_tool callbacks
├── tools/
│   ├── __init__.py
│   ├── conversation.py      # say_hello, say_goodbye
│   └── weather.py           # get_weather, get_weather_stateful
├── utils/
│   ├── __init__.py
│   └── interaction.py       # call_agent_async helper
├── .env.example             # Example environment variables file
├── .gitignore
├── main.py                  # Main execution script, orchestrates the steps
├── config.py                # Handles API key loading and initial setup
└── requirements.txt         # Project dependencies
```

**File Contents:**

**1. `requirements.txt`**

```txt
google-adk
litellm
python-dotenv
google-generativeai # Explicitly add if needed for types, ADK usually includes it
```

**2. `.gitignore`**

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
*.env
.env

# VSCode
.vscode/

# Other
*.log
*.tmp
```

**3. `.env.example`**

```dotenv
# Rename this file to .env and add your actual API keys
# Get from Google AI Studio: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"

# Get from OpenAI Platform: https://platform.openai.com/api-keys
OPENAI_API_KEY="YOUR_OPENAI_API_KEY"

# Get from Anthropic Console: https://console.anthropic.com/settings/keys
ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
```

**4. `config.py`**

```python
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Key Configuration ---

def get_api_key(env_var_name: str) -> str | None:
    """Safely retrieves an API key from environment variables."""
    key = os.environ.get(env_var_name)
    if not key or key == f"YOUR_{env_var_name}":
        logging.warning(f"Environment variable '{env_var_name}' not set or using placeholder.")
        return None
    return key

GOOGLE_API_KEY = get_api_key("GOOGLE_API_KEY")
OPENAI_API_KEY = get_api_key("OPENAI_API_KEY")
ANTHROPIC_API_KEY = get_api_key("ANTHROPIC_API_KEY")

# Configure ADK environment variables
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False" # Use API keys directly

def check_api_keys():
    """Prints the status of the loaded API keys."""
    print("--- API Key Status ---")
    print(f"Google API Key set: {'Yes' if GOOGLE_API_KEY else 'No (Set in .env!)'}")
    print(f"OpenAI API Key set: {'Yes' if OPENAI_API_KEY else 'No (Set in .env!)'}")
    print(f"Anthropic API Key set: {'Yes' if ANTHROPIC_API_KEY else 'No (Set in .env!)'}")
    print("----------------------")
    # Set keys in environment if they were successfully retrieved, needed by LiteLLM/ADK
    if GOOGLE_API_KEY: os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
    if OPENAI_API_KEY: os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    if ANTHROPIC_API_KEY: os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY


# --- Application Constants ---
APP_NAME = "weather_tutorial_adk"

# --- Logging and Warnings ---
def setup_logging():
    """Configures basic logging."""
    logging.basicConfig(level=logging.ERROR) # Default to ERROR to avoid verbose ADK logs
    # Use logging.INFO for more details during development if needed
    # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Suppress specific noisy warnings if necessary
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module='google.protobuf')
    warnings.filterwarnings("ignore") # Generally ignore warnings for cleaner tutorial output


# --- Initial Setup Call ---
setup_logging()
# check_api_keys() # Can be called from main.py after setup

```

**5. `agents/__init__.py`** (Empty file)

**6. `agents/base_models.py`**

```python
# Define Model Constants for easier use and consistency

# Gemini Models (via Google Generative AI directly)
MODEL_GEMINI_1_5_FLASH = "gemini-1.5-flash-latest" # Check latest naming convention if needed
MODEL_GEMINI_1_5_PRO = "gemini-1.5-pro-latest"

# Other Models (via LiteLLM)
# Note: Specific model names might change. Refer to LiteLLM or provider docs.
MODEL_GPT_4O = "openai/gpt-4o"
MODEL_CLAUDE_3_SONNET = "anthropic/claude-3-sonnet-20240229"
MODEL_CLAUDE_3_HAIKU = "anthropic/claude-3-haiku-20240307"

# Default models for different agent types (can be overridden)
DEFAULT_WEATHER_MODEL = MODEL_GEMINI_1_5_PRO
DEFAULT_GREETING_MODEL = MODEL_GEMINI_1_5_FLASH # Use cheaper model for simple tasks
DEFAULT_FAREWELL_MODEL = MODEL_GEMINI_1_5_FLASH
DEFAULT_ROOT_MODEL = MODEL_GEMINI_1_5_PRO # Root needs good reasoning for delegation

```

**7. `agents/weather_agent.py`**

```python
import logging
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from tools.weather import get_weather, get_weather_stateful # Assuming tools are structured
from agents.base_models import (
    MODEL_GEMINI_1_5_PRO,
    MODEL_GPT_4O,
    MODEL_CLAUDE_3_SONNET,
    DEFAULT_WEATHER_MODEL
)
import config # To check API keys

# Agent using the default (Gemini) model
def create_weather_agent_v1() -> Agent | None:
    """Creates the basic weather agent (v1) using the default model."""
    if not config.GOOGLE_API_KEY:
        logging.error("Google API Key missing. Cannot create default weather agent.")
        return None
    try:
        agent = Agent(
            name="weather_agent_v1",
            model=DEFAULT_WEATHER_MODEL,
            description="Provides weather information for specific cities.",
            instruction="You are a helpful weather assistant. Your primary goal is to provide current weather reports. "
                        "When the user asks for the weather in a specific city, "
                        "you MUST use the 'get_weather' tool to find the information. "
                        "Analyze the tool's response: if the status is 'error', inform the user politely about the error message. "
                        "If the status is 'success', present the weather 'report' clearly and concisely to the user. "
                        "Only use the tool when a city is mentioned for a weather request.",
            tools=[get_weather],
        )
        logging.info(f"Agent '{agent.name}' created using model '{DEFAULT_WEATHER_MODEL}'.")
        return agent
    except Exception as e:
        logging.error(f"Failed to create weather_agent_v1: {e}")
        return None


# Agent using GPT-4o via LiteLlm
def create_weather_agent_gpt() -> Agent | None:
    """Creates the weather agent using GPT-4o via LiteLLM."""
    if not config.OPENAI_API_KEY:
        logging.error("OpenAI API Key missing. Cannot create GPT weather agent.")
        return None
    try:
        agent = Agent(
            name="weather_agent_gpt",
            model=LiteLlm(model=MODEL_GPT_4O),
            description="Provides weather information (using GPT-4o).",
            instruction="You are a helpful weather assistant powered by GPT-4o. "
                        "Use the 'get_weather' tool for city weather requests. "
                        "Clearly present successful reports or polite error messages based on the tool's output status.",
            tools=[get_weather],
        )
        logging.info(f"Agent '{agent.name}' created using model '{MODEL_GPT_4O}'.")
        return agent
    except Exception as e:
        logging.error(f"Could not create GPT agent '{MODEL_GPT_4O}'. Check API Key and model name. Error: {e}")
        return None

# Agent using Claude Sonnet via LiteLlm
def create_weather_agent_claude() -> Agent | None:
    """Creates the weather agent using Claude Sonnet via LiteLLM."""
    if not config.ANTHROPIC_API_KEY:
        logging.error("Anthropic API Key missing. Cannot create Claude weather agent.")
        return None
    try:
        agent = Agent(
            name="weather_agent_claude",
            model=LiteLlm(model=MODEL_CLAUDE_3_SONNET),
            description="Provides weather information (using Claude Sonnet).",
            instruction="You are a helpful weather assistant powered by Claude Sonnet. "
                        "Use the 'get_weather' tool for city weather requests. "
                        "Analyze the tool's dictionary output ('status', 'report'/'error_message'). "
                        "Clearly present successful reports or polite error messages.",
            tools=[get_weather],
        )
        logging.info(f"Agent '{agent.name}' created using model '{MODEL_CLAUDE_3_SONNET}'.")
        return agent
    except Exception as e:
        logging.error(f"Could not create Claude agent '{MODEL_CLAUDE_3_SONNET}'. Check API Key and model name. Error: {e}")
        return None

# Note: The stateful tool (`get_weather_stateful`) will be used by the root agent later,
# not directly by these initial weather agents.
```

**8. `agents/greeting_agent.py`**

```python
import logging
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # Example using LiteLLM for sub-agent
from tools.conversation import say_hello
from agents.base_models import DEFAULT_GREETING_MODEL, MODEL_GPT_4O # Example: Using GPT or default
import config

def create_greeting_agent() -> Agent | None:
    """Creates the specialized greeting agent."""
    # Decide which model to use (e.g., default Gemini or GPT if available)
    # model_to_use = DEFAULT_GREETING_MODEL
    # model_provider = "Google"
    # requires_key = config.GOOGLE_API_KEY

    # Example: Prioritize GPT if available
    model_to_use_obj = None
    model_name_log = ""
    if config.OPENAI_API_KEY:
        model_to_use_obj = LiteLlm(model=MODEL_GPT_4O)
        model_name_log = MODEL_GPT_4O
        logging.info("Using GPT-4o for Greeting Agent.")
    elif config.GOOGLE_API_KEY:
         model_to_use_obj = DEFAULT_GREETING_MODEL # Use default Gemini Flash if GPT not available
         model_name_log = DEFAULT_GREETING_MODEL
         logging.info("Using Default Gemini Flash for Greeting Agent.")
    else:
        logging.error("No suitable API key found for Greeting Agent (Google or OpenAI).")
        return None

    try:
        agent = Agent(
            name="greeting_agent",
            model=model_to_use_obj,
            instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
                        "Use the 'say_hello' tool to generate the greeting. "
                        "If the user provides their name, make sure to pass it to the tool. "
                        "Do not engage in any other conversation or tasks.",
            description="Handles simple greetings and hellos using the 'say_hello' tool.", # Crucial for delegation
            tools=[say_hello],
        )
        logging.info(f"✅ Agent '{agent.name}' created using model '{model_name_log}'.")
        return agent
    except Exception as e:
        logging.error(f"❌ Could not create Greeting agent. Check API Key/Model ({model_name_log}). Error: {e}")
        return None

```

**9. `agents/farewell_agent.py`**

```python
import logging
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # Example using LiteLLM for sub-agent
from tools.conversation import say_goodbye
from agents.base_models import DEFAULT_FAREWELL_MODEL, MODEL_GPT_4O # Example: Using GPT or default
import config

def create_farewell_agent() -> Agent | None:
    """Creates the specialized farewell agent."""
    # Decide which model to use (similar logic as greeting agent)
    model_to_use_obj = None
    model_name_log = ""
    if config.OPENAI_API_KEY: # Example: Prioritize GPT if available
        model_to_use_obj = LiteLlm(model=MODEL_GPT_4O)
        model_name_log = MODEL_GPT_4O
        logging.info("Using GPT-4o for Farewell Agent.")
    elif config.GOOGLE_API_KEY:
         model_to_use_obj = DEFAULT_FAREWELL_MODEL # Use default Gemini Flash if GPT not available
         model_name_log = DEFAULT_FAREWELL_MODEL
         logging.info("Using Default Gemini Flash for Farewell Agent.")
    else:
        logging.error("No suitable API key found for Farewell Agent (Google or OpenAI).")
        return None

    try:
        agent = Agent(
            name="farewell_agent",
            model=model_to_use_obj,
            instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
                        "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
                        "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
                        "Do not perform any other actions.",
            description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.", # Crucial for delegation
            tools=[say_goodbye],
        )
        logging.info(f"✅ Agent '{agent.name}' created using model '{model_name_log}'.")
        return agent
    except Exception as e:
        logging.error(f"❌ Could not create Farewell agent. Check API Key/Model ({model_name_log}). Error: {e}")
        return None

```

**10. `agents/root_agent.py`**

```python
import logging
from typing import List, Callable, Optional, Dict, Any
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm # If needed for root
from agents.base_models import DEFAULT_ROOT_MODEL
from tools.weather import get_weather, get_weather_stateful
from callbacks.guardrails import block_keyword_guardrail, block_paris_tool_guardrail
import config

# --- Base Root Agent for Delegation (Step 3) ---
def create_root_agent_team(greeting_agent: Agent, farewell_agent: Agent) -> Agent | None:
    """Creates the root agent configured for basic delegation (v2)."""
    if not config.GOOGLE_API_KEY: # Assuming root uses Google by default
         logging.error("Google API Key missing. Cannot create Root Agent Team.")
         return None

    sub_agents = [agent for agent in [greeting_agent, farewell_agent] if agent]
    if len(sub_agents) != 2:
        logging.warning("Root agent team created with missing sub-agents.")
        # Decide if you want to proceed with missing agents or return None
        # return None

    try:
        agent = Agent(
            name="weather_agent_v2_team",
            model=DEFAULT_ROOT_MODEL,
            description="The main coordinator agent. Handles weather requests and delegates greetings/farewells.",
            instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to provide weather information. "
                        "Use the 'get_weather' tool ONLY for specific weather requests (e.g., 'weather in London'). "
                        "You have specialized sub-agents: "
                        "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
                        "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
                        "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
                        "If it's a weather request, handle it yourself using 'get_weather'. "
                        "For anything else, respond appropriately or state you cannot handle it.",
            tools=[get_weather],
            sub_agents=sub_agents,
        )
        logging.info(f"✅ Root Agent '{agent.name}' created with sub-agents: {[sa.name for sa in sub_agents]}")
        return agent
    except Exception as e:
        logging.error(f"❌ Failed to create root_agent_team: {e}")
        return None


# --- Stateful Root Agent (Step 4) ---
def create_root_agent_stateful(greeting_agent: Agent, farewell_agent: Agent) -> Agent | None:
    """Creates the stateful root agent using the stateful tool and output_key (v4)."""
    if not config.GOOGLE_API_KEY: # Assuming root uses Google by default
         logging.error("Google API Key missing. Cannot create Stateful Root Agent.")
         return None

    sub_agents = [agent for agent in [greeting_agent, farewell_agent] if agent]
    if len(sub_agents) != 2:
        logging.warning("Stateful root agent created with missing sub-agents.")
        # return None # Optional: enforce sub-agents

    try:
        agent = Agent(
            name="weather_agent_v4_stateful",
            model=DEFAULT_ROOT_MODEL,
            description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
            instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
                        "The tool will format the temperature based on user preference stored in state. "
                        "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                        "Handle only weather requests, greetings, and farewells.",
            tools=[get_weather_stateful], # Use the state-aware tool
            sub_agents=sub_agents,
            output_key="last_weather_report" # Auto-save agent's final weather response
        )
        logging.info(f"✅ Root Agent '{agent.name}' created using stateful tool and output_key.")
        return agent
    except Exception as e:
        logging.error(f"❌ Failed to create root_agent_stateful: {e}")
        return None

# --- Root Agent with Model Guardrail (Step 5) ---
def create_root_agent_with_model_guardrail(greeting_agent: Agent, farewell_agent: Agent) -> Agent | None:
    """Creates the root agent with the before_model_callback guardrail (v5)."""
    if not config.GOOGLE_API_KEY:
         logging.error("Google API Key missing. Cannot create Model Guardrail Root Agent.")
         return None

    sub_agents = [agent for agent in [greeting_agent, farewell_agent] if agent]
    if len(sub_agents) != 2:
        logging.warning("Model guardrail root agent created with missing sub-agents.")
        # return None

    try:
        agent = Agent(
            name="weather_agent_v5_model_guardrail",
            model=DEFAULT_ROOT_MODEL,
            description="Main agent: Handles weather, delegates greetings/farewells, includes input keyword guardrail.",
            instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                        "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                        "Handle only weather requests, greetings, and farewells.",
            tools=[get_weather_stateful], # Still uses stateful tool
            sub_agents=sub_agents,
            output_key="last_weather_report",
            before_model_callback=block_keyword_guardrail # Assign the guardrail
        )
        logging.info(f"✅ Root Agent '{agent.name}' created with before_model_callback.")
        return agent
    except Exception as e:
        logging.error(f"❌ Failed to create root_agent_with_model_guardrail: {e}")
        return None


# --- Root Agent with Tool Guardrail (Step 6) ---
def create_root_agent_with_tool_guardrail(greeting_agent: Agent, farewell_agent: Agent) -> Agent | None:
    """Creates the root agent with both before_model and before_tool callbacks (v6)."""
    if not config.GOOGLE_API_KEY:
         logging.error("Google API Key missing. Cannot create Tool Guardrail Root Agent.")
         return None

    sub_agents = [agent for agent in [greeting_agent, farewell_agent] if agent]
    if len(sub_agents) != 2:
        logging.warning("Tool guardrail root agent created with missing sub-agents.")
        # return None

    try:
        agent = Agent(
            name="weather_agent_v6_tool_guardrail",
            model=DEFAULT_ROOT_MODEL,
            description="Main agent: Handles weather, delegates, includes input AND tool guardrails.",
            instruction="You are the main Weather Agent. Provide weather using 'get_weather_stateful'. "
                        "Delegate greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
                        "Handle only weather, greetings, and farewells.",
            tools=[get_weather_stateful],
            sub_agents=sub_agents,
            output_key="last_weather_report",
            before_model_callback=block_keyword_guardrail, # Keep model guardrail
            before_tool_callback=block_paris_tool_guardrail # Add tool guardrail
        )
        logging.info(f"✅ Root Agent '{agent.name}' created with BOTH callbacks.")
        return agent
    except Exception as e:
        logging.error(f"❌ Failed to create root_agent_with_tool_guardrail: {e}")
        return None
```

**11. `tools/__init__.py`** (Empty file)

**12. `tools/weather.py`**

```python
import logging
from google.adk.tools.tool_context import ToolContext

# Best Practice: Use logging instead of print for tool execution tracking
logger = logging.getLogger(__name__)

# --- Mock Weather Data ---
MOCK_WEATHER_DB_CELSIUS = {
    "newyork": {"temp_c": 25, "condition": "sunny"},
    "london": {"temp_c": 15, "condition": "cloudy"},
    "tokyo": {"temp_c": 18, "condition": "light rain"},
}

# --- Basic Weather Tool (Step 1) ---
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city (basic mock).

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    logger.info(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    # Use Celsius data directly for the simple report
    if city_normalized in MOCK_WEATHER_DB_CELSIUS:
        data = MOCK_WEATHER_DB_CELSIUS[city_normalized]
        report = f"The weather in {city.capitalize()} is {data['condition']} with a temperature of {data['temp_c']}°C."
        return {"status": "success", "report": report}
    else:
        logger.warning(f"Tool: get_weather - City '{city}' not found in mock DB.")
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


# --- State-Aware Weather Tool (Step 4) ---
def get_weather_stateful(city: str, tool_context: ToolContext) -> dict:
    """Retrieves weather, converting temp unit based on session state preference.

    Args:
        city (str): The name of the city.
        tool_context (ToolContext): Provides access to session state.

    Returns:
        dict: Weather report dictionary with 'status' and 'report'/'error_message'.
              Temperature unit depends on 'user_preference_temperature_unit' in state.
    """
    logger.info(f"--- Tool: get_weather_stateful called for {city} in agent {tool_context.agent_name} ---")

    # Read preference from state, defaulting to Celsius
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")
    logger.info(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    if city_normalized in MOCK_WEATHER_DB_CELSIUS:
        data = MOCK_WEATHER_DB_CELSIUS[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        # Format temperature based on state preference
        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32 # Calculate Fahrenheit
            temp_unit = "°F"
        else: # Default to Celsius
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        logger.info(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        # Write back to state (Example: last city checked)
        try:
            tool_context.state["last_city_checked_stateful"] = city
            logger.info(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")
        except Exception as e:
            logger.error(f"--- Tool: Failed to write to state: {e} ---")


        return result
    else:
        logger.warning(f"Tool: get_weather_stateful - City '{city}' not found.")
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        return {"status": "error", "error_message": error_msg}

```

**13. `tools/conversation.py`**

```python
import logging

logger = logging.getLogger(__name__)

def say_hello(name: str = "there") -> str:
    """Provides a simple greeting, optionally addressing the user by name.

    Args:
        name (str, optional): The name of the person to greet. Defaults to "there".

    Returns:
        str: A friendly greeting message.
    """
    logger.info(f"--- Tool: say_hello called with name: {name} ---")
    return f"Hello, {name}!"

def say_goodbye() -> str:
    """Provides a simple farewell message to conclude the conversation."""
    logger.info(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

```

**14. `callbacks/__init__.py`** (Empty file)

**15. `callbacks/guardrails.py`**

```python
import logging
from typing import Optional, Dict, Any
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.generativeai import types # For creating response content

logger = logging.getLogger(__name__)

# --- Before Model Callback (Step 5) ---
def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """
    Inspects the latest user message for 'BLOCK'. If found, blocks the LLM call
    and returns a predefined LlmResponse. Otherwise, returns None to proceed.
    """
    agent_name = callback_context.agent_name
    logger.info(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    last_user_message_text = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                part = content.parts[0]
                if hasattr(part, 'text') and part.text: # Check if Part has text
                    last_user_message_text = part.text
                    break

    logger.info(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---")

    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper():
        logger.warning(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call for {agent_name}! ---")
        try:
            callback_context.state["guardrail_block_keyword_triggered"] = True
            logger.info(f"--- Callback: Set state 'guardrail_block_keyword_triggered': True ---")
        except Exception as e:
             logger.error(f"--- Callback: Failed to write guardrail trigger to state: {e} ---")

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
            )
        )
    else:
        logger.info(f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
        return None


# --- Before Tool Callback (Step 6) ---
def block_paris_tool_guardrail(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    """
    Checks if 'get_weather_stateful' is called for 'Paris'.
    If so, blocks the tool execution and returns a specific error dictionary.
    Otherwise, allows the tool call to proceed by returning None.
    """
    tool_name = tool.name
    agent_name = tool_context.agent_name
    logger.info(f"--- Callback: block_paris_tool_guardrail running for tool '{tool_name}' in agent '{agent_name}' ---")
    logger.info(f"--- Callback: Inspecting args: {args} ---")

    target_tool_name = "get_weather_stateful" # Match the function name
    blocked_city = "paris"

    if tool_name == target_tool_name:
        city_argument = args.get("city", "")
        if city_argument and city_argument.lower() == blocked_city:
            logger.warning(f"--- Callback: Detected blocked city '{city_argument}' for tool {tool_name}. Blocking tool execution! ---")
            try:
                tool_context.state["guardrail_tool_block_triggered"] = True
                logger.info(f"--- Callback: Set state 'guardrail_tool_block_triggered': True ---")
            except Exception as e:
                 logger.error(f"--- Callback: Failed to write tool guardrail trigger to state: {e} ---")


            # Return a dictionary mimicking the tool's error format
            return {
                "status": "error",
                "error_message": f"Policy restriction: Weather checks for '{city_argument.capitalize()}' are currently disabled by a tool guardrail."
            }
        else:
             logger.info(f"--- Callback: City '{city_argument}' is allowed for tool '{tool_name}'. ---")
    else:
        logger.info(f"--- Callback: Tool '{tool_name}' is not the target tool ({target_tool_name}). Allowing. ---")

    logger.info(f"--- Callback: Allowing tool '{tool_name}' to proceed. ---")
    return None # Allow tool execution
```

**16. `utils/__init__.py`** (Empty file)

**17. `utils/interaction.py`**

```python
import logging
from google.generativeai import types
from google.adk.runners import Runner

logger = logging.getLogger(__name__)

async def call_agent_async(
    query: str,
    runner: Runner,
    user_id: str,
    session_id: str
):
    """Sends a query to the specified agent runner and prints the final response."""
    print(f"\n>>> User Query ({user_id}/{session_id}): {query}")

    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response." # Default

    try:
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            # Optional: Log all events for debugging
            # logger.debug(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

            if event.is_final_response():
                if event.content and event.content.parts:
                    part = event.content.parts[0]
                    if hasattr(part, 'text') and part.text:
                         final_response_text = part.text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                # Add more checks for different event types if needed
                break # Stop processing events for this turn

    except Exception as e:
        logger.error(f"Error during agent run for query '{query}': {e}", exc_info=True)
        final_response_text = f"An error occurred: {e}"

    print(f"<<< Agent Response ({runner.agent.name}): {final_response_text}")
    return final_response_text

```

**18. `main.py`**

```python
import asyncio
import logging
import time # For state update timestamp example
from typing import Dict

# --- ADK Imports ---
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner

# --- Project Imports ---
import config # Loads .env, sets up logging
from utils.interaction import call_agent_async
from agents.weather_agent import (
    create_weather_agent_v1,
    create_weather_agent_gpt,
    create_weather_agent_claude
)
from agents.greeting_agent import create_greeting_agent
from agents.farewell_agent import create_farewell_agent
from agents.root_agent import (
    create_root_agent_team,
    create_root_agent_stateful,
    create_root_agent_with_model_guardrail,
    create_root_agent_with_tool_guardrail
)

# --- Setup ---
logger = logging.getLogger(__name__)
config.setup_logging() # Ensure logging is configured
config.check_api_keys() # Check and print API key status


# === Step Simulation Functions ===

async def run_step1_basic_agent():
    """Simulates Step 1: Basic Weather Agent"""
    print("\n\n--- Step 1: Basic Weather Agent ---")
    agent = create_weather_agent_v1()
    if not agent:
        print("❌ Skipping Step 1 due to missing agent.")
        return

    session_service = InMemorySessionService()
    user_id = "user_step1"
    session_id = "session_step1_001"
    session_service.create_session(config.APP_NAME, user_id, session_id)

    runner = Runner(agent=agent, app_name=config.APP_NAME, session_service=session_service)
    print(f"Runner created for agent '{runner.agent.name}'.")

    await call_agent_async("What is the weather like in London?", runner, user_id, session_id)
    await call_agent_async("How about Paris?", runner, user_id, session_id)
    await call_agent_async("Tell me the weather in New York", runner, user_id, session_id)


async def run_step2_multi_model():
    """Simulates Step 2: Testing GPT and Claude Models"""
    print("\n\n--- Step 2: Multi-Model Agents (GPT & Claude) ---")

    # Test GPT Agent
    agent_gpt = create_weather_agent_gpt()
    if agent_gpt:
        print("\n--- Testing GPT Agent ---")
        session_service_gpt = InMemorySessionService()
        user_id_gpt = "user_step2_gpt"
        session_id_gpt = "session_step2_gpt_001"
        session_service_gpt.create_session(config.APP_NAME, user_id_gpt, session_id_gpt)
        runner_gpt = Runner(agent=agent_gpt, app_name=config.APP_NAME, session_service=session_service_gpt)
        await call_agent_async("What's the weather in Tokyo?", runner_gpt, user_id_gpt, session_id_gpt)
    else:
        print("\n❌ Skipping GPT Agent test (agent creation failed, check API key).")

    # Test Claude Agent
    agent_claude = create_weather_agent_claude()
    if agent_claude:
        print("\n--- Testing Claude Agent ---")
        session_service_claude = InMemorySessionService()
        user_id_claude = "user_step2_claude"
        session_id_claude = "session_step2_claude_001"
        session_service_claude.create_session(config.APP_NAME, user_id_claude, session_id_claude)
        runner_claude = Runner(agent=agent_claude, app_name=config.APP_NAME, session_service=session_service_claude)
        await call_agent_async("Weather in London please.", runner_claude, user_id_claude, session_id_claude)
    else:
        print("\n❌ Skipping Claude Agent test (agent creation failed, check API key).")


async def run_step3_agent_team():
    """Simulates Step 3: Agent Team Delegation"""
    print("\n\n--- Step 3: Agent Team Delegation ---")
    greeting_agent = create_greeting_agent()
    farewell_agent = create_farewell_agent()

    if not greeting_agent or not farewell_agent:
        print("❌ Skipping Step 3 due to missing sub-agents.")
        return

    root_agent = create_root_agent_team(greeting_agent, farewell_agent)
    if not root_agent:
        print("❌ Skipping Step 3 due to missing root agent.")
        return

    session_service = InMemorySessionService()
    user_id = "user_step3"
    session_id = "session_step3_001"
    session_service.create_session(config.APP_NAME, user_id, session_id)

    runner = Runner(agent=root_agent, app_name=config.APP_NAME, session_service=session_service)
    print(f"Runner created for agent '{runner.agent.name}'.")

    await call_agent_async("Hello there!", runner, user_id, session_id)
    await call_agent_async("What is the weather in New York?", runner, user_id, session_id)
    await call_agent_async("Thanks, bye!", runner, user_id, session_id)


async def run_step4_session_state():
    """Simulates Step 4: Session State and Stateful Tools"""
    print("\n\n--- Step 4: Session State & Stateful Tool ---")
    greeting_agent = create_greeting_agent()
    farewell_agent = create_farewell_agent()

    if not greeting_agent or not farewell_agent:
        print("❌ Skipping Step 4 due to missing sub-agents.")
        return None # Return None to signal failure to subsequent steps

    root_agent = create_root_agent_stateful(greeting_agent, farewell_agent)
    if not root_agent:
        print("❌ Skipping Step 4 due to missing stateful root agent.")
        return None

    # Create a dedicated session service for stateful tests
    session_service_stateful = InMemorySessionService()
    user_id = "user_stateful"
    session_id = "session_state_demo_001"

    # Initialize state
    initial_state = {"user_preference_temperature_unit": "Celsius"}
    session_service_stateful.create_session(config.APP_NAME, user_id, session_id, state=initial_state)
    print(f"Session '{session_id}' created for user '{user_id}' with initial state: {initial_state}")

    runner = Runner(agent=root_agent, app_name=config.APP_NAME, session_service=session_service_stateful)
    print(f"Runner created for agent '{runner.agent.name}'.")

    # --- Interaction Flow ---
    print("\n--- Turn 1: Requesting weather in London (expect Celsius) ---")
    await call_agent_async("What's the weather in London?", runner, user_id, session_id)

    print("\n--- Manually Updating State: Setting unit to Fahrenheit (DEMO ONLY) ---")
    # !! IMPORTANT: Direct state modification is specific to InMemorySessionService !!
    # !! In production, use ToolContext.state or EventActions(state_delta=...) !!
    try:
        # Access the internal storage (specific to InMemorySessionService implementation)
        session_key = (config.APP_NAME, user_id, session_id)
        if session_key in session_service_stateful.sessions:
            stored_session: Session = session_service_stateful.sessions[session_key]
            stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
            stored_session.last_update_time = time.time() # Update timestamp
            print(f"--- Stored session state updated. Current 'user_preference_temperature_unit': {stored_session.state['user_preference_temperature_unit']} ---")
        else:
             print(f"--- Error: Could not find session '{session_id}' in internal storage for update. ---")
    except Exception as e:
        print(f"--- Error updating internal session state: {e} ---")


    print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
    await call_agent_async("Tell me the weather in New York.", runner, user_id, session_id)

    print("\n--- Turn 3: Sending a greeting (testing delegation + output_key override) ---")
    await call_agent_async("Hi!", runner, user_id, session_id)

    # --- Inspect Final State ---
    print("\n--- Inspecting Final Session State (End of Step 4) ---")
    final_session = session_service_stateful.get_session(config.APP_NAME, user_id, session_id)
    if final_session:
        print(f"Final State: {final_session.state}")
    else:
        print("Error: Could not retrieve final session state.")

    # Return the service and IDs for reuse in next steps
    return {"service": session_service_stateful, "user_id": user_id, "session_id": session_id}


async def run_step5_model_guardrail(stateful_context: Optional[Dict]):
    """Simulates Step 5: Input Guardrail (before_model_callback)"""
    print("\n\n--- Step 5: Model Input Guardrail (block 'BLOCK') ---")
    if not stateful_context:
        print("❌ Skipping Step 5 as previous stateful step failed.")
        return

    session_service = stateful_context["service"]
    user_id = stateful_context["user_id"]
    session_id = stateful_context["session_id"]

    greeting_agent = create_greeting_agent()
    farewell_agent = create_farewell_agent()

    if not greeting_agent or not farewell_agent:
        print("❌ Skipping Step 5 due to missing sub-agents.")
        return

    root_agent = create_root_agent_with_model_guardrail(greeting_agent, farewell_agent)
    if not root_agent:
        print("❌ Skipping Step 5 due to missing model guardrail root agent.")
        return

    # Use the SAME session service from Step 4
    runner = Runner(agent=root_agent, app_name=config.APP_NAME, session_service=session_service)
    print(f"Runner created for agent '{runner.agent.name}' using existing stateful session.")

    # --- Interaction Flow ---
    print("\n--- Testing Model Guardrail ---")
    await call_agent_async("What is the weather in London?", runner, user_id, session_id) # Should use Fahrenheit from prev step
    await call_agent_async("BLOCK the request for weather in Tokyo", runner, user_id, session_id)
    await call_agent_async("Hello again", runner, user_id, session_id)

    # --- Inspect Final State ---
    print("\n--- Inspecting Final Session State (End of Step 5) ---")
    final_session = session_service.get_session(config.APP_NAME, user_id, session_id)
    if final_session:
        print(f"Final State: {final_session.state}")
        print(f"(Guardrail Triggered Flag: {final_session.state.get('guardrail_block_keyword_triggered')})") # Check flag
    else:
        print("Error: Could not retrieve final session state.")


async def run_step6_tool_guardrail(stateful_context: Optional[Dict]):
    """Simulates Step 6: Tool Argument Guardrail (before_tool_callback)"""
    print("\n\n--- Step 6: Tool Argument Guardrail (block 'Paris') ---")
    if not stateful_context:
        print("❌ Skipping Step 6 as previous stateful step failed.")
        return

    session_service = stateful_context["service"]
    user_id = stateful_context["user_id"]
    session_id = stateful_context["session_id"]

    greeting_agent = create_greeting_agent()
    farewell_agent = create_farewell_agent()

    if not greeting_agent or not farewell_agent:
        print("❌ Skipping Step 6 due to missing sub-agents.")
        return

    root_agent = create_root_agent_with_tool_guardrail(greeting_agent, farewell_agent)
    if not root_agent:
        print("❌ Skipping Step 6 due to missing tool guardrail root agent.")
        return

    # Use the SAME session service from Step 4/5
    runner = Runner(agent=root_agent, app_name=config.APP_NAME, session_service=session_service)
    print(f"Runner created for agent '{runner.agent.name}' using existing stateful session.")

    # --- Interaction Flow ---
    print("\n--- Testing Tool Guardrail ---")
    await call_agent_async("What's the weather in New York?", runner, user_id, session_id) # Allowed
    await call_agent_async("How about Paris?", runner, user_id, session_id) # Blocked by tool guardrail
    await call_agent_async("Tell me the weather in London.", runner, user_id, session_id) # Allowed

    # --- Inspect Final State ---
    print("\n--- Inspecting Final Session State (End of Step 6) ---")
    final_session = session_service.get_session(config.APP_NAME, user_id, session_id)
    if final_session:
        print(f"Final State: {final_session.state}")
        print(f"(Tool Guardrail Triggered Flag: {final_session.state.get('guardrail_tool_block_triggered')})") # Check flag
    else:
        print("Error: Could not retrieve final session state.")


# === Main Execution ===
async def main():
    """Runs all steps of the ADK Weather Bot tutorial."""

    await run_step1_basic_agent()
    await run_step2_multi_model()
    await run_step3_agent_team()

    # Steps 4, 5, and 6 share the same stateful session
    stateful_run_context = await run_step4_session_state()
    await run_step5_model_guardrail(stateful_run_context)
    await run_step6_tool_guardrail(stateful_run_context)

    print("\n\n--- Tutorial Complete ---")

if __name__ == "__main__":
    asyncio.run(main())
```

**19. `.vscode/settings.json` (Optional)**

```json
{
    "python.analysis.typeCheckingMode": "basic", // Or "strict"
    "python.linting.pylintEnabled": true,
    "python.linting.enabled": true,
    "python.formatting.provider": "black", // Or "autopep8"
    "editor.formatOnSave": true,
    // Add the project root to python.analysis.extraPaths if imports aren't resolving
    // "python.analysis.extraPaths": ["."]
}
```

**How to Run:**

1.  **Clone/Create Files:** Create the directory structure and files as listed above.
2.  **Create Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure API Keys:**
    *   Rename `.env.example` to `.env`.
    *   Open `.env` and paste your actual API keys from Google AI Studio, OpenAI Platform, and Anthropic Console.
5.  **Run the Main Script:**
    ```bash
    python main.py
    ```

**Explanation of Changes and Clean Code Practices:**

1.  **Modularity:** Code is broken down into logical units (agents, tools, callbacks, config, utils, main). This improves readability and maintainability.
2.  **Separation of Concerns:** Each file/module has a specific responsibility (e.g., `config.py` handles setup, `tools/weather.py` defines only weather-related tools).
3.  **Configuration Management:** API keys are loaded from environment variables using `.env` and `python-dotenv`, which is much safer than hardcoding. `config.py` centralizes loading and checks.
4.  **Clear Naming:** Functions, variables, and files have descriptive names (e.g., `create_root_agent_stateful`, `block_paris_tool_guardrail`).
5.  **Agent Creation Functions:** Instead of defining agents directly in `main.py`, we use factory functions (e.g., `create_weather_agent_v1`) within the `agents/` modules. This keeps `main.py` cleaner and focused on orchestration.
6.  **Error Handling:** Basic `try...except` blocks are added around agent creation, especially for models requiring API keys, logging errors if keys are missing or creation fails.
7.  **Logging:** Replaced most `print` statements within tools and callbacks with `logging`. This is standard practice for libraries and applications. `main.py` still uses `print` for user-facing output.
8.  **Type Hinting:** Added type hints (`-> Agent | None`, `Dict`, `Optional`, etc.) for better code clarity and static analysis.
9.  **Constants:** Model names and the App Name are defined as constants in `agents/base_models.py` and `config.py` for consistency and easier updates.
10. **Dependency Injection (Implicit):** Agent creation functions take dependencies (like sub-agents) as arguments where needed (`create_root_agent_team` needs greeting/farewell agents).
11. **State Management:** The stateful session service (`session_service_stateful`) is created in Step 4 and explicitly passed to the runners in Steps 5 and 6 to ensure state continuity. The manual state update in Step 4 is clearly marked as a demo-specific technique for `InMemorySessionService`.
12. **Asynchronous Structure:** `main.py` uses `async def main()` and `asyncio.run()` to correctly handle the asynchronous nature of ADK's `run_async`.
13. **`requirements.txt`:** Standard way to declare project dependencies.
14. **`.gitignore`:** Prevents committing sensitive files (`.env`) and unnecessary clutter (`__pycache__`).
15. **`utils/interaction.py`:** The `call_agent_async` helper is moved to a utility module, making it reusable and cleaning up `main.py`.

This structure provides a robust and maintainable foundation, reflecting how you'd typically organize a Python application using ADK in a development environment like VS Code.