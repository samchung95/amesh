package provider

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

type apiClient struct {
	endpoint string
	token    string
	tenant   string
	http     *http.Client
}

type apiResponse struct {
	body   []byte
	header http.Header
	status int
}

func newAPIClient(endpoint, token, tenant string) (*apiClient, error) {
	parsed, err := url.Parse(strings.TrimRight(endpoint, "/"))
	if err != nil || (parsed.Scheme != "http" && parsed.Scheme != "https") || parsed.Host == "" {
		return nil, fmt.Errorf("endpoint must be an absolute HTTP(S) URL")
	}
	if token == "" {
		return nil, fmt.Errorf("token is required through provider configuration or AMESH_TOKEN")
	}
	return &apiClient{
		endpoint: parsed.String(), token: token, tenant: tenant,
		http: &http.Client{Timeout: 30 * time.Second},
	}, nil
}

func (client *apiClient) do(
	ctx context.Context,
	method string,
	path string,
	body []byte,
	contentType string,
) (apiResponse, error) {
	request, err := http.NewRequestWithContext(
		ctx,
		method,
		client.endpoint+path,
		bytes.NewReader(body),
	)
	if err != nil {
		return apiResponse{}, fmt.Errorf("create AMESH request: %w", err)
	}
	request.Header.Set("Authorization", "Bearer "+client.token)
	request.Header.Set("X-Amesh-Tenant", client.tenant)
	request.Header.Set("Accept", "application/json")
	if len(body) > 0 {
		request.Header.Set("Content-Type", contentType)
	}
	response, err := client.http.Do(request)
	if err != nil {
		return apiResponse{}, fmt.Errorf("AMESH request failed: %w", err)
	}
	defer response.Body.Close()
	responseBody, err := io.ReadAll(io.LimitReader(response.Body, 8<<20))
	if err != nil {
		return apiResponse{}, fmt.Errorf("read AMESH response: %w", err)
	}
	result := apiResponse{body: responseBody, header: response.Header.Clone(), status: response.StatusCode}
	if response.StatusCode < 200 || response.StatusCode >= 300 {
		return result, apiError(response.StatusCode, responseBody)
	}
	return result, nil
}

func apiError(status int, body []byte) error {
	detail := ""
	var problem map[string]any
	if json.Unmarshal(body, &problem) == nil {
		if value, ok := problem["code"].(string); ok {
			detail = " (" + value + ")"
		}
	}
	return fmt.Errorf("AMESH API returned HTTP %d%s", status, detail)
}

func renderPath(template string, model documentModel, tenant string) string {
	replacements := map[string]string{
		"{tenant}":    tenant,
		"{namespace}": model.Namespace.ValueString(),
		"{key}":       model.Key.ValueString(),
		"{server_id}": model.ServerID.ValueString(),
		"{revision}":  model.Revision.ValueString(),
	}
	result := template
	for marker, value := range replacements {
		result = strings.ReplaceAll(result, marker, url.PathEscape(value))
	}
	return result
}

func selectCollectionItem(body []byte, field, expected string) ([]byte, bool, error) {
	var collection []json.RawMessage
	if err := json.Unmarshal(body, &collection); err != nil {
		return nil, false, fmt.Errorf("decode AMESH collection: %w", err)
	}
	for _, item := range collection {
		if objectField(item, field) == expected {
			return item, true, nil
		}
	}
	return nil, false, nil
}
