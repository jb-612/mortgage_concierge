% README for Mortgage Concierge Agent
# Mortgage Concierge

This sample demonstrates the use of Google’s Agent Development Kit (ADK) to build a professional mortgage advisor.  
The agent conducts a step‑by‑step borrower profiling workflow, grounds its advice in real bank policy documents,  
and surfaces available loan repayment tracks.

## Overview

Borrower interactions are divided into two main phases:
1. **Phase 1 – Profile Gathering**  
   The agent asks for property value, down payment, income, debts, credit score, and risk tolerance.
   After each response it stores the value in session state via the `store_state` tool.
   Once all fields are captured, it confirms the information.
2. **Phase 2 – Loan Options & Eligibility**  
   (Planned) The agent will evaluate eligibility, present loan track options (via `list_loan_tracks`),
   and guide the borrower through application steps.

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
  - `root_agent` (in `mortgage_concierge/agent.py`): Orchestrates the borrower profiling flow.
- **Tools**  
  - `search_bank_docs` – semantic/keyword search over ingested bank policy docs.
  - `list_loan_tracks` – loads and returns loan track configurations from JSON.
  - `store_state` – persists arbitrary key/value pairs in session state.
- **Shared Libraries**  
  - `memory_ingestion` – reads `.txt`/`.md` docs into ADK’s in-memory memory service.
  - `memory_store` – global `InMemoryMemoryService` & `InMemorySessionService`.
  - `types.py` – Pydantic `BorrowerProfile` schema for session state.
- **Prompts**  
  - `AGENT_INSTRUCTION` defines the Phase 1 instruction template in `prompt.py`.

## Setup and Installation

### Prerequisites
- Python 3.11+  
- ADK CLI (`pip install google-adk`)  
- (Optional) OpenAI or other LLM provider credentials

### Clone and Install
```bash
git clone <your-repo-url>
cd <your-repo-root>
pip install -r requirements.txt
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
LOAN_TRACKS_PATH=./_knowledge_base/loan_tracks.json
```

## Running the Agent

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

## Testing
Run unit tests:
```bash
pytest tests/unit
```  

## Next Steps
- **Phase 2:** Implement eligibility checks and loan‐rate quoting.
- **Semantic RAG:** Swap in an embeddings vector store for more robust retrieval.
- **Sub‑agents:** Break out eligibility, comparison, and application into specialized agents.