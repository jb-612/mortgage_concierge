Below is an explanation of how our Mortgage Concierge agent ingests bank policy documents into memory, provides search over them, and manages session state. We then suggest next steps to create a sub-agent for enhanced retrieval.

---

### 1. Bootstrapped Memory Ingestion (bootstrap.py)
**Purpose:**  
- The bootstrap module provides a cached initialization approach using `@lru_cache(maxsize=None)`. 
- The `init()` function loads environment variables and triggers document ingestion.
- The `ingest_bank_docs_to_memory()` function (in memory_ingestion.py) scans `BANK_DOCS_PATH` (defaults to `_knowledge_base/bank_docs`), reads all `.txt` and `.md` files, creates a system session per file via `InMemorySessionService`, and stores the content as events in the global `InMemoryMemoryService`.

**Role in the Solution:**  
- Ensures that bank policy documents are ingested exactly once per process runtime.
- Provides a clean separation between initialization and usage.
- Supports the ADK memory service pattern for long-term knowledge storage.

---

### 2. Document Search (`tools/bank_docs.py`)
**Purpose:**  
- Implements `search_bank_docs(query)` as an ADK `FunctionTool`.  
- Calls the global `memory_service.search_memory(app_name="mortgage_advisor", user_id="system", query=query)`
  to retrieve matching `MemoryResult` entries and extracts up to 200 characters of snippet text from each event.

**Role in the Solution:**  
- Enables the agent to ground its advice in factual policy snippets, supporting retrieval-augmented answers.
- This tool is explicitly referenced in `AGENT_INSTRUCTION` when the model needs bank policy details.
- Follows the ADK pattern for tool usage with a clear docstring explaining when to use the tool.

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

### 4. Agent Integration (`agent.py`)
**How It Ties Together:**  
- The agent file loads environment variables and configures the model.
- The OpenAPI tools for loan calculator endpoints are loaded via `load_loan_calculator_api_tools()`.
- The `Agent` is initialized with all necessary tools:
  - `store_state_tool` for phase 1 profiling and calculator state management.
  - `search_bank_docs` for document retrieval.
  - `list_loan_tracks` for listing available loan products.
  - OpenAPI-generated REST API tools for loan calculations.

**Overall Flow:**  
1. **Startup:** Bootstrap's `init()` runs once via import or explicit call, configuring environment and populating the memory service.
2. **Phase 1 Conversation:**
   - The model asks for profile fields; after each, it invokes `store_state`.
3. **Retrieval Calls:**
   - When instructions specify, the model emits a `search_bank_docs` function call.
   - The tool returns policy snippets; the LLM's next generation uses them for grounded answers.
4. **Phase 2 Calculations (Planned):**
   - The agent will automatically trigger `calculateLoan` and store results in session state.
   - When requested, it will display results from session state.
   - For "what-if" scenarios, it will use `recalculateWithNewRate` and `recalculateWithNewTerm` with the stored GUID.

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
  The `@lru_cache` decorator ensures optimal performance by preventing redundant document ingestion, following the singleton pattern.

– **State Management:**  
  Session state is correctly managed via the `ToolContext` pattern, providing a clean interface for tools to share information.

– **OpenAPI Integration:**  
  The use of ADK's OpenAPI tooling to generate REST API tools follows best practices for external service integration.

---

### Next Steps: Enhanced Retrieval and Calculator Integration

1. **Phase 2 Loan Calculator Implementation:**
   - Update the prompt to use background calculation after profile collection
   - Implement session state storage for loan calculation results
   - Add user prompting for rate/term alternatives

2. **Enhanced Semantic Retrieval:**
   - Implement a `retrieval_agent` that:
     - Uses embeddings to vectorize queries and document chunks
     - Calls a vector-store-backed `search_memory` (e.g., `ChromaDB` as in mortgage-chroma-mcp)
     - Returns top‑k context snippets to the main agent
   - Integration options:
     - Standalone service with API endpoints
     - Sub-agent accessed via an agent tool

3. **Session‑Aware Retrieval:**
   - Leverage `tool_context.state` (e.g., `user_profile`) to personalize retrieval
   - Filter policies by relevance to borrower's specific situation
   - Combine session state with loan calculation results for targeted advice

By enhancing both the calculator integration and retrieval capabilities, the mortgage advisor can provide more personalized, context-aware financial guidance.