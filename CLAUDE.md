# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands

### Using uv (Recommended)
- Create virtual environment: `uv venv`
- Install dependencies: `uv pip install -r requirements.txt`
- Install ADK CLI: `uv pip install "google-adk[cli]"`
- Run all tests: `uv run python -m pytest tests/`
- Run a single test: `uv run python -m pytest tests/unit/test_loan_calculator.py::test_fallback_mode_loads_file -v`
- Run tests with specific pytest mark: `uv run python -m pytest -m asyncio`
- Activate environment: `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
- Run the agent locally via ADK CLI: `adk run mortgage_concierge`
- Run the web UI: `adk web` (then select mortgage_concierge from dropdown)
- Run API server: `adk api_server mortgage_concierge`

### Using pip (Alternative)
- Create virtual environment: `python -m venv .venv`
- Activate environment: `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
- Install dependencies: `pip install -r requirements.txt`
- Install ADK CLI: `pip install "google-adk[cli]"`
- Run all tests: `pytest tests/`
- Run a single test: `pytest tests/unit/test_loan_calculator.py::test_fallback_mode_loads_file -v`
- Run tests with specific pytest mark: `pytest -m asyncio`
- Run the agent locally via ADK CLI: `adk run mortgage_concierge`
- Run the web UI: `adk web` (then select mortgage_concierge from dropdown)
- Run API server: `adk api_server mortgage_concierge`

## Environment Setup
- Create `.env` file in project root with:
  ```
  # LLM model selection
  OPENAI_API_KEY=<your-openai-key>  # Or use Google AI/Vertex AI credentials
  MORTGAGE_MODEL=openai/gpt-4  # Optional override of default model
  
  # Paths to knowledge base
  BANK_DOCS_PATH=./_knowledge_base/bank_docs
  LOAN_TRACKS_PATH=./_knowledge_base/json/interest_tracks.json
  
  # Optional calculator API URLs
  CALCULATOR_API_URL=<calculator-api-url>  # For production
  RECALC_RATE_API_URL=<recalc-rate-api-url>  # For production
  RECALC_TERM_API_URL=<recalc-term-api-url>  # For production
  
  # For local development/testing, falls back to mock JSON files in tests/unit/data/
  ```

## Project Architecture
- **Bootstrap Pattern:** Uses `@lru_cache` in bootstrap.py to ensure one-time initialization
- **Memory Management:** 
  - Long-term knowledge stored in ADK's `InMemoryMemoryService`
  - Bank documents ingested at startup
  - Retrieved via `search_bank_docs` tool
- **Session State:**
  - User profile and calculation data stored in session state
  - Access via `tool_context.state` in tools
  - Follow session state naming conventions (e.g., `loan_calculation_guid`)
- **OpenAPI Integration:**
  - Loan calculator tools generated from `mortgage_concierge/openapi/loan_calculator.yaml` spec
  - Calculator endpoints require GUID for recalculation operations

## Code Style Guidelines
- Use Python 3.11+ features and typing
- Use uv for dependency management and virtual environments
- Import order: standard lib → third-party → local modules (separated by blank lines)
- Use `snake_case` for functions/variables, `PascalCase` for classes
- Document with docstrings (use type annotations instead of docstring types)
- Use Pydantic for data models and validation
- Use `lru_cache` for expensive operations that can be cached
- Error handling: use specific exceptions in try/except blocks
- Prefer f-strings for string formatting
- Keep model initialization and configuration in agent.py
- Use constants.py for shared constants
- Tools should follow ADK guidelines:
  - Clear function names that indicate purpose
  - Descriptive docstrings explaining purpose, usage context and return values
  - Return dictionaries with status field ("ok"/"error") for consistent error handling
  - Use `tool_context` parameter to access session state
  - Store/retrieve state via `tool_context.state` dictionary

## Session State Conventions
When managing calculator state, use these state keys:
- `loan_calculation_guid` - Store the GUID from initial calculation
- `loan_initial_results` - Store complete calculation results
- `loan_selected_track` - Store selected loan track information
- `loan_custom_rate` - Store any custom rate specified by user
- `loan_custom_term` - Store any custom term requested by user