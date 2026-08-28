# Plugin SDK compatibility and deprecation policy

AMESH versions the manifest, extension API and wire protocol independently. Published JSON Schemas
are normative; language SDKs must not add behavior that cannot be represented by those schemas.

The compatibility rules are:

- patch releases may clarify documentation and fix implementations without changing accepted or
  emitted contract documents;
- minor releases may add optional fields, enum handling that is explicitly forward-compatible, new
  operations behind negotiation, and new SDK helpers;
- removing or renaming a field, making an optional field required, changing meaning or type, removing
  an operation, or narrowing accepted behavior requires a major contract version;
- a breaking contract change never enters a minor or patch release without an approved ADR that
  names the exception, migration, affected versions and support window;
- plugins declare both a platform SemVer range and supported protocol versions. Resolution fails
  closed when no intersection exists; an installed historical version remains evidence-addressable;
- deprecations identify the subject, introduction version, planned removal version, replacement and
  user-facing message in the manifest. Normal removal occurs only in a major contract version after
  at least two minor releases and 180 days of published notice;
- urgent security removal may shorten that window only through a published advisory and approved
  exception. The old behavior must fail with a structured compatibility error, not disappear silently.

CI regenerates and compares the manifest/request/response schemas. A schema diff that violates these
rules blocks release until the version and migration evidence are corrected.
