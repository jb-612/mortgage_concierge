---
title: "25-04-20 Mortgage Concierge: Import & Memory Search Fixes"
date: 2025-04-20
---

# Mortgage Concierge Agent: Issues Encountered & Resolutions

This document captures the key errors encountered while initializing and querying the bank-docs memory store in the `mortgage_concierge` agent, along with the changes applied to fix them.

## 1. Missing `google.adk.types.Event` Import
Error:
```text
ModuleNotFoundError: No module named 'google.adk.types'
```
Root Cause:
- ADK moved `Event` into the `google.adk.events` module.
Fix:
- In `shared_libraries/memory_ingestion.py`, changed:
  ```py
  from google.adk.types import Event
  ```
  to:
  ```py
  from google.adk.events import Event
  ```

## 2. Pydantic ValidationError for Missing `author`
Error:
```text
1 validation error for Event
author
  Field required [type=missing]
```
Root Cause:
- Constructed `Event` objects without supplying the required `author` field.
Fix:
- Added `author="system"` to all `Event(...)` calls in `memory_ingestion.py`.

## 3. Serialization Failure: Non-serializable Memory Service
Error:
```text
Unable to serialize unknown type: <class 'google.adk.memory.in_memory_memory_service.InMemoryMemoryService'>
```
Root Cause:
- The `search_bank_docs` tool was caching the `memory_service` instance in the `ToolContext.state`, causing the ADK telemetry serializer to encounter an unsupported type.
Fix:
- Removed storing `memory_service` in context state; always reference the module-level `memory_service` directly.

## 4. Incorrect `search_memory` Call Signature
Error:
```text
search_memory() takes 1 positional argument but 4 were given
```
Root Cause:
- `InMemoryMemoryService.search_memory` requires keyword-only args (`app_name=`, `user_id=`, `query=`).
Fix:
- Updated call in `tools/bank_docs.py`:
  ```py
  memory_service.search_memory(
      app_name="mortgage_advisor",
      user_id="system",
      query=query,
  )
  ```

## 5. AttributeError on `SearchMemoryResponse.get`
Error:
```text
'SearchMemoryResponse' object has no attribute 'get'
```
Root Cause:
- Treated the response as a plain dict with `response.get("results")`, but `SearchMemoryResponse` exposes `.memories`.
Fix:
- Iterate over `response.memories` (each a `MemoryResult`) and extract snippets from `mem.events`.

## 6. Empty Search Results due to `user_id` Mismatch
Issue:
- All searches returned no matches because the ingestion used `user_id="system"`, while the tool code was searching under `user_id="default_user"`.
Fix:
- Changed the `user_id` in the search call to `"system"` to align with ingestion.

---
End of session log for 2025-04-20.