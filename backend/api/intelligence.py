from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from models import RemedyEvent, RemedyEventCreate
from services import intelligence_service

router = APIRouter()


@router.get("/intelligence/suggestions", tags=["Intelligence"])
def get_suggestions() -> List[Dict[str, Any]]:
    """Retrieves a list of AI-guided suggestions and returns them in a frontend-friendly shape.

    The internal Suggestion model (title/description/action_type) is mapped to the
    frontend shape (id, type, category, message, action) so the UI can render consistently.
    """
    raw = intelligence_service.get_all_suggestions()

    mapped = []
    for s in raw:
        action_type = getattr(s, 'action_type', '') or getattr(s, 'actionType', '') or ''
        # derive a simple type and action route for the frontend
        if 'endorse' in action_type:
            s_type = 'overdue'
        elif 'follow' in action_type:
            s_type = 'unresponded'
        elif 'insight' in action_type:
            s_type = 'insight'
        else:
            s_type = 'other'

        action_route = None
        if action_type in ('send_notice', 'follow_up'):
            action_route = '/notices'
        elif action_type in ('endorse_bill', 'endorse'):
            action_route = '/endorse'
        elif action_type == 'open_dispatch':
            action_route = '/dispatch'

        mapped.append({
            'id': s.id,
            'type': s_type,
            'category': getattr(s, 'title', '') or getattr(s, 'category', '') or action_type or 'Other',
            'message': getattr(s, 'description', '') or getattr(s, 'message', '') or getattr(s, 'title', ''),
            'action': action_route,
            'priority': getattr(s, 'priority', None),
        })

    return mapped


@router.patch("/intelligence/suggestions/{suggestion_id}/resolve", response_model=RemedyEvent, tags=["Intelligence"])
def resolve_suggestion(suggestion_id: str, event_data: RemedyEventCreate):
    """Mark a suggestion as resolved and log a RemedyEvent."""
    try:
        return intelligence_service.resolve_suggestion(
            suggestion_id=suggestion_id,
            action=event_data.action,
            actor=event_data.actor,
            stage=event_data.stage,
            document_url=event_data.document_url,
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
