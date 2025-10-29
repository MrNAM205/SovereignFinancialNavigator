from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional

from services import dispatch_service
from models import DispatchEvent, DispatchStatus

router = APIRouter()

# In-memory database for dispatch events
dispatch_db: List[DispatchEvent] = []

class DispatchRequest(BaseModel):
    document_id: str
    document_type: str = 'notice'
    dispatch_method: str
    tracking_number: Optional[str] = None

class StatusUpdateRequest(BaseModel):
    status: DispatchStatus

@router.post("/dispatch", response_model=DispatchEvent, tags=["Dispatch"])
def create_dispatch_event(request: DispatchRequest):
    """Logs a new dispatch event for a document."""
    try:
        return dispatch_service.log_dispatch(
            document_id=request.document_id,
            document_type=request.document_type,
            dispatch_method=request.dispatch_method,
            tracking_number=request.tracking_number
        )
    except (ValueError, NotImplementedError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@router.get("/dispatch", response_model=List[DispatchEvent], tags=["Dispatch"])
def get_all_dispatches():
    """Gets all dispatch events."""
    return dispatch_service.get_all_dispatch_events()

@router.get("/dispatch/{document_id}", response_model=List[DispatchEvent], tags=["Dispatch"])
def get_dispatch_history(document_id: str):
    """Gets the dispatch history for a specific document."""
    return dispatch_service.get_dispatch_events_for_document(document_id)

@router.put("/dispatch/{dispatch_id}/status", response_model=DispatchEvent, tags=["Dispatch"])
def update_dispatch_status(dispatch_id: str, request: StatusUpdateRequest):
    """Updates the status of a specific dispatch event."""
    try:
        return dispatch_service.update_dispatch_status(dispatch_id, request.status)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
