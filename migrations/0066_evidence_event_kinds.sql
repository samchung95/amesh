BEGIN;

ALTER TABLE execution_evidence_events
    DROP CONSTRAINT execution_evidence_events_kind_check;

ALTER TABLE execution_evidence_events
    ADD CONSTRAINT execution_evidence_events_kind_check
    CHECK (
        kind IN (
            'STATE', 'LOG', 'METRIC', 'OUTPUT', 'ARTIFACT',
            'AGENT', 'MODEL', 'TOOL', 'ERROR', 'APPROVAL',
            'INTERVENTION', 'CONTROL', 'DECISION'
        )
    );

COMMIT;
