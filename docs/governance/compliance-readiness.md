# SOC 2 and ISO/IEC 27001 readiness

## Scope

AMESH is designed for SOC 2 and ISO/IEC 27001 readiness before GA. Readiness means the architecture, policies, procedures and evidence model make applicable controls traceable and reviewable. It does not mean AMESH or an operator is certified.

Certification depends on the operating organisation, deployed environment, people, processes, evidence period and independent auditor or certification body.

## Control crosswalk

AMESH maintains a versioned machine-readable crosswalk with:

- framework and control identifier;
- applicability decision and rationale;
- responsible owner;
- linked URS requirements and epics;
- implementation or operating procedure;
- automated and manual evidence sources;
- evidence collection cadence;
- test or review method;
- exceptions, compensating controls and expiry;
- current gap and remediation plan;
- release and deployment scope.

Framework text is referenced according to applicable rights and is not copied into the repository beyond what is permitted.

## Evidence domains

Evidence packages may include:

- user, group, role, binding and service-account inventories;
- authentication, authorization and access-review records;
- protected-branch, review, merge and release evidence;
- configuration and change history;
- audit events and audit-access events;
- vulnerability, dependency, container and secret-scan results;
- SBOMs, signatures and provenance;
- backup verification and restore-exercise results;
- incident, alert and response records;
- availability, capacity and recovery reports;
- key, certificate and secret-reference rotation evidence;
- tenant-isolation and negative authorization test results;
- risk acceptance and exception records.

Evidence export is permission-scoped, redacted and checksummed. Exporting evidence is itself audited.
The implemented API and package layout are documented in the
[audit and compliance guide](../api/audit-and-compliance.md), with operating procedures in the
[audit evidence runbook](../operations/audit-evidence.md).

## Architecture implications

- Audit events must be complete enough to identify actor, delegated identity, tenant, resource, action, result, reason, timestamp, correlation and trace context.
- Security-relevant state changes should write audit evidence transactionally with the state change where possible.
- Retention and legal hold are independent from normal workflow-data retention.
- Release artifacts require SBOM, signature, provenance and reproducible-build evidence.
- Access reviews require stable inventories and explainable inherited permissions.
- Backup and restore evidence records measured RPO and RTO rather than only the existence of a backup job.
- AI-authored changes require attributable implementer, reviewer and verifier identities and deterministic eligibility evidence.
- Secrets and protected values are never included in evidence exports.

## Release gate

Before GA:

1. every applicable control in the selected readiness scope has an owner and mapping;
2. every Must mapping has at least one defined evidence source and verification method;
3. missing evidence and exceptions are reported rather than silently passed;
4. a sample evidence package is reviewed independently;
5. product documentation clearly distinguishes readiness, customer responsibility and certification.

Formal SOC 2 examination or ISO/IEC 27001 certification is not a v1 release gate unless a later product decision changes the scope.
