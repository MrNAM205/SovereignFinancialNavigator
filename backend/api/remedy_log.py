from fastapi import APIRouter, HTTPException
from typing import List

from models import RemedyEvent, RemedyEventCreate
from services import remedy_log_service

router = APIRouter()

@router.post("/remedy-log", response_model=RemedyEvent, tags=["Remedy Log"])
def create_remedy_event(event_data: RemedyEventCreate) -> RemedyEvent:
    """Creates a new remedy event via the service."""
    try:
        return remedy_log_service.log_remedy_event(
            action=event_data.action,
            actor=event_data.actor,
            stage=event_data.stage,
            document_url=event_data.document_url,
        )
    except Exception as e:
        # In a real app, you'd have more specific error handling and logging
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/remedy-log", response_model=List[RemedyEvent], tags=["Remedy Log"])
def get_remedy_log() -> List[RemedyEvent]:
    """Retrieves all remedy events from the service."""
    return remedy_log_service.get_remedy_log()
