package provider

import (
	"context"

	"github.com/hashicorp/terraform-plugin-framework/resource/schema/planmodifier"
)

type semanticDocumentModifier struct {
	raw bool
}

func (modifier semanticDocumentModifier) Description(_ context.Context) string {
	return "Suppresses JSON/YAML formatting-only changes."
}

func (modifier semanticDocumentModifier) MarkdownDescription(ctx context.Context) string {
	return modifier.Description(ctx)
}

func (modifier semanticDocumentModifier) PlanModifyString(
	_ context.Context,
	request planmodifier.StringRequest,
	response *planmodifier.StringResponse,
) {
	if request.PlanValue.IsNull() || request.PlanValue.IsUnknown() ||
		request.StateValue.IsNull() || request.StateValue.IsUnknown() {
		return
	}
	planned, planErr := canonicalDocument(request.PlanValue.ValueString(), modifier.raw)
	state, stateErr := canonicalDocument(request.StateValue.ValueString(), modifier.raw)
	if planErr == nil && stateErr == nil && planned == state {
		response.PlanValue = request.StateValue
	}
}
