package ameshclient

import (
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/hex"
	"io"
	"net/http"
	"os"
	"testing"
	"time"
)

type fakeHTTPDoer struct {
	responses []*http.Response
	requests  []*http.Request
}

func (f *fakeHTTPDoer) Do(request *http.Request) (*http.Response, error) {
	f.requests = append(f.requests, request)
	response := f.responses[0]
	f.responses = f.responses[1:]
	return response, nil
}

func TestExecutionClientRetriesIdempotentLaunch(t *testing.T) {
	detail := `{"execution":{"execution_id":"0198cafe-0000-7000-8000-000000000001","tenant_id":"default","state":"SUCCESS","epoch":1,"version":2,"namespace":"examples.mvp","flow_id":"hello_world","created_at":"2026-08-23T00:00:00Z","updated_at":"2026-08-23T00:00:01Z"},"taskRuns":[]}`
	transport := &fakeHTTPDoer{responses: []*http.Response{
		{StatusCode: 503, Header: http.Header{"Retry-After": []string{"0"}}, Body: io.NopCloser(bytes.NewBufferString("{}"))},
		{StatusCode: 200, Header: http.Header{}, Body: io.NopCloser(bytes.NewBufferString(detail))},
	}}
	client, err := NewExecutionClientWithTransport(
		"https://amesh.test", "test-token", "default", transport,
		SDKRetryPolicy{MaxAttempts: 2, InitialDelay: 0, MaximumDelay: 0},
	)
	if err != nil {
		t.Fatal(err)
	}
	client.sleep = func(time.Duration) {}
	result, err := client.Launch(context.Background(), "examples.mvp", "hello_world", nil, "local", "stable-key")
	if err != nil {
		t.Fatal(err)
	}
	if result.Execution.State != EXECUTIONSTATE_SUCCESS || len(transport.requests) != 2 {
		t.Fatalf("unexpected result or request count: %#v %d", result.Execution.State, len(transport.requests))
	}
	for _, request := range transport.requests {
		if request.Header.Get("Idempotency-Key") != "stable-key" || request.Header.Get("Authorization") != "Bearer test-token" {
			t.Fatalf("missing authenticated idempotency headers: %#v", request.Header)
		}
	}
}

func TestVerifyWebhook(t *testing.T) {
	secret := "webhook-secret"
	timestamp := int64(1_800_000_000)
	deliveryID := "0198cafe-0000-7000-8000-000000000002"
	body := []byte(`{"event":"execution.completed"}`)
	mac := hmac.New(sha256.New, []byte(secret))
	mac.Write([]byte("1800000000." + deliveryID + "."))
	mac.Write(body)
	signature := "v1=" + hex.EncodeToString(mac.Sum(nil))
	if !VerifyWebhook(secret, timestamp, deliveryID, body, signature, time.Unix(timestamp+30, 0), 5*time.Minute) {
		t.Fatal("expected valid signature")
	}
	if VerifyWebhook(secret, timestamp, deliveryID, body, signature, time.Unix(timestamp+301, 0), 5*time.Minute) {
		t.Fatal("expected stale signature rejection")
	}
}

func TestLiveExecutionConformance(t *testing.T) {
	endpoint := os.Getenv("AMESH_SDK_LIVE_ENDPOINT")
	if endpoint == "" {
		t.Skip("live endpoint not configured")
	}
	client, err := NewExecutionClient(endpoint, os.Getenv("AMESH_SDK_LIVE_TOKEN"), envOr("AMESH_SDK_LIVE_TENANT", "default"))
	if err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 90*time.Second)
	defer cancel()
	launched, err := client.Launch(
		ctx,
		envOr("AMESH_SDK_LIVE_NAMESPACE", "examples.getting_started"),
		envOr("AMESH_SDK_LIVE_FLOW", "hello_world"),
		map[string]any{"name": "Go SDK"},
		"local",
		"",
	)
	if err != nil {
		t.Fatal(err)
	}
	completed, err := client.WaitForTerminal(ctx, launched.Execution.ExecutionId, 250*time.Millisecond)
	if err != nil {
		t.Fatal(err)
	}
	if completed.Execution.State != EXECUTIONSTATE_SUCCESS {
		t.Fatalf("unexpected terminal state: %s", completed.Execution.State)
	}
	if _, err = client.Get(ctx, launched.Execution.ExecutionId); err != nil {
		t.Fatal(err)
	}
	if _, err = client.Logs(ctx, launched.Execution.ExecutionId); err != nil {
		t.Fatal(err)
	}
	if _, err = client.Artifacts(ctx, launched.Execution.ExecutionId); err != nil {
		t.Fatal(err)
	}
}

func envOr(name, fallback string) string {
	if value := os.Getenv(name); value != "" {
		return value
	}
	return fallback
}
