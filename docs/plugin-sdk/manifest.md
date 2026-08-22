# Plugin manifest and SDK contract

`amesh.plugin/v1` is the stable package declaration shared by every SDK and transport. The normative
JSON Schemas are generated at `schemas/plugin-manifest.schema.json`, `plugin-request.schema.json` and
`plugin-response.schema.json`. Python protocols in `amesh.plugin_sdk` are convenience bindings for the
same JSON contract; they do not make Python object identity or imports part of the platform protocol.

```yaml
schemaVersion: amesh.plugin/v1
name: example.notifications
version: 1.2.0
vendor: Example Corp
license: Apache-2.0
compatibility:
  platformVersion: ">=0.2.0,<1.0.0"
  protocolVersions: [amesh.plugin.rpc/v1]
entryPoints:
  - name: notification.main
    resourceType: example.notifications.send
    type: notification
    apiVersion: amesh.extension/v1
    transport: stdio
    target: bin/example-notifier
    configurationSchema:
      $schema: https://json-schema.org/draft/2020-12/schema
      type: object
      properties:
        channel: {type: string, title: Channel}
        token: {type: string, title: Token, writeOnly: true}
      required: [channel, token]
      additionalProperties: false
    outputSchema: {type: object}
    documentation:
      title: Example notification
      description: Send one notification.
      category: Communication
      propertyOrder: [channel, token]
      examples: [{channel: operations, token: secret://notification-token}]
dependencies: []
capabilities:
  required: [notification.publish]
  networkAccess: restricted
  allowedEgress: [api.example.com:443]
  filesystemAccess: none
  secretScopes: [notification.token]
deprecations: []
```

Manifest identity uses a lowercase dotted name and a SemVer version. Every entry point declares one
of `task`, `trigger`, `condition`, `runner`, `storage`, `secret`, `expression` or `notification`, a
transport target, Draft 2020-12 configuration/output schemas and documentation metadata. `name` is
the package-local entry-point identifier; optional `resourceType` is the public DSL/catalog type and
defaults to `name`. Entry-point names, type/resource-type pairs and dependency names are unique.

The catalog generator copies configuration schemas and documentation, then derives ordered UI
controls. JSON Schema type selects number, checkbox, list or object controls; `enum` selects a choice;
and `writeOnly` or `format: password` selects a secret control. A UI may render different widgets, but
must submit values that validate against the published schema.

Capability declarations are deny-first. Plugins list required platform capabilities, network mode and
destinations, workspace access and secret scopes. Installation/execution policy may grant a subset;
the local harness returns structured `plugin.capability.*` errors for gaps before invoking a handler.

Requests and responses carry `amesh.plugin.rpc/v1`, plugin/entry-point identity and an invocation ID.
Capability tokens are secret-typed and scoped to one session. Runtime implementations may use stdio,
gRPC or HTTP framing, but transport adapters must preserve the same request, response and structured
error documents.
