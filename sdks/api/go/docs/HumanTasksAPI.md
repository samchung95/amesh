# \HumanTasksAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost**](HumanTasksAPI.md#ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost) | **Post** /api/v1/human-tasks/{human_task_id}/actions | Act On Human Task
[**ListHumanTaskNotificationsApiV1HumanTaskNotificationsGet**](HumanTasksAPI.md#ListHumanTaskNotificationsApiV1HumanTaskNotificationsGet) | **Get** /api/v1/human-task-notifications | List Human Task Notifications
[**ListHumanTasksApiV1HumanTasksGet**](HumanTasksAPI.md#ListHumanTasksApiV1HumanTasksGet) | **Get** /api/v1/human-tasks | List Human Tasks



## ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost

> HumanTask ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost(ctx, humanTaskId).HumanTaskActionRequest(humanTaskActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Act On Human Task

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
	humanTaskId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	humanTaskActionRequest := *openapiclient.NewHumanTaskActionRequest(openapiclient.HumanTaskActionKind("APPROVE"), "IdempotencyKey_example") // HumanTaskActionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.HumanTasksAPI.ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost(context.Background(), humanTaskId).HumanTaskActionRequest(humanTaskActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `HumanTasksAPI.ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost`: HumanTask
	fmt.Fprintf(os.Stdout, "Response from `HumanTasksAPI.ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**humanTaskId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **humanTaskActionRequest** | **HumanTaskActionRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**HumanTask**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListHumanTaskNotificationsApiV1HumanTaskNotificationsGet

> []HumanTaskNotification ListHumanTaskNotificationsApiV1HumanTaskNotificationsGet(ctx).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Human Task Notifications

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
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.HumanTasksAPI.ListHumanTaskNotificationsApiV1HumanTaskNotificationsGet(context.Background()).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `HumanTasksAPI.ListHumanTaskNotificationsApiV1HumanTaskNotificationsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListHumanTaskNotificationsApiV1HumanTaskNotificationsGet`: []HumanTaskNotification
	fmt.Fprintf(os.Stdout, "Response from `HumanTasksAPI.ListHumanTaskNotificationsApiV1HumanTaskNotificationsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListHumanTaskNotificationsApiV1HumanTaskNotificationsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]HumanTaskNotification**](HumanTaskNotification.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListHumanTasksApiV1HumanTasksGet

> []HumanTask ListHumanTasksApiV1HumanTasksGet(ctx).Namespace(namespace).IncludeClosed(includeClosed).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Human Tasks

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
	includeClosed := true // bool |  (optional) (default to false)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.HumanTasksAPI.ListHumanTasksApiV1HumanTasksGet(context.Background()).Namespace(namespace).IncludeClosed(includeClosed).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `HumanTasksAPI.ListHumanTasksApiV1HumanTasksGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListHumanTasksApiV1HumanTasksGet`: []HumanTask
	fmt.Fprintf(os.Stdout, "Response from `HumanTasksAPI.ListHumanTasksApiV1HumanTasksGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListHumanTasksApiV1HumanTasksGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **includeClosed** | **bool** |  | [default to false]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]HumanTask**](HumanTask.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
