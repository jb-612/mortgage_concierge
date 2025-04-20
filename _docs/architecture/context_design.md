Below is an explanation of how our Mortgage Concierge agent ingests bank policy documents into memory, provides search over them, and manages session state. We then suggest next steps to create a sub-agent for enhanced retrieval.

---

### 1. Memory Ingestion (memory_ingestion.py)
**Purpose:**  
- At agent startup, `mortgage_concierge.agent` calls `ingest_bank_docs_to_memory()`.  
- This function scans `BANK_DOCS_PATH` (defaults to `_knowledge_base/bank_docs`), reads all `.txt` and `.md` files,
  creates a system session per file via `InMemorySessionService`, and stores the content as events in the global
  `InMemoryMemoryService`.

**Role in the Solution:**  
- Ensures that all bank policy documents are available in the in-memory store before any user interaction.
- Provides the basis for contextual, retrieval-augmented generation by making document contents queryable.

---

### 2. Document Search (`tools/bank_docs.py`)
**Purpose:**  
- Implements `search_bank_docs(query)` as an ADK `FunctionTool`.  
- Calls the global `memory_service.search_memory(app_name="mortgage_advisor", user_id="system", query=query)`
  to retrieve matching `MemoryResult` entries and extracts up to 200 characters of snippet text from each event.

**Role in the Solution:**  
- Enables the agent to ground its advice in factual policy snippets, supporting retrieval-augmented answers.
- This tool is explicitly called in `AGENT_INSTRUCTION` when the model needs bank policy details.

---

### 3. State Persistence (`tools/store_state.py`)
**Purpose:**  
- Provides `store_state(state: dict, tool_context)`, merging the given `state` dict into `tool_context.state`.

**Role in the Solution:**  
- Used by the agent (phase 1) to `memorize` each borrower profile field into session state under the `user_profile` key.
- Supports passing structured data (e.g. `BorrowerProfile`) between conversational turns.
  
---

### 4. Agent Integration (`agent.py`)
**How It Ties Together:**  
- At import time, `ingest_bank_docs_to_memory()` is called to load the knowledge base.
- The `Agent` is initialized with tools:
  - `store_state_tool` for phase 1 profiling.
  - `search_bank_docs` for document retrieval.
  - `list_loan_tracks` for listing available loan products.
  - (Future) sub-agents or additional tools.

**Overall Flow:**  
1. **Startup:**  memory ingestion runs once, populating the memory_service.
2. **Phase 1 Conversation:**
   - The model asks for profile fields; after each, it invokes `store_state`.
3. **Retrieval Calls:**
   - When instructions specify, the model emits a `search_bank_docs` function call.
   - The tool returns policy snippets; the LLM’s next generation uses them for grounded answers.

---

### Complementary Roles

These components provide a cohesive retrieval-augmented workflow:
- **Ingestion (memory_ingestion):** Bootstraps KB content into memory.
- **Retrieval (search_bank_docs):** Keyword‑based recall of policy snippets.
- **State (store_state):** Persists borrower profile and any interim data.
- **Product Listing (list_loan_tracks):** Static retrieval of loan configuration.

---

### Final Considerations

– **Ensure Sequence:**  
  Make sure that the ingestion tool (upload_bank_docs_tool) is triggered before any search requests are made. This can be done as part of your session startup flow or via testing scripts.

– **State Management:**  
  The use of the tool_context.state to cache the memory service is a good design choice, ensuring that you aren’t reinitializing the memory service unnecessarily.

– **Agent Registration:**  
  The agent configuration in agent.py correctly registers all these tools so that they’re available to the agent at runtime.

---

### Next Steps: Enhanced Retrieval via a Sub‑Agent

To move beyond simple keyword lookup and improve relevance:
1. **Sub‑Agent for Semantic Retrieval:**
   - Implement a `retrieval_agent` that:
     - Uses embeddings (OpenAI or VertexAI) to vectorize queries and document chunks.
     - Calls a vector-store-backed `search_memory` or a specialized RAG retrieval tool (e.g., `in memory ChomaDB`).
     - Returns top‑k context snippets to the main agent.
2. **Query Expansion & Refinement:**
   - Wrap user questions in a small LLM chain to rephrase or expand keywords before search.
   - Integrate as a lightweight tool or in a callback to improve hit rates.
3. **Session‑Aware Retrieval:**
   - Leverage `tool_context.state` (e.g., `user_profile`) to bias retrieval (e.g., only show policies relevant to the borrower’s credit range).

By layering a dedicated retrieval sub-agent, you can achieve true semantic RAG, ensuring that your mortgage advisor leverages the full richness of your policy documents for accurate, context‑aware answers.

