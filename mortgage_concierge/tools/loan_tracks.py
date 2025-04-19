"""
Tool for listing available loan track options from a JSON file.
"""
import os
import json

from google.adk.tools import FunctionTool, ToolContext

# Path to the loan tracks JSON file (configurable via env)
LOAN_TRACKS_PATH = os.getenv(
    "LOAN_TRACKS_PATH",
    os.path.join(os.getcwd(), "_knowledge_base", "loan_tracks.json")
)

# Implementation: load and list loan track options
def _list_loan_tracks_impl(tool_context: ToolContext) -> dict:
    """
    Load and return all loan track entries from the JSON file.
    """
    if not os.path.isfile(LOAN_TRACKS_PATH):
        return {"error": f"Loan tracks file not found: {LOAN_TRACKS_PATH}"}
    try:
        with open(LOAN_TRACKS_PATH, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return {"error": str(e)}
    return {"loan_tracks": data}

# Expose as ADK FunctionTool; override name for consistency
_list_loan_tracks_impl.__name__ = "list_loan_tracks"
list_loan_tracks = FunctionTool(_list_loan_tracks_impl)