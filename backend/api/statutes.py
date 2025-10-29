from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any

from services import statute_service

router = APIRouter()

@router.get("/statutes", response_model=List[Dict[str, Any]], tags=["Statutes"])
def list_all_statutes():
    """Retrieves a list of all available statutes."""
    return statute_service.get_all_statutes()

@router.get("/statutes/search", response_model=List[Dict[str, Any]], tags=["Statutes"])
def search_for_statutes(q: str = Query(..., min_length=3)):
    """Searches statutes based on a query string."""
    return statute_service.search_statutes(q)

@router.get("/statutes/{statute_id}", response_model=Dict[str, Any], tags=["Statutes"])
def get_single_statute(statute_id: str):
    """Retrieves a single statute by its ID."""
    statute = statute_service.get_statute_by_id(statute_id)
    if not statute:
        raise HTTPException(status_code=404, detail="Statute not found.")
    return statute
