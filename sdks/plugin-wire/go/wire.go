// Package ameshplugin defines AMESH isolated-plugin wire contracts.
// The normative schema is schemas/plugin-wire.schema.json.
package ameshplugin

const WireVersion = "amesh.plugin.wire/v1"

const (
	MethodHandshake = "amesh.handshake"
	MethodDiscover  = "amesh.discover"
	MethodValidate  = "amesh.validate"
	MethodInvoke    = "amesh.invoke"
	MethodCancel    = "amesh.cancel"
	MethodShutdown  = "amesh.shutdown"
)

var RequiredFeatures = []string{
	"schema-discovery",
	"validation",
	"execution",
	"cancellation",
	"heartbeats",
	"logs",
	"metrics",
	"artifacts",
}

type WorkloadIdentity struct {
	SessionID     string `json:"sessionId"`
	WorkloadToken string `json:"workloadToken"`
	ExpiresAt     string `json:"expiresAt"`
}

type CapabilityEnvelope struct {
	CapabilityTokens map[string]string `json:"capabilityTokens"`
	Secrets          map[string]string `json:"secrets"`
	Files            map[string]string `json:"files"`
	AllowedEgress    []string          `json:"allowedEgress"`
	PlatformAPIs     []string          `json:"platformApis"`
}

type PluginRequest struct {
	ProtocolVersion string                 `json:"protocolVersion"`
	Plugin          string                 `json:"plugin"`
	EntryPoint      string                 `json:"entryPoint"`
	Operation       string                 `json:"operation"`
	Session         map[string]any         `json:"session"`
	Configuration   map[string]any         `json:"configuration"`
	Input           map[string]any         `json:"input"`
	Context         map[string]any         `json:"context"`
}

type InvocationParams struct {
	SessionID     string             `json:"sessionId"`
	WorkloadToken string             `json:"workloadToken"`
	Request       PluginRequest      `json:"request"`
	Capabilities  CapabilityEnvelope `json:"capabilities"`
}

type EntryPoint struct {
	Name                string         `json:"name"`
	Type                string         `json:"type"`
	ResourceType        string         `json:"resourceType"`
	ConfigurationSchema map[string]any `json:"configurationSchema"`
	OutputSchema        map[string]any `json:"outputSchema,omitempty"`
}

type DiscoveryResult struct {
	SessionID     string       `json:"sessionId"`
	WorkloadToken string       `json:"workloadToken"`
	EntryPoints   []EntryPoint `json:"entryPoints"`
}

type PluginResponse struct {
	ProtocolVersion string                   `json:"protocolVersion"`
	InvocationID    string                   `json:"invocationId"`
	Output          map[string]any           `json:"output"`
	Logs            []map[string]any         `json:"logs"`
	Errors          []map[string]any         `json:"errors"`
	Checkpoint      map[string]any           `json:"checkpoint,omitempty"`
}

type PluginHandler func(PluginRequest, CapabilityEnvelope) (PluginResponse, error)
