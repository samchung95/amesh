# Kestra 1.3.30 compatibility evidence

These clean-room fixtures target Kestra `v1.3.30`, revision `db49f3b`, using only public
documentation and black-box behavior. Reference observations are captured explicitly against the
digest-pinned `kestra/kestra:v1.3.30` image declared in the compatibility manifest and stored in the
isolated evidence directory. Local conformance tests compare AMESH behavior with that recorded
fixture; the ordinary merge gate does not start a live Kestra server. Raw upstream public identifiers
remain in the evidence directory rather than implementation source. The same source passes through
AMESH's source-preserving importer and native validator.

`kestra-1.3.30-observations.json` records the normalized, non-destructive reference and AMESH shadow
observations compared by the conformance tests. External side effects are suppressed or mocked;
duration is compared only within the explicit tolerance. The machine compatibility manifest remains
the authority for gaps and blocks a full-version compatibility claim while any gap is unresolved.
