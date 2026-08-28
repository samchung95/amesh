BEGIN;

ALTER TABLE flow_revisions
    DROP CONSTRAINT IF EXISTS flow_revisions_tenant_id_flow_id_semantic_hash_key;

ALTER TABLE flow_revision_events
    DROP CONSTRAINT flow_revision_events_flow_id_fkey,
    ADD CONSTRAINT flow_revision_events_flow_id_fkey
        FOREIGN KEY (flow_id) REFERENCES flows(id) ON DELETE CASCADE;

CREATE OR REPLACE FUNCTION amesh_delete_flow_revision_event_outbox() RETURNS trigger AS $$
BEGIN
    DELETE FROM messages_outbox
    WHERE tenant_id = OLD.tenant_id AND message_id = OLD.event_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER delete_flow_revision_event_outbox
BEFORE DELETE ON flow_revision_events
FOR EACH ROW EXECUTE FUNCTION amesh_delete_flow_revision_event_outbox();

COMMIT;
