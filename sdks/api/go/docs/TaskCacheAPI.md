# \TaskCacheAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ListTaskCacheEntriesApiV1TaskCacheGet**](TaskCacheAPI.md#ListTaskCacheEntriesApiV1TaskCacheGet) | **Get** /api/v1/task-cache | List Task Cache Entries
[**PurgeTaskCacheEntriesApiV1TaskCachePurgePost**](TaskCacheAPI.md#PurgeTaskCacheEntriesApiV1TaskCachePurgePost) | **Post** /api/v1/task-cache/purge | Purge Task Cache Entries



## ListTaskCacheEntriesApiV1TaskCacheGet

> []TaskCacheEntry ListTaskCacheEntriesApiV1TaskCacheGet(ctx).KeyPrefix(keyPrefix).Namespace(namespace).FlowId(flowId).TaskId(taskId).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Task Cache Entries

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
	keyPrefix := "keyPrefix_example" // string |  (optional)
	namespace := "namespace_example" // string |  (optional)
	flowId := "flowId_example" // string |  (optional)
	taskId := "taskId_example" // string |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TaskCacheAPI.ListTaskCacheEntriesApiV1TaskCacheGet(context.Background()).KeyPrefix(keyPrefix).Namespace(namespace).FlowId(flowId).TaskId(taskId).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TaskCacheAPI.ListTaskCacheEntriesApiV1TaskCacheGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListTaskCacheEntriesApiV1TaskCacheGet`: []TaskCacheEntry
	fmt.Fprintf(os.Stdout, "Response from `TaskCacheAPI.ListTaskCacheEntriesApiV1TaskCacheGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListTaskCacheEntriesApiV1TaskCacheGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **keyPrefix** | **string** |  |
 **namespace** | **string** |  |
 **flowId** | **string** |  |
 **taskId** | **string** |  |
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]TaskCacheEntry**](TaskCacheEntry.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PurgeTaskCacheEntriesApiV1TaskCachePurgePost

> TaskCachePurgeResult PurgeTaskCacheEntriesApiV1TaskCachePurgePost(ctx).TaskCachePurgeRequest(taskCachePurgeRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Purge Task Cache Entries

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
	taskCachePurgeRequest := *openapiclient.NewTaskCachePurgeRequest("Reason_example") // TaskCachePurgeRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TaskCacheAPI.PurgeTaskCacheEntriesApiV1TaskCachePurgePost(context.Background()).TaskCachePurgeRequest(taskCachePurgeRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TaskCacheAPI.PurgeTaskCacheEntriesApiV1TaskCachePurgePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PurgeTaskCacheEntriesApiV1TaskCachePurgePost`: TaskCachePurgeResult
	fmt.Fprintf(os.Stdout, "Response from `TaskCacheAPI.PurgeTaskCacheEntriesApiV1TaskCachePurgePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPurgeTaskCacheEntriesApiV1TaskCachePurgePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **taskCachePurgeRequest** | [**TaskCachePurgeRequest**](TaskCachePurgeRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**TaskCachePurgeResult**](TaskCachePurgeResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
