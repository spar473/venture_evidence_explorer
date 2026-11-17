CREATE TRIGGER immutable_sources_update BEFORE UPDATE ON sources
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_sources_delete BEFORE DELETE ON sources
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_observations_update BEFORE UPDATE ON observations
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_observations_delete BEFORE DELETE ON observations
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_awards_update BEFORE UPDATE ON awards
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_awards_delete BEFORE DELETE ON awards
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_connections_update BEFORE UPDATE ON connections
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_connections_delete BEFORE DELETE ON connections
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_annotations_update BEFORE UPDATE ON annotations
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_annotations_delete BEFORE DELETE ON annotations
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_annotation_evidence_update BEFORE UPDATE ON annotation_evidence
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_annotation_evidence_delete BEFORE DELETE ON annotation_evidence
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_review_events_update BEFORE UPDATE ON review_events
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER immutable_review_events_delete BEFORE DELETE ON review_events
BEGIN SELECT RAISE(ABORT, 'Immutable evidence: append a new version or review event'); END;
CREATE TRIGGER connection_subject BEFORE INSERT ON connections
WHEN NOT EXISTS (SELECT 1 FROM observations o WHERE o.observation_id=NEW.observation_id AND o.venture_id=NEW.venture_id AND o.field='uoa_connection')
BEGIN SELECT RAISE(ABORT, 'Connection evidence subject mismatch'); END;
CREATE TRIGGER annotation_subject BEFORE INSERT ON annotation_evidence
WHEN NOT EXISTS (SELECT 1 FROM observations o JOIN annotations a ON a.venture_id=o.venture_id WHERE o.observation_id=NEW.observation_id AND a.annotation_id=NEW.annotation_id)
BEGIN SELECT RAISE(ABORT, 'Annotation evidence subject mismatch'); END;
