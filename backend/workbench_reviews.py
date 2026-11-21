"""Append-only analyst disputes, stored beside immutable source records."""

from contextlib import closing
from datetime import datetime, timezone
import sqlite3
from typing import Literal
from uuid import uuid4

from fastapi import HTTPException, Request
from pydantic import Field, field_validator

from .database import migrate
from .ingestion import StrictModel


class DisputeRequest(StrictModel):
    request_id: str = Field(pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    claim_id: str = Field(min_length=1, max_length=250)
    analyst: str = Field(min_length=1, max_length=120)
    rationale: str = Field(min_length=1, max_length=2400)

    @field_validator('analyst', 'rationale', mode='before')
    @classmethod
    def strip_whitespace(cls, value):
        return value.strip() if isinstance(value, str) else value


class ClaimReview(DisputeRequest):
    review_id: str
    subject_id: str
    decision: Literal['disputed']
    recorded_at: str


def claim_reviews(conn):
    if not conn.execute("SELECT 1 FROM sqlite_schema WHERE type='table' AND name='workbench_claim_reviews'").fetchone():
        return {}
    reviews = {}
    for row in conn.execute('SELECT * FROM workbench_claim_reviews ORDER BY recorded_at, rowid'):
        reviews.setdefault(row['claim_id'], []).append(ClaimReview.model_validate(dict(row)))
    return reviews


def append_dispute(db, subject_id, body):
    from .cohort_audit import run_audit
    from .precedents import PrecedentCatalog, SubjectNotFound

    with closing(sqlite3.connect(db.resolve().as_uri() + '?mode=rw', uri=True, isolation_level=None)) as conn:
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys=ON')
        migrate(conn)
        conn.execute('BEGIN IMMEDIATE')
        try:
            existing = conn.execute(
                'SELECT * FROM workbench_claim_reviews WHERE request_id=?', (body.request_id,)
            ).fetchone()
            if existing:
                review = ClaimReview.model_validate(dict(existing))
                if review.subject_id != subject_id or any(
                    getattr(review, key) != val for key, val in body.model_dump().items()
                ):
                    raise ValueError('Dispute request ID was already used for different content')
                return review
            now = datetime.now(timezone.utc)
            audit = run_audit()
            catalog = PrecedentCatalog(conn, max(now.date().isoformat(), audit['follow_up']['as_of']), audit=audit)
            row = catalog.row(subject_id, 'first_institutional_round')
            if not any(claim.claim_id == body.claim_id for claim in row.claims):
                raise SubjectNotFound('Claim is unavailable for this subject')
            review = ClaimReview(
                **body.model_dump(),
                review_id=str(uuid4()),
                subject_id=subject_id,
                decision='disputed',
                recorded_at=now.isoformat(),
            )
            record = review.model_dump()
            conn.execute(
                """INSERT INTO workbench_claim_reviews
                (review_id, request_id, subject_id, claim_id, decision, analyst, rationale, recorded_at)
                VALUES (:review_id, :request_id, :subject_id, :claim_id, :decision, :analyst, :rationale, :recorded_at)""",
                record,
            )
            conn.execute('COMMIT')
            return review
        finally:
            if conn.in_transaction:
                conn.execute('ROLLBACK')


def install(app, db):
    from .precedents import SubjectNotFound

    @app.post('/api/precedents/{subject_id}/disputes', response_model=ClaimReview)
    def dispute(subject_id: str, body: DisputeRequest, request: Request):
        origin = request.headers.get('origin')
        if origin and origin.rstrip('/') != str(request.base_url).rstrip('/'):
            raise HTTPException(403, 'Cross-origin local claim writes are refused')
        try:
            return append_dispute(db, subject_id, body)
        except SubjectNotFound as error:
            raise HTTPException(404, str(error)) from error
        except ValueError as error:
            raise HTTPException(409, str(error)) from error
