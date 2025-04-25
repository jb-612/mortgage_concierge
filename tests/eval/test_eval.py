# Copyright 2025 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Evaluation tests for the mortgage concierge agent."""

import pathlib
import glob
import os

import dotenv
from google.adk.evaluation import AgentEvaluator
import pytest


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


def test_loan_calculator():
    """Test the agent's ability to calculate mortgage loans."""
    AgentEvaluator.evaluate(
        "mortgage_concierge",
        str(pathlib.Path(__file__).parent / "data/loan_calculator.evalset.json"),
        num_runs=4
    )


def test_recorded_sessions():
    """Test the agent with recorded web sessions if they exist."""
    # Get all recorded sessions in the data/recorded-sessions directory
    recorded_sessions_dir = pathlib.Path(__file__).parent / "data/recorded-sessions"
    if not recorded_sessions_dir.exists():
        pytest.skip("No recorded sessions found")
    
    session_files = list(recorded_sessions_dir.glob("*.evalset.json"))
    if not session_files:
        pytest.skip("No recorded sessions found")
    
    # Run the evaluation for each session file
    for session_file in session_files:
        print(f"Testing with recorded session: {session_file.name}")
        AgentEvaluator.evaluate(
            "mortgage_concierge",
            str(session_file),
            num_runs=1  # Only need to run once for recorded sessions
        )