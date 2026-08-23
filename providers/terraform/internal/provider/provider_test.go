package provider

import (
	"context"
	"sort"
	"testing"
)

func TestProviderRegistersEveryRequiredResourceAndDataSource(t *testing.T) {
	t.Parallel()
	configured := &ameshProvider{version: "test"}
	resources := configured.Resources(context.Background())
	dataSources := configured.DataSources(context.Background())
	if len(resources) != 14 || len(dataSources) != 14 {
		t.Fatalf("expected 14 resources and data sources, got %d and %d", len(resources), len(dataSources))
	}
	names := make([]string, 0, len(resourceDescriptors()))
	for _, descriptor := range resourceDescriptors() {
		if descriptor.CreateMethod == "" || descriptor.ReadPath == "" {
			t.Fatalf("%s is missing create/read behavior", descriptor.Name)
		}
		names = append(names, descriptor.Name)
	}
	sort.Strings(names)
	wanted := []string{
		"app", "binding", "dashboard", "file", "flow", "group", "key_value", "namespace",
		"plugin_policy", "role", "service_account", "tenant", "user", "worker_group",
	}
	for index := range wanted {
		if names[index] != wanted[index] {
			t.Fatalf("unexpected provider surface: %#v", names)
		}
	}
}

func TestProviderConfigurationUsesEnvironmentDefaults(t *testing.T) {
	t.Setenv("AMESH_ENDPOINT", "https://amesh.internal")
	t.Setenv("AMESH_TOKEN", "environment-token")
	t.Setenv("AMESH_TENANT", "tenant-b")
	if got := configuredValue(providerModel{}.Endpoint, "AMESH_ENDPOINT", defaultEndpoint); got != "https://amesh.internal" {
		t.Fatalf("unexpected endpoint %q", got)
	}
	if got := configuredValue(providerModel{}.Token, "AMESH_TOKEN", ""); got != "environment-token" {
		t.Fatalf("unexpected token source %q", got)
	}
	if got := configuredValue(providerModel{}.Tenant, "AMESH_TENANT", "default"); got != "tenant-b" {
		t.Fatalf("unexpected tenant %q", got)
	}
}
