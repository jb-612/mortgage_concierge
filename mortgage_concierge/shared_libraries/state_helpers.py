"""
Helper functions for managing session state in the mortgage concierge app.

These functions help ensure consistent state management across tool calls
and provide utilities for session state access and manipulation.
"""
import logging
from typing import Dict, Any, Optional
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

def ensure_session_state(
    key: str, 
    tool_context: ToolContext, 
    default_value: Any = None
) -> Any:
    """
    Ensures a key exists in the session state, returning its value or a default.
    
    Args:
        key: The state key to check for
        tool_context: The ADK tool context
        default_value: Value to set if key doesn't exist
        
    Returns:
        The value from the state, or the default if not found
    """
    if key not in tool_context.state:
        if default_value is not None:
            tool_context.state[key] = default_value
            logger.info(f"Initialized session state key '{key}' with default value")
        else:
            logger.warning(f"Session state key '{key}' not found and no default provided")
    
    return tool_context.state.get(key, default_value)

def get_loan_calculation_guid(tool_context: ToolContext) -> Optional[str]:
    """
    Retrieves the loan calculation GUID from session state.
    
    Args:
        tool_context: The ADK tool context
        
    Returns:
        The GUID string if found, None otherwise
    """
    return tool_context.state.get("loan_calculation_guid")

def get_user_profile(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieves the user profile from session state.
    
    Args:
        tool_context: The ADK tool context
        
    Returns:
        The user profile dictionary, or an empty dict if not found
    """
    return tool_context.state.get("user_profile", {})

def get_proposed_packages(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieves the proposed mortgage packages from session state.
    Initializes the state key if it doesn't exist.
    
    Args:
        tool_context: The ADK tool context
        
    Returns:
        Dictionary of packages keyed by package_id
    """
    return ensure_session_state("proposed_packages", tool_context, {})

def save_package_to_state(
    package_id: str, 
    package_data: Dict[str, Any], 
    tool_context: ToolContext
) -> None:
    """
    Saves a mortgage package to the session state.
    
    Args:
        package_id: Unique identifier for the package
        package_data: Package data to store
        tool_context: The ADK tool context
    """
    packages = get_proposed_packages(tool_context)
    packages[package_id] = package_data
    tool_context.state["proposed_packages"] = packages
    logger.info(f"Saved package '{package_id}' to session state")

def get_package_evaluation_results(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Retrieves package evaluation results from session state.
    Initializes the state key if it doesn't exist.
    
    Args:
        tool_context: The ADK tool context
        
    Returns:
        Dictionary of evaluation results keyed by evaluation_id
    """
    return ensure_session_state("package_evaluations", tool_context, {})