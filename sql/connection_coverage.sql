-- Overlapping relationships; do not sum as unique ventures.
SELECT * FROM v_connection_coverage ORDER BY distinct_ventures DESC,connection_type;
