# Namespace resources

Select a namespace in the control-room header, then open **Namespaces** to manage files, typed
key-values and secret references. File and KV writes require the corresponding `write` permission;
executions additionally require `use`. Secret values are never entered in the UI or API.

## Files

```powershell
uv run amesh namespace files upload examples.shared config/rules.json .\rules.json --content-type application/json
uv run amesh namespace files list examples.shared
uv run amesh namespace files versions examples.shared config/rules.json
uv run amesh namespace files download examples.shared config/rules.json .\downloaded-rules.json
uv run amesh namespace files move examples.shared config/rules.json archive/rules.json
uv run amesh namespace files delete examples.shared archive/rules.json
```

Child namespaces inherit the nearest parent file unless they upload the same path. Deleting a child
override leaves a tombstone so the parent does not unexpectedly reappear. `expectedVersion` in the API
or `--expected-version` in the CLI provides compare-and-set protection.

## Typed key-values

```powershell
uv run amesh namespace kv set examples.shared release.channel --type STRING --value stable
uv run amesh namespace kv set examples.shared retry.limit --type NUMBER --value 3
uv run amesh namespace kv list examples.shared
uv run amesh namespace kv changes examples.shared --after 0
```

Supported types are `STRING`, `NUMBER`, `BOOLEAN`, `DATETIME`, `DATE`, `DURATION` and `JSON`.
Use `--expires-at` with an ISO-8601 timestamp for TTL and `--expected-version` for CAS. A task reads a
value with `{{ kv('release.channel') }}`; KV entries do not inherit from parent namespaces.

## Runtime secret references

Set the secret value in the API/executor process environment, then bind only its variable name:

```powershell
$env:PRODUCTION_API_KEY = '<value supplied by the deployment secret mechanism>'
uv run amesh namespace secrets bind examples.shared API_KEY PRODUCTION_API_KEY
uv run amesh namespace secrets list examples.shared
```

The flow must declare the logical key in `contract.secretScopes` before using
`{{ secret('API_KEY') }}`. The environment value is resolved immediately before task rendering and is
redacted from persisted task results and evidence. Parent secret bindings are inherited; KV entries
are not.

## Promotion

```powershell
uv run amesh namespace resources export examples.shared .\shared-resources.json
uv run amesh namespace resources import examples.production .\shared-resources.json
```

The checksum-protected bundle includes local files, local KV entries and secret provider references.
It never includes resolved secret plaintext. Inspect and version the bundle as deployment input; do
not replace the checksum manually.
