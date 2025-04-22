"""
One‑time bootstrap utilities for Mortgage Concierge.

Call `bootstrap.init()` once at process start‑up (CLI, wsgi, etc.).
"""
import asyncio
from dotenv import load_dotenv

from mortgage_concierge.shared_libraries.memory_ingestion import (
    ingest_bank_docs_to_memory,
)

_lock = asyncio.Lock()
_done: bool = False


async def init(app_name: str = "mortgage_advisor") -> None:
    """Load env vars and ingest bank docs exactly once per process."""
    global _done
    if _done:
        return
    async with _lock:
        if _done:  # double‑checked locking
            return
        # Load environment variables from `.env`
        load_dotenv()
        # Ingest bank documents into the memory service
        ingest_bank_docs_to_memory(app_name=app_name)
        _done = True


def init_sync(app_name: str = "mortgage_advisor") -> None:
    """Synchronous helper for environments without an existing event‑loop."""
    asyncio.run(init(app_name=app_name))
