% README for Mortgage Concierge Agent
# Mortgage Concierge

This sample demonstrates the use of Google's Agent Development Kit (ADK) to build a professional mortgage advisor.  
The agent conducts a step‑by‑step borrower profiling workflow, grounds its advice in real bank policy documents,  
and surfaces available loan repayment tracks.

## Overview

Borrower interactions are divided into four main phases:
1. **Phase 1 – Profile Gathering**  
   The agent asks for property value, down payment, income, debts, credit score, and risk tolerance.
   After each response it stores the value in session state via the `store_state` tool.
   Once all fields are captured, it confirms the information.
2. **Phase 2 – Loan Options & Eligibility**  
   The agent evaluates eligibility, calculates loan options (via `loan_calculator_tool`), 
   recalculates with different rates or terms (via `recalculate_rate_tool` and `recalculate_term_tool`),
   presents loan track options (via `list_loan_tracks`), and guides the borrower through application steps.
3. **Phase 3 – Multi-Track Simulation**  
   The agent can simulate complex mortgage packages with multiple loan tracks (via `simulate_loan_tracks`),
   such as a 60/40 split between fixed and variable rate portions, creating comprehensive mortgage packages
   with weighted average rates and combined payment calculations.
4. **Phase 4 – Package Evaluation**  
   The agent evaluates mortgage packages (via `evaluate_mortgage_package_tool`) based on risk assessment,
   affordability analysis, and cost efficiency metrics, providing personalized recommendations based on
   the borrower's financial profile and risk tolerance.

At any point, for factual grounding in bank policies, the agent can call:
- `search_bank_docs(query)` – returns snippets from ingested .txt/.md documents.

## Agent Details

| Feature            | Description                                          |
|--------------------|------------------------------------------------------|
| Interaction Type   | Conversational                                       |
| Complexity         | Intermediate                                         |
| Agent Type         | Single LLM Agent + Tools                             |
| Components         | Tools, Memory, Prompts, Pydantic Models              |
| Vertical           | Financial / Mortgage                                 |

### Key Components
- **Agents**  
  - `root_agent` (in `mortgage_concierge/agent.py`): Orchestrates the mortgage advisor workflow.
  - `LoanSimulationAgent` (in `mortgage_concierge/sub_agents/loan_simulation/agent.py`): Specialized agent for simulating multiple loan tracks.
  - `PackageEvaluatorAgent` (in `mortgage_concierge/sub_agents/package_evaluator/agent.py`): Specialized agent for evaluating mortgage packages.
- **Tools**  
  - `search_bank_docs` – semantic/keyword search over ingested bank policy docs.
  - `list_loan_tracks` – loads and returns loan track configurations from JSON.
  - `store_state` – persists arbitrary key/value pairs in session state.
  - `loan_calculator_tool` – calculates loan details and stores results in session state with GUID.
  - `recalculate_rate_tool` – recalculates loan with a new interest rate using stored GUID.
  - `recalculate_term_tool` – recalculates loan with a new term using stored GUID.
  - `simulate_loan_tracks` – simulates multiple loan tracks and creates comprehensive mortgage packages.
  - `evaluate_mortgage_package_tool` – evaluates mortgage packages with risk, affordability, and cost analysis.
- **Shared Libraries**  
  - `memory_ingestion` – reads `.txt`/`.md` docs into ADK's in-memory memory service.
  - `memory_store` – global `InMemoryMemoryService` & `InMemorySessionService`.
  - `types.py` – Pydantic `BorrowerProfile` schema for session state.
- **Prompts**  
  - `AGENT_INSTRUCTION` defines comprehensive instructions for all phases in `prompt.py`.

## Setup and Installation

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer and resolver
- (Optional) OpenAI or other LLM provider credentials

### Clone and Install

#### Using uv (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd <your-repo-root>

# Create a virtual environment
uv venv

# Install dependencies
uv pip install -r requirements.txt
uv pip install "google-adk[cli]"

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
# .venv\Scripts\activate   # Windows
```

#### Using pip (Alternative)
```bash
# Clone the repository
git clone <your-repo-url>
cd <your-repo-root>

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
# or
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
pip install "google-adk[cli]"
```

### Environment Variables
Create a `.env` file in the project root with:
```ini
# LLM model selection
OPENAI_API_KEY=<your-openai-key>
# Optional override of default model
MORTGAGE_MODEL=openai/gpt-4

# Paths to your bank policy docs and loan tracks JSON
BANK_DOCS_PATH=./_knowledge_base/bank_docs
LOAN_TRACKS_PATH=./_knowledge_base/json/interest_tracks.json

# Optional API URLs for loan calculator
CALCULATOR_API_URL=<calculator-api-url>
RECALC_RATE_API_URL=<recalc-rate-api-url>
RECALC_TERM_API_URL=<recalc-term-api-url>
```

## Running the Agent

Make sure your virtual environment is activated before running these commands:
```bash
source .venv/bin/activate  # Linux/macOS
# or
# .venv\Scripts\activate   # Windows
```

### CLI
Start a local chat session:
```bash
adk run mortgage_concierge
```  

### Web Interface
```bash
adk web
```  
Open the UI, select **mortgage_concierge** from the dropdown, and chat.

### Programmatic Server
```bash
adk api_server mortgage_concierge
```  
Use HTTP API or custom client scripts.

### Using uv directly
You can also run the agent without activating the virtual environment:
```bash
# CLI
uv run adk run mortgage_concierge

# Web Interface
uv run adk web

# Programmatic Server
uv run adk api_server mortgage_concierge
```

## Testing

### Using uv (Recommended)
Run unit tests:
```bash
# In the project root
uv run python -m pytest tests/unit
```

### Using activated virtual environment
```bash
# With virtual environment activated
python -m pytest tests/unit
```

## Implementation Progress
- **Phase 1:**
  - ✅ Implemented structured borrower profile gathering workflow
  - ✅ Added session state management for user profile data
  - ✅ Integrated bank policy document retrieval
- **Phase 2:**
  - ✅ Implemented GUID-based loan calculator API integration
  - ✅ Added session state management for calculation results
  - ✅ Implemented background calculation flow
  - ✅ Integrated rate and term recalculation capabilities
- **Phase 3:**
  - ✅ Implemented LoanSimulationAgent for multi-track simulations
  - ✅ Added support for combined fixed/variable rate packages
  - ✅ Created simulation tool interfaces for the main agent
  - ✅ Added weighted average calculations for package metrics
- **Phase 4:**
  - ✅ Implemented PackageEvaluatorAgent with comprehensive scoring system
  - ✅ Added detailed risk assessment capabilities
  - ✅ Created affordability analysis based on user financial profile
  - ✅ Integrated cost efficiency evaluation and personalized recommendations

## Next Steps
- **Phase 5 - Callbacks, Artifacts & UI Enhancements:**
  - **Artifacts:** Persist amortization tables as CSV artifacts for later retrieval
  - **UI Enhancements:** Implement chart/table rendering for package comparisons
  - **Callbacks:** Add request/response tracing and performance metrics
- **Phase 6 - Full Recommendation Workflow:**
  - **Orchestration:** Implement the complete recommendation workflow
  - **Document Generation:** Add capability for generating application documents
  - **Semantic RAG:** Swap in an embeddings vector store for more robust retrieval
  - **Enhanced UX:** Further improve personalized advice based on financial profile