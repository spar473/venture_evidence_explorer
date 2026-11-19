CREATE TABLE pool_imports (
  packet_sha256 TEXT PRIMARY KEY,
  kind TEXT NOT NULL CHECK (kind = 'fixture'),
  as_of TEXT NOT NULL,
  raw_bytes BLOB NOT NULL
);
CREATE TABLE pool_companies (
  packet_sha256 TEXT NOT NULL REFERENCES pool_imports,
  company_id TEXT NOT NULL,
  display_name TEXT NOT NULL,
  venture_id TEXT REFERENCES ventures(venture_id),
  research_subject_id TEXT,
  status TEXT NOT NULL CHECK (status IN ('reached_outcome', 'closed_before_outcome',
      'acquired_or_ipo_before_outcome', 'observed_no_outcome', 'lost_to_follow_up', 'unknown')),
  censor_on TEXT,
  PRIMARY KEY (packet_sha256, company_id),
  UNIQUE (packet_sha256, venture_id),
  UNIQUE (packet_sha256, research_subject_id),
  CHECK ((censor_on IS NOT NULL) = (status IN ('observed_no_outcome', 'lost_to_follow_up')))
);
CREATE TABLE pool_aliases (
  packet_sha256 TEXT NOT NULL,
  company_id TEXT NOT NULL,
  alias TEXT NOT NULL,
  PRIMARY KEY (packet_sha256, company_id, alias),
  FOREIGN KEY (packet_sha256, company_id) REFERENCES pool_companies
);
CREATE TABLE pool_sources (
  packet_sha256 TEXT NOT NULL REFERENCES pool_imports,
  source_id TEXT NOT NULL,
  url TEXT NOT NULL,
  published_on TEXT,
  retrieved_on TEXT NOT NULL,
  PRIMARY KEY (packet_sha256, source_id)
);
CREATE TABLE pool_witnesses (
  packet_sha256 TEXT NOT NULL,
  witness_id TEXT NOT NULL,
  source_id TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('publisher_dated', 'archived_capture')),
  available_on TEXT NOT NULL,
  captured_at TEXT,
  witness_url TEXT NOT NULL,
  locator TEXT NOT NULL,
  PRIMARY KEY (packet_sha256, witness_id),
  UNIQUE (packet_sha256, witness_id, source_id),
  FOREIGN KEY (packet_sha256, source_id) REFERENCES pool_sources,
  CHECK ((captured_at IS NOT NULL) = (kind = 'archived_capture'))
);
CREATE TABLE pool_events (
  packet_sha256 TEXT NOT NULL,
  event_id TEXT NOT NULL,
  company_id TEXT NOT NULL,
  kind TEXT NOT NULL,
  date_value TEXT,
  date_precision TEXT NOT NULL CHECK (date_precision IN ('day','month','quarter','year','unknown')),
  date_lower TEXT,
  date_upper TEXT,
  source_id TEXT NOT NULL,
  passage TEXT NOT NULL,
  round_label TEXT,
  PRIMARY KEY (packet_sha256, event_id),
  UNIQUE (packet_sha256, event_id, company_id),
  FOREIGN KEY (packet_sha256, company_id) REFERENCES pool_companies,
  FOREIGN KEY (packet_sha256, source_id) REFERENCES pool_sources
);
CREATE TABLE pool_snapshots (
  packet_sha256 TEXT NOT NULL,
  snapshot_id TEXT NOT NULL,
  company_id TEXT NOT NULL,
  stage_event_id TEXT NOT NULL,
  as_of TEXT NOT NULL,
  PRIMARY KEY (packet_sha256, snapshot_id),
  FOREIGN KEY (packet_sha256, stage_event_id, company_id) REFERENCES pool_events(packet_sha256, event_id, company_id)
);
CREATE TABLE pool_snapshot_features (
  packet_sha256 TEXT NOT NULL,
  snapshot_id TEXT NOT NULL,
  feature TEXT NOT NULL,
  value_json TEXT NOT NULL,
  source_id TEXT NOT NULL,
  witness_id TEXT NOT NULL,
  passage TEXT NOT NULL,
  PRIMARY KEY (packet_sha256, snapshot_id, feature),
  FOREIGN KEY (packet_sha256, snapshot_id) REFERENCES pool_snapshots,
  FOREIGN KEY (packet_sha256, witness_id, source_id) REFERENCES pool_witnesses(packet_sha256, witness_id, source_id)
);
CREATE TRIGGER pool_feature_witness_date BEFORE INSERT ON pool_snapshot_features
WHEN (SELECT available_on FROM pool_witnesses WHERE packet_sha256=NEW.packet_sha256 AND witness_id=NEW.witness_id)
   > (SELECT as_of FROM pool_snapshots WHERE packet_sha256=NEW.packet_sha256 AND snapshot_id=NEW.snapshot_id)
BEGIN
  SELECT RAISE(ABORT, 'Snapshot evidence was available after the cutoff');
END;
CREATE TRIGGER pool_witnesses_immutable BEFORE UPDATE ON pool_witnesses
BEGIN SELECT RAISE(ABORT, 'Pool witnesses are immutable'); END;
CREATE TRIGGER pool_snapshots_immutable BEFORE UPDATE ON pool_snapshots
BEGIN SELECT RAISE(ABORT, 'Pool snapshots are immutable'); END;
CREATE TRIGGER pool_features_immutable BEFORE UPDATE ON pool_snapshot_features
BEGIN SELECT RAISE(ABORT, 'Pool snapshot features are immutable'); END;
