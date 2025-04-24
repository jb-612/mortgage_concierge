#!/usr/bin/env python
# Test script to verify that the agent is properly loaded and initialized

import asyncio
from google.adk.executors import execute_agent
from google.adk.events import Event
from google.genai.types import Content, Part

# Import bootstrap first to ensure docs are loaded
from mortgage_concierge.bootstrap import init
from mortgage_concierge.agent import root_agent

# Initialize environment before using the agent
init(app_name="mortgage_advisor")
print("✅ Bootstrap initialized")

# Test directly calling the bank docs tool
from mortgage_concierge.tools.bank_docs import _search_bank_docs_impl
from google.adk.tools import ToolContext

# Simple tool context for testing
class SimpleToolContext:
    def __init__(self):
        self.state = {}

async def test_bank_docs_tool():
    """Test the bank docs search tool directly."""
    print("\n🔍 Testing bank docs search tool...\n")
    
    context = SimpleToolContext()
    result = _search_bank_docs_impl("mortgage tracks", context)
    
    print(f"Search result status: {result.get('status')}")
    print(f"Found {len(result.get('results', []))} results")
    
    for i, item in enumerate(result.get('results', []), 1):
        print(f"\n--- Result {i} ---")
        print(f"File: {item.get('file')}")
        print(f"Snippet: {item.get('snippet')[:100]}...")

async def test_agent():
    """Test the agent using the ADK execute_agent function."""
    print("\n🔍 Testing agent with bank docs query...\n")
    
    # Create a user message
    user_message = Event(
        author="user",
        content=Content(parts=[Part(text="Tell me about the different mortgage tracks available.")])
    )
    
    # Execute the agent
    result = await execute_agent(root_agent, [user_message])
    
    # Print the responses
    for event in result.events:
        if event.author == root_agent.name and event.content:
            for part in event.content.parts:
                if hasattr(part, "text") and part.text:
                    print(f"Agent: {part.text[:100]}...")

# Run the tests
if __name__ == "__main__":
    # First test the tool directly
    asyncio.run(test_bank_docs_tool())
    
    # Then test the full agent
    try:
        asyncio.run(test_agent())
    except Exception as e:
        print(f"\nError running agent test: {e}")
        print("Note: This might be due to an incompatible ADK version.")