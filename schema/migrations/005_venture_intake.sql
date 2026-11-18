-- Local assertions have their own contract and never become publisher evidence.
CREATE TABLE intake_drafts (
 draft_id TEXT PRIMARY KEY, created_at TEXT NOT NULL
);
CREATE TABLE intake_revisions (
 revision_id TEXT PRIMARY KEY, draft_id TEXT NOT NULL REFERENCES intake_drafts(draft_id),
 revision_number INTEGER NOT NULL CHECK(revision_number>0), request_id TEXT UNIQUE NOT NULL,
 payload_json TEXT NOT NULL, payload_sha256 TEXT NOT NULL, saved_at TEXT NOT NULL,
 UNIQUE(draft_id,revision_number)
);
CREATE INDEX ix_intake_latest ON intake_revisions(draft_id,revision_number DESC);
CREATE TRIGGER immutable_intake_drafts_update BEFORE UPDATE ON intake_drafts
BEGIN SELECT RAISE(ABORT,'Immutable intake history'); END;
CREATE TRIGGER immutable_intake_drafts_delete BEFORE DELETE ON intake_drafts
BEGIN SELECT RAISE(ABORT,'Immutable intake history'); END;
CREATE TRIGGER immutable_intake_revisions_update BEFORE UPDATE ON intake_revisions
BEGIN SELECT RAISE(ABORT,'Immutable intake history'); END;
CREATE TRIGGER immutable_intake_revisions_delete BEFORE DELETE ON intake_revisions
BEGIN SELECT RAISE(ABORT,'Immutable intake history'); END;
