CREATE TABLE discovery_imports (packet_sha256 TEXT PRIMARY KEY, raw_bytes BLOB NOT NULL, metadata_json TEXT NOT NULL, validation_as_of TEXT NOT NULL);
CREATE TABLE discovery_records (record_id TEXT PRIMARY KEY, collection TEXT NOT NULL, record_json TEXT NOT NULL);
CREATE INDEX ix_discovery_collection ON discovery_records(collection);
CREATE TABLE discovery_membership (packet_sha256 TEXT NOT NULL REFERENCES discovery_imports(packet_sha256),record_id TEXT NOT NULL REFERENCES discovery_records(record_id),ordinal INTEGER NOT NULL,PRIMARY KEY(packet_sha256,record_id));
CREATE TABLE discovery_links (owner_id TEXT NOT NULL REFERENCES discovery_records(record_id),role TEXT NOT NULL,target_id TEXT NOT NULL REFERENCES discovery_records(record_id),PRIMARY KEY(owner_id,role,target_id));
CREATE TABLE discovery_decision_documents (document_sha256 TEXT PRIMARY KEY,raw_bytes BLOB NOT NULL);
CREATE TABLE discovery_reviews (
 decision_id TEXT PRIMARY KEY, discovery_id TEXT NOT NULL REFERENCES discovery_records(record_id),kind TEXT NOT NULL,
 document_sha256 TEXT NOT NULL REFERENCES discovery_decision_documents(document_sha256),decision_json TEXT NOT NULL
);
CREATE TRIGGER immutable_discovery_imports_update BEFORE UPDATE ON discovery_imports BEGIN SELECT RAISE(ABORT,'Immutable discovery evidence'); END;
CREATE TRIGGER immutable_discovery_imports_delete BEFORE DELETE ON discovery_imports BEGIN SELECT RAISE(ABORT,'Immutable discovery evidence'); END;
CREATE TRIGGER immutable_discovery_records_update BEFORE UPDATE ON discovery_records BEGIN SELECT RAISE(ABORT,'Immutable discovery evidence'); END;
CREATE TRIGGER immutable_discovery_records_delete BEFORE DELETE ON discovery_records BEGIN SELECT RAISE(ABORT,'Immutable discovery evidence'); END;
CREATE TRIGGER immutable_discovery_membership_update BEFORE UPDATE ON discovery_membership BEGIN SELECT RAISE(ABORT,'Immutable discovery evidence'); END;
CREATE TRIGGER immutable_discovery_membership_delete BEFORE DELETE ON discovery_membership BEGIN SELECT RAISE(ABORT,'Immutable discovery evidence'); END;
CREATE TRIGGER immutable_discovery_links_update BEFORE UPDATE ON discovery_links BEGIN SELECT RAISE(ABORT,'Immutable discovery evidence'); END;
CREATE TRIGGER immutable_discovery_links_delete BEFORE DELETE ON discovery_links BEGIN SELECT RAISE(ABORT,'Immutable discovery evidence'); END;
CREATE TRIGGER immutable_discovery_reviews_update BEFORE UPDATE ON discovery_reviews BEGIN SELECT RAISE(ABORT,'Immutable discovery review'); END;
CREATE TRIGGER immutable_discovery_reviews_delete BEFORE DELETE ON discovery_reviews BEGIN SELECT RAISE(ABORT,'Immutable discovery review'); END;
CREATE TRIGGER immutable_discovery_documents_update BEFORE UPDATE ON discovery_decision_documents BEGIN SELECT RAISE(ABORT,'Immutable discovery review'); END;
CREATE TRIGGER immutable_discovery_documents_delete BEFORE DELETE ON discovery_decision_documents BEGIN SELECT RAISE(ABORT,'Immutable discovery review'); END;
