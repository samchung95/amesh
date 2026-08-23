package provider

import (
	"context"
	"os"

	"github.com/hashicorp/terraform-plugin-framework/datasource"
	"github.com/hashicorp/terraform-plugin-framework/provider"
	providerschema "github.com/hashicorp/terraform-plugin-framework/provider/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

const defaultEndpoint = "http://localhost:8000"

type ameshProvider struct {
	version string
}

type providerModel struct {
	Endpoint types.String `tfsdk:"endpoint"`
	Token    types.String `tfsdk:"token"`
	Tenant   types.String `tfsdk:"tenant"`
}

var _ provider.Provider = &ameshProvider{}

func New(version string) func() provider.Provider {
	return func() provider.Provider { return &ameshProvider{version: version} }
}

func (configured *ameshProvider) Metadata(
	_ context.Context,
	_ provider.MetadataRequest,
	response *provider.MetadataResponse,
) {
	response.TypeName = "amesh"
	response.Version = configured.version
}

func (configured *ameshProvider) Schema(
	_ context.Context,
	_ provider.SchemaRequest,
	response *provider.SchemaResponse,
) {
	response.Schema = providerschema.Schema{
		Description: "Manage AMESH configuration through its public API.",
		Attributes: map[string]providerschema.Attribute{
			"endpoint": providerschema.StringAttribute{
				Optional:    true,
				Description: "AMESH API base URL. Defaults to AMESH_ENDPOINT or http://localhost:8000.",
			},
			"token": providerschema.StringAttribute{
				Optional:    true,
				Sensitive:   true,
				Description: "AMESH bearer token. Prefer the AMESH_TOKEN environment variable.",
			},
			"tenant": providerschema.StringAttribute{
				Optional:    true,
				Description: "Tenant header used for API calls. Defaults to AMESH_TENANT or default.",
			},
		},
	}
}

func (configured *ameshProvider) Configure(
	ctx context.Context,
	request provider.ConfigureRequest,
	response *provider.ConfigureResponse,
) {
	var configuration providerModel
	response.Diagnostics.Append(request.Config.Get(ctx, &configuration)...)
	if response.Diagnostics.HasError() {
		return
	}
	endpoint := configuredValue(configuration.Endpoint, "AMESH_ENDPOINT", defaultEndpoint)
	token := configuredValue(configuration.Token, "AMESH_TOKEN", "")
	tenant := configuredValue(configuration.Tenant, "AMESH_TENANT", "default")
	client, err := newAPIClient(endpoint, token, tenant)
	if err != nil {
		response.Diagnostics.AddError("Invalid AMESH provider configuration", err.Error())
		return
	}
	response.DataSourceData = client
	response.ResourceData = client
}

func configuredValue(value types.String, environment string, fallback string) string {
	if !value.IsNull() && !value.IsUnknown() && value.ValueString() != "" {
		return value.ValueString()
	}
	if selected := os.Getenv(environment); selected != "" {
		return selected
	}
	return fallback
}

func (configured *ameshProvider) Resources(_ context.Context) []func() resource.Resource {
	descriptors := resourceDescriptors()
	resources := make([]func() resource.Resource, 0, len(descriptors))
	for _, selected := range descriptors {
		descriptor := selected
		resources = append(resources, func() resource.Resource {
			return newDocumentResource(descriptor)
		})
	}
	return resources
}

func (configured *ameshProvider) DataSources(_ context.Context) []func() datasource.DataSource {
	descriptors := resourceDescriptors()
	dataSources := make([]func() datasource.DataSource, 0, len(descriptors))
	for _, selected := range descriptors {
		descriptor := selected
		dataSources = append(dataSources, func() datasource.DataSource {
			return newDocumentDataSource(descriptor)
		})
	}
	return dataSources
}
