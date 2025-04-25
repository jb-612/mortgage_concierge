#!/usr/bin/env python
"""
Script to run ADK-based integration tests for mortgage_concierge.
Requires the ADK API server to be running at http://0.0.0.0:8765.

Usage:
    1. Start ADK API server: adk api_server --port 8765
    2. Run this script: python tests/integration/run_adk_tests.py
"""
import os
import sys
import json
import time
import requests
from pathlib import Path

# Base URL for the ADK API server
BASE_URL = "http://0.0.0.0:8765"
APP_NAME = "mortgage_concierge"
USER_ID = "test_user_" + str(int(time.time()))
SESSION_ID = "test_session_" + str(int(time.time()))

def check_server_running():
    """Check if the ADK API server is running."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        return response.status_code == 200
    except requests.RequestException:
        return False

def create_session(initial_state=None):
    """Create a new session for testing."""
    if initial_state is None:
        initial_state = {}
    
    session_url = f"{BASE_URL}/apps/{APP_NAME}/users/{USER_ID}/sessions/{SESSION_ID}"
    session_payload = {"state": initial_state}
    
    try:
        response = requests.post(session_url, json=session_payload)
        if response.status_code != 200:
            print(f"Failed to create session: {response.text}")
            return False
        return True
    except requests.RequestException as e:
        print(f"Error creating session: {e}")
        return False

def send_query(query_text):
    """Send a query to the agent and return the response events."""
    run_url = f"{BASE_URL}/run"
    query_payload = {
        "app_name": APP_NAME,
        "user_id": USER_ID,
        "session_id": SESSION_ID,
        "new_message": {
            "role": "user",
            "parts": [{
                "text": query_text
            }]
        }
    }
    
    try:
        response = requests.post(run_url, json=query_payload)
        if response.status_code != 200:
            print(f"Failed to send query: {response.text}")
            return None
        return response.json()
    except requests.RequestException as e:
        print(f"Error sending query: {e}")
        return None

def extract_tool_calls(events):
    """Extract tool calls from events."""
    tool_calls = []
    for event in events:
        if event.get("content", {}).get("parts"):
            for part in event["content"]["parts"]:
                if part.get("functionCall"):
                    tool_call = {
                        "tool_name": part["functionCall"]["name"],
                        "tool_input": part["functionCall"]["args"]
                    }
                    tool_calls.append(tool_call)
    return tool_calls

def extract_responses(events):
    """Extract text responses from events."""
    responses = []
    for event in events:
        if event.get("content", {}).get("role") == "model" and event.get("content", {}).get("parts"):
            for part in event["content"]["parts"]:
                if part.get("text"):
                    responses.append(part["text"])
    return responses

def run_test_file(test_file_path):
    """Run a test file against the ADK API server."""
    # Load test file
    with open(test_file_path, 'r') as f:
        test_data = json.load(f)
    
    print(f"🧪 Running test file: {test_file_path}")
    
    # Create new session
    if not create_session({"user_profile": {}}):
        print("❌ Failed to create session")
        return False
    
    # Process each test case
    success = True
    for i, test_case in enumerate(test_data):
        print(f"\n📝 Test case {i+1}: {test_case['query'][:50]}...")
        
        # Send query
        events = send_query(test_case["query"])
        if events is None:
            print("❌ Failed to send query")
            success = False
            continue
        
        # Extract tool calls and responses
        tool_calls = extract_tool_calls(events)
        responses = extract_responses(events)
        
        # Verify expected tool use
        expected_tool_use = test_case.get("expected_tool_use", [])
        for j, expected_tool in enumerate(expected_tool_use):
            tool_name = expected_tool["tool_name"]
            
            # Check if tool was called
            matching_tools = [t for t in tool_calls if t["tool_name"] == tool_name]
            if not matching_tools:
                print(f"❌ Expected tool not called: {tool_name}")
                success = False
            else:
                print(f"✅ Tool called correctly: {tool_name}")
        
        # Print responses
        if responses:
            print(f"📣 Agent response: {responses[-1][:100]}...")
        else:
            print("❌ No agent response received")
            success = False
    
    return success

def main():
    """Main entry point for the test runner."""
    # Check if the ADK API server is running
    if not check_server_running():
        print("❌ ADK API server is not running at", BASE_URL)
        print("Please start the server with: adk api_server --port 8765")
        return 1
    
    # Get all test files
    script_dir = Path(__file__).parent
    test_files = list(script_dir.glob("*.test.json"))
    
    if not test_files:
        print("❌ No test files found in", script_dir)
        return 1
    
    # Run all test files
    all_success = True
    for test_file in test_files:
        if not run_test_file(test_file):
            all_success = False
    
    if all_success:
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())