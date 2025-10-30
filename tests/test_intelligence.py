import os
import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def _resolved_file_path() -> str:
    base = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', 'data')
    return os.path.join(base, 'resolved_suggestions.json')


def _remove_resolved_file():
    path = _resolved_file_path()
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def test_resolve_suggestion_persists(monkeypatch):
    # Ensure no prior resolved file
    _remove_resolved_file()

    # Mock intelligence service to return a predictable suggestion
    mock_suggestion = SimpleNamespace(
        id='test-sugg-1',
        title='Test Suggestion',
        description='This is a test suggestion',
        action_type='follow_up',
        priority=1,
    )

    import backend.services.intelligence_service as intel_svc

    monkeypatch.setattr(intel_svc, 'get_all_suggestions', lambda: [mock_suggestion])

    payload = {
        'action': 'dismiss_suggestion',
        'actor': 'user',
        'stage': 'test',
        'document_url': None,
    }

    res = client.patch(f"/api/intelligence/suggestions/{mock_suggestion.id}/resolve", json=payload)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body.get('action') == payload['action']
    assert body.get('actor') == payload['actor']

    # File should exist and contain the resolved id
    path = _resolved_file_path()
    assert os.path.exists(path)
    with open(path, 'r', encoding='utf-8') as fh:
        data = json.load(fh)
        assert isinstance(data, list)
        assert 'test-sugg-1' in data


def test_resolve_nonexistent_returns_404(monkeypatch):
    # Mock intelligence service to return no suggestions
    import backend.services.intelligence_service as intel_svc

    monkeypatch.setattr(intel_svc, 'get_all_suggestions', lambda: [])

    payload = {
        'action': 'dismiss_suggestion',
        'actor': 'user',
        'stage': 'test',
        'document_url': None,
    }

    res = client.patch('/api/intelligence/suggestions/nonexistent-id/resolve', json=payload)
    assert res.status_code == 404
