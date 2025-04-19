
**( this document resides as `ADVISOR_DESIGN.md` in the docs of your `neo_advisor_service` repository)**

---

**Mortgage Advisor - Detailed Design Document**

**Version:** 1.0
**Date:** 2023-10-27

**Table of Contents:**

1.  [Overview & Goals](#1-overview--goals)
2.  [High-Level Architecture](#2-high-level-architecture)
3.  [Repository & Package Structure](#3-repository--package-structure)
4.  [Core Data Models (Pydantic Schemas)](#4-core-data-models-pydantic-schemas)
5.  [Phased Implementation Roadmap](#5-phased-implementation-roadmap)
    *   [Phase 0: Scaffolding](#phase-0-scaffolding)
    *   [Phase 1: MVP Chat & Profiling](#phase-1-mvp-chat--profiling)
    *   [Phase 2: Session State & Contextual Grounding (RAG Simulation)](#phase-2-session-state--contextual-grounding-rag-simulation)
    *   [Phase 3: Single-Track Loan Simulation (Calculator Tool)](#phase-3-single-track-loan-simulation-calculator-tool)
    *   [Phase 4: Variable Tuning & Simulation Comparison](#phase-4-variable-tuning--simulation-comparison)
    *   [Phase 5: Multi-Track Mortgage Packages](#phase-5-multi-track-mortgage-packages)
6.  [Tool Implementation Details](#6-tool-implementation-details)
    *   [Memory Tool (`tools/memory.py`)](#memory-tool-toolsmemorypy)
    *   [Bank Docs Tool (`tools/bank_docs.py`)](#bank-docs-tool-toolsbank_docspy)
    *   [Calculator Tool (`tools/calculator.py`)](#calculator-tool-toolscalculatorpy)
7.  [Agent & Prompt Design](#7-agent--prompt-design)
8.  [Frontend Interaction (React Client)](#8-frontend-interaction-react-client)
9.  [Testing Strategy](#9-testing-strategy)
10. [Deployment Strategy](#10-deployment-strategy)
11. [Future Considerations & Scalability](#11-future-considerations--scalability)

---

## 1. Overview & Goals

The Mortgage Advisor is a conversational AI service built using the Google Agent Development Kit (ADK). It aims to provide users with personalized guidance through the complex process of understanding and selecting mortgage options.

**Core Goals:**

*   Engage users in a natural, helpful conversation about their mortgage needs.
*   Gather relevant user information (financial profile, preferences, goals).
*   Provide contextual information based on simulated bank policies and documentation.
*   Simulate various loan scenarios (single and multi-track) using an external calculator service.
*   Present clear comparisons of different mortgage packages, highlighting pros and cons.
*   Maintain conversation state and user context across interactions.
*   Offer a robust and extensible architecture inspired by ADK best practices and the `travel-concierge` sample.

This document outlines the architecture, components, data models, and phased implementation plan for building the Mortgage Advisor.

## 2. High-Level Architecture

The system follows a standard client-server architecture facilitated by ADK:

```mermaid
graph LR
    A[React Client (Chat UI)] <-- SSE / REST --> B(ADK API Server);
    B -- ADK Run --> C{MortgageAdvisor Agent (ADK)};
    C -- Tool Calls --> D[Tools];
    D -- memory.py --> E[Session State (In-Memory/Redis)];
    D -- bank_docs.py --> F[Bank Docs Source (Files/VectorDB)];
    D -- calculator.py --> G((External Calculator Service));

    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#ccf,stroke:#333,stroke-width:2px
    style D fill:#ffc,stroke:#333,stroke-width:1px
    style G fill:#f66,stroke:#333,stroke-width:1px
```

**Components:**

1.  **React Client:** Web-based chat interface providing the user interaction layer. Communicates with the backend via REST (for session management, potentially) and Server-Sent Events (SSE) for real-time agent interaction streaming.
2.  **ADK API Server:** A lightweight server (e.g., FastAPI) started via `adk api_server mortgage_advisor`. It exposes endpoints (`/run_sse`, session management) to handle client requests and interact with the ADK agent runtime.
3.  **MortgageAdvisor Agent (ADK):** The core logic unit built with `google.adk.agents.Agent`. It manages the conversation flow, interprets user input, decides when to use tools, processes tool responses, and formulates replies, guided by its instruction prompt. Initially a single agent, potentially evolving.
4.  **Tools:** ADK functions or AgentTools invoked by the LLM based on the agent's prompt. They perform specific, non-conversational tasks:
    *   `memory.py`: Manages reading/writing to the session state.
    *   `bank_docs.py`: Retrieves information from simulated bank documentation (RAG pattern).
    *   `calculator.py`: Interfaces with the external loan calculation service.
5.  **Session State:** Stores conversation context, user profile, simulation results, etc., across turns within a user session. Managed via the `memory.py` tool. Starts in-memory, potentially moves to persistent storage (e.g., Redis).
6.  **Bank Docs Source:** The knowledge base for the `bank_docs.py` tool. Starts as simple text files, could evolve into a vector database for semantic search.
7.  **External Calculator Service:** A separate microservice (or function) responsible for performing the actual loan amortization calculations based on provided parameters. Accessed via HTTP requests from the `calculator.py` tool.

## 3. Repository & Package Structure

The project structure mirrors `travel-concierge` for consistency and adherence to ADK conventions:

```
mortgage_advisor/
│
├── __init__.py
├── agent.py                      # Defines MortgageAdvisorAgent (Phase 0+)
├── prompt.py                     # Main system prompt template (Phase 0+)
│
├── shared_libraries/             # Cross-cutting utils & types (Phase 1+)
│   ├── __init__.py
│   ├── constants.py              # State keys, etc.
│   └── types.py                  # Pydantic models (BorrowerProfile, LoanTrack, etc.)
│
├── tools/                        # ADK Tools (Implemented phase by phase)
│   ├── __init__.py
│   ├── memory.py                 # (Phase 1+)
│   ├── bank_docs.py              # (Phase 2+)
│   └── calculator.py             # (Phase 3+)
│
└── sub_agents/                   # Conceptual separation, logic initially in main agent's prompt
    ├── __init__.py
    ├── intake/                   # (Phase 1 logic)
    │   ├── agent.py              # (Placeholder/Future)
    │   └── prompt.py             # (Placeholder/Future)
    ├── profiling/                # (Phase 1 logic)
    ├── simulation/               # (Phase 3+ logic)
    ├── packaging/                # (Phase 4+ logic)
    └── follow_up/                # (Phase 5 logic)

tests/                            # Pytest tests (Phase 1+)
│   └── unit/
│       └── test_tools.py         # Example
eval/                             # ADK Evaluation framework tests (Phase 1+)
│   └── data/
deployment/                       # Deployment scripts (Phase 2+)
│   └── deploy.py
.env.example
pyproject.toml
DESIGN.md                         # This document
README.md
```

## 4. Core Data Models (Pydantic Schemas)

Defined in `mortgage_advisor/shared_libraries/types.py` using Pydantic for type safety and integration with ADK.

```python
# mortgage_advisor/shared_libraries/types.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class BorrowerProfile(BaseModel):
    """Represents the information gathered about the borrower."""
    name: Optional[str] = Field(default=None, description="Borrower's full name.")
    # age: Optional[int] = Field(default=None, description="Borrower's age.") # Consider if needed
    # residency_status: Optional[str] = Field(default=None, description="e.g., Citizen, Permanent Resident") # Consider if needed
    estimated_property_value: Optional[float] = Field(default=None, description="Estimated value of the property being purchased.")
    down_payment_amount: Optional[float] = Field(default=None, description="Amount the borrower intends to pay upfront.")
    gross_annual_income: Optional[float] = Field(default=None, description="Borrower's total annual income before taxes.")
    total_monthly_debt_payments: Optional[float] = Field(default=None, description="Borrower's existing monthly debt obligations (loans, credit cards).")
    credit_score_range: Optional[Literal["poor", "fair", "good", "very_good", "excellent"]] = Field(default=None, description="Estimated credit score category.")
    desired_loan_amount: Optional[float] = Field(default=None, description="Calculated or stated loan amount needed (Property Value - Down Payment).")
    preferred_loan_years: Optional[int] = Field(default=None, description="Borrower's preferred loan duration in years.")
    preferred_monthly_payment: Optional[float] = Field(default=None, description="Target maximum monthly mortgage payment.")
    risk_tolerance: Optional[Literal["low", "medium", "high"]] = Field(default="medium", description="Borrower's comfort level with interest rate fluctuations.")
    preferred_track_types: List[Literal["FIXED", "CPI", "PRIME", "VARIABLE"]] = Field(default_factory=list, description="Types of loan tracks the user is interested in.")

class LoanTrackInput(BaseModel):
    """Input parameters for a single loan track calculation."""
    principal: float = Field(description="The loan amount for this specific track.")
    years: int = Field(description="The duration of this loan track in years.")
    track_type: Literal["FIXED", "CPI", "PRIME", "VARIABLE"] = Field(description="The type of interest rate mechanism.")
    # Base rate determined by calculator service, override is optional
    override_interest_rate: Optional[float] = Field(default=None, description="Optional rate to force for simulation (e.g., 5.5 for 5.5%).")

class LoanTrackOutput(BaseModel):
    """Output results from a single loan track calculation."""
    input_params: LoanTrackInput = Field(description="The input parameters used for this calculation.")
    interest_rate_used: float = Field(description="The actual annual interest rate used (base or override, e.g., 5.5 for 5.5%).")
    monthly_payment: float = Field(description="Calculated monthly principal and interest payment.")
    total_principal_paid: float = Field(description="Total principal paid over the life of the loan (should match input principal).")
    total_interest_paid: float = Field(description="Total interest paid over the life of the loan.")
    total_payment: float = Field(description="Total principal + total interest paid.")
    # amortization_schedule: Optional[List[dict]] = Field(default=None, description="Optional detailed payment schedule.") # Keep optional for brevity

class MortgagePackage(BaseModel):
    """Represents a proposed mortgage structure composed of multiple loan tracks."""
    package_id: str = Field(description="Unique identifier for this package proposal (e.g., 'package_A').")
    description: str = Field(description="Brief description summarizing the package strategy (e.g., 'Balanced Fixed/CPI Mix').")
    tracks: List[LoanTrackOutput] = Field(description="List of calculated loan tracks constituting this package.")
    total_loan_amount: float = Field(description="Sum of principal across all tracks.")
    total_initial_monthly_payment: float = Field(description="Sum of initial monthly payments across all tracks.")
    estimated_total_payment: float = Field(description="Sum of total payments across all tracks (note: variable rates make this an estimate).")
    pros: List[str] = Field(default_factory=list, description="List of advantages of this package.")
    cons: List[str] = Field(default_factory=list, description="List of disadvantages or risks of this package.")

# Add other necessary types like SessionState structure if needed
```

## 5. Phased Implementation Roadmap

### Phase 0: Scaffolding

*   **Goal:** Set up the basic project structure and a minimal runnable agent.
*   **ADK Components:**
    *   `mortgage_advisor/agent.py`: Define `MortgageAdvisorAgent` inheriting from `google.adk.agents.Agent`.
    *   `mortgage_advisor/prompt.py`: Define `AGENT_INSTRUCTION_PHASE0` with a simple greeting and purpose.
*   **Code Example (`agent.py`):**
    ```python
    from google.adk.agents import Agent
    from .prompt import AGENT_INSTRUCTION_PHASE0

    MortgageAdvisorAgent = Agent(
        model="gemini-1.5-flash-latest", # Or your preferred model
        name="mortgage_advisor_agent",
        description="A friendly conversational agent introducing mortgage concepts.",
        instruction=AGENT_INSTRUCTION_PHASE0,
        # tools=[], # No tools yet
    )
    ```
*   **Code Example (`prompt.py`):**
    ```python
    AGENT_INSTRUCTION_PHASE0 = """
    You are a friendly and helpful Mortgage Advisor assistant.
    Introduce yourself briefly.
    Explain that you can help users understand mortgages, but your capabilities are currently limited.
    Engage in simple conversation. Do not attempt calculations or ask for personal financial details yet.
    """
    ```
*   **Testing:** Run `adk run mortgage_advisor` or `adk web` and have a basic conversation.

### Phase 1: MVP Chat & Profiling

*   **Goal:** Gather basic borrower information and store it.
*   **ADK Components:**
    *   `Agent`: `MortgageAdvisorAgent`
    *   `Prompt`: Update instruction (`AGENT_INSTRUCTION_PHASE1`) to ask profiling questions sequentially (property value, down payment, income, debt, credit range, risk tolerance). Instruct to use the `memorize` tool after getting answers.
    *   `Tool`: `tools/memory.py` - Implement `memorize(key: str, value: Any, tool_context: ToolContext)`. Initially stores in `tool_context.state` dictionary.
    *   `Schema`: `shared_libraries/types.py` - Define `BorrowerProfile`.
    *   `State`: Use key `user_profile` in `tool_context.state` to store a `BorrowerProfile` instance (or dictionary representation).
*   **Prompt Snippet (`prompt.py`):**
    ```python
    # AGENT_INSTRUCTION_PHASE1 (Partial)
    # ... (Introduction) ...
    To help you better, I need to understand your situation. Let's go step-by-step.
    First, what is the estimated value of the property you're considering?
    {{#if user_profile.estimated_property_value}}
    Okay, got it (${{user_profile.estimated_property_value}}). Next, how much are you planning for a down payment?
    {{/if}}
    {{#if user_profile.down_payment_amount}}
    Great (${{user_profile.down_payment_amount}}). Now, what's your approximate gross annual income?
    (Use the memorize tool to store the 'estimated_property_value' under the 'user_profile' key in the state once provided)
    {{/if}}
    # ... continue for other profile fields ...

    Once all information is gathered:
    Okay, let me summarize what I have:
    - Property Value: {{user_profile.estimated_property_value}}
    - Down Payment: {{user_profile.down_payment_amount}}
    # ... etc ...
    Does that look correct?

    Current Profile State:
    <user_profile>
    {{user_profile}}
    </user_profile>
    """ # Note: Use a templating engine or f-strings for state injection
    ```
*   **Tool Implementation (`memory.py`):**
    ```python
    from google.adk.tools import ToolContext, tool
    from typing import Any
    from ..shared_libraries.types import BorrowerProfile # Assuming Pydantic

    PROFILE_KEY = "user_profile"

    @tool
    def memorize(key: str, value: Any, tool_context: ToolContext):
        """Stores or updates a piece of information in the session state.
           Specifically handles updating fields within the 'user_profile'.
        """
        state = tool_context.state
        if PROFILE_KEY not in state:
            state[PROFILE_KEY] = BorrowerProfile().model_dump() # Initialize if needed

        if key in BorrowerProfile.model_fields:
            # Basic type conversion attempt (can be made more robust)
            field_type = BorrowerProfile.model_fields[key].annotation
            try:
                if field_type == Optional[float] or field_type == float:
                    processed_value = float(str(value).replace("$","").replace(",",""))
                elif field_type == Optional[int] or field_type == int:
                     processed_value = int(str(value).replace("$","").replace(",",""))
                else:
                     processed_value = value
                state[PROFILE_KEY][key] = processed_value
                status = f"Stored {key} = {processed_value} in profile."
            except (ValueError, TypeError) as e:
                status = f"Failed to store {key}: Invalid value '{value}' for type {field_type}. Error: {e}"

        else:
             # Generic key storage (less common if profile is main focus)
             state[key] = value
             status = f"Stored generic key '{key}'."

        print(f"Memory Tool: {status}") # For debugging
        print(f"Current Profile State: {state.get(PROFILE_KEY)}")
        return {"status": status, "updated_profile": state.get(PROFILE_KEY)}
    ```
*   **Testing:** Use `AgentEvaluator` to test conversations that collect profile data, asserting `memorize` tool calls with correct args and final state.

### Phase 2: Session State & Contextual Grounding (RAG Simulation)

*   **Goal:** Introduce persistent sessions (conceptually) and answer policy questions using simulated documents.
*   **ADK Components:**
    *   `Agent`: `MortgageAdvisorAgent`.
    *   `Prompt`: Update instruction (`AGENT_INSTRUCTION_PHASE2`) to use the `bank_document_search` tool when asked about general bank policies, rates, or term definitions. Inject `{user_profile}` into the prompt.
    *   `Tool`: `tools/bank_docs.py` - Implement `bank_document_search(query: str)`. Initially reads from local `.txt` files based on keywords in the query.
    *   `Tool`: `tools/memory.py` - No major change, but emphasize its role in loading/saving state if persistence were added (ADK handles session loading with `InMemorySessionService` for now).
    *   `State`: `user_profile` is now loaded/persisted conceptually.
*   **Tool Implementation (`bank_docs.py` - Simplified):**
    ```python
    import os
    from google.adk.tools import tool

    DOCS_DIR = "bank_policy_docs" # Create this directory with some .txt files

    @tool
    def bank_document_search(query: str) -> dict:
        """Searches simulated bank documents for information related to the query."""
        results = []
        try:
            if not os.path.exists(DOCS_DIR):
                 return {"error": f"Documentation directory not found: {DOCS_DIR}"}

            keywords = query.lower().split()
            # Very basic keyword matching across files
            for filename in os.listdir(DOCS_DIR):
                if filename.endswith(".txt"):
                    filepath = os.path.join(DOCS_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if any(keyword in content.lower() for keyword in keywords):
                                # Return first relevant snippet found (improve with better matching/ranking later)
                                snippet = content[:500] + "..." # Basic snippet
                                results.append({"source": filename, "snippet": snippet})
                                # For simplicity, return just the first hit
                                return {"relevant_info": f"From {filename}: {snippet}"}
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}") # Log error

            if not results:
                return {"relevant_info": "I couldn't find specific details on that topic in my current documents."}

        except Exception as e:
            return {"error": f"An error occurred during document search: {e}"}

        # Fallback if loop completes without returning
        return {"relevant_info": "I couldn't find specific details on that topic in my current documents."}

    ```
*   **Testing:** Test conversations asking policy questions ("What's LTV?", "Explain fixed rates"), assert `bank_document_search` calls and plausible grounded responses.

### Phase 3: Single-Track Loan Simulation (Calculator Tool)

*   **Goal:** Integrate the loan calculator for basic simulations.
*   **ADK Components:**
    *   `Agent`: `MortgageAdvisorAgent`.
    *   `Prompt`: Update instruction (`AGENT_INSTRUCTION_PHASE3`) to explain the `calculator_tool`. Guide the agent to:
        1.  Extract `desired_loan_amount` and `preferred_loan_years` from `user_profile`. If missing, ask.
        2.  Ask for `preferred_track_types` or suggest 'FIXED'.
        3.  Construct `LoanTrackInput`.
        4.  Call `calculator_tool`.
        5.  Present `LoanTrackOutput` clearly (monthly payment, rate, total interest).
        6.  Use `memorize` to store the result in `current_simulation`.
    *   `Tool`: `tools/calculator.py` - Implement `calculator_tool(input_data: LoanTrackInput)`. This function *wraps* the call to the external service. Start with a mock implementation.
    *   `Schema`: `shared_libraries/types.py` - Define `LoanTrackInput`, `LoanTrackOutput`.
    *   `State`: Add `current_simulation` (stores `LoanTrackOutput`).
*   **Tool Implementation (`calculator.py` - Mock Wrapper):**
    ```python
    from google.adk.tools import tool
    import requests # Or your preferred HTTP client
    import json
    from ..shared_libraries.types import LoanTrackInput, LoanTrackOutput

    # Placeholder - Replace with your actual calculator service URL
    CALCULATOR_API_ENDPOINT = "http://localhost:5001/calculate" # Example

    # Mock base rates (replace with actual fetching if needed)
    BASE_RATES = {
        "FIXED": 5.0,
        "CPI": 3.5,
        "PRIME": 4.0,
        "VARIABLE": 4.2,
    }

    @tool
    def calculator_tool(input_data: LoanTrackInput) -> dict:
        """Calls the external loan calculator service for a single track."""
        # Prepare payload for the external service
        payload = input_data.model_dump()

        # Determine rate to use
        rate_to_use = input_data.override_interest_rate
        if rate_to_use is None:
            rate_to_use = BASE_RATES.get(input_data.track_type, 5.0) # Default fallback
        payload['interest_rate'] = rate_to_use # Add the rate for the external service

        print(f"Calling Calculator Service with: {payload}")

        try:
            # --- Replace with actual HTTP call ---
            # response = requests.post(CALCULATOR_API_ENDPOINT, json=payload, timeout=10)
            # response.raise_for_status() # Raise exception for bad status codes
            # result_data = response.json()
            # --- Mock Implementation ---
            mock_monthly = (payload['principal'] * (rate_to_use / 100 / 12)) / (1 - (1 + rate_to_use / 100 / 12)**(-payload['years'] * 12))
            mock_total_payment = mock_monthly * payload['years'] * 12
            mock_total_interest = mock_total_payment - payload['principal']
            result_data = {
                "monthly_payment": round(mock_monthly, 2),
                "total_principal_paid": round(payload['principal'], 2),
                "total_interest_paid": round(mock_total_interest, 2),
                "total_payment": round(mock_total_payment, 2),
                "interest_rate_used": rate_to_use,
                # "amortization_schedule": [] # Optional
            }
            # --- End Mock ---

            # Validate and structure the output using Pydantic model
            # Ensure keys match LoanTrackOutput fields
            output = LoanTrackOutput(
                input_params=input_data, # Echo input
                interest_rate_used=result_data['interest_rate_used'],
                monthly_payment=result_data['monthly_payment'],
                total_principal_paid=result_data['total_principal_paid'],
                total_interest_paid=result_data['total_interest_paid'],
                total_payment=result_data['total_payment']
            )
            print(f"Calculator Service Response (parsed): {output.model_dump_json(indent=2)}")
            # Return as dict for ADK
            return output.model_dump()

        except requests.exceptions.RequestException as e:
            print(f"Error calling calculator service: {e}")
            return {"error": f"Failed to reach calculator service: {e}"}
        except (json.JSONDecodeError, KeyError, ValueError) as e: # Include Pydantic validation errors if applicable
             print(f"Error processing calculator response: {e}")
             return {"error": f"Invalid response from calculator service: {e}"}
        except Exception as e:
            print(f"Unexpected error in calculator tool: {e}")
            return {"error": f"An unexpected error occurred: {e}"}

    ```
*   **Testing:** Test conversations triggering calculations. Assert `calculator_tool` calls with correct `LoanTrackInput` args. Assert agent presents results clearly. Use mocked calculator responses.

### Phase 4: Variable Tuning & Simulation Comparison

*   **Goal:** Allow the agent to run multiple simulations and compare them.
*   **ADK Components:**
    *   `Agent`: `MortgageAdvisorAgent`.
    *   `Prompt`: Update instruction (`AGENT_INSTRUCTION_PHASE4`) to handle user requests like "What if I pay over 30 years?" or "Show me a lower rate." Instruct the agent to:
        1.  Identify the parameter to change (years, override_rate).
        2.  Construct a *new* `LoanTrackInput`.
        3.  Call `calculator_tool`.
        4.  Retrieve the `current_simulation` from state using `memorize` (or implicitly via prompt injection).
        5.  Compare the new result with `current_simulation`, highlighting differences in monthly payment and total interest.
        6.  Explain the trade-offs clearly.
    *   `Tool`: `calculator_tool` (use `override_interest_rate`).
    *   `State`: Use `current_simulation` for comparison. Maybe add `comparison_simulation` temporarily if needed for complex comparisons.
*   **Prompt Snippet (`prompt.py`):**
    ```python
    # AGENT_INSTRUCTION_PHASE4 (Partial)
    # ... (Previous instructions) ...
    If the user asks to see a different scenario (e.g., different loan term, different rate):
    1. Identify the change requested.
    2. Create a *new* LoanTrackInput based on the current profile/simulation but with the requested change (e.g., update 'years', set 'override_interest_rate').
    3. Call the calculator_tool with the new input.
    4. Let's call the result 'new_output'. Compare 'new_output' with the 'current_simulation' stored in the state.
    5. Explain the difference clearly to the user. For example: "Okay, for a {{new_output.input_params.years}}-year term, the monthly payment would be ${{new_output.monthly_payment:.2f}}. Compared to the {{current_simulation.input_params.years}}-year option (${{current_simulation.monthly_payment:.2f}}/month), this is lower monthly, but the total interest paid would be ${{new_output.total_interest_paid:.2f}} instead of ${{current_simulation.total_interest_paid:.2f}}."
    6. Ask the user if they want to explore further or focus on one of the options. Remember to update 'current_simulation' if the user prefers the new scenario.

    Current Simulation State:
    <current_simulation>
    {{current_simulation}}
    </current_simulation>
    ```
*   **Testing:** Test scenarios like "show me 30 years", "what if rate is 4.5%". Assert correct `calculator_tool` calls (with overrides) and that the agent's response includes a comparison referencing previous results.

### Phase 5: Multi-Track Mortgage Packages

*   **Goal:** Propose and simulate packages with multiple loan tracks.
*   **ADK Components:**
    *   `Agent`: `MortgageAdvisorAgent`.
    *   `Prompt`: Major update (`AGENT_INSTRUCTION_PHASE5`). This requires careful orchestration logic:
        1.  Define "Mortgage Package" concept.
        2.  Based on `user_profile.risk_tolerance` and `desired_loan_amount`, propose 1-3 package structures (e.g., "Conservative: 70% Fixed, 30% CPI", "Balanced: 50% Fixed, 50% PRIME", "Aggressive: 100% VARIABLE"). Get splits/types from `bank_document_search` potentially.
        3.  For *each track* within a proposed package:
            *   Calculate the principal for that track (e.g., 70% of `desired_loan_amount`).
            *   Determine years (can be same or different per track, start with same).
            *   Create `LoanTrackInput`.
            *   Call `calculator_tool`.
        4.  Collect all `LoanTrackOutput` results for the package.
        5.  Aggregate metrics: `total_initial_monthly_payment`, `estimated_total_payment`.
        6.  Formulate `pros` and `cons` based on track types and results.
        7.  Create a `MortgagePackage` object.
        8.  Use `memorize` to store the proposed packages in `proposed_packages` list in state.
        9.  Present the packages clearly to the user, allowing comparison.
    *   `Tool`: `calculator_tool`.
    *   `Schema`: `shared_libraries/types.py` - Define `MortgagePackage`.
    *   `State`: Add `proposed_packages` (list of `MortgagePackage`), `selected_package`.
*   **Code Example (`types.py`):** (Included in Section 4)
*   **Agent Logic (Conceptual Prompt Flow):**
    ```
    User: "Show me some package options."
    Agent: (Reads profile) "Okay, based on your medium risk tolerance, I can suggest a balanced package. How about 50% Fixed over 25 years and 50% PRIME over 25 years? Let me calculate that."
    Agent: (Calculates principal splits)
    Agent: --> CALL calculator_tool(principal=175k, years=25, track_type='FIXED')
    Agent: <-- RECEIVE LoanTrackOutput_Fixed
    Agent: --> CALL calculator_tool(principal=175k, years=25, track_type='PRIME')
    Agent: <-- RECEIVE LoanTrackOutput_Prime
    Agent: (Aggregates results, creates MortgagePackage_A)
    Agent: --> CALL memorize(key='proposed_packages', value=[MortgagePackage_A], mode='append') # Append package
    Agent: "Okay, Package A (Balanced) looks like this:
            - Track 1: $175k Fixed @ 5.0% (Monthly: $1023.45)
            - Track 2: $175k PRIME @ 4.0% (Monthly: $923.87)
            - Total Initial Monthly: $1947.32
            - Pros: Stable fixed portion, potential savings from PRIME.
            - Cons: PRIME portion rate can change.
            Would you like to see another option, perhaps more conservative?"
    ```
*   **Testing:** Complex scenarios. Test package proposal logic based on risk tolerance. Assert multiple `calculator_tool` calls per package. Assert correct aggregation and presentation. Validate the structure of `MortgagePackage` in state.

## 6. Tool Implementation Details

### Memory Tool (`tools/memory.py`)

*   **Purpose:** Provide a stateful mechanism for the agent across turns within a session.
*   **Implementation:**
    *   Use `@tool` decorator on functions like `memorize`, `retrieve` (if needed).
    *   Accept `ToolContext` to access `tool_context.state`.
    *   Initial backend: Python dictionary (`tool_context.state`). ADK's `InMemorySessionService` handles this persistence per session *in memory*.
    *   Phase 2+ (Persistence): Abstract the storage. The tool function could check an environment variable or config to decide whether to write to `tool_context.state` (for testing/local) or call a persistent backend (Redis, Database) via a helper class. ADK's `SessionService` interface could be implemented for persistent backends if needed beyond simple key-value.
    *   Handle serialization/deserialization, especially for complex Pydantic objects stored in state. `model_dump()` and `model_validate()` are useful.

### Bank Docs Tool (`tools/bank_docs.py`)

*   **Purpose:** Ground agent responses in factual (simulated) bank policies.
*   **Implementation:**
    *   Phase 2 (Simple): Keyword search across `.txt` files in a designated directory. Return raw snippets.
    *   Phase 2+ (RAG):
        *   Preprocessing: Chunk documents, generate embeddings (e.g., using Vertex AI Embeddings API), store in a vector database (FAISS locally, Vertex AI Vector Search managed).
        *   Runtime: Embed the user query, perform similarity search in the vector DB, retrieve relevant chunks.
        *   Optional Re-ranking/Synthesis: Potentially use another LLM call (or the main agent) to synthesize a concise answer from the retrieved chunks instead of returning raw snippets.
    *   Define as `@tool` or `AgentTool` if synthesis requires LLM reasoning.

### Calculator Tool (`tools/calculator.py`)

*   **Purpose:** Offload complex financial calculations to a dedicated, reliable service.
*   **Implementation:**
    *   Use `@tool`. Define clear input (`LoanTrackInput`) and output (`LoanTrackOutput`) Pydantic schemas.
    *   **Wrapper Logic:** This tool function is primarily an *HTTP client*. It takes the `LoanTrackInput`, constructs the JSON payload for the external service, makes the HTTP POST request, handles potential errors (network issues, timeouts, bad responses), parses the JSON response, validates it against `LoanTrackOutput`, and returns the result as a dictionary.
    *   **Mocking:** For early phases and testing, replace the HTTP call with a Python function that performs a simplified calculation or returns hardcoded data based on input.
    *   **External Service:** Needs to be developed separately. It should accept `principal`, `years`, `track_type`, `interest_rate` (the tool determines which rate to send) and return `monthly_payment`, `total_interest_paid`, etc.

## 7. Agent & Prompt Design

*   **Main Agent (`MortgageAdvisorAgent`):** Starts as the single orchestrator. Its prompt grows significantly with each phase.
*   **Prompt Engineering:**
    *   **Clarity:** Instructions must be unambiguous.
    *   **Role Definition:** Clearly define the agent's persona and limitations for each phase.
    *   **Tool Usage:** Explicitly state *when* and *how* to use each tool, including expected inputs and how to interpret outputs.
    *   **State Injection:** Use a templating mechanism (like f-strings or Jinja2-style `{{variable}}`) to inject relevant state (`user_profile`, `current_simulation`, etc.) into the prompt context for each turn. ADK facilitates this.
    *   **Flow Control:** Guide the agent through the conversation steps (ask profile Q1 -> memorize -> ask Q2 -> ... -> call calculator -> present result -> ask for variations -> ...).
    *   **Error Handling:** Include instructions on how to respond if a tool fails or returns an error (e.g., "I couldn't reach the calculator right now, let's try again later.").
*   **Sub-Agents (Conceptual vs. Actual):** Initially, the logic for "intake," "simulation," "packaging" resides within the main agent's prompt. If prompts become excessively long or complex (Phase 4/5), refactor by creating actual `Agent` instances for these tasks and using `AgentTool` in the main agent to delegate specific parts of the workflow, similar to `travel-concierge`'s structure.

## 8. Frontend Interaction (React Client)

*   **Connection:** Use standard HTTP/WebSocket libraries to connect to the `adk api_server` endpoints. Fetch/EventSource API is suitable for SSE.
*   **Session Management:** The client needs to obtain and send a `session_id` with each `/run_sse` request to maintain context. Session creation might be implicit on the first request or via a dedicated endpoint.
*   **SSE Handling:**
    *   Listen for `message` events on the SSE stream.
    *   Parse the `data` field (which is a JSON string representing an ADK event).
    *   **Event Types:**
        *   `content` event with `author="agent"` and `parts=[{"text": "..."}]`: Display the text in the chat UI.
        *   `content` event with `author="agent"` and `parts=[{"functionCall": {...}}]`: Optionally display a "Thinking..." or "Calling tool..." indicator. The `name` and `args` are available.
        *   `content` event with `author="tool"` and `parts=[{"functionResponse": {...}}]`: This is crucial.
            *   The agent *receives* this internally to continue reasoning.
            *   The frontend can *also* inspect the `name` and `response` fields. If `name == "calculator_tool"`, the frontend could parse the `response` (which is the `LoanTrackOutput` dict) and render a formatted table/card *alongside* the agent's textual summary. This provides a richer UI.
            *   Similarly, responses from `bank_document_search` could be displayed differently.
        *   `error` event: Display an appropriate error message to the user.
*   **UI Rendering:** Design components to display text messages, potentially tool calls/responses, and specialized renderings for calculator results or package comparisons based on parsed SSE events.

## 9. Testing Strategy

*   **Unit Tests (`tests/unit`):**
    *   Test individual tool functions (`calculator.py` mock, `memory.py`, `bank_docs.py` simple cases) in isolation using `pytest`.
    *   Test Pydantic schema validation.
*   **Integration Tests (ADK Evaluation Framework - `eval/`):**
    *   Define test cases in JSON format (similar to `travel-concierge/eval/data/`).
    *   Each test case represents a conversation turn or sequence.
    *   Specify `query`, `expected_tool_use` (tool name and key arguments), and `reference` (expected agent text response).
    *   Use `google.adk.evaluation.AgentEvaluator.evaluate("mortgage_advisor", "eval/data/test_file.json")`.
    *   Crucial for ensuring prompts guide the agent correctly, tools are called appropriately, and state is managed as expected through phases.
*   **Golden Tests:** Snapshot the full text output of specific conversations and compare against known good versions to catch regressions in conversational flow or presentation.
*   **Mocking:** Use `pytest.mark.parametrize` and fixtures to inject mocked tool responses (especially for the calculator and potentially bank docs) during evaluation tests.

## 10. Deployment Strategy

*   Follow the pattern in `travel-concierge/deployment/deploy.py`.
*   Use `vertexai.preview.reasoning_engines.AdkApp` to wrap the `MortgageAdvisorAgent`.
*   Define dependencies in `pyproject.toml` for the deployment environment.
*   Include necessary packages (the `mortgage_advisor` package itself, potentially data files for `bank_docs`) in the `extra_packages` list for `agent_engines.create`.
*   Configure environment variables (API keys, external service URLs) needed by the deployed agent using the `env_vars` parameter.
*   Deploy to Vertex AI Agent Engine (Reasoning Engines).

## 11. Future Considerations & Scalability

*   **Persistent State:** Replace `InMemorySessionService` with a Redis or database-backed implementation for production.
*   **Real RAG:** Implement proper document chunking, embedding, and vector search for `bank_docs.py`.
*   **Real Calculator Integration:** Connect `calculator.py` to the actual external service API.
*   **Authentication/Authorization:** Secure the API server endpoints.
*   **Multi-Lingual Support:** Adapt prompts and potentially models.
*   **Advanced Profiling:** Incorporate more sophisticated financial analysis or risk assessment logic.
*   **Actual Sub-Agents:** If complexity warrants, refactor logic from the main prompt into dedicated `Agent` instances invoked via `AgentTool` for better modularity and maintainability.
*   **Observability:** Integrate logging and tracing (ADK supports tracing).

---

This detailed design provides a solid foundation. Remember that prompt engineering and testing will be highly iterative throughout each phase. Good luck!