package ameshclient

import (
	"bufio"
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strconv"
	"strings"
	"time"
)

var terminalExecutionStates = map[ExecutionState]bool{
	EXECUTIONSTATE_CANCELLED: true,
	EXECUTIONSTATE_SUCCESS:   true,
	EXECUTIONSTATE_FAILED:    true,
	EXECUTIONSTATE_WARNING:   true,
}

var retryableHTTPStatus = map[int]bool{408: true, 429: true, 502: true, 503: true, 504: true}

// HTTPDoer permits transport replacement and is safe for concurrent use when its implementation is.
type HTTPDoer interface {
	Do(*http.Request) (*http.Response, error)
}

// SDKRetryPolicy controls bounded retries for reads and idempotent launches.
type SDKRetryPolicy struct {
	MaxAttempts  int
	InitialDelay time.Duration
	MaximumDelay time.Duration
}

// DefaultSDKRetryPolicy returns the release-qualified retry defaults.
func DefaultSDKRetryPolicy() SDKRetryPolicy {
	return SDKRetryPolicy{MaxAttempts: 3, InitialDelay: 250 * time.Millisecond, MaximumDelay: 2 * time.Second}
}

// SDKError is the normalized AMESH transport/API error.
type SDKError struct {
	Status    int
	Code      string
	RequestID string
	Retryable bool
	Message   string
}

func (e *SDKError) Error() string { return e.Message }

// ExecutionClient is a concurrent-safe high-level client over generated AMESH models.
type ExecutionClient struct {
	endpoint   string
	token      string
	tenant     string
	httpClient HTTPDoer
	retry      SDKRetryPolicy
	timeout    time.Duration
	sleep      func(time.Duration)
}

// NewExecutionClient constructs a client using net/http. The returned client is safe for concurrent use.
func NewExecutionClient(endpoint, token, tenant string) (*ExecutionClient, error) {
	return NewExecutionClientWithTransport(endpoint, token, tenant, http.DefaultClient, DefaultSDKRetryPolicy())
}

// NewExecutionClientWithTransport permits custom HTTP, proxy, mTLS and test transports.
func NewExecutionClientWithTransport(
	endpoint, token, tenant string,
	httpClient HTTPDoer,
	retry SDKRetryPolicy,
) (*ExecutionClient, error) {
	if endpoint == "" || token == "" || tenant == "" || httpClient == nil {
		return nil, fmt.Errorf("endpoint, token, tenant and httpClient are required")
	}
	if retry.MaxAttempts < 1 || retry.InitialDelay < 0 || retry.MaximumDelay < 0 {
		return nil, fmt.Errorf("invalid retry policy")
	}
	return &ExecutionClient{
		endpoint: strings.TrimRight(endpoint, "/"), token: token, tenant: tenant,
		httpClient: httpClient, retry: retry, timeout: 30 * time.Second, sleep: time.Sleep,
	}, nil
}

// Launch starts one execution with a stable caller key. An empty key is generated securely.
func (c *ExecutionClient) Launch(
	ctx context.Context,
	namespace, flowID string,
	inputs map[string]any,
	runner, idempotencyKey string,
) (*ExecutionDetail, error) {
	if idempotencyKey == "" {
		var err error
		idempotencyKey, err = randomIdempotencyKey()
		if err != nil {
			return nil, err
		}
	}
	if runner == "" {
		runner = "local"
	}
	body := map[string]any{
		"namespace": namespace, "flowId": flowID, "inputs": inputs,
		"runner": runner, "idempotencyKey": idempotencyKey,
	}
	var result ExecutionDetail
	if err := c.jsonRequest(ctx, http.MethodPost, "/api/v1/executions", body, idempotencyKey, true, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// Get returns the generated execution detail model.
func (c *ExecutionClient) Get(ctx context.Context, executionID string) (*ExecutionDetail, error) {
	var result ExecutionDetail
	if err := c.jsonRequest(ctx, http.MethodGet, "/api/v1/executions/"+url.PathEscape(executionID), nil, "", true, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// WaitForTerminal polls until a terminal state or the context/deadline ends.
func (c *ExecutionClient) WaitForTerminal(
	ctx context.Context,
	executionID string,
	poll time.Duration,
) (*ExecutionDetail, error) {
	for {
		detail, err := c.Get(ctx, executionID)
		if err != nil {
			return nil, err
		}
		if terminalExecutionStates[detail.Execution.State] {
			return detail, nil
		}
		select {
		case <-ctx.Done():
			return nil, ctx.Err()
		case <-time.After(poll):
		}
	}
}

// Cancel reads fencing values and submits a version/epoch-bound cancel request.
func (c *ExecutionClient) Cancel(
	ctx context.Context,
	executionID, reason string,
	graceSeconds float64,
) (*ExecutionDetail, error) {
	current, err := c.Get(ctx, executionID)
	if err != nil {
		return nil, err
	}
	body := map[string]any{
		"action": "REQUEST_CANCEL", "expectedVersion": current.Execution.Version,
		"expectedEpoch": current.Execution.Epoch, "reason": reason, "graceSeconds": graceSeconds,
	}
	var result ExecutionDetail
	if err := c.jsonRequest(
		ctx, http.MethodPost,
		"/api/v1/executions/"+url.PathEscape(executionID)+"/interventions",
		body, "", false, &result,
	); err != nil {
		return nil, err
	}
	return &result, nil
}

// Logs returns generated TaskLog models.
func (c *ExecutionClient) Logs(ctx context.Context, executionID string) ([]TaskLog, error) {
	var result []TaskLog
	err := c.jsonRequest(ctx, http.MethodGet, "/api/v1/executions/"+url.PathEscape(executionID)+"/logs", nil, "", true, &result)
	return result, err
}

// Artifacts returns generated execution-artifact models.
func (c *ExecutionClient) Artifacts(ctx context.Context, executionID string) ([]ExecutionArtifact, error) {
	var result []ExecutionArtifact
	err := c.jsonRequest(ctx, http.MethodGet, "/api/v1/executions/"+url.PathEscape(executionID)+"/files", nil, "", true, &result)
	return result, err
}

// DownloadArtifact downloads exact artifact bytes.
func (c *ExecutionClient) DownloadArtifact(ctx context.Context, executionID, artifactID string) ([]byte, error) {
	return c.request(
		ctx, http.MethodGet,
		"/api/v1/executions/"+url.PathEscape(executionID)+"/files/"+url.PathEscape(artifactID),
		nil, "", true, "application/octet-stream",
	)
}

// StreamLogs parses application/x-ndjson incrementally and invokes consume for each object.
func (c *ExecutionClient) StreamLogs(
	ctx context.Context,
	executionID string,
	consume func(json.RawMessage) error,
) error {
	body, err := c.request(
		ctx, http.MethodGet,
		"/api/v1/executions/"+url.PathEscape(executionID)+"/logs/stream",
		nil, "", true, "application/x-ndjson",
	)
	if err != nil {
		return err
	}
	scanner := bufio.NewScanner(bytes.NewReader(body))
	for scanner.Scan() {
		line := bytes.TrimSpace(scanner.Bytes())
		if len(line) > 0 {
			if !json.Valid(line) {
				return &SDKError{Status: 502, Code: "invalid_response", Message: "AMESH returned invalid NDJSON"}
			}
			if err := consume(append(json.RawMessage(nil), line...)); err != nil {
				return err
			}
		}
	}
	return scanner.Err()
}

func (c *ExecutionClient) jsonRequest(
	ctx context.Context,
	method, path string,
	document any,
	idempotencyKey string,
	retryable bool,
	result any,
) error {
	body, err := c.request(ctx, method, path, document, idempotencyKey, retryable, "application/json")
	if err != nil {
		return err
	}
	if err := json.Unmarshal(body, result); err != nil {
		return &SDKError{Status: 502, Code: "invalid_response", Message: "AMESH returned invalid JSON"}
	}
	return nil
}

func (c *ExecutionClient) request(
	ctx context.Context,
	method, path string,
	document any,
	idempotencyKey string,
	retryable bool,
	accept string,
) ([]byte, error) {
	var encoded []byte
	var err error
	if document != nil {
		encoded, err = json.Marshal(document)
		if err != nil {
			return nil, err
		}
	}
	delay := c.retry.InitialDelay
	var lastErr error
	for attempt := 0; attempt < c.retry.MaxAttempts; attempt++ {
		requestContext := ctx
		cancel := func() {}
		if c.timeout > 0 {
			requestContext, cancel = context.WithTimeout(ctx, c.timeout)
		}
		req, createErr := http.NewRequestWithContext(requestContext, method, c.endpoint+path, bytes.NewReader(encoded))
		if createErr != nil {
			cancel()
			return nil, createErr
		}
		req.Header.Set("Accept", accept)
		req.Header.Set("Authorization", "Bearer "+c.token)
		req.Header.Set("X-Amesh-Tenant", c.tenant)
		if document != nil {
			req.Header.Set("Content-Type", "application/json")
		}
		if idempotencyKey != "" {
			req.Header.Set("Idempotency-Key", idempotencyKey)
		}
		response, sendErr := c.httpClient.Do(req)
		if sendErr != nil {
			cancel()
			lastErr = &SDKError{Status: 0, Code: "transport_error", Retryable: true, Message: "AMESH transport failed"}
			if !retryable || attempt+1 >= c.retry.MaxAttempts {
				return nil, lastErr
			}
		} else {
			responseBody, readErr := io.ReadAll(response.Body)
			response.Body.Close()
			cancel()
			if readErr != nil {
				return nil, readErr
			}
			if response.StatusCode >= 200 && response.StatusCode < 300 {
				return responseBody, nil
			}
			apiErr := sdkResponseError(response, responseBody)
			lastErr = apiErr
			if !retryable || !apiErr.Retryable || attempt+1 >= c.retry.MaxAttempts {
				return nil, apiErr
			}
			delay = retryAfter(response.Header, delay)
		}
		c.sleep(delay)
		delay *= 2
		if delay > c.retry.MaximumDelay {
			delay = c.retry.MaximumDelay
		}
	}
	return nil, lastErr
}

// VerifyWebhook verifies version, timestamp skew and HMAC-SHA256 in constant time.
func VerifyWebhook(
	secret string,
	timestamp int64,
	deliveryID string,
	body []byte,
	signature string,
	now time.Time,
	tolerance time.Duration,
) bool {
	if tolerance < 0 || abs64(now.Unix()-timestamp) > int64(tolerance/time.Second) {
		return false
	}
	mac := hmac.New(sha256.New, []byte(secret))
	fmt.Fprintf(mac, "%d.%s.", timestamp, deliveryID)
	mac.Write(body)
	expected := "v1=" + hex.EncodeToString(mac.Sum(nil))
	return subtle.ConstantTimeCompare([]byte(expected), []byte(signature)) == 1
}

func sdkResponseError(response *http.Response, body []byte) *SDKError {
	message := fmt.Sprintf("AMESH request failed with HTTP %d", response.StatusCode)
	code := "request_failed"
	var value map[string]any
	if json.Unmarshal(body, &value) == nil {
		if detail, ok := value["detail"].(string); ok && len(detail) <= 512 {
			message = detail
		}
		if candidate, ok := value["code"].(string); ok {
			code = candidate
		}
	}
	return &SDKError{
		Status: response.StatusCode, Code: code, RequestID: response.Header.Get("x-request-id"),
		Retryable: retryableHTTPStatus[response.StatusCode], Message: message,
	}
}

func retryAfter(headers http.Header, fallback time.Duration) time.Duration {
	seconds, err := strconv.ParseFloat(headers.Get("retry-after"), 64)
	if err != nil || seconds < 0 {
		return fallback
	}
	return time.Duration(seconds * float64(time.Second))
}

func randomIdempotencyKey() (string, error) {
	value := make([]byte, 16)
	if _, err := rand.Read(value); err != nil {
		return "", err
	}
	return hex.EncodeToString(value), nil
}

func abs64(value int64) int64 {
	if value < 0 {
		return -value
	}
	return value
}
