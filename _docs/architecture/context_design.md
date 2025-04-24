Below is an explanation of how our Mortgage Concierge agent ingests bank policy documents into memory, provides search over them, and manages session state. We then suggest next steps to create a sub-agent for enhanced retrieval.

---

### 1. Bootstrapped Memory Ingestion (bootstrap.py and __init__.py)
**Purpose:**  
- The bootstrap module provides a cached initialization approach using `@lru_cache(maxsize=None)`. 
- The `init()` function loads environment variables and triggers document ingestion.
- The `ingest_bank_docs_to_memory()` function (in memory_ingestion.py) scans `BANK_DOCS_PATH` (defaults to `_knowledge_base/bank_docs`), reads all `.txt` and `.md` files, creates a system session per file via `InMemorySessionService`, and stores the content as events in the global `InMemoryMemoryService`.
- Package `__init__.py` calls bootstrap.init() at import time, following ADK best practices.

**Role in the Solution:**  
- Ensures that bank policy documents are ingested exactly once per process runtime.
- Provides a clean separation between initialization and usage.
- Avoids import-time side effects in core agent modules.
- Handles initialization errors with proper logging.
- Supports the ADK memory service pattern for long-term knowledge storage.

---

### 2. Document Search (`tools/bank_docs.py`)
**Purpose:**  
- Implements `search_bank_docs(query)` as an ADK `FunctionTool`.  
- Calls the global `memory_service.search_memory(app_name="mortgage_advisor", user_id="system", query=query)`
  to retrieve matching `MemoryResult` entries and extracts up to 300 characters of snippet text from each event.
- Returns standardized results format with `status` field: `{"status": "success", "results": [{"file": "...", "snippet": "..."}]}`
- Includes proper error handling and logging.

**Role in the Solution:**  
- Enables the agent to ground its advice in factual policy snippets, supporting retrieval-augmented answers.
- This tool is explicitly referenced in `AGENT_INSTRUCTION` when the model needs bank policy details.
- Follows the ADK pattern for tool usage with a clear docstring explaining when to use the tool.
- Documents are stored with session_id format `doc:{filename}` and retrieved with this prefix.

---

### 3. State Persistence (`tools/store_state.py`)
**Purpose:**  
- Provides `store_state(state: dict, tool_context)`, merging the given `state` dict into `tool_context.state`.
- Uses the ADK `ToolContext` parameter to access session state.

**Role in the Solution:**  
- Used by the agent (phase 1) to memorize each borrower profile field into session state.
- Supports passing structured data (e.g. `BorrowerProfile`) between conversational turns.
- Will be extended to store loan calculation results (e.g. `loan_calculation_guid`, `loan_initial_results`) in Phase 2.
  
---

### 4. Agent Integration (`__init__.py` and `agent.py`)
**How It Ties Together:**  
- The package's `__init__.py` calls `bootstrap.init()` to ensure docs are loaded before agent use.
- The agent file (`agent.py`) configures the model with no import-time side effects.
- The OpenAPI tools for loan calculator endpoints are loaded via `load_loan_calculator_api_tools()`.
- The `Agent` is initialized with all necessary tools:
  - `store_state_tool` for phase 1 profiling and calculator state management.
  - `search_bank_docs` for document retrieval.
  - `list_loan_tracks` for listing available loan products.
  - OpenAPI-generated REST API tools for loan calculations.

**Overall Flow:**  
1. **Startup:** Bootstrap's `init()` runs from `__init__.py` when imported by ADK, configuring environment and populating the memory service.
2. **Phase 1 Conversation:**
   - The model asks for profile fields; after each, it invokes `store_state`.
3. **Retrieval Calls:**
   - When instructions specify, the model emits a `search_bank_docs` function call.
   - The tool returns policy snippets in a standardized format: `{"status": "success", "results": [{"file": "...", "snippet": "..."}]}`.
   - The LLM's next generation uses these snippets for grounded answers.
4. **Phase 2 Calculations:**
   - The agent automatically triggers `loan_calculator_tool` and stores results in session state.
   - When requested, it displays results from session state.
   - For "what-if" scenarios, it uses `recalculate_rate_tool` and `recalculate_term_tool` with the stored GUID.

---

### Memory & State Architecture

The implementation follows ADK's memory and state architecture:

1. **Long-Term Knowledge (Memory):**
   - Bank policy documents and rules are stored in the `memory_service`
   - These are ingested at startup and remain available throughout the process lifecycle
   - Accessed via `search_bank_docs` for retrieval-augmented generation

2. **Session State (ToolContext.state):**
   - Borrower profile data stored via `store_state_tool`
   - Session-specific values like `loan_calculation_guid` and results
   - User preferences like selected loan tracks

3. **Tool Context Usage:**
   - Tools access shared session state via the `tool_context` parameter
   - This follows the ADK pattern for tools to read/write state as needed

---

### Final Considerations

– **Bootstrap Optimizations:**  
  The `@lru_cache` decorator ensures optimal performance by preventing redundant document ingestion, following the singleton pattern. The bootstrap is properly triggered via `__init__.py` at package import time.

– **State Management:**  
  Session state is correctly managed via the `ToolContext` pattern, providing a clean interface for tools to share information.

– **OpenAPI Integration:**  
  The use of ADK's OpenAPI tooling to generate REST API tools follows best practices for external service integration.

– **Testing Support:**
  The `test_bank_docs.py` script provides a way to verify that documents are properly loaded and searchable, supporting easy debugging and validation.

---

### Next Steps: Enhanced Retrieval and Calculator Integration

1. **Phase 2 Loan Calculator Integration (Completed):**
   - ✅ Update the prompt to use background calculation after profile collection
   - ✅ Implement session state storage for loan calculation results
   - ✅ Add user prompting for rate/term alternatives
   - ⬜ Complete eligibility checks based on bank policy rules

2. **Enhanced Semantic Retrieval:**
   - Implement a `retrieval_agent` that:
     - Uses embeddings to vectorize queries and document chunks
     - Calls a vector-store-backed `search_memory` (e.g., `ChromaDB` as in mortgage-chroma-mcp)
     - Returns top‑k context snippets to the main agent
   - Integration options:
     - Standalone service with API endpoints
     - Sub-agent accessed via an agent tool
   - Leverage the existing bootstrap mechanism for proper initialization

3. **Session‑Aware Retrieval:**
   - Leverage `tool_context.state` (e.g., `user_profile`) to personalize retrieval
   - Filter policies by relevance to borrower's specific situation
   - Combine session state with loan calculation results for targeted advice

4. **Testing and Validation (Initiated):**
   - ✅ Create basic test scripts for document search and retrieval
   - ⬜ Add comprehensive test cases that validate all agent tools
   - ⬜ Implement integration tests that verify end-to-end flows

By enhancing both the calculator integration and retrieval capabilities, the mortgage advisor can provide more personalized, context-aware financial guidance. The proper bootstrapping implementation now ensures reliable document access throughout the agent lifecycle.