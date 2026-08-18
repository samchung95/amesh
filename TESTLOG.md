# Test Log

## M-0: Repository housekeeping + M-1: MVP re-scope — 2026-08-19

Spec source: PLAN.md M-0/M-1 DoD (housekeeping items from the 2026-08-18 repo review).

Verified (commands run from the repo root with the project's Python 3.12 venv):

- [x] `ruff format --check .` — 202 files, clean (was: 6 files needing reformat).
- [x] `ruff check .` — clean (was: 12 errors).
- [x] `python -m mypy` — strict, 18 source files, no issues (was: 3 pre-existing errors in `dsl/validator.py`, confirmed pre-existing via `git stash` against the baseline commit).
- [x] `python -m pytest` — 16 passed (13 baseline + 3 new regression tests), 1 benign starlette deprecation warning.
- [x] `python scripts/validate_backlog.py` — 103 epics, 900 requirements, 992 trace links valid.
- [x] `python scripts/check_clean_room.py` — lexical gate passed.
- [x] `python scripts/regenerate_planning_artifacts.py` then `git status` — zero drift (after `newline="\n"` fix; previously produced CRLF churn for every generated file on Windows).
- [x] `python scripts/generate_contracts.py` then `git status` — zero drift; fastapi/pydantic/pydantic-settings now pinned exactly so the byte-stable contract test cannot break via unpinned upgrades.
- [x] CLI smoke (real app): `python -m amesh validate examples/hello-world.yaml` → valid, stable semantic hash.
- [x] `dependsOn` bug: snake_case `depends_on` cycle now detected (`test_snake_case_depends_on_is_honoured`); snake/camel documents hash identically (`test_snake_case_and_camel_case_dependencies_hash_identically`).
- [x] Proto rename: `grep -r openorchestrator proto/` → no matches; packages are `amesh.worker.v1` / `amesh.plugin.v1`.
- [x] Git: repository initialized, baseline commit of the full tree, work on branch `worktree-housekeeping-mvp-rescope`.

Adversarial pass:

- Mixed spelling (`dependsOn` + `depends_on` on one task): **bug found** — validated silently with the snake_case copy riding along as an inert extra in the canonical dump. Fixed with a `mode="before"` validator rejecting conflicting spellings; regression test `test_conflicting_dependency_spellings_are_rejected`; probe re-run now rejects.
- Regeneration determinism on Windows: **bug found** — both generator scripts emitted CRLF via `write_text` default newline translation, which would trip the CI drift gates for any contributor on Windows. Fixed with `newline="\n"`; regeneration re-run shows zero modified files.

Not covered (deliberate):

- Proto files are not compiled (no `protoc` in the toolchain; repo commits no generated code) — the rename is textual and README-consistent only.
- `make validate` via GNU make (not present on this Windows host) — the underlying commands were run individually instead.
- The FastAPI server was exercised through the test client and CLI, not a live `uvicorn` boot.
- App-level defects noted in the review but scoped out of housekeeping (post-body 2 MiB guard, unbounded `applied_event_ids`, reducer fencing) — tracked for MVP weeks 1–2 in PLAN.md.

Verdict: PASS — M-0 and M-1 closed.
