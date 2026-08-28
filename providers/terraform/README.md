# AMESH Terraform and OpenTofu provider

This first-party provider manages AMESH configuration through the public HTTP and SCIM APIs. One
protocol-v5 binary supports Terraform 1.x and OpenTofu 1.x.

## Local development

Run the provider tests in the repository's pinned Go container:

```console
docker run --rm -v "$PWD:/workspace" -w /workspace/providers/terraform golang:1.25 go test ./...
```

Build the local binary:

```console
docker run --rm -v "$PWD:/workspace" -w /workspace/providers/terraform golang:1.25 \
  go build -o build/terraform-provider-amesh
```

Configure credentials through `AMESH_ENDPOINT`, `AMESH_TOKEN` and `AMESH_TENANT` where possible.
The provider token is sensitive. A resource's `secret_environment` may name an environment variable
whose value replaces `${AMESH_SECRET}` in memory immediately before the request; the resolved value
is never written to provider state.

Every managed resource accepts a JSON or YAML `document`. Formatting-only changes are normalized,
while refresh records a redacted remote digest and sets `drifted` if it differs from the last apply.
Import identifiers use `kind|tenant|namespace|key` and may append `|server_id` for server-generated
SCIM, binding, service-account, tenant or plugin-policy identifiers. Percent-encode literal `|`
characters in individual parts.

Namespace bundles, apps, roles, service accounts and worker-group policy sets are retained by the
server when removed from Terraform state because their lifecycle includes server-owned history or
shared references. Their generated resource documentation calls out this behavior. All other
resources invoke their native AMESH delete contract.

## Release qualification

`.goreleaser.yml` builds amd64 and arm64 archives for Linux, macOS and Windows, includes the protocol
manifest in SHA-256 checksums and requires a detached GPG checksum signature. A version tag runs the
repository release workflow. Registry ownership, the production GPG key and release credentials are
operator inputs; public publication cannot be qualified by a local development environment.
