# \NamespacesAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet**](NamespacesAPI.md#GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet) | **Get** /api/v1/namespaces/{namespace}/workflow-metadata | Get Namespace Workflow Metadata
[**UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut**](NamespacesAPI.md#UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut) | **Put** /api/v1/namespaces/{namespace}/workflow-metadata | Upsert Namespace Workflow Metadata



## GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet

> NamespaceWorkflowMetadataView GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet(ctx, namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Namespace Workflow Metadata

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespacesAPI.GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet(context.Background(), namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespacesAPI.GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet`: NamespaceWorkflowMetadataView
	fmt.Fprintf(os.Stdout, "Response from `NamespacesAPI.GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**NamespaceWorkflowMetadataView**](NamespaceWorkflowMetadataView.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut

> NamespaceWorkflowMetadata UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut(ctx, namespace).NamespaceWorkflowMetadataUpdate(namespaceWorkflowMetadataUpdate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Upsert Namespace Workflow Metadata

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
	namespaceWorkflowMetadataUpdate := *openapiclient.NewNamespaceWorkflowMetadataUpdate() // NamespaceWorkflowMetadataUpdate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespacesAPI.UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut(context.Background(), namespace).NamespaceWorkflowMetadataUpdate(namespaceWorkflowMetadataUpdate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespacesAPI.UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut`: NamespaceWorkflowMetadata
	fmt.Fprintf(os.Stdout, "Response from `NamespacesAPI.UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **namespaceWorkflowMetadataUpdate** | [**NamespaceWorkflowMetadataUpdate**](NamespaceWorkflowMetadataUpdate.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**NamespaceWorkflowMetadata**](NamespaceWorkflowMetadata.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
