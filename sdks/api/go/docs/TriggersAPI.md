# \TriggersAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ListTriggerOccurrencesApiV1TriggerOccurrencesGet**](TriggersAPI.md#ListTriggerOccurrencesApiV1TriggerOccurrencesGet) | **Get** /api/v1/trigger-occurrences | List Trigger Occurrences
[**ListTriggerRuntimeStatesApiV1TriggersGet**](TriggersAPI.md#ListTriggerRuntimeStatesApiV1TriggersGet) | **Get** /api/v1/triggers | List Trigger Runtime States
[**PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost**](TriggersAPI.md#PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost) | **Post** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/pause | Pause Trigger Runtime
[**PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet**](TriggersAPI.md#PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet) | **Get** /api/v1/flows/{namespace}/{flow_id}/schedules/{trigger_id}/preview | Preview Schedule
[**ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost**](TriggersAPI.md#ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost) | **Post** /api/v1/trigger-occurrences/{occurrence_id}/replay | Replay Trigger Occurrence
[**ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost**](TriggersAPI.md#ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost) | **Post** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/resume | Resume Trigger Runtime
[**TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost**](TriggersAPI.md#TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost) | **Post** /api/v1/webhooks/{namespace}/{flow_id}/{trigger_id} | Trigger Webhook



## ListTriggerOccurrencesApiV1TriggerOccurrencesGet

> []TriggerOccurrence ListTriggerOccurrencesApiV1TriggerOccurrencesGet(ctx).Namespace(namespace).FlowId(flowId).TriggerId(triggerId).State(state).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Trigger Occurrences

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
	flowId := "flowId_example" // string |  (optional)
	triggerId := "triggerId_example" // string |  (optional)
	state := openapiclient.TriggerOccurrenceState("ACCEPTED") // TriggerOccurrenceState |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TriggersAPI.ListTriggerOccurrencesApiV1TriggerOccurrencesGet(context.Background()).Namespace(namespace).FlowId(flowId).TriggerId(triggerId).State(state).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TriggersAPI.ListTriggerOccurrencesApiV1TriggerOccurrencesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListTriggerOccurrencesApiV1TriggerOccurrencesGet`: []TriggerOccurrence
	fmt.Fprintf(os.Stdout, "Response from `TriggersAPI.ListTriggerOccurrencesApiV1TriggerOccurrencesGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListTriggerOccurrencesApiV1TriggerOccurrencesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **flowId** | **string** |  |
 **triggerId** | **string** |  |
 **state** | **TriggerOccurrenceState** |  |
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]TriggerOccurrence**](TriggerOccurrence.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListTriggerRuntimeStatesApiV1TriggersGet

> []TriggerRuntimeState ListTriggerRuntimeStatesApiV1TriggersGet(ctx).Namespace(namespace).FlowId(flowId).TriggerId(triggerId).Active(active).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Trigger Runtime States

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
	flowId := "flowId_example" // string |  (optional)
	triggerId := "triggerId_example" // string |  (optional)
	active := true // bool |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TriggersAPI.ListTriggerRuntimeStatesApiV1TriggersGet(context.Background()).Namespace(namespace).FlowId(flowId).TriggerId(triggerId).Active(active).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TriggersAPI.ListTriggerRuntimeStatesApiV1TriggersGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListTriggerRuntimeStatesApiV1TriggersGet`: []TriggerRuntimeState
	fmt.Fprintf(os.Stdout, "Response from `TriggersAPI.ListTriggerRuntimeStatesApiV1TriggersGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListTriggerRuntimeStatesApiV1TriggersGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **flowId** | **string** |  |
 **triggerId** | **string** |  |
 **active** | **bool** |  |
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]TriggerRuntimeState**](TriggerRuntimeState.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost

> TriggerRuntimeState PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost(ctx, namespace, flowId, triggerId).TriggerActionRequest(triggerActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Pause Trigger Runtime

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
	triggerId := "triggerId_example" // string |
	triggerActionRequest := *openapiclient.NewTriggerActionRequest("Reason_example") // TriggerActionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TriggersAPI.PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost(context.Background(), namespace, flowId, triggerId).TriggerActionRequest(triggerActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TriggersAPI.PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost`: TriggerRuntimeState
	fmt.Fprintf(os.Stdout, "Response from `TriggersAPI.PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**triggerId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **triggerActionRequest** | **TriggerActionRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**TriggerRuntimeState**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet

> SchedulePreview PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet(ctx, namespace, flowId, triggerId).After(after).Count(count).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Preview Schedule

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
    "time"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	flowId := "flowId_example" // string |
	triggerId := "triggerId_example" // string |
	after := time.Now() // time.Time |  (optional)
	count := int32(56) // int32 |  (optional) (default to 5)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TriggersAPI.PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet(context.Background(), namespace, flowId, triggerId).After(after).Count(count).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TriggersAPI.PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet`: SchedulePreview
	fmt.Fprintf(os.Stdout, "Response from `TriggersAPI.PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**triggerId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **after** | **time.Time** |  |
 **count** | **int32** |  | [default to 5]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**SchedulePreview**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost

> TriggerOccurrence ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost(ctx, occurrenceId).TriggerActionRequest(triggerActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Replay Trigger Occurrence

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
	occurrenceId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	triggerActionRequest := *openapiclient.NewTriggerActionRequest("Reason_example") // TriggerActionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TriggersAPI.ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost(context.Background(), occurrenceId).TriggerActionRequest(triggerActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TriggersAPI.ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost`: TriggerOccurrence
	fmt.Fprintf(os.Stdout, "Response from `TriggersAPI.ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**occurrenceId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **triggerActionRequest** | **TriggerActionRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**TriggerOccurrence**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost

> TriggerRuntimeState ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost(ctx, namespace, flowId, triggerId).TriggerActionRequest(triggerActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Resume Trigger Runtime

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
	triggerId := "triggerId_example" // string |
	triggerActionRequest := *openapiclient.NewTriggerActionRequest("Reason_example") // TriggerActionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TriggersAPI.ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost(context.Background(), namespace, flowId, triggerId).TriggerActionRequest(triggerActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TriggersAPI.ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost`: TriggerRuntimeState
	fmt.Fprintf(os.Stdout, "Response from `TriggersAPI.ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**triggerId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **triggerActionRequest** | **TriggerActionRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**TriggerRuntimeState**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost

> ExecutionDetail TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost(ctx, namespace, flowId, triggerId).Runner(runner).Prefer(prefer).IdempotencyKey(idempotencyKey).XEventId(xEventId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Trigger Webhook

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
	triggerId := "triggerId_example" // string |
	runner := openapiclient.RunnerMode("local") // RunnerMode |  (optional) (default to "local")
	prefer := "prefer_example" // string |  (optional)
	idempotencyKey := "idempotencyKey_example" // string |  (optional)
	xEventId := "xEventId_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TriggersAPI.TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost(context.Background(), namespace, flowId, triggerId).Runner(runner).Prefer(prefer).IdempotencyKey(idempotencyKey).XEventId(xEventId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TriggersAPI.TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost`: ExecutionDetail
	fmt.Fprintf(os.Stdout, "Response from `TriggersAPI.TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**triggerId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiTriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **runner** | **RunnerMode** |  | [default to &quot;local&quot;]
 **prefer** | **string** |  |
 **idempotencyKey** | **string** |  |
 **xEventId** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ExecutionDetail**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
