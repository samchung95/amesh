# Kestra 1.3.30 compatibility evidence

These clean-room fixtures target Kestra `v1.3.30`, revision `db49f3b`, using only public
documentation and black-box behavior. CI starts the digest-pinned `kestra/kestra:v1.3.30` image
declared in the compatibility manifest in an isolated local container and submits
`conformance/kestra/1.3.30/kestra-core-flow.yaml` to the pinned server validator. Raw upstream public
identifiers remain in that isolated evidence directory rather than implementation source. The same
source then passes through AMESH's source-preserving importer and native validator.

`kestra-1.3.30-observations.json` records the normalized, non-destructive reference and AMESH shadow
observations compared by the conformance tests. External side effects are suppressed or mocked;
duration is compared only within the explicit tolerance. The machine compatibility manifest remains
the authority for gaps and blocks a full-version compatibility claim while any gap is unresolved.
