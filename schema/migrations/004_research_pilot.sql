-- Distinct research namespace. No promotion into the original retrieval corpus.
CREATE TABLE research_imports (
 namespace TEXT NOT NULL, packet_sha256 TEXT NOT NULL, format_version TEXT NOT NULL CHECK(format_version='0.2.1'),
 raw_bytes BLOB NOT NULL, metadata_json TEXT NOT NULL, semantic_sha256 TEXT NOT NULL,
 validation_as_of TEXT NOT NULL, imported_at TEXT NOT NULL,
 PRIMARY KEY(namespace,packet_sha256)
);
CREATE TABLE research_records (
 namespace TEXT NOT NULL, collection TEXT NOT NULL CHECK(collection IN
 ('subjects','parties','sources','observations','events','event_reports','unknowns',
 'proposed_annotations','readiness','reconciliation_cases','access_gaps','review_events','requirements','conclusions')),
 record_id TEXT NOT NULL, record_json TEXT NOT NULL, PRIMARY KEY(namespace,record_id)
);
CREATE INDEX ix_research_collection ON research_records(namespace,collection);
CREATE TABLE research_import_records (
 namespace TEXT NOT NULL, packet_sha256 TEXT NOT NULL, record_id TEXT NOT NULL, record_order INTEGER NOT NULL,
 PRIMARY KEY(namespace,packet_sha256,record_id),
 FOREIGN KEY(namespace,packet_sha256) REFERENCES research_imports(namespace,packet_sha256),
 FOREIGN KEY(namespace,record_id) REFERENCES research_records(namespace,record_id)
);
CREATE TABLE research_links (
 namespace TEXT NOT NULL, owner_id TEXT NOT NULL, field_path TEXT NOT NULL, target_id TEXT NOT NULL,
 PRIMARY KEY(namespace,owner_id,field_path,target_id),
 FOREIGN KEY(namespace,owner_id) REFERENCES research_records(namespace,record_id),
 FOREIGN KEY(namespace,target_id) REFERENCES research_records(namespace,record_id)
);
CREATE INDEX ix_research_link_target ON research_links(namespace,target_id);
CREATE TABLE research_time_values (
 namespace TEXT NOT NULL, owner_id TEXT NOT NULL, field_path TEXT NOT NULL,
 raw_value TEXT, precision TEXT NOT NULL CHECK(precision IN ('unknown','day','month','year')),
 lower_bound TEXT, upper_bound TEXT, basis TEXT NOT NULL, unknown_reason TEXT,
 PRIMARY KEY(namespace,owner_id,field_path),
 FOREIGN KEY(namespace,owner_id) REFERENCES research_records(namespace,record_id),
 CHECK((precision='unknown' AND raw_value IS NULL AND lower_bound IS NULL AND upper_bound IS NULL AND unknown_reason IS NOT NULL)
 OR (precision<>'unknown' AND raw_value IS NOT NULL AND lower_bound IS NOT NULL AND upper_bound IS NOT NULL AND lower_bound<=upper_bound))
);
CREATE TABLE research_mapping_documents (
 decision_sha256 TEXT PRIMARY KEY, raw_bytes BLOB NOT NULL,
 validation_as_of TEXT NOT NULL, imported_at TEXT NOT NULL
);
CREATE TABLE research_identity_mappings (
 mapping_id TEXT PRIMARY KEY, namespace TEXT NOT NULL, subject_id TEXT NOT NULL,
 venture_id TEXT NOT NULL REFERENCES ventures(venture_id),
 state TEXT NOT NULL CHECK(state IN ('proposed','resolved','rejected')),
 scope TEXT NOT NULL CHECK(scope='brand_project_only'),
 actor_role TEXT NOT NULL CHECK(actor_role IN ('supplied_proposal','owner','independent_reviewer')),
 actor_id TEXT, decided_on TEXT, evidence_ids_json TEXT NOT NULL, rationale TEXT NOT NULL,
 source_packet_sha256 TEXT NOT NULL,
 decision_document_sha256 TEXT REFERENCES research_mapping_documents(decision_sha256),
 supersedes_mapping_id TEXT REFERENCES research_identity_mappings(mapping_id),
 legal_identity_state TEXT NOT NULL CHECK(legal_identity_state='unresolved'),
 FOREIGN KEY(namespace,subject_id) REFERENCES research_records(namespace,record_id),
 FOREIGN KEY(namespace,source_packet_sha256) REFERENCES research_imports(namespace,packet_sha256),
 CHECK((state='proposed' AND actor_role='supplied_proposal' AND actor_id IS NULL AND decided_on IS NULL)
 OR (state IN ('resolved','rejected') AND actor_role IN ('owner','independent_reviewer') AND length(trim(actor_id))>0 AND decided_on IS NOT NULL))
);
CREATE INDEX ix_research_mapping_subject ON research_identity_mappings(namespace,subject_id);
CREATE TRIGGER research_mapping_subject BEFORE INSERT ON research_identity_mappings
WHEN NOT EXISTS(SELECT 1 FROM research_records WHERE namespace=NEW.namespace AND record_id=NEW.subject_id AND collection='subjects')
BEGIN SELECT RAISE(ABORT, 'Research mapping target must be a research subject'); END;
CREATE TRIGGER research_link_namespace BEFORE INSERT ON research_links
WHEN NEW.namespace<>'research:0.2.1'
BEGIN SELECT RAISE(ABORT, 'Unsupported research namespace'); END;
CREATE TRIGGER immutable_research_imports_update BEFORE UPDATE ON research_imports
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_imports_delete BEFORE DELETE ON research_imports
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_records_update BEFORE UPDATE ON research_records
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_records_delete BEFORE DELETE ON research_records
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_import_records_update BEFORE UPDATE ON research_import_records
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_import_records_delete BEFORE DELETE ON research_import_records
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_links_update BEFORE UPDATE ON research_links
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_links_delete BEFORE DELETE ON research_links
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_time_values_update BEFORE UPDATE ON research_time_values
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_time_values_delete BEFORE DELETE ON research_time_values
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_identity_mappings_update BEFORE UPDATE ON research_identity_mappings
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_identity_mappings_delete BEFORE DELETE ON research_identity_mappings
BEGIN SELECT RAISE(ABORT,'Immutable research evidence'); END;

CREATE TRIGGER immutable_research_mapping_documents_update BEFORE UPDATE ON research_mapping_documents
BEGIN SELECT RAISE(ABORT, 'Immutable research evidence'); END;
CREATE TRIGGER immutable_research_mapping_documents_delete BEFORE DELETE ON research_mapping_documents
BEGIN SELECT RAISE(ABORT, 'Immutable research evidence'); END;
