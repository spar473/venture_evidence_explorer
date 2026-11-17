CREATE VIEW v_programme_recognition AS
 SELECT programme, award_year, COUNT(*) AS recorded_awards,
 COUNT(DISTINCT venture_id) AS distinct_ventures
 FROM awards GROUP BY programme, award_year;
CREATE VIEW v_connection_coverage AS
 SELECT connection_type, COUNT(*) AS recorded_connections,
 COUNT(DISTINCT venture_id) AS distinct_ventures
 FROM connections GROUP BY connection_type;
CREATE VIEW v_source_coverage AS
 SELECT v.venture_id, v.display_name,
 COUNT(DISTINCT o.source_id) AS source_count,
 COUNT(o.observation_id) AS observation_count,
 MIN(s.published_at) AS earliest_source_date,
 MAX(s.published_at) AS latest_source_date,
 MAX(s.retrieved_at) AS latest_retrieval_date,
 date('now') AS as_of_date,
 CAST(julianday(date('now')) - julianday(MAX(s.published_at)) AS INTEGER) AS latest_source_age_days,
 CASE WHEN MAX(s.published_at) IS NULL THEN 'No sourced observations recorded'
 ELSE 'Historical publisher reports; current status unverified' END AS evidence_note
 FROM ventures v LEFT JOIN observations o USING(venture_id)
 LEFT JOIN sources s USING(source_id) GROUP BY v.venture_id, v.display_name;
CREATE VIEW v_raw_observations AS SELECT * FROM v_observation_evidence;
CREATE VIEW v_proposed_annotations AS SELECT * FROM annotations WHERE review_status='proposed';
CREATE TABLE review_events (
 review_event_id TEXT PRIMARY KEY,
 observation_id TEXT REFERENCES observations(observation_id),
 annotation_id TEXT REFERENCES annotations(annotation_id),
 decision TEXT NOT NULL CHECK(decision IN ('accepted','rejected','needs_review')),
 reviewer TEXT NOT NULL, reviewed_at TEXT NOT NULL, rationale TEXT NOT NULL,
 CHECK((observation_id IS NULL) != (annotation_id IS NULL))
);
