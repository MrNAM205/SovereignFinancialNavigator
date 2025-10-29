import os
import yaml
from typing import List, Dict, Any

STATUTES_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "shared", "constants", "statutes")
)

_statutes_cache: List[Dict[str, Any]] = []

def _load_statutes():
    """Loads all statutes from YAML files in the statutes directory."""
    if _statutes_cache:
        return

    for filename in os.listdir(STATUTES_DIR):
        if filename.endswith('.yml') or filename.endswith('.yaml'):
            filepath = os.path.join(STATUTES_DIR, filename)
            with open(filepath, 'r') as f:
                data = yaml.safe_load(f)
                if data and 'statutes' in data:
                    _statutes_cache.extend(data['statutes'])

def get_all_statutes() -> List[Dict[str, Any]]:
    """Returns a list of all loaded statutes."""
    _load_statutes()
    return _statutes_cache

def search_statutes(query: str) -> List[Dict[str, Any]]:
    """Searches statutes by title, excerpt, or tags."""
    _load_statutes()
    query = query.lower()
    
    return [s for s in _statutes_cache if 
            query in s['title'].lower() or 
            query in s['excerpt'].lower() or 
            any(query in tag.lower() for tag in s.get('tags', []))]

def get_statute_by_id(statute_id: str) -> Dict[str, Any] | None:
    """Finds a single statute by its unique ID."""
    _load_statutes()
    return next((s for s in _statutes_cache if s['id'] == statute_id), None)
