# \WorkersAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DrainWorkerApiV1WorkersWorkerIdDrainPost**](WorkersAPI.md#DrainWorkerApiV1WorkersWorkerIdDrainPost) | **Post** /api/v1/workers/{worker_id}/drain | Drain Worker
[**ListRunnerCapabilitiesApiV1RunnersCapabilitiesGet**](WorkersAPI.md#ListRunnerCapabilitiesApiV1RunnersCapabilitiesGet) | **Get** /api/v1/runners/capabilities | List Runner Capabilities
[**ListWorkersApiV1WorkersGet**](WorkersAPI.md#ListWorkersApiV1WorkersGet) | **Get** /api/v1/workers | List Workers



## DrainWorkerApiV1WorkersWorkerIdDrainPost

> WorkerInventory DrainWorkerApiV1WorkersWorkerIdDrainPost(ctx, workerId).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Drain Worker

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
	workerId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	expectedVersion := int32(56) // int32 |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.WorkersAPI.DrainWorkerApiV1WorkersWorkerIdDrainPost(context.Background(), workerId).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WorkersAPI.DrainWorkerApiV1WorkersWorkerIdDrainPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DrainWorkerApiV1WorkersWorkerIdDrainPost`: WorkerInventory
	fmt.Fprintf(os.Stdout, "Response from `WorkersAPI.DrainWorkerApiV1WorkersWorkerIdDrainPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**workerId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDrainWorkerApiV1WorkersWorkerIdDrainPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **expectedVersion** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**WorkerInventory**](WorkerInventory.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListRunnerCapabilitiesApiV1RunnersCapabilitiesGet

> []RunnerCapabilities ListRunnerCapabilitiesApiV1RunnersCapabilitiesGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Runner Capabilities

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
	resp, r, err := apiClient.WorkersAPI.ListRunnerCapabilitiesApiV1RunnersCapabilitiesGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WorkersAPI.ListRunnerCapabilitiesApiV1RunnersCapabilitiesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListRunnerCapabilitiesApiV1RunnersCapabilitiesGet`: []RunnerCapabilities
	fmt.Fprintf(os.Stdout, "Response from `WorkersAPI.ListRunnerCapabilitiesApiV1RunnersCapabilitiesGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListRunnerCapabilitiesApiV1RunnersCapabilitiesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]RunnerCapabilities**](RunnerCapabilities.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListWorkersApiV1WorkersGet

> []WorkerInventory ListWorkersApiV1WorkersGet(ctx).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Workers

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
	resp, r, err := apiClient.WorkersAPI.ListWorkersApiV1WorkersGet(context.Background()).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `WorkersAPI.ListWorkersApiV1WorkersGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListWorkersApiV1WorkersGet`: []WorkerInventory
	fmt.Fprintf(os.Stdout, "Response from `WorkersAPI.ListWorkersApiV1WorkersGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListWorkersApiV1WorkersGetRequest struct via the builder pattern


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

[**[]WorkerInventory**](WorkerInventory.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
