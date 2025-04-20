"""
Tool for simple text searching bank policy documents.
"""

import os
import glob

from google.adk.tools import FunctionTool, ToolContext

# Directory containing bank policy text files (configurable via env)
BANK_DOCS_PATH = os.getenv(
    "BANK_DOCS_PATH", os.path.join(os.getcwd(), "_knowledge_base", "bank_docs")
)


# Implementation: search for query in bank documents
def _search_bank_docs_txt_impl(query: str, tool_context: ToolContext) -> dict:
    """
    Search all .txt files under BANK_DOCS_PATH for the given query substring.
    Returns a list of matching snippets with filenames.
    """
    results = []
    q_lower = query.lower()
    # Determine files to search: directory (include .txt/.md) or single file
    filepaths = []
    if os.path.isdir(BANK_DOCS_PATH):
        for ext in ("*.txt", "*.md"):
            filepaths.extend(glob.glob(os.path.join(BANK_DOCS_PATH, ext)))
    elif os.path.isfile(BANK_DOCS_PATH):
        filepaths = [BANK_DOCS_PATH]
    else:
        return {"error": f"Bank docs path not found: {BANK_DOCS_PATH}"}

    for filepath in filepaths:
        try:
            text = open(filepath, encoding="utf-8").read()
        except Exception:
            continue
        text_lower = text.lower()
        idx = text_lower.find(q_lower)
        if idx < 0:
            continue
        # Extract snippet around match
        start = max(0, idx - 50)
        end = min(len(text), idx + len(query) + 50)
        snippet = text[start:end].replace("\n", " ")
        results.append({"file": os.path.basename(filepath), "snippet": snippet.strip()})
    return {"results": results}


# Expose as ADK FunctionTool; override name to match desired tool name
_search_bank_docs_txt_impl.__name__ = "search_bank_docs_txt"
search_bank_docs_txt = FunctionTool(_search_bank_docs_txt_impl)