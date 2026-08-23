package provider

import (
	"context"
	"fmt"

	"github.com/hashicorp/terraform-plugin-framework/datasource"
	datasourceschema "github.com/hashicorp/terraform-plugin-framework/datasource/schema"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

type documentDataSource struct {
	descriptor resourceDescriptor
	client     *apiClient
}

type dataSourceModel struct {
	ID             types.String `tfsdk:"id"`
	Key            types.String `tfsdk:"key"`
	Namespace      types.String `tfsdk:"namespace"`
	ServerID       types.String `tfsdk:"server_id"`
	RemoteDocument types.String `tfsdk:"remote_document"`
	RemoteDigest   types.String `tfsdk:"remote_digest"`
	Revision       types.String `tfsdk:"revision"`
	ETag           types.String `tfsdk:"etag"`
}

var (
	_ datasource.DataSource              = &documentDataSource{}
	_ datasource.DataSourceWithConfigure = &documentDataSource{}
)

func newDocumentDataSource(descriptor resourceDescriptor) datasource.DataSource {
	return &documentDataSource{descriptor: descriptor}
}

func (source *documentDataSource) Metadata(
	_ context.Context,
	request datasource.MetadataRequest,
	response *datasource.MetadataResponse,
) {
	response.TypeName = request.ProviderTypeName + "_" + source.descriptor.Name
}

func (source *documentDataSource) Schema(
	_ context.Context,
	_ datasource.SchemaRequest,
	response *datasource.SchemaResponse,
) {
	response.Schema = datasourceschema.Schema{
		Description: "Read " + source.descriptor.Description,
		Attributes: map[string]datasourceschema.Attribute{
			"id":              datasourceschema.StringAttribute{Computed: true},
			"key":             datasourceschema.StringAttribute{Required: true, Description: "Caller-owned key, name or path."},
			"namespace":       datasourceschema.StringAttribute{Optional: true, Description: namespaceDescription(source.descriptor.Namespace)},
			"server_id":       datasourceschema.StringAttribute{Optional: true, Computed: true, Description: "Server-generated identifier for generated-ID resources."},
			"remote_document": datasourceschema.StringAttribute{Computed: true, Sensitive: true, Description: "Canonical redacted remote representation."},
			"remote_digest":   datasourceschema.StringAttribute{Computed: true, Description: "SHA-256 of the redacted remote representation."},
			"revision":        datasourceschema.StringAttribute{Computed: true},
			"etag":            datasourceschema.StringAttribute{Computed: true},
		},
	}
}

func (source *documentDataSource) Configure(
	_ context.Context,
	request datasource.ConfigureRequest,
	response *datasource.ConfigureResponse,
) {
	if request.ProviderData == nil {
		return
	}
	client, ok := request.ProviderData.(*apiClient)
	if !ok {
		response.Diagnostics.AddError("Unexpected provider data", "AMESH provider returned an incompatible client")
		return
	}
	source.client = client
}

func (source *documentDataSource) Read(
	ctx context.Context,
	request datasource.ReadRequest,
	response *datasource.ReadResponse,
) {
	var configuration dataSourceModel
	response.Diagnostics.Append(request.Config.Get(ctx, &configuration)...)
	if response.Diagnostics.HasError() {
		return
	}
	if source.client == nil {
		response.Diagnostics.AddError("Provider is not configured", "Configure the AMESH provider before using data sources.")
		return
	}
	resourceState := documentModel{
		Key: configuration.Key, Namespace: configuration.Namespace, ServerID: configuration.ServerID,
	}
	managed := documentResource{descriptor: source.descriptor, client: source.client}
	result, found, err := managed.read(ctx, resourceState)
	if err != nil {
		response.Diagnostics.AddError("Unable to read AMESH data source", err.Error())
		return
	}
	if !found {
		response.Diagnostics.AddError("AMESH resource not found", fmt.Sprintf("No %s matched the configured identity.", source.descriptor.Name))
		return
	}
	remote, err := redactedDocument(result.body, source.descriptor)
	if err != nil {
		response.Diagnostics.AddError("Unable to decode AMESH data source", err.Error())
		return
	}
	configuration.ID = types.StringValue(stableID(source.descriptor.Name, source.client.tenant, configuration.Namespace.ValueString(), configuration.Key.ValueString()))
	configuration.RemoteDocument = types.StringValue(remote)
	configuration.RemoteDigest = types.StringValue(documentDigest(remote))
	if selected := objectField(result.body, source.descriptor.ServerIDField); selected != "" {
		configuration.ServerID = types.StringValue(selected)
	}
	if selected := objectField(result.body, source.descriptor.RevisionField); selected != "" {
		configuration.Revision = types.StringValue(selected)
	} else {
		configuration.Revision = types.StringValue("")
	}
	configuration.ETag = types.StringValue(result.header.Get("ETag"))
	response.Diagnostics.Append(response.State.Set(ctx, &configuration)...)
}
