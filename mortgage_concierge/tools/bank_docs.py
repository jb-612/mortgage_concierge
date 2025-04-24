"""
Tool for searching ingested bank policy documents in memory.
"""
import os
import logging
from google.adk.tools import FunctionTool, ToolContext
from mortgage_concierge.shared_libraries.memory_store import memory_service

logger = logging.getLogger(__name__)

def _search_bank_docs_impl(query: str, tool_context: ToolContext) -> dict:
    """
    Search for information in the loaded bank policy documents.
    
    Args:
        query: The search query string
        tool_context: Tool invocation context containing session state
        
    Returns:
        dict: Result dictionary with status and results/error_message
            Format: {"status": "success", "results": [...]} 
            or {"status": "error", "error_message": "..."}
    """
    logger.info(f"Searching bank docs for: {query}")
    
    # Search the ingested bank documents in memory_service
    try:
        # Search the documents ingested under the 'system' user
        response = memory_service.search_memory(
            app_name="mortgage_advisor",
            user_id="system",
            query=query,
        )
    except Exception as exc:
        logger.error(f"Memory search failed: {exc}")
        return {
            "status": "error", 
            "error_message": f"Memory search failed: {exc}"
        }

    # Build results from SearchMemoryResponse.memories (MemoryResult items)
    results: list[dict[str, str]] = []
    for mem in getattr(response, "memories", []):
        session_id = getattr(mem, "session_id", "unknown")
        # Convert doc:filename.txt format to just filename
        file_name = session_id.replace("doc:", "") if session_id.startswith("doc:") else session_id
        
        # mem.events is a list of Event objects
        for ev in getattr(mem, "events", []):
            snippet = ""
            if ev.content and ev.content.parts:
                # Concatenate all text parts of the event
                text = "".join(
                    part.text for part in ev.content.parts if hasattr(part, 'text') and part.text
                )
                snippet = text[:300] + ("..." if len(text) > 300 else "")
            
            if snippet:  # Only add results with actual content
                results.append({
                    "file": file_name,
                    "snippet": snippet,
                })
    
    logger.info(f"Found {len(results)} results for query: {query}")
    return {
        "status": "success",
        "results": results
    }

_search_bank_docs_impl.__name__ = "search_bank_docs"
search_bank_docs = FunctionTool(_search_bank_docs_impl)