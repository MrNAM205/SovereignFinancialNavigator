import uuid
from datetime import datetime, timedelta
from typing import List

from models import Suggestion, DispatchStatus

# Import the in-memory databases
from api.dispatch import dispatch_db
from api.notices import notices_db
from api.creditors import creditors_db
from api.monthly_bills import monthly_bills_db

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
    return all_suggestions
