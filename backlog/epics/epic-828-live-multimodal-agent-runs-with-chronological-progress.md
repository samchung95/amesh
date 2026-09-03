# EPIC-828 — Live multimodal agent runs with chronological progress

- **Milestone:** M8 — Differentiation and general availability
- **Priority:** Must
- **Domain:** `differentiation`
- **Primary persona:** AI application and workflow developer
- **Parity scope:** AMESH quality and architecture requirement

## Outcome

Let users watch a running agent as one truthful, reconnectable chronological timeline and make governed image input a shared platform capability for workflows, tasks, plugins and sessions without exposing hidden reasoning or duplicating binary state.

## In scope

- [x] Governed image input is a shared platform primitive over artifact, workflow, task and plugin contracts—not a session-orchestrator-only feature; every node may carry the typed reference and every consuming node declares whether it can interpret image content.
- [x] A versioned provider- and harness-neutral progress contract carries a global durable cursor, attempt identity, turn and activity correlation, stable segment identity, typed phase and status, timestamps, idempotent source sequence and bounded public detail.
- [x] The canonical journal records progress, model, policy, approval, tool, validation, artifact, output and terminal events in accepted arrival order; non-contiguous progress segments are never merged, so a fixture proves thinking 1, tool work and thinking 2 remain three chronological activities.
- [x] Progress reaches authorized clients while the session is still running, and reconnect from the last acknowledged cursor reproduces the same order without gaps or duplicates across retries, restarts and a change of session attempt.
- [x] Only fixed, taxonomy-defined factual lifecycle status may appear as thinking detail; provider-authored summaries, raw or hidden chain-of-thought, reasoning content or details, encrypted reasoning, scratchpads, prompts, messages, continuation state, credentials, secrets and protected personal data never enter the public progress contract.
- [x] Streaming is bounded by declared frame, segment, session, buffer and rate limits with explicit coalescing, truncation, heartbeat, backpressure, cancellation, timeout and partial-segment terminal semantics; slow observers cannot block canonical execution.
- [x] Pi and future conforming harnesses use the same progress sink and multimodal message contract, while AMESH remains the only authority allowed to call providers, resolve image bytes, execute tools and commit workflow or session state.
- [x] A versioned provider-neutral content-part contract represents text and image references with tenant, asset identity, immutable checksum, media type, byte size, optional safe display metadata and placement order without embedding object-store credentials or raw image bytes in durable events.
- [x] Authenticated clients can upload or select one or more bounded images for a session's initial request and supported later message requests, and those images reach the exact pinned image-capable model together with text and structured-output constraints.
- [x] Workflow authors can declare image inputs, bind image references into any task or agent-session node, and pass images produced or selected at one stage into later eligible nodes, loops, branches and subflows without copying binary payloads into the flow document, execution row or event journal.
- [x] Ordinary task and plugin inputs and outputs use the same image-reference value, so non-agent workflows can ingest, transform, route or hand off governed images without depending on the session service.
- [x] Task, model, provider and harness capability declarations identify supported input modalities and limits; admission fails before provider work when an image is routed to an incompatible node or exact model route, with a typed safe error instead of silently dropping or textifying the image.
- [x] Image ingestion validates supported media type, actual decoded content, checksum, size, count and tenant ownership; private images remain in governed object storage and public traces expose reference metadata only under existing authorization, retention and legal-hold controls.
- [x] The OpenRouter adapter maps governed image references to the provider's supported multipart request shape only at invocation time, preserves image-related usage and cost evidence when reported, and streams normalized progress without leaking provider-specific fields into canonical contracts.
- [x] Canonical session APIs, the selected OpenAI-compatible image-input subset, workflow schemas, CLI and generated Python, TypeScript, Java and Go SDKs expose the new typed contracts with documented compatibility and unsupported-case behavior.
- [x] The Session Control Room, Session Orchestrator trace and workflow run inspector render one accessible live timeline; only contiguous deltas with the same segment identity may coalesce, image inputs appear as safe thumbnails or metadata, and reconnect, loading, empty, failure and reduced-motion states are explicit.
- [x] Provider-free conformance fixtures and an opt-in OpenRouter openai/gpt-5.6-luna qualification prove image-plus-text input, structured output, usage and cost accounting, live chronological progress, tool interleaving, reconnect and restart behavior through Pi.

## Explicit non-goals

- Persisting, reconstructing or exposing hidden chain-of-thought, raw reasoning streams, scratchpads or encrypted reasoning payloads
- Persisting or displaying provider-authored thought or summary text as public progress
- Creating an unbounded token transcript, replacing the canonical session journal or allowing a harness or provider to write it directly
- Building OCR, computer-vision analysis, image editing or image-generation tools into AMESH core; those remain provider or plugin capabilities
- Allowing arbitrary remote image URLs to bypass governed ingestion, tenant authorization, egress policy or SSRF protections
- Claiming that every task, provider or model can consume images when it has not declared and passed the multimodal conformance contract
- Adding audio, video or general file multimodality beyond the image-input contract in this epic
- Changing immutable capability pins or replacing workflow and session state authority during an active run

## Non-functional requirements

- [ ] No epic-specific NFR is mapped yet; general security, maintainability and test gates still apply.

## Dependencies

- EPIC-010
- EPIC-205
- EPIC-401
- EPIC-507
- EPIC-605
- EPIC-703
- EPIC-807
- EPIC-808
- EPIC-812
- EPIC-813
- EPIC-819
- EPIC-821
- EPIC-823
- EPIC-824
- EPIC-826
- EPIC-827

## Architecture impact

- Primary bounded area: `differentiation`.
- Public contracts introduced or changed must be versioned and documented.
- Durable state changes must use the command/event/outbox model.
- Tenant, authorization, audit, telemetry and failure behavior must be reviewed.

## Verification plan

- Contract-first schema, privacy and event-reducer tests for progress segments, multimodal content parts, bounds, idempotency and the exact thinking-1/tool/thinking-2 sequence.
- Workflow data-contract, object-storage, expression, loop, branch and subflow tests that route digest-pinned image references through initial and intermediate nodes.
- Provider and Pi harness conformance tests for ordered progress delivery, image-capability negotiation, multipart mapping, structured output, usage, cost, timeout and cancellation.
- PostgreSQL journal and API tests for atomic event append, attempt-aware cursors, concurrent readers, reconnect, restart, tenant isolation, payload redaction and terminal closure.
- OpenAI-compatible adapter, canonical OpenAPI, CLI and generated Python, TypeScript, Java and Go SDK compatibility and drift tests.
- React unit and Playwright tests for session image attachment, workflow image binding, live chronological rendering, reconnect de-duplication, responsive layouts and accessibility.
- Adversarial image tests for forged media types, oversized or corrupt content, cross-tenant references, external-URL SSRF attempts, event/evidence leakage and unsupported models.
- Complete Docker-local verification aggregate followed by an opt-in OpenRouter openai/gpt-5.6-luna multimodal live smoke.
- Acceptance criterion 10 and workflow definition-of-done item 2: [`tests/workflow/test_image_data_contracts.py`](../../tests/workflow/test_image_data_contracts.py), exact pytest node `tests/workflow/test_image_data_contracts.py::test_governed_image_ref_survives_branch_loop_subflow_and_retry`, proves one governed reference preserves tenant, checksum and retry identity through a branch, loop, subflow and later image-capable agent binding without durable binary copying.
- Workflow definition-of-done item 2 executable journey: [`docs/how-to/route-governed-images-through-workflows.md`](../../docs/how-to/route-governed-images-through-workflows.md), [`examples/governed-image-routing.yaml`](../../examples/governed-image-routing.yaml) and [`examples/governed-image-child.yaml`](../../examples/governed-image-child.yaml).
- Documentation and migration-note definition-of-done evidence: [`migrations/README.md`](../../migrations/README.md) and [`migrations/0072_agent_session_progress.sql`](../../migrations/0072_agent_session_progress.sql).
- Acceptance criteria 2–6: exact chronology, privacy, idempotency, cursor and bound evidence is in [`tests/domain/test_agent_progress.py`](../../tests/domain/test_agent_progress.py), [`tests/tasks/test_bounded_agent_tasks.py`](../../tests/tasks/test_bounded_agent_tasks.py) and [`tests/api/test_agent_progress_api.py`](../../tests/api/test_agent_progress_api.py).
- Acceptance criteria 1 and 8–14: shared image value, validation, routing, modality admission and provider-boundary evidence is in [`tests/domain/test_image_inputs.py`](../../tests/domain/test_image_inputs.py), [`tests/domain/test_image_validation.py`](../../tests/domain/test_image_validation.py), [`tests/workflow/test_image_data_contracts.py`](../../tests/workflow/test_image_data_contracts.py), [`tests/tasks/test_agent_sessions.py`](../../tests/tasks/test_agent_sessions.py), [`tests/adapters/test_openai_compatible.py`](../../tests/adapters/test_openai_compatible.py) and [`tests/adapters/test_openai_session.py`](../../tests/adapters/test_openai_session.py).
- Acceptance criteria 7 and 17: Pi authority, ordered progress, multimodal, cache-accounting, timeout and live Luna evidence is in [`tests/adapters/test_agent_session_harness.py`](../../tests/adapters/test_agent_session_harness.py), [`harnesses/pi/test/worker.test.mjs`](../../harnesses/pi/test/worker.test.mjs) and [`tests/llm/test_openrouter_pi_qualification.py`](../../tests/llm/test_openrouter_pi_qualification.py).
- Acceptance criterion 9 later-turn evidence: exact pytest nodes `tests/tasks/test_agent_sessions.py::test_later_session_turn_resumes_exact_checkpoint_with_text_and_image`, `tests/tasks/test_agent_sessions.py::test_later_session_turn_rejects_unsupported_image_route_before_model_io`, `tests/api/test_agent_session_service_contract.py::test_follow_up_message_is_image_governed_exactly_pinned_and_idempotent` and `tests/adapters/postgres/test_agent_session_repository.py::test_session_journal_is_idempotent_recoverable_and_projected_to_execution_evidence`.
- Acceptance criterion 15: canonical route, CLI and four generated-client drift evidence is in [`tests/api/test_agent_session_service_contract.py`](../../tests/api/test_agent_session_service_contract.py), [`tests/test_agent_session_cli.py`](../../tests/test_agent_session_cli.py) and [`tests/test_generated_contracts.py`](../../tests/test_generated_contracts.py).
- Acceptance criterion 16: component and three-surface browser evidence is in [`frontend/src/features/agent-sessions/AgentProgressTimeline.test.tsx`](../../frontend/src/features/agent-sessions/AgentProgressTimeline.test.tsx), [`frontend/e2e/agent-sessions.spec.ts`](../../frontend/e2e/agent-sessions.spec.ts), [`frontend/e2e/session-orchestrator.spec.ts`](../../frontend/e2e/session-orchestrator.spec.ts) and `frontend/e2e/shell.spec.ts::inspects a canonical agent run and submits one frozen replay`.
- Add requirement-to-test evidence links before changing any requirement to Verified.
- Add failure, duplicate, restart and authorization scenarios where applicable.

## Definition of done

- [x] One documented session journey accepts text plus an image, displays live ordered progress around at least one intervening activity and returns the pinned structured result without exposing hidden reasoning or image bytes in public evidence.
- [x] One documented workflow journey accepts an image, passes its immutable reference through an intermediate node into a later image-capable agent node and preserves lineage, tenant isolation and retry identity.
- [x] The provider, harness, journal and public-stream contracts preserve chronological segment boundaries under reconnect and restart, including thinking 1, work and thinking 2 with no regrouping.
- [x] Image capability negotiation, validation, storage, authorization, retention and unsupported-route failures are enforced before external model work and verified without adding client-domain image processing to AMESH core.
- [x] Canonical APIs, OpenAI-compatible subset, CLI, four SDKs and all three run-inspection UI surfaces are current, documented and covered by focused contract and accessibility tests.
- [x] The complete Docker-local gate passes and a separate opt-in Luna run records multimodal, progress, structured-output, token, cost and cache evidence with explicit provider-specific non-claims.
- [x] All Must requirements listed above are implemented or explicitly re-scoped through an approved decision.
- [x] Public API, DSL, event and plugin contract changes pass compatibility checks.
- [x] Unit, contract, integration and end-to-end evidence appropriate to risk is linked.
- [x] Security, tenant isolation, redaction and audit behavior are reviewed.
- [x] Documentation, examples, migration notes and operational runbooks are updated.
- [x] Performance and recovery budgets are measured when this epic is on a critical path.
- [x] `python scripts/validate_backlog.py` passes.

## Risks and unknowns

- If progress is buffered or grouped after a turn, the visible trace can reorder model reasoning around real tool work and become operationally misleading.
- Reasoning-shaped provider fields can expose hidden model rationale or private context unless the public progress taxonomy is allowlisted before persistence.
- Per-token persistence and unbounded observers can overload PostgreSQL and execution workers unless batching, limits and backpressure are explicit.
- Image bytes or signed URLs can leak through messages, traces, evidence, caches or portable bundles unless durable records contain only governed references and safe metadata.
- Provider and model image limits vary, so capability drift can create silent degradation unless exact routes are checked and qualified at admission and invocation.
- Attempt-local cursors can skip events after retry unless reconnect identity includes the attempt or uses a service-wide monotonic cursor.

## Traceability

- Functional requirements: none
- Non-functional requirements: none specifically mapped
- Source scope: AMESH quality and architecture requirement
