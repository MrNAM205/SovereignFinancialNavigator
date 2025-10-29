from fastapi import APIRouter, HTTPException
from typing import List
from datetime import date
import uuid

from models import ViolationEvent

router = APIRouter()

violations_db: List[ViolationEvent] = []

@router.get("/violations", response_model=List[ViolationEvent], tags=["FDCPA Violations"])
def get_violations():
    """Retrieves all logged FDCPA violation events."""
    return violations_db

@router.post("/violations", response_model=ViolationEvent, tags=["FDCPA Violations"])
def create_violation(violation_data: ViolationEvent):
    """Logs a new FDCPA violation event."""
    try:
        # In a real app, ID would be handled by the database
        violation_data.id = str(uuid.uuid4())
        violations_db.append(violation_data)
        return violation_data
    except Exception as e:
        # Add more specific error handling as needed
        raise HTTPException(status_code=400, detail=str(e))
