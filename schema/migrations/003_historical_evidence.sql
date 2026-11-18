-- Additive metadata: legacy evidence tables and their bytes are unchanged.
CREATE TABLE import_documents (
 seed_sha256 TEXT PRIMARY KEY REFERENCES imports(seed_sha256), raw_bytes BLOB NOT NULL
);
CREATE TABLE evidence_dates (
 date_id TEXT PRIMARY KEY, owner_kind TEXT NOT NULL CHECK(owner_kind IN ('source','observation','award')),
 owner_id TEXT NOT NULL, date_role TEXT NOT NULL CHECK(date_role IN ('publication','effective','announcement','event')),
 precision TEXT NOT NULL CHECK(precision IN ('unknown','day','month','year')),
 lower_bound TEXT, upper_bound TEXT,
 UNIQUE(owner_kind,owner_id,date_role),
 CHECK((precision='unknown' AND lower_bound IS NULL AND upper_bound IS NULL) OR
       (precision<>'unknown' AND lower_bound IS NOT NULL AND upper_bound IS NOT NULL AND lower_bound<=upper_bound))
);
CREATE TABLE source_availability (
 source_id TEXT PRIMARY KEY REFERENCES sources(source_id), available_at TEXT NOT NULL,
 evidence_locator TEXT NOT NULL CHECK(length(trim(evidence_locator))>0)
);
CREATE TABLE observation_values (
 observation_id TEXT PRIMARY KEY REFERENCES observations(observation_id),
 value_type TEXT NOT NULL CHECK(value_type IN ('financial_value','event_value')), value_json TEXT NOT NULL
);
CREATE TABLE observation_relations (
 relation_id TEXT PRIMARY KEY,
 observation_id TEXT NOT NULL REFERENCES observations(observation_id),
 replacement_id TEXT NOT NULL REFERENCES observations(observation_id),
 relation_type TEXT NOT NULL CHECK(relation_type IN ('supersedes','corrects')),
 reviewer TEXT NOT NULL CHECK(length(trim(reviewer))>0), recorded_at TEXT NOT NULL,
 rationale TEXT NOT NULL CHECK(length(trim(rationale))>0),
 CHECK(observation_id<>replacement_id)
);
CREATE INDEX ix_observation_relations_old ON observation_relations(observation_id);
CREATE INDEX ix_review_observation_date ON review_events(observation_id,reviewed_at);
CREATE TRIGGER relation_subject BEFORE INSERT ON observation_relations
WHEN NOT EXISTS (
 SELECT 1 FROM observations old JOIN observations new ON old.venture_id=new.venture_id AND old.field=new.field
 WHERE old.observation_id=NEW.observation_id AND new.observation_id=NEW.replacement_id
)
BEGIN SELECT RAISE(ABORT, 'Correction/supersession evidence subject mismatch'); END;
CREATE TRIGGER relation_cycle BEFORE INSERT ON observation_relations
WHEN EXISTS (
 WITH RECURSIVE successors(id) AS (
 SELECT NEW.replacement_id UNION SELECT r.replacement_id FROM observation_relations r JOIN successors s ON r.observation_id=s.id
 ) SELECT 1 FROM successors WHERE id=NEW.observation_id
)
BEGIN SELECT RAISE(ABORT, 'Correction/supersession cycle'); END;
CREATE TRIGGER date_subject BEFORE INSERT ON evidence_dates
WHEN NOT ((NEW.owner_kind='source' AND NEW.date_role='publication' AND EXISTS(SELECT 1 FROM sources WHERE source_id=NEW.owner_id)) OR
 (NEW.owner_kind='observation' AND NEW.date_role IN ('effective','announcement') AND EXISTS(SELECT 1 FROM observations WHERE observation_id=NEW.owner_id)) OR
 (NEW.owner_kind='award' AND NEW.date_role='event' AND EXISTS(SELECT 1 FROM awards WHERE award_id=NEW.owner_id)))
BEGIN SELECT RAISE(ABORT, 'Date evidence owner mismatch'); END;
CREATE TRIGGER immutable_import_documents_update BEFORE UPDATE ON import_documents
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
CREATE TRIGGER immutable_import_documents_delete BEFORE DELETE ON import_documents
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
CREATE TRIGGER immutable_evidence_dates_update BEFORE UPDATE ON evidence_dates
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
CREATE TRIGGER immutable_evidence_dates_delete BEFORE DELETE ON evidence_dates
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
CREATE TRIGGER immutable_source_availability_update BEFORE UPDATE ON source_availability
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
CREATE TRIGGER immutable_source_availability_delete BEFORE DELETE ON source_availability
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
CREATE TRIGGER immutable_observation_values_update BEFORE UPDATE ON observation_values
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
CREATE TRIGGER immutable_observation_values_delete BEFORE DELETE ON observation_values
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
CREATE TRIGGER immutable_observation_relations_update BEFORE UPDATE ON observation_relations
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
CREATE TRIGGER immutable_observation_relations_delete BEFORE DELETE ON observation_relations
BEGIN SELECT RAISE(ABORT, 'Immutable evidence'); END;
