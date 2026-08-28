# Declare and run typed flow data

Declare inputs on the flow. The same definitions validate every launch and generate the control-room
form and API schema.

```yaml
inputs:
  - id: message
    type: STRING
    required: true
    displayName: Message
    placeholder: Enter a message
    validation:
      minLength: 2
  - id: credential
    type: SECRET
    required: true
    sensitive: true
```

Supported types are `STRING`, `INTEGER`, `NUMBER`, `BOOLEAN`, `DATETIME`, `DURATION`, `ENUM`, `ARRAY`,
`OBJECT`, `FILE` and `SECRET` (lowercase spellings also work). Datetimes require a time-zone offset;
durations use ISO-8601; enums declare `values`; arrays may declare `itemType`; object and array inputs
may add a Draft 2020-12 `schema`. A `SECRET` value must be a `secret://...` reference, never plaintext.

Use **Flows → Open graph → Run this flow** to submit the generated form, or inspect its contract:

```http
GET /api/v1/flows/{namespace}/{flowId}/data-contract
```

JSON API launches use the same property names:

```json
{
  "namespace": "examples.data",
  "flowId": "typed-data",
  "inputs": {
    "message": "hello",
    "credential": "secret://examples/service-token"
  }
}
```

For a `FILE`, send either an existing internal reference such as `{"uri":"s3://..."}` or a bounded
inline object containing `name`, `contentType` and `contentBase64`. AMESH writes inline bytes to the
tenant object store and persists only URI, size and checksum metadata.

Declare terminal flow outputs as expressions. Add `type` for validation and `sensitive: true` for
public redaction:

```yaml
outputs:
  result:
    type: string
    value: "{{ outputs.work.value }}"
  privateResult:
    type: string
    value: "{{ inputs.message }}"
    sensitive: true
```

Completed outputs appear on the execution detail API and control-room page. Static `variables` remain
under `vars`, execution inputs under `inputs`, task results under `outputs`, and mutable key-value data
under the key-value context; AMESH does not merge these namespaces.

For compatibility, a legacy flow with no `inputs` section accepts a bounded ad-hoc input object and
its generated schema sets `additionalProperties: true`. Once at least one input is declared, the
contract is strict and rejects unknown names.
