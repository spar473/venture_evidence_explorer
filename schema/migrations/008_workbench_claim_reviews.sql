CREATE TABLE workbench_claim_reviews (
  review_id TEXT PRIMARY KEY,
  request_id TEXT NOT NULL UNIQUE,
  subject_id TEXT NOT NULL,
  claim_id TEXT NOT NULL,
  decision TEXT NOT NULL CHECK (decision = 'disputed'),
  analyst TEXT NOT NULL CHECK (length(trim(analyst)) > 0),
  rationale TEXT NOT NULL CHECK (length(trim(rationale)) > 0),
  recorded_at TEXT NOT NULL
);
CREATE INDEX workbench_claim_reviews_claim ON workbench_claim_reviews(claim_id, recorded_at);
CREATE TRIGGER workbench_claim_reviews_immutable_update BEFORE UPDATE ON workbench_claim_reviews
BEGIN SELECT RAISE(ABORT, 'Workbench claim reviews are append-only'); END;
CREATE TRIGGER workbench_claim_reviews_immutable_delete BEFORE DELETE ON workbench_claim_reviews
BEGIN SELECT RAISE(ABORT, 'Workbench claim reviews are append-only'); END;
