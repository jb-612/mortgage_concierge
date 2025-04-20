# ChromaDB Integration Plan

This document outlines a detailed step-by-step plan to integrate the standalone `chroma-mcp` service into the Mortgage Concierge agent, enabling semantic retrieval over bank policy documents via ADK’s HTTP tool support.

## Objectives
1. Leverage `chroma-mcp` as a separate MCP service (in-memory or HTTP client) without adding Docker complexity for local development.
2. Replace or augment the existing `search_bank_docs` FunctionTool with a Chroma‑backed HTTP tool for semantic RAG.
3. Keep the existing single LLM agent (`root_agent`) intact for now; defer sub‑agent refactoring until retrieval logic grows.

## Prerequisites
- Mortgage Concierge repo cloned and setup (`pip install -r requirements.txt`).
- `chroma-mcp` code present under project root (or installable via `pip install -e mortgage-chroma-mcp`).
- ADK CLI installed (`pip install google-adk`) and configured.
- Familiarity with ADK Function and MCP tool docs:
  - `_docs/adk-docs/docs/tools/function-tools.md`
  - `_docs/adk-docs/docs/tools/mcp-tools.md`
- OpenAI or other embedding API keys set in environment for `chroma-mcp`.
  
### Configuration (Ports)
Before launching services locally, set or export your preferred ports to avoid collisions:

```bash
# ADK core services
export ADK_API_PORT=8008      # default ADK API server port
export ADK_WEB_PORT=3008      # default ADK Web UI port

# Chroma MCP HTTP endpoint
export CHROMA_MCP_HOST=localhost
export CHROMA_MCP_PORT=8000   # default Chroma MCP HTTP port
```

When running via ADK CLI or uvicorn, reference these variables. For example:

```bash
adk run mortgage_concierge --port $ADK_API_PORT
adk web --port $ADK_WEB_PORT
adk run chroma-mcp --client-type http --host $CHROMA_MCP_HOST --port $CHROMA_MCP_PORT
```
  
## High‑Level Workflow
1. **Launch Chroma MCP Service**
   - Run locally via ADK:
     ```bash
     adk run chroma-mcp --client-type http --host localhost --port 8000
     ```
   - Confirm service is listening on `http://localhost:8000`.
2. **Register HTTP FunctionTool**
   - In `mortgage_concierge/agent.py`, add:
     ```python
     from google.adk import HttpTool

     chroma_search_tool = HttpTool(
         name="chroma_search_docs",
         description="Semantic search over bank policy via Chroma MCP",
         endpoint="http://localhost:8000/query_documents"
     )
     ```
   - Include `chroma_search_tool` in the agent’s tools list alongside `store_state` and `list_loan_tracks`.
3. **Document Ingestion**
   - Option A: On agent startup, scan `BANK_DOCS_PATH`, chunk each file, and call:
     ```python
     await mcp.call_tool("chroma_create_collection", {"collection_name": "bank_policy"})
     await mcp.call_tool("chroma_add_documents", {"collection_name": "bank_policy", "documents": chunks, "ids": ids})
     ```
   - Option B: Expose a custom FunctionTool (`upload_bank_docs_to_chroma`) that the agent can invoke once to ingest all docs.
4. **Prompt & Tool Usage**
   - Modify `AGENT_INSTRUCTION` in `prompt.py` to reference `chroma_search_docs(query)` instead of `search_bank_docs`.
   - Ensure examples illustrate a function call:
     ```json
     {"name": "chroma_search_docs", "arguments": {"collection_name":"bank_policy", "query_texts":[user_query], "n_results":5}}
     ```
5. **Testing & Validation**
   - Start both services: `adk run chroma-mcp` and `adk run mortgage_concierge`.
   - Chat via CLI or Web UI, trigger a retrieval request (e.g. "What is the maximum loan-to-value ratio for FHA?") and verify semantic results.
   - Add unit tests in `tests/` mocking the HTTP endpoint or using a real ephemeral client.
6. **Fallback & Rollback**
   - Retain `search_bank_docs` implementation for keyword fallback if the Chroma service is unavailable.
   - In the agent’s error handler, catch HTTP failures and route to `search_bank_docs`.

## Future Enhancements
- **Sub‑Agent**: If retrieval logic becomes complex (query rewriting, reranking, multi‑step filtering), extract a `retrieval_agent` to encapsulate semantic RAG.
- **Dynamic Uploads**: Add an `/upload` HTTP endpoint in `chroma-mcp` and expose a matching FunctionTool to ingest new documents at runtime.
- **Persistence**: Switch `chroma-mcp` client type from `ephemeral` to `persistent` for production safety.
- **Security**: Secure the HTTP endpoint (mTLS or API keys) when exposing beyond localhost.

---
_Last updated: YYYY-MM-DD_