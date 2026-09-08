BEGIN;

-- Flow-test state already has forced tenant RLS; its repositories now use that boundary.
GRANT SELECT, INSERT, UPDATE, DELETE ON flow_test_definitions TO amesh_runtime;
GRANT SELECT, INSERT ON flow_test_runs TO amesh_runtime;
GRANT SELECT, INSERT, UPDATE ON flow_test_quality_gates TO amesh_runtime;

COMMIT;
