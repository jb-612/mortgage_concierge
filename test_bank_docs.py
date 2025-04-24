#!/usr/bin/env python
# Test script to verify bank docs are properly loaded

import logging
from mortgage_concierge.bootstrap import init
from mortgage_concierge.tools.bank_docs import _search_bank_docs_impl
from mortgage_concierge.shared_libraries.memory_store import memory_service

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Simple tool context for testing
class SimpleToolContext:
    def __init__(self):
        self.state = {}

def test_bank_docs():
    """Test that bank docs are properly loaded and can be searched."""
    print("\n===== Testing Bank Docs Loading and Search =====\n")
    
    # Initialize the environment
    print("Initializing bootstrap...")
    init(app_name="mortgage_advisor")
    print("Bootstrap initialized successfully")
    
    # Check what documents we have in memory
    print("\nChecking documents in memory:")
    try:
        response = memory_service.search_memory(
            app_name="mortgage_advisor",
            user_id="system",
            query="*"  # Simple wildcard to get everything
        )
        print(f"Found {len(getattr(response, 'memories', []))} documents in memory")
        for mem in getattr(response, "memories", []):
            session_id = getattr(mem, "session_id", "unknown")
            print(f"- {session_id}")
    except Exception as e:
        print(f"Error searching memory: {e}")
    
    # Test the search function
    print("\nTesting search function:")
    search_queries = [
        "mortgage tracks",
        "interest rates",
        "eligibility criteria",
        "loan terms"
    ]
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        context = SimpleToolContext()
        result = _search_bank_docs_impl(query, context)
        
        if result.get("status") == "success":
            print(f"✅ Search successful! Found {len(result.get('results', []))} results")
            
            # Show the first 2 results
            for i, item in enumerate(result.get('results', [])[:2], 1):
                print(f"\n--- Result {i} ---")
                print(f"File: {item.get('file')}")
                print(f"Snippet: {item.get('snippet')[:150]}...")
        else:
            print(f"❌ Search failed: {result.get('error_message')}")
    
    print("\n===== Bank Docs Test Complete =====")

if __name__ == "__main__":
    test_bank_docs()