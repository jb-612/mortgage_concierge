# mortgage_concierge/bootstrap.py
"""
Bootstrap module for the mortgage_concierge application.

This module handles initialization tasks that should be performed once before 
the agent is used, such as loading environment variables and ingesting bank documents
into memory for retrieval.

It follows ADK best practices by:
1. Avoiding import-time side effects (initialization happens explicitly via init())
2. Using lru_cache to ensure operations only happen once per process
3. Providing a clean initialization API that can be called from various entry points
"""

import logging
import os
from functools import lru_cache
from dotenv import load_dotenv
from mortgage_concierge.shared_libraries.memory_ingestion import ingest_bank_docs_to_memory

logger = logging.getLogger(__name__)

@lru_cache(maxsize=None)
def init(app_name: str = "mortgage_advisor") -> None:
    """
    Initialize the mortgage concierge application environment.
    
    This function:
    1. Loads environment variables from .env file
    2. Ingests bank documents into memory for search functionality
    
    Args:
        app_name: The application name to use for document sessions
                  (defaults to "mortgage_advisor")
    
    Returns:
        None
    
    Note:
        - Due to @lru_cache, this function will only execute its body once
          per Python process, regardless of how many times it's called
        - This function should be called before any agent interactions begin
    """
    logger.info(f"Initializing mortgage concierge bootstrap for app: {app_name}")
    
    # Load environment variables (no-op if already loaded)
    load_dotenv()
    
    # Ensure necessary environment variables are set
    docs_path = os.getenv("BANK_DOCS_PATH", os.path.join(os.getcwd(), "_knowledge_base", "bank_docs"))
    logger.info(f"Using bank docs path: {docs_path}")
    
    # Ingest bank documents into memory for search functionality
    ingest_bank_docs_to_memory(app_name)
    logger.info("Bank document ingestion complete")