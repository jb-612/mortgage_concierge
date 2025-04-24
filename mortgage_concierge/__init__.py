# mortgage_concierge/__init__.py
#
# Entry point for ADK CLI (adk run mortgage_concierge)
#
# This file is imported by ADK when loading the agent package.
# It's important to initialize the bootstrap here to ensure bank docs
# are loaded before any agent interactions begin.

from mortgage_concierge.bootstrap import init
from mortgage_concierge.agent import root_agent

# Initialize the environment once before agent interactions begin
init("mortgage_advisor")

# Make the root_agent available for direct import
__all__ = ["root_agent"]
