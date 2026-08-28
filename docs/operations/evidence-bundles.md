# Evidence bundle operations

Migration `0061_canonical_evidence_bundles.sql` is additive. Apply it through the normal
transactional migration runner before enabling canonical evidence retrieval. It creates the
tenant-isolated immutable projection and its post-commit outbox event; do not edit or delete a
bundle in place.

For the checked-in local profile, set `AMESH_EVIDENCE_OBJECT_ROOT` to a writable directory. Large
redacted payloads are stored under their SHA-256 digest and are verified by digest and byte count
on every read. Back up this directory with the database. A missing object is unavailable evidence,
not an empty successful result; restore the object or use the provider-neutral object-store adapter
before retrying retrieval.

The REST, CLI and SDK surfaces cap a page at 500 records. A `404` means the execution or canonical
bundle is absent; `503` means PostgreSQL or external object storage is unavailable. A digest
mismatch or immutable conflict is an integrity incident: stop writes for the affected execution,
retain the original database row and object bytes for investigation, and repair through an approved
forward migration or restore. Retention and deletion must be handled by the platform's approved
tenant lifecycle process, not by ad hoc SQL.
