PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS sources (
 source_id TEXT PRIMARY KEY, title TEXT NOT NULL, url TEXT NOT NULL,
 publisher TEXT NOT NULL, source_type TEXT NOT NULL,
 published_at TEXT NOT NULL, retrieved_at TEXT NOT NULL,
 content_version TEXT NOT NULL, archive_path TEXT, limitations TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS ventures (
 venture_id TEXT PRIMARY KEY, display_name TEXT NOT NULL, aliases_json TEXT NOT NULL,
 entity_type TEXT NOT NULL, legal_name TEXT, registration_id TEXT,
 current_operating_status TEXT, current_funding_stage TEXT,
 selection_bucket TEXT NOT NULL, identity_review_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS observations (
 observation_id TEXT PRIMARY KEY, venture_id TEXT NOT NULL REFERENCES ventures(venture_id),
 field TEXT NOT NULL, value_text TEXT NOT NULL,
 source_id TEXT NOT NULL REFERENCES sources(source_id), locator TEXT NOT NULL,
 assertion_type TEXT NOT NULL, effective_at TEXT, date_basis TEXT NOT NULL,
 review_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS awards (
 award_id TEXT PRIMARY KEY, venture_id TEXT NOT NULL REFERENCES ventures(venture_id),
 programme TEXT NOT NULL CHECK(programme IN ('velocity_100k','velocity_ideas')),
 award_year INTEGER NOT NULL, award_label TEXT NOT NULL,
 place INTEGER CHECK(place IS NULL OR place > 0), event_date TEXT,
 source_id TEXT NOT NULL REFERENCES sources(source_id), locator TEXT NOT NULL,
 review_status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS connections (
 connection_id TEXT PRIMARY KEY, venture_id TEXT NOT NULL REFERENCES ventures(venture_id),
 connection_type TEXT NOT NULL, institution TEXT NOT NULL,
 observation_id TEXT NOT NULL REFERENCES observations(observation_id)
);
CREATE TABLE IF NOT EXISTS annotations (
 annotation_id TEXT PRIMARY KEY, venture_id TEXT NOT NULL REFERENCES ventures(venture_id),
 field TEXT NOT NULL, value_text TEXT NOT NULL,
 basis_observation_ids_json TEXT NOT NULL, origin TEXT NOT NULL,
 review_status TEXT NOT NULL, purpose TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS annotation_evidence (
 annotation_id TEXT NOT NULL REFERENCES annotations(annotation_id),
 observation_id TEXT NOT NULL REFERENCES observations(observation_id),
 PRIMARY KEY(annotation_id, observation_id)
);
CREATE TABLE IF NOT EXISTS imports (
 seed_sha256 TEXT PRIMARY KEY, schema_version INTEGER NOT NULL, prepared_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_observations_subject ON observations(venture_id, field);
CREATE INDEX IF NOT EXISTS ix_awards_programme ON awards(programme,award_year);
CREATE INDEX IF NOT EXISTS ix_connections_type ON connections(connection_type);
CREATE VIEW IF NOT EXISTS v_observation_evidence AS
 SELECT o.*, s.title AS source_title, s.url, s.publisher, s.published_at, s.retrieved_at
 FROM observations o JOIN sources s USING(source_id);
CREATE VIEW IF NOT EXISTS v_award_evidence AS
 SELECT a.*, v.display_name, s.url, s.published_at, s.retrieved_at
 FROM awards a JOIN ventures v USING(venture_id) JOIN sources s USING(source_id);

