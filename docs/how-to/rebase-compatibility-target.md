# Rebase the compatibility target

Use this procedure to move AMESH from one pinned public compatibility release to another without transferring reference implementation material into the implementation context.

## Prepare the research record

1. Assign a reference researcher who is not the implementer for the rebase changes.
2. Record the public release version, tag, full commit, release date, retrieval date and public documentation indexes.
3. Write neutral behavior changes and independent black-box fixtures. Do not attach upstream source, tests, documentation prose or assets.
4. Obtain reviewer approval for the research record before giving the neutral specification and fixtures to the implementer.

## Update the pinned target

1. Create a dedicated branch.
2. Change `parity_target` in `project-baseline.json`.
3. Change `target`, source locations, identifiers and retrieval dates in `requirements/source-provenance.json`.
4. Update the pinned release section in `SOURCES.md` and the target description in `docs/product/parity-charter.md`.
5. Update affected canonical requirements, epic labels and independently authored fixtures. Use `difference:intentional` or `parity:deferred` only when that disposition is explicit and reviewed.

## Regenerate and review

1. Run:

   ```powershell
   uv run --extra runtime --extra dev python scripts/regenerate_planning_artifacts.py
   uv run --extra runtime --extra dev python scripts/validate_backlog.py
   uv run --extra runtime --extra dev python scripts/check_clean_room.py
   uvx --from 'reuse[charset-normalizer]==6.2.0' reuse lint
   ```

2. Review every changed entry in `requirements/compatibility-inventory.json`. A target change must never silently turn a prior verified item into a compatibility claim for the new release.
3. Run the affected positive, negative, recovery and differential fixtures.

## Run the isolated similarity review

1. In the reviewer context, check out the exact target commit outside the AMESH repository.
2. Run:

   ```powershell
   uv run python scripts/check_clean_room.py --reference-tree ..\isolated-reference
   ```

3. Review every reported path pair. The report contains only AMESH paths, reference paths and one-way token-shingle counts; do not copy reference content into the repository or implementation prompts.
4. Delete the isolated reference checkout after the review.

## Accept the rebase

The rebase is complete only when the target matches across the baseline, URS, provenance registry and compatibility inventory; all inventory rows have known source identifiers and explicit dispositions; affected fixtures pass; REUSE and similarity gates pass; and the reviewer and verifier are independent from the implementer.
