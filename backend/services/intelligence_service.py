import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Set
import os
import json

from models import Suggestion

# Import the in-memory databases
from api.dispatch import dispatch_db
from api.notices import notices_db
from api.creditors import creditors_db
from api.monthly_bills import monthly_bills_db

# For logging resolutions
from services import remedy_log_service

# Track resolved suggestion IDs in-memory (persistent to file)
resolved_suggestions: Set[str] = set()

# Simple file persistence for resolved suggestions (development only)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
RESOLVED_FILE = os.path.join(DATA_DIR, 'resolved_suggestions.json')

def _ensure_data_dir():
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
    except Exception:
        pass

def _load_resolved():
    global resolved_suggestions
    try:
        if os.path.exists(RESOLVED_FILE):
            with open(RESOLVED_FILE, 'r', encoding='utf-8') as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    resolved_suggestions = set(map(str, data))
    except Exception:
        # If anything goes wrong, leave set empty and continue
        resolved_suggestions = set()

def _save_resolved():
    try:
        _ensure_data_dir()
        with open(RESOLVED_FILE, 'w', encoding='utf-8') as fh:
            json.dump(list(resolved_suggestions), fh)
    except Exception:
        # Best-effort persist - ignore errors in dev
        pass

# Load persisted resolved suggestions at module import
_load_resolved()

def detect_unresponded_notices() -> List[Suggestion]:
    """Generates suggestions for notices that have not been responded to."""
    suggestions: List[Suggestion] = []
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Find notices that were sent but never updated to delivered or responded
    for dispatch in dispatch_db:
        if dispatch.document_type == 'notice' and dispatch.sent_at < thirty_days_ago and not dispatch.responded_at and not dispatch.delivered_at:
            notice = next((n for n in notices_db if n.id == dispatch.document_id), None)
            if notice:
                creditor = next((c for c in creditors_db if c.id == notice.creditor_id), None)
                creditor_name = creditor.name if creditor else "Unknown Creditor"

                suggestions.append(Suggestion(
                    id=str(uuid.uuid4()),
                    title="Follow-up on Unresponded Notice",
                    description=f"The notice sent to {creditor_name} on {dispatch.sent_at.strftime('%Y-%m-%d')} has not received a response in over 30 days.",
                    action_type="follow_up",
                    priority=4,
                    related_document_id=notice.id
                ))
    return suggestions

def detect_overdue_endorsements() -> List[Suggestion]:
    """Generates suggestions for monthly bills that are past due and pending endorsement."""
    suggestions: List[Suggestion] = []
    today = datetime.utcnow().date()

    for bill in monthly_bills_db:
        if bill.status == 'pending' and bill.due_date < today:
            creditor = next((c for c in creditors_db if c.id == bill.creditor_id), None)
            creditor_name = creditor.name if creditor else "Unknown Creditor"

            suggestions.append(Suggestion(
                id=str(uuid.uuid4()),
                title="Overdue Bill Endorsement",
                description=f"The bill from {creditor_name} with a due date of {bill.due_date} is overdue for endorsement or dispute.",
                action_type="endorse_bill",
                priority=5,
                related_document_id=bill.id
            ))
    return suggestions

def get_all_suggestions() -> List[Suggestion]:
    """Runs all suggestion detectors and returns a combined list."""
    all_suggestions = []
    all_suggestions.extend(detect_unresponded_notices())
    all_suggestions.extend(detect_overdue_endorsements())
    # Future detectors can be added here
    # Filter out suggestions that have been resolved/dismissed
    return [s for s in all_suggestions if s.id not in resolved_suggestions]


def resolve_suggestion(suggestion_id: str, action: str, actor: str = 'user', stage: str = 'notice', document_url: Optional[str] = None):
    """
    Marks a suggestion as resolved (in-memory) and logs a RemedyEvent via the remedy log service.

    Returns the logged RemedyEvent.
    """
    # Verify the suggestion exists in the current set before resolving
    current = get_all_suggestions()
    if not any(s.id == suggestion_id for s in current):
        raise ValueError(f"Suggestion {suggestion_id} not found or already resolved")

    # Record resolution and log an event
    resolved_suggestions.add(suggestion_id)
    _save_resolved()
    event = remedy_log_service.log_remedy_event(
        action=action,
        actor=actor,
        stage=stage,
        document_url=document_url,
    )
    return event
