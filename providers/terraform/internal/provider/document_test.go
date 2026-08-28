package provider

import (
	"encoding/json"
	"strings"
	"testing"
)

func TestCanonicalDocumentSuppressesFormattingOnlyChanges(t *testing.T) {
	t.Parallel()
	yamlDocument := "enabled: true\nlabels:\n  b: two\n  a: one\n"
	jsonDocument := `{"labels":{"a":"one","b":"two"},"enabled":true}`
	yamlCanonical, err := canonicalDocument(yamlDocument, false)
	if err != nil {
		t.Fatal(err)
	}
	jsonCanonical, err := canonicalDocument(jsonDocument, false)
	if err != nil {
		t.Fatal(err)
	}
	if yamlCanonical != jsonCanonical {
		t.Fatalf("semantic documents differ:\n%s\n%s", yamlCanonical, jsonCanonical)
	}
}

func TestRequestDocumentExpandsSecretWithoutReturningIt(t *testing.T) {
	t.Setenv("AMESH_TEST_SECRET", "resolved-private-value")
	descriptor := resourceDescriptor{Name: "key_value"}
	body, err := requestDocument(
		`{"type":"STRING","value":"${AMESH_SECRET}","secretToken":"server-token"}`,
		descriptor,
		"AMESH_TEST_SECRET",
	)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(body), "resolved-private-value") {
		t.Fatal("secret placeholder was not expanded for the request")
	}
	redacted, err := redactedDocument(body, descriptor)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(redacted, "server-token") {
		t.Fatal("server-resolved secret appeared in provider state")
	}
	if !strings.Contains(redacted, "[REDACTED]") {
		t.Fatal("redacted response marker is missing")
	}
}

func TestSCIMPatchIsDeterministicAndExcludesServerFields(t *testing.T) {
	t.Parallel()
	body, err := scimPatch([]byte(`{"id":"server","userName":"ada","active":true,"schemas":["core"]}`))
	if err != nil {
		t.Fatal(err)
	}
	var patch map[string]any
	if err := json.Unmarshal(body, &patch); err != nil {
		t.Fatal(err)
	}
	operations := patch["Operations"].([]any)
	if len(operations) != 2 {
		t.Fatalf("expected two mutable operations, got %d", len(operations))
	}
	first := operations[0].(map[string]any)
	if first["path"] != "active" {
		t.Fatalf("operations are not sorted: %#v", operations)
	}
}

func TestStableIDRoundTrip(t *testing.T) {
	t.Parallel()
	id := stableID("file", "default", "team space", "flows/demo.yaml")
	parts := strings.Split(id, "|")
	if len(parts) != 4 || decodeIDPart(parts[2]) != "team space" || decodeIDPart(parts[3]) != "flows/demo.yaml" {
		t.Fatalf("unexpected stable id %q", id)
	}
}

func TestProjectRemoteDocumentKeepsCallerShapeAndSecretPlaceholder(t *testing.T) {
	t.Parallel()
	desired := `{"type":"STRING","value":"${AMESH_SECRET}"}`
	remote := `{"type":"STRING","value":"[REDACTED]","resourceVersion":2,"updatedAt":"later"}`
	projected, err := projectRemoteDocument(desired, remote, false)
	if err != nil {
		t.Fatal(err)
	}
	if projected != desired {
		t.Fatalf("unexpected projection %s", projected)
	}

	drifted, err := projectRemoteDocument(
		`{"type":"STRING","value":"expected"}`,
		`{"type":"STRING","value":"changed","resourceVersion":2}`,
		false,
	)
	if err != nil {
		t.Fatal(err)
	}
	if drifted != `{"type":"STRING","value":"changed"}` {
		t.Fatalf("remote drift was not projected: %s", drifted)
	}
}

func TestWithoutObjectFieldsBuildsImportDocument(t *testing.T) {
	t.Parallel()
	document := `{"key":"sample","type":"STRING","value":"ok","resourceVersion":4,"metadata":{},"expiresAt":null}`
	actual := withoutObjectFields(document, []string{"key", "resourceVersion"}, false)
	if actual != `{"type":"STRING","value":"ok"}` {
		t.Fatalf("unexpected import document: %s", actual)
	}
}

func TestSecretPathIsRedactedWhenEnvironmentIsUnavailable(t *testing.T) {
	t.Parallel()
	desired := `{"type":"STRING","value":"${AMESH_SECRET}","metadata":{"owner":"ops"}}`
	remote := `{"type":"STRING","value":"resolved-private-value","metadata":{"owner":"ops"}}`
	redacted := redactDesiredSecretPaths(remote, desired, false)
	if strings.Contains(redacted, "resolved-private-value") || !strings.Contains(redacted, "[REDACTED]") {
		t.Fatalf("secret path was not redacted: %s", redacted)
	}
}
