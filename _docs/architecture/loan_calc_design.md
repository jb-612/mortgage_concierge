  Below is a proposed phased design for rolling out your real‐calculator integration, complete with
    test‐fallbacks, incremental API coverage, and an eventual sub‑agent architecture to orchestrate
    multi‐track simulations and recommendations.

    ----------------------------------------------------------------------------------------------------------
    ---

    # Mortgage Concierge – Loan Calculator Integration  

    ## 1. Overview & Goals  

    We currently have a mock loan_calculator_tool that returns hard‑coded JSON for one scenario. Our end goal
    is to:

    • Replace the mock with real calls to three REST endpoints
      – POST /api/calculate‑loan
      – POST /api/recalculate‑rate
      – POST /api/recalculate‑term
    • Provide a seamless fallback to the existing mock JSON during local/offline development
    • Build up from single‑call integration to a full “multi‑track” simulation sub‑agent + evaluator
    • Leverage ADK’s FunctionTools, OpenAPI tooling, ToolContext callbacks, Artifacts & Sessions

    ## 2. Application Prerequisites  

    • The calculator service is running on http://localhost:8001 and hosts:
      – /api/calculate‑loan – takes {amount, termYears} → returns loan details
      – /api/recalculate‑rate – takes {amount, termYears, overrideRate} → returns new payment details
      – /api/recalculate‑term – takes {amount, desiredPayment, interestRate} → returns feasible term and
    payment
    • Add requests to your service dependencies
    • Ensure .env contains LOAN_CALCULATOR_API_URL=http://localhost:8001/api/calculate‑loan

    ## 3. Phase 1 – Single‑Endpoint Integration  

    3.1. Extract mock JSON
      • Copy the existing mock response for amount=500000, termYears=20 into
    tests/unit/data/calculator_mock.json
      • In your unit tests, load that file to drive fallback scenarios
    3.2. Tool Implementation
      • In mortgage_concierge/tools/loan_calculator.py, update loan_calculator_tool to:
        – Read LOAN_CALCULATOR_API_URL env var.
        – If set, POST { amount, termYears } and return { status: 'ok', data: <response> }.
        – On network/JSON errors, log and return { status: 'error', error_message: … }.
        – Else (no URL), load the mock JSON from tests/unit/data/… and return it as before.
    3.3. Tests
      • Write pytest cases that:
        – Monkeypatch requests.post to return a fake Response with a minimal payload.
        – Assert that the tool returns status: ok and correct parsed fields.
        – With no LOAN_CALCULATOR_API_URL, assert it loads the mock JSON fallback.

    ## 4. Phase 2 – Recalculation Endpoints  

    4.1. New FunctionTools
      • recalculate_rate_tool(amount: float, termYears: int, overrideRate: float) → dict
      • recalculate_term_tool(amount: float, desiredPayment: float, interestRate: float) → dict
    4.2. Env & Configuration
      • Introduce RECALC_RATE_API_URL and RECALC_TERM_API_URL (or derive from a base URL + path)
    4.3. Prompts & Instructions
      • Update prompt.py Phase 4 snippet to instruct the agent when to call each recalculation tool.
    4.4. Tests
      • Extract minimal mock JSONs into tests/unit/data/recalc_rate_mock.json and recalc_term_mock.json.
      • Test both success and error paths.

    ## 5. Phase 3 – Advanced Multi‑Track Simulation (Sub‑Agent Architecture)  

    5.1. Custom Sub‑Agent
      • Create a new LoanSimulationAgent (see ADK Custom Agents guide) responsible for:
        1. Receiving a list of (amount, term, trackType, overrideRate?) specs
        2. Calling the appropriate calculator/recalc tools for each track in parallel or sequence
        3. Aggregating the outputs into a single MortgagePackage object
        4. Returning the list of packages to the root agent
    5.2. Root → Sub‑Agent Tool
      • Wrap LoanSimulationAgent in an AgentTool (per ADK’s agents‑as‑tools docs)
    5.3. State & Artifacts
      • Store each simulation’s amortization schedule as an artifact (via tool_context.save_artifact)
      • Persist overall package proposals in session.state['proposed_packages']
    5.4. Evaluator Sub‑Agent
      • Build a second sub‑agent PackageEvaluatorAgent to score packages based on risk, payments, total
    interest
      • Root agent transfers control to evaluator once the user selects one or more samples

    ## 6. Phase 4 – Callbacks, Artifacts & UI Enhancements  

    6.1. Callbacks
      • Use a before_tool_callback to stamp each outgoing request with a trace ID
      • Use an after_tool_callback to log performance metrics
    6.2. Artifacts
      • Persist large amortization tables as CSV artifacts for later retrieval
      • In web UI, hook into ADK’s artifact renderer to display charts/tables
    6.3. Sessions
      • Leverage SessionService so a returning user sees their previous proposed_packages

    ## 7. Phase 5 – Full Recommendation Workflow  

    • Orchestrate the entire flow in the root agent:

        1. Profile gathering → `store_state_tool`
        2. Track listing → `list_loan_tracks`
        3. Single simulation → `calculator_tool`
        4. “What‑if” variations → `recalculate_*_tool`
        5. Multi‑track packages → `LoanSimulationAgent`
        6. Evaluation → `PackageEvaluatorAgent`
        7. Final recommendation & document generation (via artifacts/plugins)

    ## 8. Next Steps & Implementation Guide  

    • Kick off Phase 1 today:

        1. Create `tests/unit/data/calculator_mock.json`
        2. Update `loan_calculator_tool` per 3.2 above
        3. Add unit tests for live vs. mock calls
           • Once Phase 1 is green, branch into **Phase 2** (next week) for recalc endpoints
           • Schedule a design review for **Phase 3** (sub‑agent orchestration)
           • Throughout, consult:
             – ADK OpenAPI Tools (for future auto‑gen endpoints)
             – ADK Callbacks & Runtime docs (for observability)
             – ADK Sessions & Artifacts (for persistence & UI)
             – ADK Multi‑Agents & Custom‑Agents (for sub‑agent best practices)

    ----------------------------------------------------------------------------------------------------------
    ---