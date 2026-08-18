# Provisional wire contracts

These Protocol Buffer files make the worker and isolated-plugin boundaries concrete enough for review.
They are **not yet stable** and no generated code is committed.

Rules before acceptance:

- authenticate every connection and bind it to tenant/worker/plugin identity;
- negotiate protocol and platform ranges;
- bound every message and use object-storage references for large data;
- preserve correlation, trace and idempotency fields in the production envelope;
- reject stale fencing tokens;
- add compatibility tests before publishing generated SDKs.
