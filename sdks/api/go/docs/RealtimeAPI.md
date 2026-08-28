# \RealtimeAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateWebhookSubscriptionApiV1WebhookSubscriptionsPost**](RealtimeAPI.md#CreateWebhookSubscriptionApiV1WebhookSubscriptionsPost) | **Post** /api/v1/webhook-subscriptions | Create Webhook Subscription
[**ListRealtimeEventsApiV1RealtimeEventsGet**](RealtimeAPI.md#ListRealtimeEventsApiV1RealtimeEventsGet) | **Get** /api/v1/realtime/events | List Realtime Events
[**ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet**](RealtimeAPI.md#ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet) | **Get** /api/v1/webhook-subscriptions/{subscription_id}/deliveries | List Webhook Delivery History
[**ListWebhookSubscriptionsApiV1WebhookSubscriptionsGet**](RealtimeAPI.md#ListWebhookSubscriptionsApiV1WebhookSubscriptionsGet) | **Get** /api/v1/webhook-subscriptions | List Webhook Subscriptions
[**ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost**](RealtimeAPI.md#ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost) | **Post** /api/v1/webhook-deliveries/{delivery_id}/replay | Replay Webhook Delivery
[**RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost**](RealtimeAPI.md#RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost) | **Post** /api/v1/webhook-subscriptions/{subscription_id}/rotate-secret | Rotate Webhook Subscription Secret
[**StreamRealtimeEventsApiV1RealtimeStreamGet**](RealtimeAPI.md#StreamRealtimeEventsApiV1RealtimeStreamGet) | **Get** /api/v1/realtime/stream | Stream Realtime Events
[**TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost**](RealtimeAPI.md#TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost) | **Post** /api/v1/webhook-subscriptions/{subscription_id}/test | Test Webhook Subscription



## CreateWebhookSubscriptionApiV1WebhookSubscriptionsPost

> ProvisionedWebhookSubscription CreateWebhookSubscriptionApiV1WebhookSubscriptionsPost(ctx).WebhookSubscriptionCreate(webhookSubscriptionCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Webhook Subscription

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
	webhookSubscriptionCreate := *openapiclient.NewWebhookSubscriptionCreate("Name_example", "Url_example") // WebhookSubscriptionCreate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.RealtimeAPI.CreateWebhookSubscriptionApiV1WebhookSubscriptionsPost(context.Background()).WebhookSubscriptionCreate(webhookSubscriptionCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `RealtimeAPI.CreateWebhookSubscriptionApiV1WebhookSubscriptionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateWebhookSubscriptionApiV1WebhookSubscriptionsPost`: ProvisionedWebhookSubscription
	fmt.Fprintf(os.Stdout, "Response from `RealtimeAPI.CreateWebhookSubscriptionApiV1WebhookSubscriptionsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateWebhookSubscriptionApiV1WebhookSubscriptionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhookSubscriptionCreate** | **WebhookSubscriptionCreate** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ProvisionedWebhookSubscription**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListRealtimeEventsApiV1RealtimeEventsGet

> RealtimeEventPage ListRealtimeEventsApiV1RealtimeEventsGet(ctx).Cursor(cursor).Namespace(namespace).FlowId(flowId).ExecutionId(executionId).EventType(eventType).Severity(severity).IncludeAudit(includeAudit).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Realtime Events

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
	cursor := "cursor_example" // string | Opaque reconnect cursor (optional)
	namespace := "namespace_example" // string |  (optional)
	flowId := "flowId_example" // string |  (optional)
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |  (optional)
	eventType := []string{"Inner_example"} // []string |  (optional)
	severity := []openapiclient.RealtimeSeverity{openapiclient.RealtimeSeverity("TRACE")} // []RealtimeSeverity |  (optional)
	includeAudit := true // bool |  (optional) (default to true)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.RealtimeAPI.ListRealtimeEventsApiV1RealtimeEventsGet(context.Background()).Cursor(cursor).Namespace(namespace).FlowId(flowId).ExecutionId(executionId).EventType(eventType).Severity(severity).IncludeAudit(includeAudit).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `RealtimeAPI.ListRealtimeEventsApiV1RealtimeEventsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListRealtimeEventsApiV1RealtimeEventsGet`: RealtimeEventPage
	fmt.Fprintf(os.Stdout, "Response from `RealtimeAPI.ListRealtimeEventsApiV1RealtimeEventsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListRealtimeEventsApiV1RealtimeEventsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **string** | Opaque reconnect cursor |
 **namespace** | **string** |  |
 **flowId** | **string** |  |
 **executionId** | **string** |  |
 **eventType** | **[]string** |  |
 **severity** | [**[]RealtimeSeverity**](RealtimeSeverity.md) |  |
 **includeAudit** | **bool** |  | [default to true]
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**RealtimeEventPage**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet

> []WebhookDeliveryHistory ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet(ctx, subscriptionId).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Webhook Delivery History

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
	subscriptionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.RealtimeAPI.ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet(context.Background(), subscriptionId).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `RealtimeAPI.ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet`: []WebhookDeliveryHistory
	fmt.Fprintf(os.Stdout, "Response from `RealtimeAPI.ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**subscriptionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]WebhookDeliveryHistory**](WebhookDeliveryHistory.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListWebhookSubscriptionsApiV1WebhookSubscriptionsGet

> []WebhookSubscription ListWebhookSubscriptionsApiV1WebhookSubscriptionsGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Webhook Subscriptions

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
	resp, r, err := apiClient.RealtimeAPI.ListWebhookSubscriptionsApiV1WebhookSubscriptionsGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `RealtimeAPI.ListWebhookSubscriptionsApiV1WebhookSubscriptionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListWebhookSubscriptionsApiV1WebhookSubscriptionsGet`: []WebhookSubscription
	fmt.Fprintf(os.Stdout, "Response from `RealtimeAPI.ListWebhookSubscriptionsApiV1WebhookSubscriptionsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListWebhookSubscriptionsApiV1WebhookSubscriptionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]WebhookSubscription**](WebhookSubscription.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost

> WebhookDelivery ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost(ctx, deliveryId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Replay Webhook Delivery

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
	deliveryId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.RealtimeAPI.ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost(context.Background(), deliveryId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `RealtimeAPI.ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost`: WebhookDelivery
	fmt.Fprintf(os.Stdout, "Response from `RealtimeAPI.ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**deliveryId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**WebhookDelivery**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost

> ProvisionedWebhookSubscription RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost(ctx, subscriptionId).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Rotate Webhook Subscription Secret

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
	subscriptionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	expectedVersion := int32(56) // int32 |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.RealtimeAPI.RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost(context.Background(), subscriptionId).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `RealtimeAPI.RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost`: ProvisionedWebhookSubscription
	fmt.Fprintf(os.Stdout, "Response from `RealtimeAPI.RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**subscriptionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **expectedVersion** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ProvisionedWebhookSubscription**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## StreamRealtimeEventsApiV1RealtimeStreamGet

> StreamRealtimeEventsApiV1RealtimeStreamGet(ctx).Cursor(cursor).Namespace(namespace).FlowId(flowId).ExecutionId(executionId).EventType(eventType).Severity(severity).IncludeAudit(includeAudit).BufferEvents(bufferEvents).MaxEvents(maxEvents).HeartbeatSeconds(heartbeatSeconds).StreamSeconds(streamSeconds).LastEventID(lastEventID).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Stream Realtime Events

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
	cursor := "cursor_example" // string | Opaque reconnect cursor (optional)
	namespace := "namespace_example" // string |  (optional)
	flowId := "flowId_example" // string |  (optional)
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |  (optional)
	eventType := []string{"Inner_example"} // []string |  (optional)
	severity := []openapiclient.RealtimeSeverity{openapiclient.RealtimeSeverity("TRACE")} // []RealtimeSeverity |  (optional)
	includeAudit := true // bool |  (optional) (default to true)
	bufferEvents := int32(56) // int32 |  (optional) (default to 100)
	maxEvents := int32(56) // int32 |  (optional) (default to 1000)
	heartbeatSeconds := float32(8.14) // float32 |  (optional) (default to 10)
	streamSeconds := float32(8.14) // float32 |  (optional) (default to 15)
	lastEventID := "lastEventID_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.RealtimeAPI.StreamRealtimeEventsApiV1RealtimeStreamGet(context.Background()).Cursor(cursor).Namespace(namespace).FlowId(flowId).ExecutionId(executionId).EventType(eventType).Severity(severity).IncludeAudit(includeAudit).BufferEvents(bufferEvents).MaxEvents(maxEvents).HeartbeatSeconds(heartbeatSeconds).StreamSeconds(streamSeconds).LastEventID(lastEventID).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `RealtimeAPI.StreamRealtimeEventsApiV1RealtimeStreamGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiStreamRealtimeEventsApiV1RealtimeStreamGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **string** | Opaque reconnect cursor |
 **namespace** | **string** |  |
 **flowId** | **string** |  |
 **executionId** | **string** |  |
 **eventType** | **[]string** |  |
 **severity** | [**[]RealtimeSeverity**](RealtimeSeverity.md) |  |
 **includeAudit** | **bool** |  | [default to true]
 **bufferEvents** | **int32** |  | [default to 100]
 **maxEvents** | **int32** |  | [default to 1000]
 **heartbeatSeconds** | **float32** |  | [default to 10]
 **streamSeconds** | **float32** |  | [default to 15]
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
- **Accept**: text/event-stream, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost

> WebhookDelivery TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost(ctx, subscriptionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Test Webhook Subscription

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
	subscriptionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.RealtimeAPI.TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost(context.Background(), subscriptionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `RealtimeAPI.TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost`: WebhookDelivery
	fmt.Fprintf(os.Stdout, "Response from `RealtimeAPI.TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**subscriptionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiTestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**WebhookDelivery**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
