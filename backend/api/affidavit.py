from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import List

from services.affidavit import generate_affidavit, generate_affidavit_of_mailing
from services import remedy_log_service
from models import RemedyEvent, Creditor, UserProfile, Notice, DispatchEvent

# Import the in-memory databases
from api.user_profile import user_profile_db
from api.creditors import creditors_db
from api.notices import notices_db
from api.dispatch import dispatch_db

router = APIRouter()

class AffidavitRequest(BaseModel):
    user: UserProfile
    creditor: Creditor
    events: List[RemedyEvent]

@router.post("/affidavit/generate", tags=["Affidavit"], response_model=dict)
def create_affidavit_endpoint(request_body: AffidavitRequest):
    """
    Generates an affidavit based on user, creditor, and remedy event data.
    """
    # In a real application, this data would be fetched from the database
    # based on authenticated user and IDs, not passed in the body.
    affidavit_text = generate_affidavit(
        user=request_body.user,
        creditor=request_body.creditor,
        events=request_body.events
    )
    return {"affidavit": affidavit_text}

@router.post("/affidavit/mailing/{dispatch_id}", tags=["Affidavit"], response_model=dict)
def create_affidavit_of_mailing_endpoint(dispatch_id: str):
    """Generates an Affidavit of Mailing for a specific dispatch event."""
    # 1. Fetch the dispatch event
    dispatch_event = next((d for d in dispatch_db if d.id == dispatch_id), None)
    if not dispatch_event:
        raise HTTPException(status_code=404, detail="Dispatch event not found")

    # 2. Fetch the associated notice
    if dispatch_event.document_type != 'notice':
        raise HTTPException(status_code=400, detail="Affidavit of Mailing can only be generated for notices.")
    
    notice = next((n for n in notices_db if n.id == dispatch_event.document_id), None)
    if not notice:
        raise HTTPException(status_code=404, detail="Associated notice not found")

    # 3. Fetch the user and creditor
    user = user_profile_db.get(notice.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Associated user not found")

    creditor = next((c for c in creditors_db if c.id == notice.creditor_id), None)
    if not creditor:
        raise HTTPException(status_code=404, detail="Associated creditor not found")

    # 4. Generate the affidavit
    affidavit_text = generate_affidavit_of_mailing(
        user=user,
        creditor=creditor,
        dispatch=dispatch_event,
        notice=notice
    )

    # 5. Log the remedy event
    remedy_log_service.log_remedy_event(
        action=f"Affidavit of Mailing Generated for {notice.template_name}",
        actor=f"user:{user.id}",
        stage="endorsement",
        document_url=f"/affidavits/mailing/{dispatch_event.id}" # Hypothetical URL
    )

    return {"affidavit_text": affidavit_text}
