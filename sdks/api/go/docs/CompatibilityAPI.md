# \CompatibilityAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPost**](CompatibilityAPI.md#CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPost) | **Post** /api/v1/executions/{namespace}/{flow_id} | Create Kestra Execution
[**GetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet**](CompatibilityAPI.md#GetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet) | **Get** /api/v1/compatibility/kestra/manifest | Get Kestra Compatibility Manifest
[**ValidateKestraFlowApiV1MainFlowsValidatePost**](CompatibilityAPI.md#ValidateKestraFlowApiV1MainFlowsValidatePost) | **Post** /api/v1/main/flows/validate | Validate Kestra Flow



## CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPost

> ExecutionDetail CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPost(ctx, namespace, flowId).KestraExecutionRequest(kestraExecutionRequest).Prefer(prefer).IdempotencyKey(idempotencyKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Kestra Execution

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
	kestraExecutionRequest := *openapiclient.NewKestraExecutionRequest() // KestraExecutionRequest |
	prefer := "prefer_example" // string |  (optional)
	idempotencyKey := "idempotencyKey_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CompatibilityAPI.CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPost(context.Background(), namespace, flowId).KestraExecutionRequest(kestraExecutionRequest).Prefer(prefer).IdempotencyKey(idempotencyKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CompatibilityAPI.CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPost`: ExecutionDetail
	fmt.Fprintf(os.Stdout, "Response from `CompatibilityAPI.CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiCreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **kestraExecutionRequest** | [**KestraExecutionRequest**](KestraExecutionRequest.md) |  |
 **prefer** | **string** |  |
 **idempotencyKey** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet

> map[string]*interface{} GetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet(ctx).Execute()

Get Kestra Compatibility Manifest

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
	resp, r, err := apiClient.CompatibilityAPI.GetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CompatibilityAPI.GetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet`: map[string]*interface{}
	fmt.Fprintf(os.Stdout, "Response from `CompatibilityAPI.GetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGetRequest struct via the builder pattern


### Return type

**map[string]*interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ValidateKestraFlowApiV1MainFlowsValidatePost

> KestraFlowImport ValidateKestraFlowApiV1MainFlowsValidatePost(ctx).Execute()

Validate Kestra Flow

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
	resp, r, err := apiClient.CompatibilityAPI.ValidateKestraFlowApiV1MainFlowsValidatePost(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CompatibilityAPI.ValidateKestraFlowApiV1MainFlowsValidatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ValidateKestraFlowApiV1MainFlowsValidatePost`: KestraFlowImport
	fmt.Fprintf(os.Stdout, "Response from `CompatibilityAPI.ValidateKestraFlowApiV1MainFlowsValidatePost`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiValidateKestraFlowApiV1MainFlowsValidatePostRequest struct via the builder pattern


### Return type

[**KestraFlowImport**](KestraFlowImport.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
