BEGIN;

CREATE OR REPLACE FUNCTION notify_amesh_work() RETURNS trigger AS $$
BEGIN
    PERFORM pg_notify(
        'amesh_work_' || replace(NEW.tenant_id::text, '-', ''),
        NEW.lane
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMIT;
