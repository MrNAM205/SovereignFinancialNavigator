from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import os
import uuid
from datetime import datetime
from typing import List

from services.notice_service import generate_notice, TEMPLATE_DIR
from services import remedy_log_service
from models import Notice
# This creates dependencies between API modules. A shared data access layer would be better.
from api.user_profile import user_profile_db
from api.creditors import creditors_db

router = APIRouter()

# In-memory database for notices
notices_db: List[Notice] = []

class NoticeRequest(BaseModel):
    template_name: str
    user_id: str
    creditor_id: str

@router.get("/notices/templates", response_model=list[str], tags=["Notices"])
def list_notice_templates():
    """Returns a list of available notice template files."""
    try:
        return [f for f in os.listdir(TEMPLATE_DIR) if f.endswith('.j2')]
    except FileNotFoundError:
        return []

@router.get("/notices/{notice_id}", response_model=Notice, tags=["Notices"])
def get_notice_by_id(notice_id: str):
    """Retrieves a single notice by its ID."""
    notice = next((n for n in notices_db if n.id == notice_id), None)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    return notice

@router.post("/notices/generate", response_model=dict, tags=["Notices"])
def generate_notice_endpoint(request: NoticeRequest):
    """Generates a notice, logs it as a remedy event, and returns the text."""
    user = user_profile_db.get(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User with id {request.user_id} not found.")

    creditor = next((c for c in creditors_db if c.id == request.creditor_id), None)
    if not creditor:
        raise HTTPException(status_code=404, detail=f"Creditor with id {request.creditor_id} not found.")

    try:
        notice_text = generate_notice(
            template_name=request.template_name,
            user=user,
            creditor=creditor
        )

        # Create and store the notice object
        new_notice = Notice(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            creditor_id=request.creditor_id,
            template_name=request.template_name,
            content=notice_text,
            created_at=datetime.utcnow()
        )
        notices_db.append(new_notice)

        # Log the remedy event
        remedy_log_service.log_remedy_event(
            action=f"Notice Generated: {request.template_name}",
            actor=f"user:{request.user_id}",
            stage="notice",
            document_url=f"/notices/{new_notice.id}" # Hypothetical URL
        )

        return {"notice_text": notice_text}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
