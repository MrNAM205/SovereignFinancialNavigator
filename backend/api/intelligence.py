from fastapi import APIRouter
from typing import List

from models import Suggestion
from services import intelligence_service

router = APIRouter()

# In-memory database for intelligence - not used yet, but follows pattern
intelligence_db: List = []

@router.get("/intelligence/suggestions", response_model=List[Suggestion], tags=["Intelligence"])
def get_suggestions():
    """Retrieves a list of AI-guided suggestions and insights."""
    return intelligence_service.get_all_suggestions()
