# Discoverable input inventory

This inventory defines which AMESH inputs are selected from authorized catalogs and which remain
authored text. It is the implementation evidence for Sprint UX-01 card `c97`.

| Surface | Input class | Control and source |
|---|---|---|
| Workspace context | Resource | Tenant is the current authorized tenant; namespace options come from authorized flows. |
| Flow and execution lists | Resource + enum | Namespace and dependent flow selectors use the flow catalog; execution state uses the complete state enum. |
| Blueprint draft | Resource/authored | Existing namespaces are offered first; “create in a new namespace” is an explicit custom path. Flow ID and content remain authored. |
| Flow run | Schema | Boolean, enum, number, file and structured controls are generated from the pinned flow input schema; strings and secrets remain authored values. |
| Visual workflow editor | Schema/resource | Task type and group use the resource catalog/graph; enum and boolean properties use schema controls. Task IDs, expressions, YAML and unconstrained task properties remain authored. |
| Dashboard | Resource + enum + identity | Namespace, dependent flow, state, worker group, grouping dimension, viewer and editor choices use authorized catalogs or finite enums. Labels and custom dimensions remain authored key/value expressions. |
| Search | Resource + enum | Namespace and common state filters are selected. “Search another state” is explicit because indexed plugins may add state vocabularies. Full text, labels and selected field value remain query text. |
| Plugin policy | Resource + enum | Installed package and exact version options come from the signed registry. Package patterns and semantic ranges require the explicit custom path. |
| Namespace resources | Resource + enum/authored | Move source and value type are selected. Paths, keys, values and environment-variable references are names being created and remain authored. |
| Administration access | Identity + enum/resource | Principal, role, group, member, service account, authorization resource/action and namespace are selected; new handles, names and descriptions remain authored. |
| Administration lifecycle/controls | Resource + enum | Namespace, dependent flow, plugin and runner targets are selected from authorized catalogs; control names, reasons, feature keys and exact confirmation phrases remain authored. |

Selectors show human-readable labels while submitting stable identifiers. Empty and loading states do
not reveal resources outside the caller's authorization. A custom text input is never shown unless the
specific contract intentionally permits new names, patterns or plugin-defined vocabulary.
