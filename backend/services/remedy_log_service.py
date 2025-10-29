
import uuid
from datetime import datetime
from typing import List, Optional

from models import RemedyEvent

# In-memory database for remedy events
remedy_log_db: List[RemedyEvent] = []

def log_remedy_event(
    action: str,
    actor: str,
    stage: str,
    document_url: Optional[str] = None,
) -> RemedyEvent:
    """
    Creates and logs a new RemedyEvent.
    """
    event = RemedyEvent(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        action=action,
        actor=actor,
        stage=stage,
        document_url=document_url,
    )
    remedy_log_db.append(event)
    return event

def get_remedy_log() -> List[RemedyEvent]:
    """
    Returns the entire remedy log.
    """
    return remedy_log_db
