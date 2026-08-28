# Network diagnostics API

`GET /api/v1/operations/network-diagnostics` returns the authenticated operator's effective network
posture. It requires `view` permission on `configuration` and is tenant-authorized like the adjacent
operations endpoints.

The versioned response includes:

- inbound TLS mode, minimum protocol and client-authentication mode;
- split/compact topology and private-endpoint state;
- trusted proxy CIDRs and the configured external base URL;
- booleans indicating whether HTTP and HTTPS proxies are configured, plus explicit no-proxy entries;
- HTTP-task egress and private-host allowlists;
- credential-free connection destinations and whether each is direct, proxied or bypassed;
- certificate readability, SHA-256 fingerprint and mounted-file modification time; and
- bounded DNS results for configured dependencies and diagnostic hosts.

Proxy URLs, usernames, passwords, private keys and configuration secrets are never serialized. A
certificate error reports only the exception type and material purpose, not key or file content.
