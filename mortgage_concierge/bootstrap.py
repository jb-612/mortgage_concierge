# mortgage_concierge/bootstrap.py  ─ tiny one‑liner style
from functools import lru_cache
from dotenv import load_dotenv
from mortgage_concierge.shared_libraries.memory_ingestion import ingest_bank_docs_to_memory


@lru_cache(maxsize=None)  # guarantees “run once per process”
def init(app_name: str = "mortgage_advisor") -> None:
    """Light‑weight bootstrap: just load env and ingest docs once."""
    load_dotenv()  # no‑op on repeat calls
    ingest_bank_docs_to_memory(app_name)
