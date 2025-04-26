"""
Loan Simulation sub-agent module.

This module contains the specialized agent for simulating multiple loan tracks
and creating mortgage packages.
"""
from mortgage_concierge.sub_agents.loan_simulation.agent import LoanSimulationAgent
from mortgage_concierge.sub_agents.loan_simulation.models import (
    LoanTrackSpecification,
    LoanCalculationResult,
    MortgageTrack,
    MortgagePackage
)