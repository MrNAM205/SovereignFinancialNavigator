import uuid
from datetime import datetime
from typing import List, Optional

from models import DispatchEvent, DispatchStatus
from services import remedy_log_service

# This is an anti-pattern. In a real app, this would be a shared data access layer.
from api.notices import notices_db
from api.dispatch import dispatch_db

def log_dispatch(
    document_id: str,
    document_type: str,
    dispatch_method: str,
    tracking_number: Optional[str] = None
) -> DispatchEvent:
    """Logs that a document has been sent and and updates its status."""
    # In a more robust system, we would have a generic way to find and update documents.
    # For now, we'll just create the dispatch event.
    if document_type == 'notice':
        doc = next((n for n in notices_db if n.id == document_id), None)
        if not doc:
            raise ValueError(f"Notice with id {document_id} not found.")
        doc.status = DispatchStatus.SENT

    new_dispatch = DispatchEvent(
        id=str(uuid.uuid4()),
        document_id=document_id,
        document_type=document_type,
        dispatch_method=dispatch_method,
        tracking_number=tracking_number,
        sent_at=datetime.utcnow(),
    )
    dispatch_db.append(new_dispatch)

    remedy_log_service.log_remedy_event(
        action=f"{document_type.capitalize()} sent via {dispatch_method}",
        actor="user",
        stage="response",
        document_url=f"/{document_type}s/{document_id}"
    )

    return new_dispatch

def get_dispatch_events_for_document(document_id: str) -> List[DispatchEvent]:
    """Retrieves all dispatch events related to a specific document."""
    return [e for e in dispatch_db if e.document_id == document_id]

def get_all_dispatch_events() -> List[DispatchEvent]:
    """Retrieves all dispatch events."""
    return dispatch_db

def update_dispatch_status(dispatch_id: str, status: DispatchStatus) -> DispatchEvent:
    """Updates the status of a dispatch event and the associated document."""
    dispatch_event = next((d for d in dispatch_db if d.id == dispatch_id), None)
    if not dispatch_event:
        raise ValueError(f"Dispatch event with id {dispatch_id} not found.")

    # Update timestamps based on new status
    if status == DispatchStatus.DELIVERED:
        dispatch_event.delivered_at = datetime.utcnow()
    elif status == DispatchStatus.RESPONDED:
        dispatch_event.responded_at = datetime.utcnow()

    # Update the document's primary status
    # As with log_dispatch, this would be more generic in a real system.
    if dispatch_event.document_type == 'notice':
        doc = next((n for n in notices_db if n.id == dispatch_event.document_id), None)
        if doc:
            doc.status = status

    # Log the status change
    remedy_log_service.log_remedy_event(
        action=f"{dispatch_event.document_type.capitalize()} status updated to {status.value}",
        actor="system", # Or user, depending on how the update is triggered
        stage="response",
        document_url=f"/{dispatch_event.document_type}s/{dispatch_event.document_id}"
    )

    return dispatch_event
