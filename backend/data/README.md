This folder stores small JSON persistence files used by lightweight services.

Currently used files:
- resolved_suggestions.json — keeps a list of suggestion IDs that have been dismissed.

This is intentionally simple and file-based for development. For production, migrate to a proper datastore.
