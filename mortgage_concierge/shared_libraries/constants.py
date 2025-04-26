"""
Constants for state keys and other shared values.
"""
import os

# State management keys
PROFILE_KEY = "user_profile"
"""
Key under which the BorrowerProfile is stored in session.state.
"""

# LLM model defaults
DEFAULT_MODEL_ID = os.getenv("MORTGAGE_MODEL", os.getenv("OPENAI_MODEL", "openai/gpt-4"))
"""
Default model ID to use for agents when no specific model is provided.
"""

# Session state keys for loan calculations
LOAN_CALCULATION_GUID_KEY = "loan_calculation_guid"
LOAN_INITIAL_RESULTS_KEY = "loan_initial_results"
LOAN_SELECTED_TRACK_KEY = "loan_selected_track"
LOAN_CUSTOM_RATE_KEY = "loan_custom_rate"
LOAN_CUSTOM_TERM_KEY = "loan_custom_term"
PROPOSED_PACKAGES_KEY = "proposed_packages"