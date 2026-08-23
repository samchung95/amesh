package provider

import (
	"context"
	"fmt"
	"net/http"
	"net/url"
	"os"
	"strings"

	"github.com/hashicorp/terraform-plugin-framework/path"
	"github.com/hashicorp/terraform-plugin-framework/resource"
	resourceschema "github.com/hashicorp/terraform-plugin-framework/resource/schema"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
	"github.com/hashicorp/terraform-plugin-framework/resource/schema/stringplanmodifier"
	"github.com/hashicorp/terraform-plugin-framework/types"
)

type documentResource struct {
	descriptor resourceDescriptor
	client     *apiClient
}

type documentModel struct {
	ID                types.String `tfsdk:"id"`
	Key               types.String `tfsdk:"key"`
	Namespace         types.String `tfsdk:"namespace"`
	Document          types.String `tfsdk:"document"`
	SecretEnvironment types.String `tfsdk:"secret_environment"`
	ServerID          types.String `tfsdk:"server_id"`
	Revision          types.String `tfsdk:"revision"`
	ETag              types.String `tfsdk:"etag"`
	RemoteDocument    types.String `tfsdk:"remote_document"`
	RemoteDigest      types.String `tfsdk:"remote_digest"`
	AppliedDigest     types.String `tfsdk:"applied_digest"`
	Drifted           types.Bool   `tfsdk:"drifted"`
}

var (
	_ resource.Resource                = &documentResource{}
	_ resource.ResourceWithConfigure   = &documentResource{}
	_ resource.ResourceWithImportState = &documentResource{}
)

func newDocumentResource(descriptor resourceDescriptor) resource.Resource {
	return &documentResource{descriptor: descriptor}
}

func (managed *documentResource) Metadata(
	_ context.Context,
	request resource.MetadataRequest,
	response *resource.MetadataResponse,
) {
	response.TypeName = request.ProviderTypeName + "_" + managed.descriptor.Name
}

func (managed *documentResource) Schema(
	_ context.Context,
	_ resource.SchemaRequest,
	response *resource.SchemaResponse,
) {
	documentModifiers := []planmodifier.String{semanticDocumentModifier{raw: managed.descriptor.RawDocument}}
	if managed.descriptor.ReplaceDocument {
		documentModifiers = append(documentModifiers, stringplanmodifier.RequiresReplace())
	}
	response.Schema = resourceschema.Schema{
		Description: managed.descriptor.Description,
		Attributes: map[string]resourceschema.Attribute{
			"id": resourceschema.StringAttribute{
				Computed:    true,
				Description: "Stable provider identifier in kind|tenant|namespace|key form.",
			},
			"key": resourceschema.StringAttribute{
				Required:      true,
				Description:   "Caller-owned immutable key, name or path.",
				PlanModifiers: []planmodifier.String{stringplanmodifier.RequiresReplace()},
			},
			"namespace": resourceschema.StringAttribute{
				Optional:      true,
				Description:   namespaceDescription(managed.descriptor.Namespace),
				PlanModifiers: []planmodifier.String{stringplanmodifier.RequiresReplace()},
			},
			"document": resourceschema.StringAttribute{
				Optional:      true,
				Computed:      true,
				Description:   "JSON or YAML configuration document. Formatting-only differences are suppressed.",
				PlanModifiers: documentModifiers,
			},
			"secret_environment": resourceschema.StringAttribute{
				Optional:    true,
				Description: "Environment variable expanded in-memory for ${AMESH_SECRET}; plaintext is never stored in state.",
			},
			"server_id": resourceschema.StringAttribute{Computed: true, Description: "Server-generated identifier when applicable."},
			"revision":  resourceschema.StringAttribute{Computed: true, Description: "Server-managed revision or resource version."},
			"etag":      resourceschema.StringAttribute{Computed: true, Description: "Latest server ETag when supplied."},
			"remote_document": resourceschema.StringAttribute{
				Computed:    true,
				Sensitive:   true,
				Description: "Canonical redacted server representation used for refresh and drift evidence.",
			},
			"remote_digest":  resourceschema.StringAttribute{Computed: true, Description: "SHA-256 of the redacted remote representation."},
			"applied_digest": resourceschema.StringAttribute{Computed: true, Description: "SHA-256 recorded after the last successful apply."},
			"drifted":        resourceschema.BoolAttribute{Computed: true, Description: "True when refresh differs from the last successful apply."},
		},
	}
}

func namespaceDescription(required bool) string {
	if required {
		return "Required AMESH namespace (or tenant slug for worker-group policy resources)."
	}
	return "Optional AMESH namespace for scoped resources."
}

func (managed *documentResource) Configure(
	_ context.Context,
	request resource.ConfigureRequest,
	response *resource.ConfigureResponse,
) {
	if request.ProviderData == nil {
		return
	}
	client, ok := request.ProviderData.(*apiClient)
	if !ok {
		response.Diagnostics.AddError("Unexpected provider data", "AMESH provider returned an incompatible client")
		return
	}
	managed.client = client
}

func (managed *documentResource) Create(
	ctx context.Context,
	request resource.CreateRequest,
	response *resource.CreateResponse,
) {
	var plan documentModel
	response.Diagnostics.Append(request.Plan.Get(ctx, &plan)...)
	if response.Diagnostics.HasError() || !managed.validateModel(&plan, &response.Diagnostics) {
		return
	}
	result, body, ok := managed.write(ctx, plan, managed.descriptor.CreateMethod, managed.descriptor.CreatePath, writeDocument, "", &response.Diagnostics)
	if !ok {
		return
	}
	managed.recordApply(&plan, result, body)
	response.Diagnostics.Append(response.State.Set(ctx, &plan)...)
}

func (managed *documentResource) Read(
	ctx context.Context,
	request resource.ReadRequest,
	response *resource.ReadResponse,
) {
	var state documentModel
	response.Diagnostics.Append(request.State.Get(ctx, &state)...)
	if response.Diagnostics.HasError() {
		return
	}
	result, found, err := managed.read(ctx, state)
	if err != nil {
		response.Diagnostics.AddError("Unable to refresh AMESH resource", err.Error())
		return
	}
	if !found {
		response.State.RemoveResource(ctx)
		return
	}
	managed.recordRefresh(&state, result)
	response.Diagnostics.Append(response.State.Set(ctx, &state)...)
}

func (managed *documentResource) Update(
	ctx context.Context,
	request resource.UpdateRequest,
	response *resource.UpdateResponse,
) {
	var plan documentModel
	var prior documentModel
	response.Diagnostics.Append(request.Plan.Get(ctx, &plan)...)
	response.Diagnostics.Append(request.State.Get(ctx, &prior)...)
	if response.Diagnostics.HasError() || !managed.validateModel(&plan, &response.Diagnostics) {
		return
	}
	plan.ServerID = prior.ServerID
	plan.Revision = prior.Revision
	result, body, ok := managed.write(
		ctx, plan, managed.descriptor.UpdateMethod, managed.descriptor.UpdatePath,
		managed.descriptor.UpdateMode, managed.descriptor.UpdateDocumentField, &response.Diagnostics,
	)
	if !ok {
		return
	}
	managed.recordApply(&plan, result, body)
	response.Diagnostics.Append(response.State.Set(ctx, &plan)...)
}

func (managed *documentResource) Delete(
	ctx context.Context,
	request resource.DeleteRequest,
	response *resource.DeleteResponse,
) {
	var state documentModel
	response.Diagnostics.Append(request.State.Get(ctx, &state)...)
	if response.Diagnostics.HasError() || managed.descriptor.RetainOnDelete {
		return
	}
	if managed.descriptor.DeleteMethod == "" {
		response.Diagnostics.AddError("AMESH resource cannot be deleted", "This resource is server-managed and must be removed outside Terraform.")
		return
	}
	_, err := managed.client.do(
		ctx,
		managed.descriptor.DeleteMethod,
		renderPath(managed.descriptor.DeletePath, state, managed.client.tenant),
		nil,
		"application/json",
	)
	if err != nil {
		if strings.Contains(err.Error(), "HTTP 404") {
			return
		}
		response.Diagnostics.AddError("Unable to delete AMESH resource", err.Error())
	}
}

func (managed *documentResource) ImportState(
	ctx context.Context,
	request resource.ImportStateRequest,
	response *resource.ImportStateResponse,
) {
	parts := strings.Split(request.ID, "|")
	if len(parts) != 4 && len(parts) != 5 {
		response.Diagnostics.AddError("Invalid import identifier", "Use kind|tenant|namespace|key or kind|tenant|namespace|key|server_id.")
		return
	}
	if parts[0] != managed.descriptor.Name {
		response.Diagnostics.AddError("Invalid import kind", fmt.Sprintf("Expected %q, received %q.", managed.descriptor.Name, parts[0]))
		return
	}
	response.Diagnostics.Append(response.State.SetAttribute(ctx, path.Root("id"), strings.Join(parts[:4], "|"))...)
	response.Diagnostics.Append(response.State.SetAttribute(ctx, path.Root("namespace"), decodeIDPart(parts[2]))...)
	response.Diagnostics.Append(response.State.SetAttribute(ctx, path.Root("key"), decodeIDPart(parts[3]))...)
	if len(parts) == 5 {
		response.Diagnostics.Append(response.State.SetAttribute(ctx, path.Root("server_id"), decodeIDPart(parts[4]))...)
	}
}

func (managed *documentResource) validateModel(model *documentModel, diagnostics interface {
	AddError(string, string)
}) bool {
	if managed.client == nil {
		diagnostics.AddError("Provider is not configured", "Configure the AMESH provider before using resources.")
		return false
	}
	if model.Document.IsNull() || model.Document.IsUnknown() || model.Document.ValueString() == "" {
		diagnostics.AddError("Missing document", "A JSON or YAML document is required for create and update.")
		return false
	}
	if managed.descriptor.Namespace && (model.Namespace.IsNull() || model.Namespace.ValueString() == "") {
		diagnostics.AddError("Missing namespace", "This AMESH resource requires namespace.")
		return false
	}
	return true
}

func (managed *documentResource) write(
	ctx context.Context,
	model documentModel,
	method string,
	pathTemplate string,
	mode writeMode,
	field string,
	diagnostics interface{ AddError(string, string) },
) (apiResponse, []byte, bool) {
	if method == "" || pathTemplate == "" {
		diagnostics.AddError("Unsupported AMESH update", "This resource is immutable and must be replaced.")
		return apiResponse{}, nil, false
	}
	secretEnvironment := ""
	if !model.SecretEnvironment.IsNull() && !model.SecretEnvironment.IsUnknown() {
		secretEnvironment = model.SecretEnvironment.ValueString()
	}
	body, err := requestDocument(model.Document.ValueString(), managed.descriptor, secretEnvironment)
	if err != nil {
		diagnostics.AddError("Invalid AMESH document", err.Error())
		return apiResponse{}, nil, false
	}
	switch mode {
	case writeSCIMPatch:
		body, err = scimPatch(body)
	case writeDocumentField:
		body, err = documentField(body, field)
	}
	if err != nil {
		diagnostics.AddError("Invalid AMESH update document", err.Error())
		return apiResponse{}, nil, false
	}
	contentType := "application/json"
	if managed.descriptor.RawDocument && !jsonDocument(body) {
		contentType = "application/yaml"
	}
	result, err := managed.client.do(
		ctx, method, renderPath(pathTemplate, model, managed.client.tenant), body, contentType,
	)
	if err != nil {
		diagnostics.AddError("AMESH apply failed", err.Error())
		return apiResponse{}, nil, false
	}
	return result, body, true
}

func (managed *documentResource) read(ctx context.Context, state documentModel) (apiResponse, bool, error) {
	result, err := managed.client.do(
		ctx,
		http.MethodGet,
		renderPath(managed.descriptor.ReadPath, state, managed.client.tenant),
		nil,
		"application/json",
	)
	if err != nil {
		if result.status == http.StatusNotFound {
			return apiResponse{}, false, nil
		}
		return apiResponse{}, false, err
	}
	if managed.descriptor.ReadMode == readCollection {
		expected := state.Key.ValueString()
		if managed.descriptor.ReadMatchField == "id" {
			expected = state.ServerID.ValueString()
		}
		item, found, selectErr := selectCollectionItem(result.body, managed.descriptor.ReadMatchField, expected)
		if selectErr != nil || !found {
			return apiResponse{}, found, selectErr
		}
		result.body = item
	}
	return result, true, nil
}

func (managed *documentResource) recordApply(model *documentModel, result apiResponse, requestBody []byte) {
	model.ID = types.StringValue(stableID(managed.descriptor.Name, managed.client.tenant, model.Namespace.ValueString(), model.Key.ValueString()))
	serverID := objectField(result.body, managed.descriptor.ServerIDField)
	if serverID == "" {
		serverID = model.ServerID.ValueString()
	}
	if serverID == "" {
		serverID = model.Key.ValueString()
	}
	model.ServerID = types.StringValue(serverID)
	revision := objectField(result.body, managed.descriptor.RevisionField)
	if revision != "" {
		model.Revision = types.StringValue(revision)
	} else if model.Revision.IsNull() || model.Revision.IsUnknown() {
		model.Revision = types.StringValue("")
	}
	model.ETag = types.StringValue(result.header.Get("ETag"))
	remote, err := managed.redactedRemote(model, result.body)
	if managed.descriptor.ReadMode == readRaw || managed.descriptor.ReadDocumentField != "" || err != nil || len(result.body) == 0 {
		remote, _ = canonicalDocument(string(requestBody), managed.descriptor.RawDocument)
	}
	digest := documentDigest(remote)
	model.RemoteDocument = types.StringValue(remote)
	model.RemoteDigest = types.StringValue(digest)
	model.AppliedDigest = types.StringValue(digest)
	model.Drifted = types.BoolValue(false)
}

func (managed *documentResource) recordRefresh(model *documentModel, result apiResponse) {
	remote, err := managed.redactedRemote(model, result.body)
	if err != nil {
		return
	}
	digest := documentDigest(remote)
	drifted := !model.AppliedDigest.IsNull() && model.AppliedDigest.ValueString() != digest
	model.RemoteDocument = types.StringValue(remote)
	model.RemoteDigest = types.StringValue(digest)
	model.Drifted = types.BoolValue(drifted)
	if model.Document.IsNull() || model.Document.IsUnknown() {
		model.Document = types.StringValue(withoutObjectFields(
			remote, managed.descriptor.ServerManagedDefaults, managed.descriptor.RawDocument,
		))
	} else if drifted {
		if projected, projectErr := projectRemoteDocument(
			model.Document.ValueString(), remote, managed.descriptor.RawDocument,
		); projectErr == nil {
			model.Document = types.StringValue(projected)
		}
	}
	if selected := objectField(result.body, managed.descriptor.ServerIDField); selected != "" {
		model.ServerID = types.StringValue(selected)
	}
	if selected := objectField(result.body, managed.descriptor.RevisionField); selected != "" {
		model.Revision = types.StringValue(selected)
	}
	model.ETag = types.StringValue(result.header.Get("ETag"))
}

func (managed *documentResource) redactedRemote(model *documentModel, body []byte) (string, error) {
	secret := ""
	if !model.SecretEnvironment.IsNull() && !model.SecretEnvironment.IsUnknown() {
		secret = os.Getenv(model.SecretEnvironment.ValueString())
	}
	remote, err := redactedDocument(body, managed.descriptor, secret)
	if err != nil {
		return "", err
	}
	if !model.Document.IsNull() && !model.Document.IsUnknown() {
		remote = redactDesiredSecretPaths(
			remote, model.Document.ValueString(), managed.descriptor.RawDocument,
		)
	}
	return remote, nil
}

func stableID(kind, tenant, namespace, key string) string {
	return strings.Join([]string{kind, encodeIDPart(tenant), encodeIDPart(namespace), encodeIDPart(key)}, "|")
}

func encodeIDPart(value string) string { return url.QueryEscape(value) }

func decodeIDPart(value string) string {
	decoded, err := url.QueryUnescape(value)
	if err != nil {
		return value
	}
	return decoded
}

func jsonDocument(body []byte) bool {
	trimmed := strings.TrimSpace(string(body))
	return strings.HasPrefix(trimmed, "{") || strings.HasPrefix(trimmed, "[")
}
