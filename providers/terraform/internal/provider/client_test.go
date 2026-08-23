package provider

import (
	"context"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestAPIClientAppliesAuthenticationTenantAndBody(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(response http.ResponseWriter, request *http.Request) {
		if request.Header.Get("Authorization") != "Bearer test-token" {
			t.Errorf("unexpected authorization header %q", request.Header.Get("Authorization"))
		}
		if request.Header.Get("X-Amesh-Tenant") != "tenant-a" {
			t.Errorf("unexpected tenant header %q", request.Header.Get("X-Amesh-Tenant"))
		}
		body, _ := io.ReadAll(request.Body)
		if string(body) != `{"enabled":true}` {
			t.Errorf("unexpected body %q", string(body))
		}
		response.Header().Set("ETag", `"revision-1"`)
		response.Header().Set("Content-Type", "application/json")
		_, _ = response.Write([]byte(`{"id":"server-id"}`))
	}))
	defer server.Close()
	client, err := newAPIClient(server.URL, "test-token", "tenant-a")
	if err != nil {
		t.Fatal(err)
	}
	result, err := client.do(context.Background(), http.MethodPut, "/resource", []byte(`{"enabled":true}`), "application/json")
	if err != nil {
		t.Fatal(err)
	}
	if objectField(result.body, "id") != "server-id" || result.header.Get("ETag") != `"revision-1"` {
		t.Fatalf("unexpected response: %#v", result)
	}
}

func TestAPIClientErrorDoesNotEchoResponseSecrets(t *testing.T) {
	t.Parallel()
	server := httptest.NewServer(http.HandlerFunc(func(response http.ResponseWriter, _ *http.Request) {
		response.WriteHeader(http.StatusBadRequest)
		_, _ = response.Write([]byte(`{"detail":"resolved-private-value"}`))
	}))
	defer server.Close()
	client, err := newAPIClient(server.URL, "test-token", "default")
	if err != nil {
		t.Fatal(err)
	}
	_, err = client.do(context.Background(), http.MethodGet, "/failure", nil, "application/json")
	if err == nil || strings.Contains(err.Error(), "resolved-private-value") {
		t.Fatalf("unsafe API error: %v", err)
	}
}

func TestSelectCollectionItem(t *testing.T) {
	t.Parallel()
	item, found, err := selectCollectionItem([]byte(`[{"id":"one"},{"id":"two"}]`), "id", "two")
	if err != nil || !found || objectField(item, "id") != "two" {
		t.Fatalf("collection lookup failed: found=%v err=%v item=%s", found, err, item)
	}
}
