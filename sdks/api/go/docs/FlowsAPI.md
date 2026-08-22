# \FlowsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ApplyFlowApiV1FlowsPut**](FlowsAPI.md#ApplyFlowApiV1FlowsPut) | **Put** /api/v1/flows | Apply Flow
[**DeleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete**](FlowsAPI.md#DeleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete) | **Delete** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision} | Delete Flow Revision
[**DiffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost**](FlowsAPI.md#DiffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost) | **Post** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/diff-draft | Diff Flow Draft
[**DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet**](FlowsAPI.md#DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet) | **Get** /api/v1/flows/{namespace}/{flow_id}/revisions/diff | Diff Flow Revisions
[**ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet**](FlowsAPI.md#ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet) | **Get** /api/v1/flows/{namespace}/{flow_id}/document | Export Flow Document
[**FormatFlowApiV1FlowsFormatPost**](FlowsAPI.md#FormatFlowApiV1FlowsFormatPost) | **Post** /api/v1/flows/format | Format Flow
[**GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet**](FlowsAPI.md#GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet) | **Get** /api/v1/flows/{namespace}/{flow_id}/data-contract | Get Flow Data Contract
[**GetFlowEditorSchemaApiV1FlowsEditorSchemaGet**](FlowsAPI.md#GetFlowEditorSchemaApiV1FlowsEditorSchemaGet) | **Get** /api/v1/flows/editor/schema | Get Flow Editor Schema
[**GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGet**](FlowsAPI.md#GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGet) | **Get** /api/v1/flows/{namespace}/{flow_id}/graph | Get Flow Graph
[**GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet**](FlowsAPI.md#GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet) | **Get** /api/v1/flows/{namespace}/{flow_id}/metadata | Get Flow Metadata
[**ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet**](FlowsAPI.md#ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet) | **Get** /api/v1/flows/{namespace}/{flow_id}/revisions | List Flow Revisions
[**ListFlowsApiV1FlowsGet**](FlowsAPI.md#ListFlowsApiV1FlowsGet) | **Get** /api/v1/flows | List Flows
[**PreviewFlowExpressionApiV1FlowsExpressionsPreviewPost**](FlowsAPI.md#PreviewFlowExpressionApiV1FlowsExpressionsPreviewPost) | **Post** /api/v1/flows/expressions/preview | Preview Flow Expression
[**PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut**](FlowsAPI.md#PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut) | **Put** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/lifecycle | Promote Flow Revision
[**RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost**](FlowsAPI.md#RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost) | **Post** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/restore | Restore Flow Revision
[**ValidateFlowApiV1FlowsValidatePost**](FlowsAPI.md#ValidateFlowApiV1FlowsValidatePost) | **Post** /api/v1/flows/validate | Validate Flow



## ApplyFlowApiV1FlowsPut

> PersistedFlow ApplyFlowApiV1FlowsPut(ctx).IfMatch(ifMatch).XAMESHSource(xAMESHSource).XAMESHCommit(xAMESHCommit).XAMESHEnvironment(xAMESHEnvironment).XAMESHDeployment(xAMESHDeployment).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Apply Flow

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	ifMatch := "ifMatch_example" // string |  (optional)
	xAMESHSource := "xAMESHSource_example" // string |  (optional)
	xAMESHCommit := "xAMESHCommit_example" // string |  (optional)
	xAMESHEnvironment := "xAMESHEnvironment_example" // string |  (optional)
	xAMESHDeployment := "xAMESHDeployment_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.ApplyFlowApiV1FlowsPut(context.Background()).IfMatch(ifMatch).XAMESHSource(xAMESHSource).XAMESHCommit(xAMESHCommit).XAMESHEnvironment(xAMESHEnvironment).XAMESHDeployment(xAMESHDeployment).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.ApplyFlowApiV1FlowsPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ApplyFlowApiV1FlowsPut`: PersistedFlow
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.ApplyFlowApiV1FlowsPut`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiApplyFlowApiV1FlowsPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **ifMatch** | **string** |  |
 **xAMESHSource** | **string** |  |
 **xAMESHCommit** | **string** |  |
 **xAMESHEnvironment** | **string** |  |
 **xAMESHDeployment** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PersistedFlow**](PersistedFlow.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete

> DeleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete(ctx, namespace, flowId, revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Delete Flow Revision

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	revision := int32(56) // int32 |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.FlowsAPI.DeleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete(context.Background(), namespace, flowId, revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.DeleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**revision** | **int32** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DiffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost

> FlowRevisionDiff DiffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost(ctx, namespace, flowId, revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Diff Flow Draft

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	revision := int32(56) // int32 |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.DiffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost(context.Background(), namespace, flowId, revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.DiffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DiffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost`: FlowRevisionDiff
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.DiffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**revision** | **int32** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDiffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowRevisionDiff**](FlowRevisionDiff.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet

> FlowRevisionDiff DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet(ctx, namespace, flowId).From(from).To(to).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Diff Flow Revisions

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	from := int32(56) // int32 |
	to := int32(56) // int32 |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet(context.Background(), namespace, flowId).From(from).To(to).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet`: FlowRevisionDiff
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **from** | **int32** |  |
 **to** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowRevisionDiff**](FlowRevisionDiff.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet

> FlowDocumentExport ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet(ctx, namespace, flowId).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Export Flow Document

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	revision := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet(context.Background(), namespace, flowId).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet`: FlowDocumentExport
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **revision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowDocumentExport**](FlowDocumentExport.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## FormatFlowApiV1FlowsFormatPost

> FlowFormatResponse FormatFlowApiV1FlowsFormatPost(ctx).Execute()

Format Flow

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.FormatFlowApiV1FlowsFormatPost(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.FormatFlowApiV1FlowsFormatPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `FormatFlowApiV1FlowsFormatPost`: FlowFormatResponse
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.FormatFlowApiV1FlowsFormatPost`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiFormatFlowApiV1FlowsFormatPostRequest struct via the builder pattern


### Return type

[**FlowFormatResponse**](FlowFormatResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet

> FlowDataContract GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet(ctx, namespace, flowId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Flow Data Contract

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet(context.Background(), namespace, flowId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet`: FlowDataContract
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowDataContract**](FlowDataContract.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetFlowEditorSchemaApiV1FlowsEditorSchemaGet

> FlowEditorSchemaResponse GetFlowEditorSchemaApiV1FlowsEditorSchemaGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Flow Editor Schema

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.GetFlowEditorSchemaApiV1FlowsEditorSchemaGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.GetFlowEditorSchemaApiV1FlowsEditorSchemaGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetFlowEditorSchemaApiV1FlowsEditorSchemaGet`: FlowEditorSchemaResponse
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.GetFlowEditorSchemaApiV1FlowsEditorSchemaGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetFlowEditorSchemaApiV1FlowsEditorSchemaGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowEditorSchemaResponse**](FlowEditorSchemaResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGet

> FlowGraph GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGet(ctx, namespace, flowId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Flow Graph

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGet(context.Background(), namespace, flowId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGet`: FlowGraph
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetFlowGraphApiV1FlowsNamespaceFlowIdGraphGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowGraph**](FlowGraph.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet

> FlowMetadataResponse GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet(ctx, namespace, flowId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Flow Metadata

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet(context.Background(), namespace, flowId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet`: FlowMetadataResponse
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowMetadataResponse**](FlowMetadataResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet

> []FlowRevisionRecord ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet(ctx, namespace, flowId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Flow Revisions

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet(context.Background(), namespace, flowId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet`: []FlowRevisionRecord
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]FlowRevisionRecord**](FlowRevisionRecord.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListFlowsApiV1FlowsGet

> []PersistedFlow ListFlowsApiV1FlowsGet(ctx).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Flows

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	cursor := "cursor_example" // string | Opaque cursor from the prior page (optional)
	limit := int32(56) // int32 |  (optional)
	filter := []string{"Inner_example"} // []string | Repeatable top-level equality filter in field=value form (optional)
	sort := "sort_example" // string | Comma-separated top-level fields; prefix descending fields with - (optional)
	fields := "fields_example" // string | Comma-separated top-level response fields (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.ListFlowsApiV1FlowsGet(context.Background()).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.ListFlowsApiV1FlowsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListFlowsApiV1FlowsGet`: []PersistedFlow
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.ListFlowsApiV1FlowsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListFlowsApiV1FlowsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **string** | Opaque cursor from the prior page |
 **limit** | **int32** |  |
 **filter** | **[]string** | Repeatable top-level equality filter in field&#x3D;value form |
 **sort** | **string** | Comma-separated top-level fields; prefix descending fields with - |
 **fields** | **string** | Comma-separated top-level response fields |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]PersistedFlow**](PersistedFlow.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PreviewFlowExpressionApiV1FlowsExpressionsPreviewPost

> ExpressionPreviewResponse PreviewFlowExpressionApiV1FlowsExpressionsPreviewPost(ctx).ExpressionPreviewRequest(expressionPreviewRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Preview Flow Expression

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	expressionPreviewRequest := *openapiclient.NewExpressionPreviewRequest("Expression_example") // ExpressionPreviewRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.PreviewFlowExpressionApiV1FlowsExpressionsPreviewPost(context.Background()).ExpressionPreviewRequest(expressionPreviewRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.PreviewFlowExpressionApiV1FlowsExpressionsPreviewPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PreviewFlowExpressionApiV1FlowsExpressionsPreviewPost`: ExpressionPreviewResponse
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.PreviewFlowExpressionApiV1FlowsExpressionsPreviewPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPreviewFlowExpressionApiV1FlowsExpressionsPreviewPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **expressionPreviewRequest** | [**ExpressionPreviewRequest**](ExpressionPreviewRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ExpressionPreviewResponse**](ExpressionPreviewResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut

> PersistedFlow PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut(ctx, namespace, flowId, revision).FlowRevisionLifecycleRequest(flowRevisionLifecycleRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Promote Flow Revision

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	revision := int32(56) // int32 |
	flowRevisionLifecycleRequest := *openapiclient.NewFlowRevisionLifecycleRequest(openapiclient.FlowLifecycle("DRAFT")) // FlowRevisionLifecycleRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut(context.Background(), namespace, flowId, revision).FlowRevisionLifecycleRequest(flowRevisionLifecycleRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut`: PersistedFlow
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**revision** | **int32** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **flowRevisionLifecycleRequest** | [**FlowRevisionLifecycleRequest**](FlowRevisionLifecycleRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PersistedFlow**](PersistedFlow.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost

> PersistedFlow RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost(ctx, namespace, flowId, revision).FlowRevisionRestoreRequest(flowRevisionRestoreRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Restore Flow Revision

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	revision := int32(56) // int32 |
	flowRevisionRestoreRequest := *openapiclient.NewFlowRevisionRestoreRequest() // FlowRevisionRestoreRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost(context.Background(), namespace, flowId, revision).FlowRevisionRestoreRequest(flowRevisionRestoreRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost`: PersistedFlow
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**revision** | **int32** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **flowRevisionRestoreRequest** | [**FlowRevisionRestoreRequest**](FlowRevisionRestoreRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PersistedFlow**](PersistedFlow.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ValidateFlowApiV1FlowsValidatePost

> FlowValidationResult ValidateFlowApiV1FlowsValidatePost(ctx).Execute()

Validate Flow

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowsAPI.ValidateFlowApiV1FlowsValidatePost(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowsAPI.ValidateFlowApiV1FlowsValidatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ValidateFlowApiV1FlowsValidatePost`: FlowValidationResult
	fmt.Fprintf(os.Stdout, "Response from `FlowsAPI.ValidateFlowApiV1FlowsValidatePost`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiValidateFlowApiV1FlowsValidatePostRequest struct via the builder pattern


### Return type

[**FlowValidationResult**](FlowValidationResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
