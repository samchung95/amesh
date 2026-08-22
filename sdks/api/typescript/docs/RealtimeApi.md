# RealtimeApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createWebhookSubscriptionApiV1WebhookSubscriptionsPost**](RealtimeApi.md#createwebhooksubscriptionapiv1webhooksubscriptionspost) | **POST** /api/v1/webhook-subscriptions | Create Webhook Subscription |
| [**listRealtimeEventsApiV1RealtimeEventsGet**](RealtimeApi.md#listrealtimeeventsapiv1realtimeeventsget) | **GET** /api/v1/realtime/events | List Realtime Events |
| [**listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet**](RealtimeApi.md#listwebhookdeliveryhistoryapiv1webhooksubscriptionssubscriptioniddeliveriesget) | **GET** /api/v1/webhook-subscriptions/{subscription_id}/deliveries | List Webhook Delivery History |
| [**listWebhookSubscriptionsApiV1WebhookSubscriptionsGet**](RealtimeApi.md#listwebhooksubscriptionsapiv1webhooksubscriptionsget) | **GET** /api/v1/webhook-subscriptions | List Webhook Subscriptions |
| [**replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost**](RealtimeApi.md#replaywebhookdeliveryapiv1webhookdeliveriesdeliveryidreplaypost) | **POST** /api/v1/webhook-deliveries/{delivery_id}/replay | Replay Webhook Delivery |
| [**rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost**](RealtimeApi.md#rotatewebhooksubscriptionsecretapiv1webhooksubscriptionssubscriptionidrotatesecretpost) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/rotate-secret | Rotate Webhook Subscription Secret |
| [**streamRealtimeEventsApiV1RealtimeStreamGet**](RealtimeApi.md#streamrealtimeeventsapiv1realtimestreamget) | **GET** /api/v1/realtime/stream | Stream Realtime Events |
| [**testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost**](RealtimeApi.md#testwebhooksubscriptionapiv1webhooksubscriptionssubscriptionidtestpost) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/test | Test Webhook Subscription |



## createWebhookSubscriptionApiV1WebhookSubscriptionsPost

> ProvisionedWebhookSubscription createWebhookSubscriptionApiV1WebhookSubscriptionsPost(webhookSubscriptionCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Webhook Subscription

### Example

```ts
import {
  Configuration,
  RealtimeApi,
} from '@amesh/client';
import type { CreateWebhookSubscriptionApiV1WebhookSubscriptionsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new RealtimeApi();

  const body = {
    // WebhookSubscriptionCreate
    webhookSubscriptionCreate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateWebhookSubscriptionApiV1WebhookSubscriptionsPostRequest;

  try {
    const data = await api.createWebhookSubscriptionApiV1WebhookSubscriptionsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **webhookSubscriptionCreate** | [WebhookSubscriptionCreate](WebhookSubscriptionCreate.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ProvisionedWebhookSubscription**](ProvisionedWebhookSubscription.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listRealtimeEventsApiV1RealtimeEventsGet

> RealtimeEventPage listRealtimeEventsApiV1RealtimeEventsGet(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Realtime Events

### Example

```ts
import {
  Configuration,
  RealtimeApi,
} from '@amesh/client';
import type { ListRealtimeEventsApiV1RealtimeEventsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new RealtimeApi();

  const body = {
    // string | Opaque reconnect cursor (optional)
    cursor: cursor_example,
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    flowId: flowId_example,
    // string (optional)
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // Array<string> (optional)
    eventType: ...,
    // Array<RealtimeSeverity> (optional)
    severity: ...,
    // boolean (optional)
    includeAudit: true,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListRealtimeEventsApiV1RealtimeEventsGetRequest;

  try {
    const data = await api.listRealtimeEventsApiV1RealtimeEventsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cursor** | `string` | Opaque reconnect cursor | [Optional] [Defaults to `undefined`] |
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **flowId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **executionId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **eventType** | `Array<string>` |  | [Optional] |
| **severity** | `Array<RealtimeSeverity>` |  | [Optional] |
| **includeAudit** | `boolean` |  | [Optional] [Defaults to `true`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**RealtimeEventPage**](RealtimeEventPage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet

> Array&lt;WebhookDeliveryHistory&gt; listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet(subscriptionId, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Webhook Delivery History

### Example

```ts
import {
  Configuration,
  RealtimeApi,
} from '@amesh/client';
import type { ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new RealtimeApi();

  const body = {
    // string
    subscriptionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGetRequest;

  try {
    const data = await api.listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subscriptionId** | `string` |  | [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;WebhookDeliveryHistory&gt;**](WebhookDeliveryHistory.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listWebhookSubscriptionsApiV1WebhookSubscriptionsGet

> Array&lt;WebhookSubscription&gt; listWebhookSubscriptionsApiV1WebhookSubscriptionsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Webhook Subscriptions

### Example

```ts
import {
  Configuration,
  RealtimeApi,
} from '@amesh/client';
import type { ListWebhookSubscriptionsApiV1WebhookSubscriptionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new RealtimeApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListWebhookSubscriptionsApiV1WebhookSubscriptionsGetRequest;

  try {
    const data = await api.listWebhookSubscriptionsApiV1WebhookSubscriptionsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;WebhookSubscription&gt;**](WebhookSubscription.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost

> WebhookDelivery replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost(deliveryId, authorization, xAmeshCSRF, xAmeshTenant)

Replay Webhook Delivery

### Example

```ts
import {
  Configuration,
  RealtimeApi,
} from '@amesh/client';
import type { ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new RealtimeApi();

  const body = {
    // string
    deliveryId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ReplayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPostRequest;

  try {
    const data = await api.replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **deliveryId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**WebhookDelivery**](WebhookDelivery.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost

> ProvisionedWebhookSubscription rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost(subscriptionId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Rotate Webhook Subscription Secret

### Example

```ts
import {
  Configuration,
  RealtimeApi,
} from '@amesh/client';
import type { RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new RealtimeApi();

  const body = {
    // string
    subscriptionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies RotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPostRequest;

  try {
    const data = await api.rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subscriptionId** | `string` |  | [Defaults to `undefined`] |
| **expectedVersion** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ProvisionedWebhookSubscription**](ProvisionedWebhookSubscription.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## streamRealtimeEventsApiV1RealtimeStreamGet

> streamRealtimeEventsApiV1RealtimeStreamGet(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, bufferEvents, maxEvents, heartbeatSeconds, streamSeconds, lastEventID, authorization, xAmeshCSRF, xAmeshTenant)

Stream Realtime Events

### Example

```ts
import {
  Configuration,
  RealtimeApi,
} from '@amesh/client';
import type { StreamRealtimeEventsApiV1RealtimeStreamGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new RealtimeApi();

  const body = {
    // string | Opaque reconnect cursor (optional)
    cursor: cursor_example,
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    flowId: flowId_example,
    // string (optional)
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // Array<string> (optional)
    eventType: ...,
    // Array<RealtimeSeverity> (optional)
    severity: ...,
    // boolean (optional)
    includeAudit: true,
    // number (optional)
    bufferEvents: 56,
    // number (optional)
    maxEvents: 56,
    // number (optional)
    heartbeatSeconds: 8.14,
    // number (optional)
    streamSeconds: 8.14,
    // string (optional)
    lastEventID: lastEventID_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies StreamRealtimeEventsApiV1RealtimeStreamGetRequest;

  try {
    const data = await api.streamRealtimeEventsApiV1RealtimeStreamGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cursor** | `string` | Opaque reconnect cursor | [Optional] [Defaults to `undefined`] |
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **flowId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **executionId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **eventType** | `Array<string>` |  | [Optional] |
| **severity** | `Array<RealtimeSeverity>` |  | [Optional] |
| **includeAudit** | `boolean` |  | [Optional] [Defaults to `true`] |
| **bufferEvents** | `number` |  | [Optional] [Defaults to `100`] |
| **maxEvents** | `number` |  | [Optional] [Defaults to `1000`] |
| **heartbeatSeconds** | `number` |  | [Optional] [Defaults to `10`] |
| **streamSeconds** | `number` |  | [Optional] [Defaults to `15`] |
| **lastEventID** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `text/event-stream`, `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Cursor-resumable server-sent event stream |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost

> WebhookDelivery testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost(subscriptionId, authorization, xAmeshCSRF, xAmeshTenant)

Test Webhook Subscription

### Example

```ts
import {
  Configuration,
  RealtimeApi,
} from '@amesh/client';
import type { TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new RealtimeApi();

  const body = {
    // string
    subscriptionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies TestWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPostRequest;

  try {
    const data = await api.testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subscriptionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**WebhookDelivery**](WebhookDelivery.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
