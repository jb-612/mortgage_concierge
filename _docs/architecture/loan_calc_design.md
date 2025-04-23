  Below is a proposed phased design for rolling out your real‐calculator integration, complete with
    test‐fallbacks, incremental API coverage, and an eventual sub‑agent architecture to orchestrate
    multi‐track simulations and recommendations.

    ----------------------------------------------------------------------------------------------------------
    ---

    # Mortgage Concierge – Loan Calculator Integration  

    ## 1. Overview & Goals  

    We currently have a mock loan_calculator_tool that returns hard‑coded JSON for one scenario. Our end goal
    is to:

    • Replace the mock with real calls to three REST endpoints
      – POST /api/calculate‑loan
      – POST /api/recalculate‑rate
      – POST /api/recalculate‑term
    • Provide a seamless fallback to the existing mock JSON during local/offline development
    • Build up from single‑call integration to a full "multi‑track" simulation sub‑agent + evaluator
    • Leverage ADK's FunctionTools, OpenAPI tooling, ToolContext callbacks, Artifacts & Sessions

    ## 2. Application Prerequisites  

    • The calculator service is running on http://localhost:8001 and hosts:
      – POST /api/calculate‑loan – takes {amount, termYears} → returns loan details with a GUID
      – POST /api/recalculate‑rate – takes {guid, newRate} → returns updated calculation
      – POST /api/recalculate‑term – takes {guid, newTermYears} → returns updated calculation
    • Add requests to your service dependencies
    • Ensure .env contains LOAN_CALCULATOR_API_URL=http://localhost:8001/api/calculate‑loan
    • Maintain OpenAPI v3 spec at mortgage_concierge/openapi/loan_calculator.yaml and use ADK's OpenAPI integration to auto‑generate RestApiTool functions

    ## 3. Phase 1 – Single‑Endpoint Integration  

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
      • Alternatively, use load_loan_calculator_api_tools() in your agent to auto‑generate RestApiTool functions (calculateLoan, recalculateWithNewRate, recalculateWithNewTerm) from the OpenAPI spec.
    3.3. Tests
      • Write pytest cases that:
        – Monkeypatch requests.post to return a fake Response with a minimal payload.
        – Assert that the tool returns status: ok and correct parsed fields.
        – With no LOAN_CALCULATOR_API_URL, assert it loads the mock JSON fallback.

    ## 4. Phase 2 – Recalculation Endpoints and Session Management

    4.1. Session State Management
      • Store the calculation GUID in session state under a descriptive key:
        - `loan_calculation_guid` - The GUID returned from initial calculation
      • Store complete calculation results in session state:
        - `loan_initial_results` - Full LoanCalculation object including amortization schedule
      • Store user preferences in session state:
        - `loan_selected_track` - The selected loan track/product
        - `loan_custom_rate` - Any custom rate specified by the user
        - `loan_custom_term` - Any custom term requested by the user
    
    4.2. OpenAPI Tool Integration
      • Use the pre-defined RestApiTools generated from the OpenAPI spec:
        - `calculateLoan` - Call with amount and termYears
        - `recalculateWithNewRate` - Call with guid and newRate
        - `recalculateWithNewTerm` - Call with guid and newTermYears
      • If not using OpenAPI tools, update manual function signatures:
        - recalculate_rate_tool(guid: str, newRate: float, tool_context: ToolContext) → dict
        - recalculate_term_tool(guid: str, newTermYears: int, tool_context: ToolContext) → dict
      • Use tool_context to read/write session state in all calculator tools
    
    4.3. Background Calculation Process
      • Trigger initial calculation automatically after collecting amount and term
      • Extract and store the GUID and full calculation results in session state
      • Only display results when user explicitly asks for loan calculation
      • Check for existence of GUID in session state before attempting recalculations
    
    4.4. Env & Configuration
      • Update .env file to include base URL that all three API endpoints will use
      • Ensure LOAN_CALCULATOR_API_BASE_URL is used to override the OpenAPI server URL
    
    4.5. Prompts & Instructions
      • Update prompt.py to instruct the agent on the background calculation flow
      • Add instructions for when to use each recalculation tool
      • Include guidance on prompting user about rate/term alternatives
      • Explain how to retrieve and interpret the LoanCalculation object
    
    4.6. Tests
      • Extract minimal mock JSONs into tests/unit/data/recalc_rate_mock.json and recalc_term_mock.json
      • Ensure mock responses include valid GUID field
      • Test both success and error paths
      • Add tests for session state management with tool_context

    ## 5. Phase 3 – Advanced Multi‑Track Simulation (Sub‑Agent Architecture)  

    5.1. Custom Sub‑Agent
      • Create a new LoanSimulationAgent (see ADK Custom Agents guide) responsible for:
        1. Receiving a list of (amount, term, trackType, customRate?) specs
        2. Calling the appropriate calculator/recalc tools for each track in parallel or sequence
        3. Aggregating the outputs into a single MortgagePackage object
        4. Returning the list of packages to the root agent
    5.2. Root → Sub‑Agent Tool
      • Wrap LoanSimulationAgent in an AgentTool (per ADK's agents‑as‑tools docs)
    5.3. State & Artifacts
      • Store each simulation's amortization schedule as an artifact (via tool_context.save_artifact)
      • Persist overall package proposals in session.state['proposed_packages']
    5.4. Evaluator Sub‑Agent
      • Build a second sub‑agent PackageEvaluatorAgent to score packages based on risk, payments, total
    interest
      • Root agent transfers control to evaluator once the user selects one or more samples

    ## 6. Phase 4 – Callbacks, Artifacts & UI Enhancements  

    6.1. Callbacks
      • Use a before_tool_callback to stamp each outgoing request with a trace ID
      • Use an after_tool_callback to log performance metrics
    6.2. Artifacts
      • Persist large amortization tables as CSV artifacts for later retrieval
      • In web UI, hook into ADK's artifact renderer to display charts/tables
    6.3. Sessions
      • Leverage SessionService so a returning user sees their previous proposed_packages

    ## 7. Phase 5 – Full Recommendation Workflow  

    • Orchestrate the entire flow in the root agent:

        1. Profile gathering → `store_state_tool`
        2. Track listing → `list_loan_tracks`
        3. Background calculation → `calculateLoan` (store GUID in session)
        4. User-requested calculation display → retrieve from session state
        5. "What‑if" variations → `recalculateWithNewRate` and `recalculateWithNewTerm` using stored GUID
        6. Multi‑track packages → `LoanSimulationAgent`
        7. Evaluation → `PackageEvaluatorAgent`
        8. Final recommendation & document generation (via artifacts/plugins)

    ## 8. Next Steps & Implementation Guide  

    • Kick off Phase 2 today:

        1. Ensure OpenAPI tools are correctly generated from the spec and available to the agent
        2. Implement the session state management logic using tool_context
        3. Update the agent's prompts to handle the background calculation flow
        4. Add instructions on using the LoanCalculation response data effectively
        5. Ensure all three mock JSON files are present for testing
        6. Throughout, consult:
          – ADK Sessions documentation for state management best practices
          – ADK Tools documentation for tool_context usage
          – ADK OpenAPI Tools documentation for RestApiTool integration
          – ADK Multi‑Agents & Custom‑Agents (for sub‑agent best practices)

    ----------------------------------------------------------------------------------------------------------
    ---