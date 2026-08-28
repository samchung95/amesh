# ADR-042: One protocol-v5 provider for Terraform and OpenTofu

- Status: Accepted
- Date: 2026-08-23
- Scope: EPIC-701

## Decision

AMESH ships one Go provider module under `providers/terraform` using HashiCorp's Terraform Plugin
Framework. The provider server uses plugin protocol version 5 so one release remains compatible with
Terraform 1.x and the OpenTofu 1.x compatibility line. Provider releases use the source address
`registry.terraform.io/amesh/amesh`; an OpenTofu filesystem mirror may install the same artifacts.

Each supported AMESH configuration kind has a named managed resource and data source. The provider
uses the public `/api/v1` and SCIM contracts rather than direct database access. Stable Terraform IDs
combine the resource kind, tenant, namespace and caller-owned key; server-generated identifiers,
versions, ETags and defaults remain computed state. Import uses that same stable ID format.

Configuration documents accept JSON or YAML. The provider canonicalizes object keys and scalar
representations before comparing plans so formatting-only changes are suppressed. Secret material is
referenced by environment-variable name and expanded only in memory for a request. Provider
configuration marks bearer tokens sensitive, response documents are recursively redacted, and the
provider never writes resolved secret plaintext into Terraform state.

Release automation builds Linux, macOS and Windows archives for amd64 and arm64, emits registry
manifest/checksum files and requires a detached GPG signature. Local qualification builds the same
matrix and verifies checksums; public registry and GitHub release publication require operator-owned
accounts and signing keys.

## Consequences

- The provider is versioned independently while its compatibility matrix pins AMESH API releases.
- Protocol-v6-only framework features are not used while OpenTofu v1 protocol-v5 parity is required.
- Server-managed immutable fields require replacement and never overwrite caller configuration.
- Registry publication is an external release action, not a prerequisite for local provider use.
