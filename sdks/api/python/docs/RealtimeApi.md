# amesh_client.RealtimeApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_webhook_subscription_api_v1_webhook_subscriptions_post**](RealtimeApi.md#create_webhook_subscription_api_v1_webhook_subscriptions_post) | **POST** /api/v1/webhook-subscriptions | Create Webhook Subscription
[**list_realtime_events_api_v1_realtime_events_get**](RealtimeApi.md#list_realtime_events_api_v1_realtime_events_get) | **GET** /api/v1/realtime/events | List Realtime Events
[**list_webhook_delivery_history_api_v1_webhook_subscriptions_subscription_id_deliveries_get**](RealtimeApi.md#list_webhook_delivery_history_api_v1_webhook_subscriptions_subscription_id_deliveries_get) | **GET** /api/v1/webhook-subscriptions/{subscription_id}/deliveries | List Webhook Delivery History
[**list_webhook_subscriptions_api_v1_webhook_subscriptions_get**](RealtimeApi.md#list_webhook_subscriptions_api_v1_webhook_subscriptions_get) | **GET** /api/v1/webhook-subscriptions | List Webhook Subscriptions
[**replay_webhook_delivery_api_v1_webhook_deliveries_delivery_id_replay_post**](RealtimeApi.md#replay_webhook_delivery_api_v1_webhook_deliveries_delivery_id_replay_post) | **POST** /api/v1/webhook-deliveries/{delivery_id}/replay | Replay Webhook Delivery
[**rotate_webhook_subscription_secret_api_v1_webhook_subscriptions_subscription_id_rotate_secret_post**](RealtimeApi.md#rotate_webhook_subscription_secret_api_v1_webhook_subscriptions_subscription_id_rotate_secret_post) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/rotate-secret | Rotate Webhook Subscription Secret
[**stream_realtime_events_api_v1_realtime_stream_get**](RealtimeApi.md#stream_realtime_events_api_v1_realtime_stream_get) | **GET** /api/v1/realtime/stream | Stream Realtime Events
[**test_webhook_subscription_api_v1_webhook_subscriptions_subscription_id_test_post**](RealtimeApi.md#test_webhook_subscription_api_v1_webhook_subscriptions_subscription_id_test_post) | **POST** /api/v1/webhook-subscriptions/{subscription_id}/test | Test Webhook Subscription


# **create_webhook_subscription_api_v1_webhook_subscriptions_post**
> ProvisionedWebhookSubscription create_webhook_subscription_api_v1_webhook_subscriptions_post(webhook_subscription_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Webhook Subscription

### Example


```python
import amesh_client
from amesh_client.models.provisioned_webhook_subscription import ProvisionedWebhookSubscription
from amesh_client.models.webhook_subscription_create import WebhookSubscriptionCreate
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.RealtimeApi(api_client)
    webhook_subscription_create = amesh_client.WebhookSubscriptionCreate() # WebhookSubscriptionCreate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Webhook Subscription
        api_response = api_instance.create_webhook_subscription_api_v1_webhook_subscriptions_post(webhook_subscription_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of RealtimeApi->create_webhook_subscription_api_v1_webhook_subscriptions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealtimeApi->create_webhook_subscription_api_v1_webhook_subscriptions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **webhook_subscription_create** | [**WebhookSubscriptionCreate**](WebhookSubscriptionCreate.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_realtime_events_api_v1_realtime_events_get**
> RealtimeEventPage list_realtime_events_api_v1_realtime_events_get(cursor=cursor, namespace=namespace, flow_id=flow_id, execution_id=execution_id, event_type=event_type, severity=severity, include_audit=include_audit, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Realtime Events

### Example


```python
import amesh_client
from amesh_client.models.realtime_event_page import RealtimeEventPage
from amesh_client.models.realtime_severity import RealtimeSeverity
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.RealtimeApi(api_client)
    cursor = 'cursor_example' # str | Opaque reconnect cursor (optional)
    namespace = 'namespace_example' # str |  (optional)
    flow_id = 'flow_id_example' # str |  (optional)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |  (optional)
    event_type = ['event_type_example'] # List[str] |  (optional)
    severity = [amesh_client.RealtimeSeverity()] # List[RealtimeSeverity] |  (optional)
    include_audit = True # bool |  (optional) (default to True)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Realtime Events
        api_response = api_instance.list_realtime_events_api_v1_realtime_events_get(cursor=cursor, namespace=namespace, flow_id=flow_id, execution_id=execution_id, event_type=event_type, severity=severity, include_audit=include_audit, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of RealtimeApi->list_realtime_events_api_v1_realtime_events_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealtimeApi->list_realtime_events_api_v1_realtime_events_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **str**| Opaque reconnect cursor | [optional]
 **namespace** | **str**|  | [optional]
 **flow_id** | **str**|  | [optional]
 **execution_id** | **UUID**|  | [optional]
 **event_type** | [**List[str]**](str.md)|  | [optional]
 **severity** | [**List[RealtimeSeverity]**](RealtimeSeverity.md)|  | [optional]
 **include_audit** | **bool**|  | [optional] [default to True]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_webhook_delivery_history_api_v1_webhook_subscriptions_subscription_id_deliveries_get**
> List[WebhookDeliveryHistory] list_webhook_delivery_history_api_v1_webhook_subscriptions_subscription_id_deliveries_get(subscription_id, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Webhook Delivery History

### Example


```python
import amesh_client
from amesh_client.models.webhook_delivery_history import WebhookDeliveryHistory
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.RealtimeApi(api_client)
    subscription_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Webhook Delivery History
        api_response = api_instance.list_webhook_delivery_history_api_v1_webhook_subscriptions_subscription_id_deliveries_get(subscription_id, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of RealtimeApi->list_webhook_delivery_history_api_v1_webhook_subscriptions_subscription_id_deliveries_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealtimeApi->list_webhook_delivery_history_api_v1_webhook_subscriptions_subscription_id_deliveries_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **subscription_id** | **UUID**|  |
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[WebhookDeliveryHistory]**](WebhookDeliveryHistory.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_webhook_subscriptions_api_v1_webhook_subscriptions_get**
> List[WebhookSubscription] list_webhook_subscriptions_api_v1_webhook_subscriptions_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Webhook Subscriptions

### Example


```python
import amesh_client
from amesh_client.models.webhook_subscription import WebhookSubscription
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.RealtimeApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Webhook Subscriptions
        api_response = api_instance.list_webhook_subscriptions_api_v1_webhook_subscriptions_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of RealtimeApi->list_webhook_subscriptions_api_v1_webhook_subscriptions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealtimeApi->list_webhook_subscriptions_api_v1_webhook_subscriptions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[WebhookSubscription]**](WebhookSubscription.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **replay_webhook_delivery_api_v1_webhook_deliveries_delivery_id_replay_post**
> WebhookDelivery replay_webhook_delivery_api_v1_webhook_deliveries_delivery_id_replay_post(delivery_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Replay Webhook Delivery

### Example


```python
import amesh_client
from amesh_client.models.webhook_delivery import WebhookDelivery
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.RealtimeApi(api_client)
    delivery_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Replay Webhook Delivery
        api_response = api_instance.replay_webhook_delivery_api_v1_webhook_deliveries_delivery_id_replay_post(delivery_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of RealtimeApi->replay_webhook_delivery_api_v1_webhook_deliveries_delivery_id_replay_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealtimeApi->replay_webhook_delivery_api_v1_webhook_deliveries_delivery_id_replay_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **delivery_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

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
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **rotate_webhook_subscription_secret_api_v1_webhook_subscriptions_subscription_id_rotate_secret_post**
> ProvisionedWebhookSubscription rotate_webhook_subscription_secret_api_v1_webhook_subscriptions_subscription_id_rotate_secret_post(subscription_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Rotate Webhook Subscription Secret

### Example


```python
import amesh_client
from amesh_client.models.provisioned_webhook_subscription import ProvisionedWebhookSubscription
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.RealtimeApi(api_client)
    subscription_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    expected_version = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Rotate Webhook Subscription Secret
        api_response = api_instance.rotate_webhook_subscription_secret_api_v1_webhook_subscriptions_subscription_id_rotate_secret_post(subscription_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of RealtimeApi->rotate_webhook_subscription_secret_api_v1_webhook_subscriptions_subscription_id_rotate_secret_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealtimeApi->rotate_webhook_subscription_secret_api_v1_webhook_subscriptions_subscription_id_rotate_secret_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **subscription_id** | **UUID**|  |
 **expected_version** | **int**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stream_realtime_events_api_v1_realtime_stream_get**
> stream_realtime_events_api_v1_realtime_stream_get(cursor=cursor, namespace=namespace, flow_id=flow_id, execution_id=execution_id, event_type=event_type, severity=severity, include_audit=include_audit, buffer_events=buffer_events, max_events=max_events, heartbeat_seconds=heartbeat_seconds, stream_seconds=stream_seconds, last_event_id=last_event_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Stream Realtime Events

### Example


```python
import amesh_client
from amesh_client.models.realtime_severity import RealtimeSeverity
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.RealtimeApi(api_client)
    cursor = 'cursor_example' # str | Opaque reconnect cursor (optional)
    namespace = 'namespace_example' # str |  (optional)
    flow_id = 'flow_id_example' # str |  (optional)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |  (optional)
    event_type = ['event_type_example'] # List[str] |  (optional)
    severity = [amesh_client.RealtimeSeverity()] # List[RealtimeSeverity] |  (optional)
    include_audit = True # bool |  (optional) (default to True)
    buffer_events = 100 # int |  (optional) (default to 100)
    max_events = 1000 # int |  (optional) (default to 1000)
    heartbeat_seconds = 10 # float |  (optional) (default to 10)
    stream_seconds = 15 # float |  (optional) (default to 15)
    last_event_id = 'last_event_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Stream Realtime Events
        api_instance.stream_realtime_events_api_v1_realtime_stream_get(cursor=cursor, namespace=namespace, flow_id=flow_id, execution_id=execution_id, event_type=event_type, severity=severity, include_audit=include_audit, buffer_events=buffer_events, max_events=max_events, heartbeat_seconds=heartbeat_seconds, stream_seconds=stream_seconds, last_event_id=last_event_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling RealtimeApi->stream_realtime_events_api_v1_realtime_stream_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **str**| Opaque reconnect cursor | [optional]
 **namespace** | **str**|  | [optional]
 **flow_id** | **str**|  | [optional]
 **execution_id** | **UUID**|  | [optional]
 **event_type** | [**List[str]**](str.md)|  | [optional]
 **severity** | [**List[RealtimeSeverity]**](RealtimeSeverity.md)|  | [optional]
 **include_audit** | **bool**|  | [optional] [default to True]
 **buffer_events** | **int**|  | [optional] [default to 100]
 **max_events** | **int**|  | [optional] [default to 1000]
 **heartbeat_seconds** | **float**|  | [optional] [default to 10]
 **stream_seconds** | **float**|  | [optional] [default to 15]
 **last_event_id** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/event-stream, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Cursor-resumable server-sent event stream |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **test_webhook_subscription_api_v1_webhook_subscriptions_subscription_id_test_post**
> WebhookDelivery test_webhook_subscription_api_v1_webhook_subscriptions_subscription_id_test_post(subscription_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Test Webhook Subscription

### Example


```python
import amesh_client
from amesh_client.models.webhook_delivery import WebhookDelivery
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.RealtimeApi(api_client)
    subscription_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Test Webhook Subscription
        api_response = api_instance.test_webhook_subscription_api_v1_webhook_subscriptions_subscription_id_test_post(subscription_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of RealtimeApi->test_webhook_subscription_api_v1_webhook_subscriptions_subscription_id_test_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RealtimeApi->test_webhook_subscription_api_v1_webhook_subscriptions_subscription_id_test_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **subscription_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

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
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
