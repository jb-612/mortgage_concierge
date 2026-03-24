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
- Run evaluation tests: `adk eval mortgage_concierge tests/eval/data/loan_calculator.evalset.json --config_file_path=tests/eval/data/test_config.json --print_detailed_results`

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
- Run evaluation tests: `python -m pytest tests/eval/test_eval.py -v`

## Tests to Run After Code Changes

After making code changes to specific components:

### Loan Calculator Components
```bash
# Unit tests
python -m pytest tests/unit/test_loan_calculator.py tests/unit/test_recalculate_tools.py

# Integration tests
python -m pytest tests/integration/test_loan_calculator_integration.py
```

### Sub-Agent Components
```bash
# Unit tests
python -m pytest tests/unit/test_simulation_tools.py tests/unit/test_evaluation_tools.py
```

### Run All Tests
```bash
# All unit tests
python -m pytest tests/unit/

# All integration tests
python -m pytest tests/integration/

# Evaluation tests
python -m pytest tests/eval/test_eval.py
```

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
- **Bootstrap Pattern:** 
  - Uses `@lru_cache` in bootstrap.py to ensure one-time initialization
  - Bootstrap is called from `__init__.py` to ensure docs are loaded before agent use
  - Following ADK best practice to avoid import-time side effects
  - Call `bootstrap.init()` explicitly before using the agent programmatically
- **Memory Management:** 
  - Long-term knowledge stored in ADK's `InMemoryMemoryService`
  - Bank documents ingested at startup via bootstrap.init()
  - Retrieved via `search_bank_docs` tool
  - Documents stored with session_id format `doc:{filename}`
- **Session State:**
  - User profile and calculation data stored in session state
  - Access via `tool_context.state` in tools
  - Follow session state naming conventions (e.g., `loan_calculation_guid`, `proposed_packages`)
- **Sub-Agent Architecture:**
  - Specialized agents for complex operations (LoanSimulationAgent, PackageEvaluatorAgent)
  - Sub-agents inherit from ADK's BaseAgent class
  - Each sub-agent has its own session and specialized tools
  - Sub-agents wrapped as function tools in the root agent
  - Results stored in session state for cross-agent data sharing
- **OpenAPI Integration:**
  - Loan calculator tools generated from `mortgage_concierge/openapi/loan_calculator.yaml` spec
  - Calculator endpoints require GUID for recalculation operations
- **Testing Framework:**
  - Unit tests in tests/unit/
  - Integration tests in tests/integration/
  - ADK Evaluation tests in tests/eval/ (using the ADK evaluation framework)

## Code Style Guidelines
- **Cyclomatic complexity cap**: CC <= 5 per function (enforced by `radon` hook; report violations during code review)
- **Auto-formatting**: `ruff format` + `ruff check --fix` (enforced by PostToolUse hook on every Edit/Write)
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

When working with package simulations and evaluations, use these state keys:
- `proposed_packages` - Dictionary of simulated mortgage packages keyed by package_id
- `package_evaluations` - Dictionary of package evaluations keyed by evaluation_id
- `amortization_artifacts` - Dictionary mapping calculation GUIDs to artifact IDs

## Development Workflow

All features follow a mandatory gated sequence. Do not skip gates.

1. **Feature Spec (GATE)** — `/feature-spec` creates `.workitems/PNN-FNN-<name>/`
2. **Design Review (GATE)** — `/design-review`, APPROVED verdict required
3. **Task Breakdown** — `/task-breakdown`, each task tagged [TDD] or [Eval-DD]
4. **Implementation**:
   - TDD tasks: `/tdd-task` — RED→GREEN→REFACTOR with 3-agent separation
   - Eval-DD tasks: `/eval-baseline` first, then `/prompt-tune`
5. **Code Review (GATE)** — `/code-review`, LGTM required
6. **Commit** — `/commit` with `Refs: PNN-FNN-TNN` traceability

### Exceptions
- Bug fixes may skip Feature Spec if referencing an existing workitem
- Documentation-only changes may skip Design Review
- Test-only changes may skip Design Review but must reference a workitem

## Quality Gates

### Automated (enforced by hooks)
- **Formatting**: `ruff format` — auto-applied after every Edit/Write
- **Linting**: `ruff check --fix` — auto-fixable issues resolved after every Edit/Write
- **Complexity**: `radon cc -s -n C` — functions with CC > 5 are blocked
- **Safety**: Dangerous commands (rm, sudo, force-push) blocked by hook

### Manual (enforced by skills)
- Tests must pass before commit (`uv run python -m pytest tests/unit/`)
- Eval scores must not regress below baseline
- No secrets in staged files
- Workitem must exist for production code changes

## ADK-Specific Conventions

### Prompt Engineering
Changes to agent instructions follow Eval-DD:
1. Capture eval baseline with `/eval-baseline`
2. Form hypothesis about expected behavioral improvement
3. Modify prompt (`prompt.py` or sub-agent instruction)
4. Run evals, compare scores against baseline
5. Accept only if scores improve or hold steady

### Eval Conventions
- Evalset format: JSON array of `{query, expected_tool_use, reference}`
- Thresholds: `tool_trajectory_avg_score >= 0.8`, `response_match_score >= 0.7`
- New behavioral features require new evalset entries
- NEVER lower thresholds without explicit justification

## Adversarial Testing

Use `/adversary <mode>` to stress-test the agent:
- `prompt-injection` — attempts to override instructions or extract system prompt
- `edge-case-borrower` — extreme financial profiles
- `conversation-stress` — rapid topic switching, contradictory requests
- `hallucination-probe` — requests for products not in knowledge base

Run adversarial suite after prompt changes. Record failures as new evalset entries.

## Workitem Structure

```
.workitems/
├── PLAN.md                       # Master feature checklist
└── PNN-FNN-<feature_name>/
    ├── design.md                 # Feature spec (APPROVED required)
    ├── tasks.md                  # Atomic tasks ([TDD] or [Eval-DD])
    └── eval-baseline.json        # Eval scores before changes
```

Naming: PNN=phase, FNN=feature, TNN=task. Example: P01-F02-T03.

## Available Skills

| Skill | Description |
|-------|-------------|
| `/feature-spec` | Create workitem folder with design and task templates |
| `/design-review` | Review design for completeness and ADK compliance |
| `/task-breakdown` | Decompose feature into atomic TDD/Eval-DD tasks |
| `/tdd-task` | Execute TDD RED-GREEN-REFACTOR with 3 agents |
| `/eval-baseline` | Capture ADK eval scores as regression baseline |
| `/prompt-tune` | Iterative prompt engineering with eval comparison |
| `/add-tool` | Scaffold new ADK tool with full TDD lifecycle |
| `/design-agent` | Design and implement new sub-agent |
| `/code-review` | Three-pass code review |
| `/commit` | Conventional commit with workitem traceability |
| `/conversation-designer` | Design conversation flows and state transitions |
| `/knowledge-curator` | Manage knowledge base documents |
| `/state-architect` | Audit and design session state contracts |
| `/eval-analyst` | Analyze eval results and identify failure patterns |
| `/adversary` | Adversarial testing with autoresearch-inspired loop |
| `/pdf-export` | Generate PDF from Markdown with Mermaid diagram pre-rendering |