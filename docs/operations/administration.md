# Administration workbench

Open **Administration** in the control room with `administration.manage`. The route is hidden from
unauthorized navigation and a direct request still receives the server-authoritative permission
decision.

The workbench has six views:

- **Namespaces** shows dotted hierarchy scopes, the selected namespace's files, typed values and
  secret-reference counts, plus inherited workflow metadata and plugin-default provenance.
- **Access** manages principals, groups, roles, bindings, service accounts and short-lived API tokens,
  and reports configured identity providers. Issued token material is displayed once.
- **Operations** refreshes readiness, services, workers, queue admission, storage, migrations and
  search health every ten seconds.
- **Controls** publishes scheduled announcements, activates scoped maintenance or kill switches,
  exposes component acknowledgements, and retains the four guarded tenant controls and ordinary
  scoped feature flags.
- **Configuration** displays effective settings with source provenance and hard redaction, and can
  reload only settings the configuration contract marks reloadable.
- **Audit** combines immediate successful/rejected control decisions with the general indexed audit
  projection.

## Apply a guarded control

1. Select **Preview change** on the relevant control.
2. Set the value and provide a reason of at least three characters.
3. Generate the impact preview and review every impact and the recovery procedure.
4. Type the exact `APPLY <CONTROL>` phrase before the five-minute approval expires.
5. Apply, then open **Audit** and verify the outcome, actor and reason.

If the draft changes, return to the form and generate a new approval. A `409` means the confirmation,
approval scope, expiry or resource version no longer matches. Refresh the controls before retrying.
Do not bypass this workflow by editing reserved `admin-` feature flags directly.

## Safety notes

- The execution kill switch stops new admission; it does not silently terminate already-running work.
- Retention configures policy intent. Actual lifecycle sweeps and restoration follow the retention and
  backup runbooks delivered by their owning epics.
- Secret values remain redacted in effective configuration regardless of browser rendering.
- A successful control and its audit record commit atomically. Rejected guarded requests produce an
  audit decision but no control change.

The API contract is documented in [Administration API](../api/administration.md).
Incident posture and maintenance workflows are documented in
[Operational controls API](../api/operational-controls.md).
