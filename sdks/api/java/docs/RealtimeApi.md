# RealtimeApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createWebhookSubscriptionApiV1WebhookSubscriptionsPost**](RealtimeApi.md#createWebhookSubscriptionApiV1WebhookSubscriptionsPost) | **POST** /api/v1/webhook-subscriptions | Create Webhook Subscription |
| [**createWebhookSubscriptionApiV1WebhookSubscriptionsPostWithHttpInfo**](RealtimeApi.md#createWebhookSubscriptionApiV1WebhookSubscriptionsPostWithHttpInfo) | **POST** /api/v1/webhook-subscriptions | Create Webhook Subscription |
| [**listRealtimeEventsApiV1RealtimeEventsGet**](RealtimeApi.md#listRealtimeEventsApiV1RealtimeEventsGet) | **GET** /api/v1/realtime/events | List Realtime Events |
| [**listRealtimeEventsApiV1RealtimeEventsGetWithHttpInfo**](RealtimeApi.md#listRealtimeEventsApiV1RealtimeEventsGetWithHttpInfo) | **GET** /api/v1/realtime/events | List Realtime Events |
| [**listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet**](RealtimeApi.md#listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet) | **GET** /api/v1/webhook-subscriptions/{subscription_id}/deliveries | List Webhook Delivery History |
| [**listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGetWithHttpInfo**](RealtimeApi.md#listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGetWithHttpInfo) | **GET** /api/v1/webhook-subscriptions/{subscription_id}/deliveries | List Webhook Delivery History |
| [**listWebhookSubscriptionsApiV1WebhookSubscriptionsGet**](RealtimeApi.md#listWebhookSubscriptionsApiV1WebhookSubscriptionsGet) | **GET** /api/v1/webhook-subscriptions | List Webhook Subscriptions |
| [**listWebhookSubscriptionsApiV1WebhookSubscriptionsGetWithHttpInfo**](RealtimeApi.md#listWebhookSubscriptionsApiV1WebhookSubscriptionsGetWithHttpInfo) | **GET** /api/v1/webhook-subscriptions | List Webhook Subscriptions |
| [**replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost**](RealtimeApi.md#replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost) | **POST** /api/v1/webhook-deliveries/{delivery_id}/replay | Replay Webhook Delivery |
| [**replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPostWithHttpInfo**](RealtimeApi.md#replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPostWithHttpInfo) | **POST** /api/v1/webhook-deliveries/{delivery_id}/replay | Replay Webhook Delivery |
| [**rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost**](RealtimeApi.md#rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/rotate-secret | Rotate Webhook Subscription Secret |
| [**rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPostWithHttpInfo**](RealtimeApi.md#rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPostWithHttpInfo) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/rotate-secret | Rotate Webhook Subscription Secret |
| [**streamRealtimeEventsApiV1RealtimeStreamGet**](RealtimeApi.md#streamRealtimeEventsApiV1RealtimeStreamGet) | **GET** /api/v1/realtime/stream | Stream Realtime Events |
| [**streamRealtimeEventsApiV1RealtimeStreamGetWithHttpInfo**](RealtimeApi.md#streamRealtimeEventsApiV1RealtimeStreamGetWithHttpInfo) | **GET** /api/v1/realtime/stream | Stream Realtime Events |
| [**testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost**](RealtimeApi.md#testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/test | Test Webhook Subscription |
| [**testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPostWithHttpInfo**](RealtimeApi.md#testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPostWithHttpInfo) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/test | Test Webhook Subscription |



## createWebhookSubscriptionApiV1WebhookSubscriptionsPost

> ProvisionedWebhookSubscription createWebhookSubscriptionApiV1WebhookSubscriptionsPost(webhookSubscriptionCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Webhook Subscription

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        WebhookSubscriptionCreate webhookSubscriptionCreate = new WebhookSubscriptionCreate(); // WebhookSubscriptionCreate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ProvisionedWebhookSubscription result = apiInstance.createWebhookSubscriptionApiV1WebhookSubscriptionsPost(webhookSubscriptionCreate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#createWebhookSubscriptionApiV1WebhookSubscriptionsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **webhookSubscriptionCreate** | [**WebhookSubscriptionCreate**](WebhookSubscriptionCreate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ProvisionedWebhookSubscription**](ProvisionedWebhookSubscription.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createWebhookSubscriptionApiV1WebhookSubscriptionsPostWithHttpInfo

> ApiResponse<ProvisionedWebhookSubscription> createWebhookSubscriptionApiV1WebhookSubscriptionsPostWithHttpInfo(webhookSubscriptionCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Webhook Subscription

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        WebhookSubscriptionCreate webhookSubscriptionCreate = new WebhookSubscriptionCreate(); // WebhookSubscriptionCreate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ProvisionedWebhookSubscription> response = apiInstance.createWebhookSubscriptionApiV1WebhookSubscriptionsPostWithHttpInfo(webhookSubscriptionCreate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#createWebhookSubscriptionApiV1WebhookSubscriptionsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **webhookSubscriptionCreate** | [**WebhookSubscriptionCreate**](WebhookSubscriptionCreate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ProvisionedWebhookSubscription**](ProvisionedWebhookSubscription.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listRealtimeEventsApiV1RealtimeEventsGet

> RealtimeEventPage listRealtimeEventsApiV1RealtimeEventsGet(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Realtime Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque reconnect cursor
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        UUID executionId = UUID.randomUUID(); // UUID |
        List<String> eventType = Arrays.asList(); // List<String> |
        List<RealtimeSeverity> severity = Arrays.asList(); // List<RealtimeSeverity> |
        Boolean includeAudit = true; // Boolean |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            RealtimeEventPage result = apiInstance.listRealtimeEventsApiV1RealtimeEventsGet(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#listRealtimeEventsApiV1RealtimeEventsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cursor** | **String**| Opaque reconnect cursor | [optional] |
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **executionId** | **UUID**|  | [optional] |
| **eventType** | [**List&lt;String&gt;**](String.md)|  | [optional] |
| **severity** | [**List&lt;RealtimeSeverity&gt;**](RealtimeSeverity.md)|  | [optional] |
| **includeAudit** | **Boolean**|  | [optional] [default to true] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**RealtimeEventPage**](RealtimeEventPage.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listRealtimeEventsApiV1RealtimeEventsGetWithHttpInfo

> ApiResponse<RealtimeEventPage> listRealtimeEventsApiV1RealtimeEventsGetWithHttpInfo(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Realtime Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque reconnect cursor
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        UUID executionId = UUID.randomUUID(); // UUID |
        List<String> eventType = Arrays.asList(); // List<String> |
        List<RealtimeSeverity> severity = Arrays.asList(); // List<RealtimeSeverity> |
        Boolean includeAudit = true; // Boolean |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<RealtimeEventPage> response = apiInstance.listRealtimeEventsApiV1RealtimeEventsGetWithHttpInfo(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#listRealtimeEventsApiV1RealtimeEventsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cursor** | **String**| Opaque reconnect cursor | [optional] |
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **executionId** | **UUID**|  | [optional] |
| **eventType** | [**List&lt;String&gt;**](String.md)|  | [optional] |
| **severity** | [**List&lt;RealtimeSeverity&gt;**](RealtimeSeverity.md)|  | [optional] |
| **includeAudit** | **Boolean**|  | [optional] [default to true] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**RealtimeEventPage**](RealtimeEventPage.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet

> List<WebhookDeliveryHistory> listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet(subscriptionId, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Webhook Delivery History

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        UUID subscriptionId = UUID.randomUUID(); // UUID |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<WebhookDeliveryHistory> result = apiInstance.listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet(subscriptionId, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subscriptionId** | **UUID**|  | |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;WebhookDeliveryHistory&gt;**](WebhookDeliveryHistory.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGetWithHttpInfo

> ApiResponse<List<WebhookDeliveryHistory>> listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGetWithHttpInfo(subscriptionId, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Webhook Delivery History

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        UUID subscriptionId = UUID.randomUUID(); // UUID |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<WebhookDeliveryHistory>> response = apiInstance.listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGetWithHttpInfo(subscriptionId, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#listWebhookDeliveryHistoryApiV1WebhookSubscriptionsSubscriptionIdDeliveriesGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subscriptionId** | **UUID**|  | |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;WebhookDeliveryHistory&gt;**](WebhookDeliveryHistory.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listWebhookSubscriptionsApiV1WebhookSubscriptionsGet

> List<WebhookSubscription> listWebhookSubscriptionsApiV1WebhookSubscriptionsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Webhook Subscriptions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<WebhookSubscription> result = apiInstance.listWebhookSubscriptionsApiV1WebhookSubscriptionsGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#listWebhookSubscriptionsApiV1WebhookSubscriptionsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;WebhookSubscription&gt;**](WebhookSubscription.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listWebhookSubscriptionsApiV1WebhookSubscriptionsGetWithHttpInfo

> ApiResponse<List<WebhookSubscription>> listWebhookSubscriptionsApiV1WebhookSubscriptionsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Webhook Subscriptions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<WebhookSubscription>> response = apiInstance.listWebhookSubscriptionsApiV1WebhookSubscriptionsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#listWebhookSubscriptionsApiV1WebhookSubscriptionsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;WebhookSubscription&gt;**](WebhookSubscription.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost

> WebhookDelivery replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost(deliveryId, authorization, xAmeshCSRF, xAmeshTenant)

Replay Webhook Delivery

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        UUID deliveryId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            WebhookDelivery result = apiInstance.replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost(deliveryId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **deliveryId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**WebhookDelivery**](WebhookDelivery.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPostWithHttpInfo

> ApiResponse<WebhookDelivery> replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPostWithHttpInfo(deliveryId, authorization, xAmeshCSRF, xAmeshTenant)

Replay Webhook Delivery

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        UUID deliveryId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<WebhookDelivery> response = apiInstance.replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPostWithHttpInfo(deliveryId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#replayWebhookDeliveryApiV1WebhookDeliveriesDeliveryIdReplayPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **deliveryId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**WebhookDelivery**](WebhookDelivery.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost

> ProvisionedWebhookSubscription rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost(subscriptionId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Rotate Webhook Subscription Secret

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        UUID subscriptionId = UUID.randomUUID(); // UUID |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ProvisionedWebhookSubscription result = apiInstance.rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost(subscriptionId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subscriptionId** | **UUID**|  | |
| **expectedVersion** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ProvisionedWebhookSubscription**](ProvisionedWebhookSubscription.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPostWithHttpInfo

> ApiResponse<ProvisionedWebhookSubscription> rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPostWithHttpInfo(subscriptionId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Rotate Webhook Subscription Secret

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        UUID subscriptionId = UUID.randomUUID(); // UUID |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ProvisionedWebhookSubscription> response = apiInstance.rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPostWithHttpInfo(subscriptionId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#rotateWebhookSubscriptionSecretApiV1WebhookSubscriptionsSubscriptionIdRotateSecretPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subscriptionId** | **UUID**|  | |
| **expectedVersion** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ProvisionedWebhookSubscription**](ProvisionedWebhookSubscription.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## streamRealtimeEventsApiV1RealtimeStreamGet

> void streamRealtimeEventsApiV1RealtimeStreamGet(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, bufferEvents, maxEvents, heartbeatSeconds, streamSeconds, lastEventID, authorization, xAmeshCSRF, xAmeshTenant)

Stream Realtime Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque reconnect cursor
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        UUID executionId = UUID.randomUUID(); // UUID |
        List<String> eventType = Arrays.asList(); // List<String> |
        List<RealtimeSeverity> severity = Arrays.asList(); // List<RealtimeSeverity> |
        Boolean includeAudit = true; // Boolean |
        Integer bufferEvents = 100; // Integer |
        Integer maxEvents = 1000; // Integer |
        BigDecimal heartbeatSeconds = new BigDecimal("10"); // BigDecimal |
        BigDecimal streamSeconds = new BigDecimal("15"); // BigDecimal |
        String lastEventID = "lastEventID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.streamRealtimeEventsApiV1RealtimeStreamGet(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, bufferEvents, maxEvents, heartbeatSeconds, streamSeconds, lastEventID, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#streamRealtimeEventsApiV1RealtimeStreamGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cursor** | **String**| Opaque reconnect cursor | [optional] |
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **executionId** | **UUID**|  | [optional] |
| **eventType** | [**List&lt;String&gt;**](String.md)|  | [optional] |
| **severity** | [**List&lt;RealtimeSeverity&gt;**](RealtimeSeverity.md)|  | [optional] |
| **includeAudit** | **Boolean**|  | [optional] [default to true] |
| **bufferEvents** | **Integer**|  | [optional] [default to 100] |
| **maxEvents** | **Integer**|  | [optional] [default to 1000] |
| **heartbeatSeconds** | **BigDecimal**|  | [optional] [default to 10] |
| **streamSeconds** | **BigDecimal**|  | [optional] [default to 15] |
| **lastEventID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: text/event-stream, application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Cursor-resumable server-sent event stream |  -  |
| **422** | Validation Error |  -  |

## streamRealtimeEventsApiV1RealtimeStreamGetWithHttpInfo

> ApiResponse<Void> streamRealtimeEventsApiV1RealtimeStreamGetWithHttpInfo(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, bufferEvents, maxEvents, heartbeatSeconds, streamSeconds, lastEventID, authorization, xAmeshCSRF, xAmeshTenant)

Stream Realtime Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque reconnect cursor
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        UUID executionId = UUID.randomUUID(); // UUID |
        List<String> eventType = Arrays.asList(); // List<String> |
        List<RealtimeSeverity> severity = Arrays.asList(); // List<RealtimeSeverity> |
        Boolean includeAudit = true; // Boolean |
        Integer bufferEvents = 100; // Integer |
        Integer maxEvents = 1000; // Integer |
        BigDecimal heartbeatSeconds = new BigDecimal("10"); // BigDecimal |
        BigDecimal streamSeconds = new BigDecimal("15"); // BigDecimal |
        String lastEventID = "lastEventID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.streamRealtimeEventsApiV1RealtimeStreamGetWithHttpInfo(cursor, namespace, flowId, executionId, eventType, severity, includeAudit, bufferEvents, maxEvents, heartbeatSeconds, streamSeconds, lastEventID, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#streamRealtimeEventsApiV1RealtimeStreamGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cursor** | **String**| Opaque reconnect cursor | [optional] |
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **executionId** | **UUID**|  | [optional] |
| **eventType** | [**List&lt;String&gt;**](String.md)|  | [optional] |
| **severity** | [**List&lt;RealtimeSeverity&gt;**](RealtimeSeverity.md)|  | [optional] |
| **includeAudit** | **Boolean**|  | [optional] [default to true] |
| **bufferEvents** | **Integer**|  | [optional] [default to 100] |
| **maxEvents** | **Integer**|  | [optional] [default to 1000] |
| **heartbeatSeconds** | **BigDecimal**|  | [optional] [default to 10] |
| **streamSeconds** | **BigDecimal**|  | [optional] [default to 15] |
| **lastEventID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


ApiResponse<Void>

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: text/event-stream, application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Cursor-resumable server-sent event stream |  -  |
| **422** | Validation Error |  -  |


## testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost

> WebhookDelivery testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost(subscriptionId, authorization, xAmeshCSRF, xAmeshTenant)

Test Webhook Subscription

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        UUID subscriptionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            WebhookDelivery result = apiInstance.testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost(subscriptionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subscriptionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**WebhookDelivery**](WebhookDelivery.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPostWithHttpInfo

> ApiResponse<WebhookDelivery> testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPostWithHttpInfo(subscriptionId, authorization, xAmeshCSRF, xAmeshTenant)

Test Webhook Subscription

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.RealtimeApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        RealtimeApi apiInstance = new RealtimeApi(defaultClient);
        UUID subscriptionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<WebhookDelivery> response = apiInstance.testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPostWithHttpInfo(subscriptionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling RealtimeApi#testWebhookSubscriptionApiV1WebhookSubscriptionsSubscriptionIdTestPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **subscriptionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**WebhookDelivery**](WebhookDelivery.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful Response |  -  |
| **422** | Validation Error |  -  |
