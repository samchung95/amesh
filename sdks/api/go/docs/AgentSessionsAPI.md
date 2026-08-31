# \AgentSessionsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost**](AgentSessionsAPI.md#ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost) | **Post** /api/v1/agent-sessions/{service_session_id}/{action} | Control Agent Session
[**CreateAgentSessionApiV1AgentSessionsPost**](AgentSessionsAPI.md#CreateAgentSessionApiV1AgentSessionsPost) | **Post** /api/v1/agent-sessions | Create Agent Session
[**GetAgentSessionApiV1AgentSessionsServiceSessionIdGet**](AgentSessionsAPI.md#GetAgentSessionApiV1AgentSessionsServiceSessionIdGet) | **Get** /api/v1/agent-sessions/{service_session_id} | Get Agent Session
[**GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet**](AgentSessionsAPI.md#GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet) | **Get** /api/v1/agent-sessions/{service_session_id}/events | Get Agent Session Events
[**GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet**](AgentSessionsAPI.md#GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet) | **Get** /api/v1/agent-sessions/{service_session_id}/messages | Get Agent Session Messages
[**GetAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet**](AgentSessionsAPI.md#GetAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet) | **Get** /api/v1/agent-sessions/{service_session_id}/progress | Get Agent Session Progress
[**GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet**](AgentSessionsAPI.md#GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet) | **Get** /api/v1/agent-sessions/{service_session_id}/result | Get Agent Session Result
[**ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGet**](AgentSessionsAPI.md#ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGet) | **Get** /api/v1/agent-sessions/harnesses | List Agent Session Harnesses
[**ListAgentSessionsApiV1AgentSessionsGet**](AgentSessionsAPI.md#ListAgentSessionsApiV1AgentSessionsGet) | **Get** /api/v1/agent-sessions | List Agent Sessions
[**OpenaiChatCompletionsV1ChatCompletionsPost**](AgentSessionsAPI.md#OpenaiChatCompletionsV1ChatCompletionsPost) | **Post** /v1/chat/completions | Openai Chat Completions
[**OpenaiResponsesV1ResponsesPost**](AgentSessionsAPI.md#OpenaiResponsesV1ResponsesPost) | **Post** /v1/responses | Openai Responses
[**PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost**](AgentSessionsAPI.md#PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost) | **Post** /api/v1/agent-sessions/{service_session_id}/messages | Post Agent Session Message
[**StreamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet**](AgentSessionsAPI.md#StreamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet) | **Get** /api/v1/agent-sessions/{service_session_id}/events/stream | Stream Agent Session Events
[**StreamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet**](AgentSessionsAPI.md#StreamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet) | **Get** /api/v1/agent-sessions/{service_session_id}/progress/stream | Stream Agent Session Progress



## ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost

> AgentSessionLaunchResponse ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost(ctx, serviceSessionId, action).AgentSessionControlRequest(agentSessionControlRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Control Agent Session

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
	serviceSessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	action := "action_example" // string |
	agentSessionControlRequest := *openapiclient.NewAgentSessionControlRequest() // AgentSessionControlRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost(context.Background(), serviceSessionId, action).AgentSessionControlRequest(agentSessionControlRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost`: AgentSessionLaunchResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**serviceSessionId** | **string** |  |
**action** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **agentSessionControlRequest** | **AgentSessionControlRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionLaunchResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateAgentSessionApiV1AgentSessionsPost

> AgentSessionLaunchResponse CreateAgentSessionApiV1AgentSessionsPost(ctx).AgentSessionCreateRequest(agentSessionCreateRequest).Prefer(prefer).IdempotencyKey(idempotencyKey).XCorrelationID(xCorrelationID).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Agent Session

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
	agentSessionCreateRequest := *openapiclient.NewAgentSessionCreateRequest() // AgentSessionCreateRequest |
	prefer := "prefer_example" // string |  (optional)
	idempotencyKey := "idempotencyKey_example" // string |  (optional)
	xCorrelationID := "xCorrelationID_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.CreateAgentSessionApiV1AgentSessionsPost(context.Background()).AgentSessionCreateRequest(agentSessionCreateRequest).Prefer(prefer).IdempotencyKey(idempotencyKey).XCorrelationID(xCorrelationID).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.CreateAgentSessionApiV1AgentSessionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateAgentSessionApiV1AgentSessionsPost`: AgentSessionLaunchResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.CreateAgentSessionApiV1AgentSessionsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateAgentSessionApiV1AgentSessionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentSessionCreateRequest** | **AgentSessionCreateRequest** |  |
 **prefer** | **string** |  |
 **idempotencyKey** | **string** |  |
 **xCorrelationID** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionLaunchResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgentSessionApiV1AgentSessionsServiceSessionIdGet

> AgentSessionServiceDetailResponse GetAgentSessionApiV1AgentSessionsServiceSessionIdGet(ctx, serviceSessionId).AfterEventIndex(afterEventIndex).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Agent Session

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
	serviceSessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	afterEventIndex := int32(56) // int32 |  (optional) (default to 0)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.GetAgentSessionApiV1AgentSessionsServiceSessionIdGet(context.Background(), serviceSessionId).AfterEventIndex(afterEventIndex).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.GetAgentSessionApiV1AgentSessionsServiceSessionIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgentSessionApiV1AgentSessionsServiceSessionIdGet`: AgentSessionServiceDetailResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.GetAgentSessionApiV1AgentSessionsServiceSessionIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**serviceSessionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgentSessionApiV1AgentSessionsServiceSessionIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **afterEventIndex** | **int32** |  | [default to 0]
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionServiceDetailResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet

> AgentSessionServiceDetailResponse GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet(ctx, serviceSessionId).AfterEventIndex(afterEventIndex).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Agent Session Events

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
	serviceSessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	afterEventIndex := int32(56) // int32 |  (optional) (default to 0)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet(context.Background(), serviceSessionId).AfterEventIndex(afterEventIndex).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet`: AgentSessionServiceDetailResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**serviceSessionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **afterEventIndex** | **int32** |  | [default to 0]
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionServiceDetailResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet

> AgentSessionServiceDetailResponse GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet(ctx, serviceSessionId).AfterEventIndex(afterEventIndex).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Agent Session Messages

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
	serviceSessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	afterEventIndex := int32(56) // int32 |  (optional) (default to 0)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet(context.Background(), serviceSessionId).AfterEventIndex(afterEventIndex).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet`: AgentSessionServiceDetailResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**serviceSessionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **afterEventIndex** | **int32** |  | [default to 0]
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionServiceDetailResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet

> AgentProgressPage GetAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet(ctx, serviceSessionId).After(after).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Agent Session Progress



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
	serviceSessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	after := "after_example" // string |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.GetAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet(context.Background(), serviceSessionId).After(after).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.GetAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet`: AgentProgressPage
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.GetAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**serviceSessionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **after** | **string** |  |
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentProgressPage**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet

> AgentSessionResultResponse GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet(ctx, serviceSessionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Agent Session Result

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
	serviceSessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet(context.Background(), serviceSessionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet`: AgentSessionResultResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**serviceSessionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionResultResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGet

> map[string]AgentSessionHarnessCatalogEntry ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Agent Session Harnesses



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
	resp, r, err := apiClient.AgentSessionsAPI.ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGet`: map[string]AgentSessionHarnessCatalogEntry
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAgentSessionHarnessesApiV1AgentSessionsHarnessesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**map[string]AgentSessionHarnessCatalogEntry**](AgentSessionHarnessCatalogEntry.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAgentSessionsApiV1AgentSessionsGet

> []AgentSessionServiceItem ListAgentSessionsApiV1AgentSessionsGet(ctx).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Agent Sessions

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
	resp, r, err := apiClient.AgentSessionsAPI.ListAgentSessionsApiV1AgentSessionsGet(context.Background()).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.ListAgentSessionsApiV1AgentSessionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAgentSessionsApiV1AgentSessionsGet`: []AgentSessionServiceItem
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.ListAgentSessionsApiV1AgentSessionsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAgentSessionsApiV1AgentSessionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]AgentSessionServiceItem**](AgentSessionServiceItem.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## OpenaiChatCompletionsV1ChatCompletionsPost

> OpenAIChatCompletionResponse OpenaiChatCompletionsV1ChatCompletionsPost(ctx).OpenAIChatCompletionRequest(openAIChatCompletionRequest).IdempotencyKey(idempotencyKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Openai Chat Completions

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
	openAIChatCompletionRequest := *openapiclient.NewOpenAIChatCompletionRequest([]*map[string]interface{}{nil}, "Model_example") // OpenAIChatCompletionRequest |
	idempotencyKey := "idempotencyKey_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.OpenaiChatCompletionsV1ChatCompletionsPost(context.Background()).OpenAIChatCompletionRequest(openAIChatCompletionRequest).IdempotencyKey(idempotencyKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.OpenaiChatCompletionsV1ChatCompletionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `OpenaiChatCompletionsV1ChatCompletionsPost`: OpenAIChatCompletionResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.OpenaiChatCompletionsV1ChatCompletionsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiOpenaiChatCompletionsV1ChatCompletionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **openAIChatCompletionRequest** | **OpenAIChatCompletionRequest** |  |
 **idempotencyKey** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**OpenAIChatCompletionResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## OpenaiResponsesV1ResponsesPost

> OpenAIResponse OpenaiResponsesV1ResponsesPost(ctx).OpenAIResponseRequest(openAIResponseRequest).IdempotencyKey(idempotencyKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Openai Responses

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
	openAIResponseRequest := *openapiclient.NewOpenAIResponseRequest(*openapiclient.NewInput(), "Model_example") // OpenAIResponseRequest |
	idempotencyKey := "idempotencyKey_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.OpenaiResponsesV1ResponsesPost(context.Background()).OpenAIResponseRequest(openAIResponseRequest).IdempotencyKey(idempotencyKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.OpenaiResponsesV1ResponsesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `OpenaiResponsesV1ResponsesPost`: OpenAIResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.OpenaiResponsesV1ResponsesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiOpenaiResponsesV1ResponsesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **openAIResponseRequest** | **OpenAIResponseRequest** |  |
 **idempotencyKey** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**OpenAIResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost

> AgentSessionLaunchResponse PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost(ctx, serviceSessionId).AgentSessionMessageRequest(agentSessionMessageRequest).Prefer(prefer).IdempotencyKey(idempotencyKey).XCorrelationID(xCorrelationID).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Post Agent Session Message



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
	serviceSessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	agentSessionMessageRequest := *openapiclient.NewAgentSessionMessageRequest() // AgentSessionMessageRequest |
	prefer := "prefer_example" // string |  (optional)
	idempotencyKey := "idempotencyKey_example" // string |  (optional)
	xCorrelationID := "xCorrelationID_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionsAPI.PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost(context.Background(), serviceSessionId).AgentSessionMessageRequest(agentSessionMessageRequest).Prefer(prefer).IdempotencyKey(idempotencyKey).XCorrelationID(xCorrelationID).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost`: AgentSessionLaunchResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionsAPI.PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**serviceSessionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **agentSessionMessageRequest** | **AgentSessionMessageRequest** |  |
 **prefer** | **string** |  |
 **idempotencyKey** | **string** |  |
 **xCorrelationID** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionLaunchResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## StreamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet

> StreamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet(ctx, serviceSessionId).AfterEventIndex(afterEventIndex).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Stream Agent Session Events



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
	serviceSessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	afterEventIndex := int32(56) // int32 |  (optional) (default to 0)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.AgentSessionsAPI.StreamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet(context.Background(), serviceSessionId).AfterEventIndex(afterEventIndex).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.StreamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**serviceSessionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiStreamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **afterEventIndex** | **int32** |  | [default to 0]
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


## StreamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet

> StreamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet(ctx, serviceSessionId).After(after).LastEventID(lastEventID).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Stream Agent Session Progress



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
	serviceSessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	after := "after_example" // string |  (optional)
	lastEventID := "lastEventID_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.AgentSessionsAPI.StreamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet(context.Background(), serviceSessionId).After(after).LastEventID(lastEventID).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionsAPI.StreamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**serviceSessionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiStreamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **after** | **string** |  |
 **lastEventID** | **string** |  |
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
