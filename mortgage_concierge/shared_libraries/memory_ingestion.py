import os
import glob
import logging
from google.genai.types import Content, Part
from google.adk.events import Event
from mortgage_concierge.shared_libraries.memory_store import memory_service, session_service

logger = logging.getLogger(__name__)

def ingest_bank_docs_to_memory(app_name: str = "mortgage_advisor") -> None:
    """
    Reads all .txt and .md files from BANK_DOCS_PATH, creates sessions with their content,
    and stores them into the global memory service.
    """
    docs_path = os.getenv("BANK_DOCS_PATH", os.path.join(os.getcwd(), "_knowledge_base", "bank_docs"))
    # Collect both .txt and .md files.
    file_patterns = [os.path.join(docs_path, "*.txt"), os.path.join(docs_path, "*.md")]
    files = []
    for pattern in file_patterns:
        files.extend(glob.glob(pattern))
    
    for fp in files:
        try:
            with open(fp, encoding="utf-8") as f:
                txt = f.read()
            sid = f"doc:{os.path.basename(fp)}"
            # Create session with required keyword-only arguments.
            sess = session_service.create_session(app_name=app_name, user_id="system", session_id=sid)
            
            # Ensure there is at least one event.
            if not sess.events:
                # Create an initial system event if none exist.
                initial_event = Event(
                    author="system",
                    content=Content(parts=[Part(text="")], role="system"),
                )
                sess.events.append(initial_event)
            
            # Create a new system event for the file content.
            new_event = Event(
                author="system",
                content=Content(parts=[Part(text=txt)], role="system"),
            )
            sess.events.append(new_event)
            
            memory_service.add_session_to_memory(sess)
            logger.info("Uploaded document: %s", fp)
        except Exception as exc:
            logger.exception("Error processing %s: %s", fp, exc)