"""
Tool for searching ingested bank policy documents in memory.
"""
import os
from google.adk.tools import FunctionTool, ToolContext
from mortgage_concierge.shared_libraries.memory_store import memory_service

def _search_bank_docs_impl(query: str, tool_context: ToolContext) -> dict:
    # Search the ingested bank documents in memory_service
    try:
        # Search the documents ingested under the 'system' user
        response = memory_service.search_memory(
            app_name="mortgage_advisor",
            user_id="system",
            query=query,
        )
    except Exception as exc:
        return {"error": f"Memory search failed: {exc}"}

    # Build results from SearchMemoryResponse.memories (MemoryResult items)
    results: list[dict[str, str]] = []
    for mem in getattr(response, "memories", []):
        session_id = getattr(mem, "session_id", "unknown")
        # mem.events is a list of Event objects
        for ev in getattr(mem, "events", []):
            snippet = ""
            if ev.content and ev.content.parts:
                # Concatenate all text parts of the event
                text = "".join(
                    part.text for part in ev.content.parts if hasattr(part, 'text') and part.text
                )
                snippet = text[:200]
            results.append({
                "file": session_id,
                "snippet": snippet,
            })
    return {"results": results}

_search_bank_docs_impl.__name__ = "search_bank_docs"
search_bank_docs = FunctionTool(_search_bank_docs_impl)