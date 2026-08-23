# \AppsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetWorkflowAppApiV1AppsNamespaceAppIdGet**](AppsAPI.md#GetWorkflowAppApiV1AppsNamespaceAppIdGet) | **Get** /api/v1/apps/{namespace}/{app_id} | Get Workflow App
[**LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost**](AppsAPI.md#LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost) | **Post** /api/v1/apps/{namespace}/{app_id}/launch | Launch Workflow App
[**ListWorkflowAppsApiV1AppsGet**](AppsAPI.md#ListWorkflowAppsApiV1AppsGet) | **Get** /api/v1/apps | List Workflow Apps
[**UpsertWorkflowAppApiV1AppsNamespaceAppIdPut**](AppsAPI.md#UpsertWorkflowAppApiV1AppsNamespaceAppIdPut) | **Put** /api/v1/apps/{namespace}/{app_id} | Upsert Workflow App



## GetWorkflowAppApiV1AppsNamespaceAppIdGet

> WorkflowApp GetWorkflowAppApiV1AppsNamespaceAppIdGet(ctx, namespace, appId).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Workflow App

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
	appId := "appId_example" // string |
	revision := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AppsAPI.GetWorkflowAppApiV1AppsNamespaceAppIdGet(context.Background(), namespace, appId).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AppsAPI.GetWorkflowAppApiV1AppsNamespaceAppIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetWorkflowAppApiV1AppsNamespaceAppIdGet`: WorkflowApp
	fmt.Fprintf(os.Stdout, "Response from `AppsAPI.GetWorkflowAppApiV1AppsNamespaceAppIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**appId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetWorkflowAppApiV1AppsNamespaceAppIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **revision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**WorkflowApp**](WorkflowApp.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost

> ExecutionDetail LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost(ctx, namespace, appId).WorkflowAppLaunchRequest(workflowAppLaunchRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Launch Workflow App

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
	appId := "appId_example" // string |
	workflowAppLaunchRequest := *openapiclient.NewWorkflowAppLaunchRequest() // WorkflowAppLaunchRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AppsAPI.LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost(context.Background(), namespace, appId).WorkflowAppLaunchRequest(workflowAppLaunchRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AppsAPI.LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost`: ExecutionDetail
	fmt.Fprintf(os.Stdout, "Response from `AppsAPI.LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**appId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiLaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **workflowAppLaunchRequest** | [**WorkflowAppLaunchRequest**](WorkflowAppLaunchRequest.md) |  |
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


## ListWorkflowAppsApiV1AppsGet

> []WorkflowApp ListWorkflowAppsApiV1AppsGet(ctx).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Workflow Apps

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
	namespace := "namespace_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AppsAPI.ListWorkflowAppsApiV1AppsGet(context.Background()).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AppsAPI.ListWorkflowAppsApiV1AppsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListWorkflowAppsApiV1AppsGet`: []WorkflowApp
	fmt.Fprintf(os.Stdout, "Response from `AppsAPI.ListWorkflowAppsApiV1AppsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListWorkflowAppsApiV1AppsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]WorkflowApp**](WorkflowApp.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpsertWorkflowAppApiV1AppsNamespaceAppIdPut

> WorkflowApp UpsertWorkflowAppApiV1AppsNamespaceAppIdPut(ctx, namespace, appId).WorkflowAppUpsertRequest(workflowAppUpsertRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Upsert Workflow App

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
	appId := "appId_example" // string |
	workflowAppUpsertRequest := *openapiclient.NewWorkflowAppUpsertRequest("FlowId_example", "Title_example") // WorkflowAppUpsertRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AppsAPI.UpsertWorkflowAppApiV1AppsNamespaceAppIdPut(context.Background(), namespace, appId).WorkflowAppUpsertRequest(workflowAppUpsertRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AppsAPI.UpsertWorkflowAppApiV1AppsNamespaceAppIdPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpsertWorkflowAppApiV1AppsNamespaceAppIdPut`: WorkflowApp
	fmt.Fprintf(os.Stdout, "Response from `AppsAPI.UpsertWorkflowAppApiV1AppsNamespaceAppIdPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**appId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUpsertWorkflowAppApiV1AppsNamespaceAppIdPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **workflowAppUpsertRequest** | [**WorkflowAppUpsertRequest**](WorkflowAppUpsertRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**WorkflowApp**](WorkflowApp.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
