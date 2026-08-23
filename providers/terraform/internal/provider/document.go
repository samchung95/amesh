package provider

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

const secretPlaceholder = "${AMESH_SECRET}"

func canonicalDocument(source string, raw bool) (string, error) {
	normalized := strings.ReplaceAll(source, "\r\n", "\n")
	var value any
	if err := json.Unmarshal([]byte(normalized), &value); err != nil {
		if yamlErr := yaml.Unmarshal([]byte(normalized), &value); yamlErr != nil {
			if raw {
				return normalized, nil
			}
			return "", fmt.Errorf("document must be JSON or YAML: %w", yamlErr)
		}
	}
	encoded, err := json.Marshal(normalizeValue(value))
	if err != nil {
		return "", fmt.Errorf("canonicalize document: %w", err)
	}
	return string(encoded), nil
}

func normalizeValue(value any) any {
	switch selected := value.(type) {
	case map[string]any:
		keys := make([]string, 0, len(selected))
		for key := range selected {
			keys = append(keys, key)
		}
		sort.Strings(keys)
		result := make(map[string]any, len(selected))
		for _, key := range keys {
			result[key] = normalizeValue(selected[key])
		}
		return result
	case map[any]any:
		result := make(map[string]any, len(selected))
		for key, item := range selected {
			result[fmt.Sprint(key)] = normalizeValue(item)
		}
		return normalizeValue(result)
	case []any:
		result := make([]any, len(selected))
		for index, item := range selected {
			result[index] = normalizeValue(item)
		}
		return result
	default:
		return selected
	}
}

func documentDigest(document string) string {
	digest := sha256.Sum256([]byte(document))
	return hex.EncodeToString(digest[:])
}

func requestDocument(source string, descriptor resourceDescriptor, secretEnvironment string) ([]byte, error) {
	canonical, err := canonicalDocument(source, descriptor.RawDocument)
	if err != nil {
		return nil, err
	}
	if descriptor.RawDocument && !json.Valid([]byte(canonical)) {
		if secretEnvironment == "" {
			return []byte(canonical), nil
		}
		secret, present := os.LookupEnv(secretEnvironment)
		if !present {
			return nil, fmt.Errorf("secret environment variable %q is not set", secretEnvironment)
		}
		return []byte(strings.ReplaceAll(canonical, secretPlaceholder, secret)), nil
	}
	var value any
	if err := json.Unmarshal([]byte(canonical), &value); err != nil {
		return nil, err
	}
	if descriptor.Inject != nil {
		object, ok := value.(map[string]any)
		if !ok {
			return nil, fmt.Errorf("%s document must be an object", descriptor.Name)
		}
		for key, item := range descriptor.Inject {
			object[key] = item
		}
	}
	if secretEnvironment != "" {
		secret, present := os.LookupEnv(secretEnvironment)
		if !present {
			return nil, fmt.Errorf("secret environment variable %q is not set", secretEnvironment)
		}
		value = replaceSecret(value, secret)
	}
	return json.Marshal(value)
}

func replaceSecret(value any, secret string) any {
	switch selected := value.(type) {
	case map[string]any:
		for key, item := range selected {
			selected[key] = replaceSecret(item, secret)
		}
		return selected
	case []any:
		for index, item := range selected {
			selected[index] = replaceSecret(item, secret)
		}
		return selected
	case string:
		return strings.ReplaceAll(selected, secretPlaceholder, secret)
	default:
		return selected
	}
}

func redactedDocument(body []byte, descriptor resourceDescriptor, secrets ...string) (string, error) {
	if descriptor.ReadMode == readRaw {
		return canonicalDocument(string(body), true)
	}
	var value any
	if err := json.Unmarshal(body, &value); err != nil {
		return "", fmt.Errorf("decode AMESH response: %w", err)
	}
	if descriptor.ReadDocumentField != "" {
		object, ok := value.(map[string]any)
		if !ok {
			return "", fmt.Errorf("AMESH response is not an object")
		}
		value = object[descriptor.ReadDocumentField]
	}
	value = redactValue(value, secrets...)
	encoded, err := json.Marshal(normalizeValue(value))
	if err != nil {
		return "", fmt.Errorf("encode AMESH response: %w", err)
	}
	return string(encoded), nil
}

func redactValue(value any, secrets ...string) any {
	switch selected := value.(type) {
	case map[string]any:
		result := make(map[string]any, len(selected))
		for key, item := range selected {
			lower := strings.ToLower(key)
			if strings.Contains(lower, "password") || strings.Contains(lower, "secret") ||
				strings.Contains(lower, "token") || strings.Contains(lower, "credential") {
				result[key] = "[REDACTED]"
				continue
			}
			result[key] = redactValue(item, secrets...)
		}
		return result
	case []any:
		result := make([]any, len(selected))
		for index, item := range selected {
			result[index] = redactValue(item, secrets...)
		}
		return result
	case string:
		result := selected
		for _, secret := range secrets {
			if secret != "" {
				result = strings.ReplaceAll(result, secret, "[REDACTED]")
			}
		}
		return result
	default:
		return selected
	}
}

func projectRemoteDocument(desired string, remote string, raw bool) (string, error) {
	desiredCanonical, err := canonicalDocument(desired, raw)
	if err != nil {
		return "", err
	}
	remoteCanonical, err := canonicalDocument(remote, raw)
	if err != nil {
		return "", err
	}
	if raw || !json.Valid([]byte(desiredCanonical)) || !json.Valid([]byte(remoteCanonical)) {
		return remoteCanonical, nil
	}
	var desiredValue any
	var remoteValue any
	if err := json.Unmarshal([]byte(desiredCanonical), &desiredValue); err != nil {
		return "", err
	}
	if err := json.Unmarshal([]byte(remoteCanonical), &remoteValue); err != nil {
		return "", err
	}
	projected, err := projectValue(desiredValue, remoteValue)
	if err != nil {
		return "", err
	}
	encoded, err := json.Marshal(projected)
	if err != nil {
		return "", err
	}
	return string(encoded), nil
}

func redactDesiredSecretPaths(remote string, desired string, raw bool) string {
	if !strings.Contains(desired, secretPlaceholder) {
		return remote
	}
	if raw {
		return "[REDACTED]"
	}
	var remoteValue any
	var desiredValue any
	if json.Unmarshal([]byte(remote), &remoteValue) != nil || json.Unmarshal([]byte(desired), &desiredValue) != nil {
		return "[REDACTED]"
	}
	redacted := redactProjectedSecrets(remoteValue, desiredValue)
	encoded, err := json.Marshal(redacted)
	if err != nil {
		return "[REDACTED]"
	}
	return string(encoded)
}

func redactProjectedSecrets(remote any, desired any) any {
	switch wanted := desired.(type) {
	case string:
		if strings.Contains(wanted, secretPlaceholder) {
			return "[REDACTED]"
		}
		return remote
	case map[string]any:
		actual, ok := remote.(map[string]any)
		if !ok {
			return remote
		}
		for key, desiredItem := range wanted {
			if remoteItem, present := actual[key]; present {
				actual[key] = redactProjectedSecrets(remoteItem, desiredItem)
			}
		}
		return actual
	case []any:
		actual, ok := remote.([]any)
		if !ok {
			return remote
		}
		for index, desiredItem := range wanted {
			if index < len(actual) {
				actual[index] = redactProjectedSecrets(actual[index], desiredItem)
			}
		}
		return actual
	default:
		return remote
	}
}

func withoutObjectFields(document string, fields []string, raw bool) string {
	canonical, err := canonicalDocument(document, raw)
	if err != nil || raw || !json.Valid([]byte(canonical)) {
		return canonical
	}
	var object map[string]any
	if json.Unmarshal([]byte(canonical), &object) != nil {
		return canonical
	}
	for _, field := range fields {
		delete(object, field)
	}
	for key, value := range object {
		switch selected := value.(type) {
		case nil:
			delete(object, key)
		case map[string]any:
			if len(selected) == 0 {
				delete(object, key)
			}
		case []any:
			if len(selected) == 0 {
				delete(object, key)
			}
		}
	}
	encoded, err := json.Marshal(object)
	if err != nil {
		return canonical
	}
	return string(encoded)
}

func projectValue(desired any, remote any) (any, error) {
	switch wanted := desired.(type) {
	case map[string]any:
		actual, ok := remote.(map[string]any)
		if !ok {
			return nil, fmt.Errorf("remote document changed object type")
		}
		result := make(map[string]any, len(wanted))
		for key, desiredItem := range wanted {
			remoteItem, present := actual[key]
			if !present {
				result[key] = desiredItem
				continue
			}
			projected, err := projectValue(desiredItem, remoteItem)
			if err != nil {
				return nil, err
			}
			result[key] = projected
		}
		return result, nil
	case string:
		if strings.Contains(wanted, secretPlaceholder) {
			return wanted, nil
		}
		return remote, nil
	default:
		return remote, nil
	}
}

func objectField(body []byte, field string) string {
	if field == "" {
		return ""
	}
	var object map[string]any
	if err := json.Unmarshal(body, &object); err != nil {
		return ""
	}
	value, present := object[field]
	if !present || value == nil {
		return ""
	}
	return fmt.Sprint(value)
}

func documentField(body []byte, field string) ([]byte, error) {
	var object map[string]any
	if err := json.Unmarshal(body, &object); err != nil {
		return nil, fmt.Errorf("decode document field: %w", err)
	}
	value, present := object[field]
	if !present {
		return nil, fmt.Errorf("document requires %q", field)
	}
	return json.Marshal(value)
}

func scimPatch(body []byte) ([]byte, error) {
	var object map[string]any
	if err := json.Unmarshal(body, &object); err != nil {
		return nil, fmt.Errorf("decode SCIM document: %w", err)
	}
	operations := make([]map[string]any, 0, len(object))
	for key, value := range object {
		if key == "schemas" || key == "id" || key == "meta" {
			continue
		}
		operations = append(operations, map[string]any{"op": "replace", "path": key, "value": value})
	}
	sort.Slice(operations, func(left, right int) bool {
		return operations[left]["path"].(string) < operations[right]["path"].(string)
	})
	return json.Marshal(map[string]any{
		"schemas":    []string{"urn:ietf:params:scim:api:messages:2.0:PatchOp"},
		"Operations": operations,
	})
}
