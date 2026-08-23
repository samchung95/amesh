# TLS, proxy and private networking

AMESH supports direct TLS or TLS termination at a trusted reverse proxy. Direct mode is appropriate
for a private listener or an installation without an ingress controller; trusted-proxy mode keeps
certificate ownership at the load balancer while AMESH validates the original socket peer before
using forwarded scheme, host or client-address data.

## Inbound TLS and mTLS

Set `NETWORK_INBOUND_TLS_MODE=direct`, mount the server certificate and private key, and configure
`NETWORK_TLS_CERTIFICATE_FILE` and `NETWORK_TLS_PRIVATE_KEY_FILE`. The reference minimum is TLS 1.2
with `ECDHE+AESGCM:ECDHE+CHACHA20`; `NETWORK_TLS_MINIMUM_VERSION=TLSv1.3` is supported where every
client is qualified. Set `NETWORK_TLS_CLIENT_AUTH=optional|required` and mount
`NETWORK_TLS_CLIENT_CA_FILE` to authenticate clients. Required client authentication covers the whole
listener, so use a private endpoint or separate release boundary when only workers/internal clients
should present certificates.

For ingress termination, use `NETWORK_INBOUND_TLS_MODE=trusted-proxy` and configure
`NETWORK_TRUSTED_PROXY_RANGES` as a JSON array containing the actual ingress/load-balancer source
CIDRs. Forwarded headers from every other peer return `400 UNTRUSTED_FORWARDED_HEADERS`. Configure
`NETWORK_EXTERNAL_BASE_URL` with the canonical HTTPS origin used in operator diagnostics and identity
provider registration.

## Outbound proxy, trust and destination policy

`NETWORK_HTTP_PROXY_URL` and `NETWORK_HTTPS_PROXY_URL` select explicit proxies. Values may contain
proxy credentials and are secret configuration; Helm should source them from
`network.proxy.existingSecret`. `NETWORK_NO_PROXY` is a JSON list of exact hosts, `.domain` suffixes,
wildcard suffixes or IP/CIDR ranges.

`NETWORK_EGRESS_ALLOWED_HOSTS` applies to `core.http`, `core.download` and webhook destinations. Each
entry is `*`, an exact host, `*.domain`, `.domain`, a literal IP or CIDR. The default `*` preserves
public-Internet compatibility. Private, loopback, link-local and reserved resolution remains denied
unless the exact hostname appears in `CORE_HTTP_ALLOWED_PRIVATE_HOSTS`. Every redirect is resolved and
rechecked before a request is sent. `NETWORK_OUTBOUND_CA_FILE` installs a custom CA; the paired
`NETWORK_OUTBOUND_CLIENT_CERTIFICATE_FILE` and `NETWORK_OUTBOUND_CLIENT_KEY_FILE` enable outbound
mTLS.

Plugin manifests separately declare `allowedEgress`; runtime grants must contain every declaration.
Kubernetes task policies continue to translate approved CIDRs into pod NetworkPolicies.

## Helm private and split topology

The chart defaults to split server/executor/scheduler/worker/indexer/maintenance Deployments and a
ClusterIP Service. Set `network.privateEndpoint=true` and provider-specific
`network.privateEndpointAnnotations` for an internal load balancer. `network.ingress` renders an
optional Ingress; `network.policy.enabled=true` limits component ingress to the selected namespaces
and egress to DNS plus explicit CIDRs.

Put server, client and CA material in `network.tls.existingSecret`. The chart mounts that Secret into
every selected component and sets paths rather than embedding material in the image. With at least
two server replicas, update the Secret and run a rolling restart. The default rolling strategy
(`maxUnavailable: 0`) keeps a ready listener while each pod loads the new material. Confirm both old
and new client trust during an overlap window, then remove the retired CA and repeat the roll.

## Diagnostics and verification

Open **Administration → Operations** or call:

```bash
curl -fsS -H "Authorization: Bearer $AMESH_TOKEN" \
  -H "X-Amesh-Tenant: default" \
  https://amesh.example.test/api/v1/operations/network-diagnostics
```

Confirm TLS mode/minimum, certificate `READY` states, proxy route selection and DNS results. The
response intentionally excludes proxy URLs and credentials. For a direct listener, qualify the
protocol independently with `openssl s_client -tls1_2` and confirm TLS 1.0/1.1 negotiation fails.
