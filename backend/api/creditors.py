from fastapi import APIRouter, HTTPException
from typing import List
import uuid

from models import Creditor

router = APIRouter()

# This would be a real database in a production application
creditors_db: List[Creditor] = []

@router.post("/creditors", response_model=Creditor, tags=["Creditors"])
def create_creditor(creditor_data: dict) -> Creditor:
    """Creates and stores a new creditor."""
    try:
        new_creditor = Creditor(
            id=str(uuid.uuid4()),
            name=creditor_data.get('name'),
            address=creditor_data.get('address'),
            contact_method=creditor_data.get('contact_method'),
            tags=creditor_data.get('tags', [])
        )
        creditors_db.append(new_creditor)
        return new_creditor
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/creditors", response_model=List[Creditor], tags=["Creditors"])
def get_creditors() -> List[Creditor]:
    """Retrieves all creditors."""
    return creditors_db
