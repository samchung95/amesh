# Plugin developer portal and certification

The AMESH plugin developer workflow is local-first and managed with `uv`. It generates a starter,
validates its configuration, produces reference documentation and runs the release certification
suite without requiring a running AMESH server.

```powershell
uv run amesh plugins scaffold ./my-plugin --name example.my-plugin
uv run amesh plugins sandbox ./my-plugin task.echo --configuration ./sample.yaml
uv run amesh plugins docs ./my-plugin --output-dir ./generated
uv run amesh plugins certify ./my-plugin --output ./certification-report.json
```

`plugins scaffold` creates a versioned manifest, Python starter, `uv` project, license placeholder,
supported-release matrix and all five reference fixture definitions. Replace the license placeholder
with the complete declared license before publishing.

## Certification checks

One `plugins certify` invocation evaluates six objective categories:

| Check | Pass condition |
| --- | --- |
| Manifest | Exactly one valid `amesh-plugin` manifest is present. |
| Schema | Every declared entry point has a valid Draft 2020-12 configuration contract. |
| Contract | Retry, cancellation, large-file, secret-redaction and worker-restart fixtures all have passing evidence. |
| Security | Capabilities are deny-first, egress has no wildcard, targets stay within the package and secret examples use `secret://` references. |
| License | A repository `LICENSE*` file is present for the declared license. |
| Compatibility | Every tracked platform release matches the declared platform range and protocol. |

The report conforms to
[`schemas/plugin-certification.schema.json`](https://github.com/samchung95/amesh/blob/main/schemas/plugin-certification.schema.json).
Its `inputDigest` covers the manifest, license, fixture definitions, fixture evidence, compatibility
matrix and public CI evidence, making identical inputs produce an identical result.

## Reference fixtures

The portable fixture catalog is checked in at
[`examples/plugin-sdk/certification-fixtures.json`](https://github.com/samchung95/amesh/blob/main/examples/plugin-sdk/certification-fixtures.json).
A plugin scaffold writes each fixture to `certification/fixtures/<name>.json` and expects the named
evidence file to contain `{"status":"passed"}` after the plugin's own contract tests exercise the
behavior. The existing `PluginContractHarness` and connector fault emulators can drive those tests.

## Quality levels

| Level | Objective criteria |
| --- | --- |
| Community | Manifest, schema and repository license checks pass. |
| Verified | All six checks pass, including all five reference fixtures. |
| Certified | Verified, plus reproducible public CI evidence tied to an immutable source commit. |

Print the criteria from the installed release with `uv run amesh plugins criteria`.

## Public CI reproduction

Add `certification/evidence.json` only after the public workflow passes:

```json
{
  "sourceCommit": "0123456789abcdef0123456789abcdef01234567",
  "runUrl": "https://github.com/example/my-plugin/actions/runs/123456",
  "workflow": "plugin-certification"
}
```

To reproduce a result, check out `sourceCommit`, install with `uv sync --frozen`, then run the same
`uv run amesh plugins certify . --output certification-report.json` command. The checked-in report
and reproduced report must have the same `inputDigest`, checks and compatibility results.

Track supported AMESH releases in `certification/compatibility.json`:

```json
{"platformVersions": ["0.2.0", "0.2.1"]}
```

Every listed release is evaluated against the manifest's `platformVersion` range. An incompatible
release fails the compatibility check and prevents Verified or Certified status.
