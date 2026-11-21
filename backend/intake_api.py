"""Explicit local intake writes; existing evidence APIs remain read-only."""

from contextlib import closing
from fastapi import HTTPException, Request
from .database import connect
from .intake import (
    Draft,
    DraftPage,
    DuplicatePage,
    SaveDraft,
    DraftCompareRequest,
    IntakeComparison,
    duplicate_candidates,
    get_draft,
    list_drafts,
    save_draft,
    compare_draft,
)


def install(app, path):
    def same_origin(request):
        origin = request.headers.get('origin')
        if origin and origin.rstrip('/') != str(request.base_url).rstrip('/'):
            raise HTTPException(403, 'Cross-origin local draft writes are refused')

    @app.get('/api/intake/duplicates', response_model=DuplicatePage)
    def duplicates(q: str = '', aliases: str = '', exclude_draft: str = ''):
        with closing(connect(path)) as conn:
            return {
                'items': duplicate_candidates(
                    conn, q, [a.strip() for a in aliases.split(',') if a.strip()], exclude_draft=exclude_draft or None
                )
                if q.strip() or aliases.strip()
                else []
            }

    @app.get('/api/intake/drafts', response_model=DraftPage)
    def drafts():
        with closing(connect(path)) as conn:
            return list_drafts(conn)

    @app.get('/api/intake/drafts/{draft_id}', response_model=Draft)
    def draft(draft_id: str):
        with closing(connect(path)) as conn:
            result = get_draft(conn, draft_id)
            if result is None:
                raise HTTPException(404, 'Draft not found')
            return result

    def save(request, body, draft_id=None):
        same_origin(request)
        try:
            return save_draft(path, body, draft_id)
        except LookupError as e:
            raise HTTPException(404, str(e)) from e
        except ValueError as e:
            raise HTTPException(409, str(e)) from e

    @app.post('/api/intake/drafts', response_model=Draft)
    def create(body: SaveDraft, request: Request):
        return save(request, body)

    @app.post('/api/intake/drafts/{draft_id}/revisions', response_model=Draft)
    def revise(draft_id: str, body: SaveDraft, request: Request):
        return save(request, body, draft_id)

    @app.post('/api/intake/drafts/{draft_id}/compare', response_model=IntakeComparison)
    def comparison(draft_id: str, body: DraftCompareRequest):
        with closing(connect(path)) as conn:
            try:
                return compare_draft(conn, draft_id, body)
            except LookupError as e:
                raise HTTPException(404, str(e)) from e
