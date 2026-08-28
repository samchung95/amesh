# ADR-063: Local recovery and protected trigger payloads

Status: accepted

Context: Split-role execution skipped handlers available in the API process, delayed fresh work by
the abandoned-work grace, and could only durably retry the redacted form of sensitive webhook input.

Decision: Dispatch fresh work immediately and apply recovery grace only to persisted running work;
compose subflow, approval and isolated-plugin handlers in every executor role. Persist trigger input
as a redacted projection plus an application-encrypted recoverable value, decrypting only when an
accepted occurrence creates its execution. Clear browser state at route/principal boundaries and
enforce the task-runner output limit in Docker as required by the shared runner contract.

Consequences: Split and monolithic execution paths retain the same capabilities without weakening
fencing. Public trigger evidence remains redacted, while durable retry can reproduce the accepted
input. Encryption-key loss makes protected pending occurrences unrecoverable and must fail closed.
