# amesh_client.TriggersApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_trigger_occurrences_api_v1_trigger_occurrences_get**](TriggersApi.md#list_trigger_occurrences_api_v1_trigger_occurrences_get) | **GET** /api/v1/trigger-occurrences | List Trigger Occurrences
[**list_trigger_runtime_states_api_v1_triggers_get**](TriggersApi.md#list_trigger_runtime_states_api_v1_triggers_get) | **GET** /api/v1/triggers | List Trigger Runtime States
[**pause_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_pause_post**](TriggersApi.md#pause_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_pause_post) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/pause | Pause Trigger Runtime
[**preview_schedule_api_v1_flows_namespace_flow_id_schedules_trigger_id_preview_get**](TriggersApi.md#preview_schedule_api_v1_flows_namespace_flow_id_schedules_trigger_id_preview_get) | **GET** /api/v1/flows/{namespace}/{flow_id}/schedules/{trigger_id}/preview | Preview Schedule
[**replay_trigger_occurrence_api_v1_trigger_occurrences_occurrence_id_replay_post**](TriggersApi.md#replay_trigger_occurrence_api_v1_trigger_occurrences_occurrence_id_replay_post) | **POST** /api/v1/trigger-occurrences/{occurrence_id}/replay | Replay Trigger Occurrence
[**resume_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_resume_post**](TriggersApi.md#resume_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_resume_post) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/resume | Resume Trigger Runtime
[**trigger_webhook_api_v1_webhooks_namespace_flow_id_trigger_id_post**](TriggersApi.md#trigger_webhook_api_v1_webhooks_namespace_flow_id_trigger_id_post) | **POST** /api/v1/webhooks/{namespace}/{flow_id}/{trigger_id} | Trigger Webhook


# **list_trigger_occurrences_api_v1_trigger_occurrences_get**
> List[TriggerOccurrence] list_trigger_occurrences_api_v1_trigger_occurrences_get(namespace=namespace, flow_id=flow_id, trigger_id=trigger_id, state=state, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Trigger Occurrences

### Example


```python
import amesh_client
from amesh_client.models.trigger_occurrence import TriggerOccurrence
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
    api_instance = amesh_client.TriggersApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    flow_id = 'flow_id_example' # str |  (optional)
    trigger_id = 'trigger_id_example' # str |  (optional)
    state = amesh_client.TriggerOccurrenceState() # TriggerOccurrenceState |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Trigger Occurrences
        api_response = api_instance.list_trigger_occurrences_api_v1_trigger_occurrences_get(namespace=namespace, flow_id=flow_id, trigger_id=trigger_id, state=state, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of TriggersApi->list_trigger_occurrences_api_v1_trigger_occurrences_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->list_trigger_occurrences_api_v1_trigger_occurrences_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **flow_id** | **str**|  | [optional]
 **trigger_id** | **str**|  | [optional]
 **state** | [**TriggerOccurrenceState**](.md)|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[TriggerOccurrence]**](TriggerOccurrence.md)

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

# **list_trigger_runtime_states_api_v1_triggers_get**
> List[TriggerRuntimeState] list_trigger_runtime_states_api_v1_triggers_get(namespace=namespace, flow_id=flow_id, trigger_id=trigger_id, active=active, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Trigger Runtime States

### Example


```python
import amesh_client
from amesh_client.models.trigger_runtime_state import TriggerRuntimeState
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
    api_instance = amesh_client.TriggersApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    flow_id = 'flow_id_example' # str |  (optional)
    trigger_id = 'trigger_id_example' # str |  (optional)
    active = True # bool |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Trigger Runtime States
        api_response = api_instance.list_trigger_runtime_states_api_v1_triggers_get(namespace=namespace, flow_id=flow_id, trigger_id=trigger_id, active=active, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of TriggersApi->list_trigger_runtime_states_api_v1_triggers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->list_trigger_runtime_states_api_v1_triggers_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **flow_id** | **str**|  | [optional]
 **trigger_id** | **str**|  | [optional]
 **active** | **bool**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[TriggerRuntimeState]**](TriggerRuntimeState.md)

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

# **pause_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_pause_post**
> TriggerRuntimeState pause_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_pause_post(namespace, flow_id, trigger_id, trigger_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Pause Trigger Runtime

### Example


```python
import amesh_client
from amesh_client.models.trigger_action_request import TriggerActionRequest
from amesh_client.models.trigger_runtime_state import TriggerRuntimeState
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
    api_instance = amesh_client.TriggersApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    trigger_id = 'trigger_id_example' # str |
    trigger_action_request = amesh_client.TriggerActionRequest() # TriggerActionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Pause Trigger Runtime
        api_response = api_instance.pause_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_pause_post(namespace, flow_id, trigger_id, trigger_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of TriggersApi->pause_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_pause_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->pause_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_pause_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **trigger_id** | **str**|  |
 **trigger_action_request** | [**TriggerActionRequest**](TriggerActionRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**TriggerRuntimeState**](TriggerRuntimeState.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **preview_schedule_api_v1_flows_namespace_flow_id_schedules_trigger_id_preview_get**
> SchedulePreview preview_schedule_api_v1_flows_namespace_flow_id_schedules_trigger_id_preview_get(namespace, flow_id, trigger_id, after=after, count=count, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Schedule

### Example


```python
import amesh_client
from amesh_client.models.schedule_preview import SchedulePreview
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
    api_instance = amesh_client.TriggersApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    trigger_id = 'trigger_id_example' # str |
    after = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    count = 5 # int |  (optional) (default to 5)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Schedule
        api_response = api_instance.preview_schedule_api_v1_flows_namespace_flow_id_schedules_trigger_id_preview_get(namespace, flow_id, trigger_id, after=after, count=count, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of TriggersApi->preview_schedule_api_v1_flows_namespace_flow_id_schedules_trigger_id_preview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->preview_schedule_api_v1_flows_namespace_flow_id_schedules_trigger_id_preview_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **trigger_id** | **str**|  |
 **after** | **datetime**|  | [optional]
 **count** | **int**|  | [optional] [default to 5]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**SchedulePreview**](SchedulePreview.md)

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

# **replay_trigger_occurrence_api_v1_trigger_occurrences_occurrence_id_replay_post**
> TriggerOccurrence replay_trigger_occurrence_api_v1_trigger_occurrences_occurrence_id_replay_post(occurrence_id, trigger_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Replay Trigger Occurrence

### Example


```python
import amesh_client
from amesh_client.models.trigger_action_request import TriggerActionRequest
from amesh_client.models.trigger_occurrence import TriggerOccurrence
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
    api_instance = amesh_client.TriggersApi(api_client)
    occurrence_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    trigger_action_request = amesh_client.TriggerActionRequest() # TriggerActionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Replay Trigger Occurrence
        api_response = api_instance.replay_trigger_occurrence_api_v1_trigger_occurrences_occurrence_id_replay_post(occurrence_id, trigger_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of TriggersApi->replay_trigger_occurrence_api_v1_trigger_occurrences_occurrence_id_replay_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->replay_trigger_occurrence_api_v1_trigger_occurrences_occurrence_id_replay_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **occurrence_id** | **UUID**|  |
 **trigger_action_request** | [**TriggerActionRequest**](TriggerActionRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**TriggerOccurrence**](TriggerOccurrence.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **resume_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_resume_post**
> TriggerRuntimeState resume_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_resume_post(namespace, flow_id, trigger_id, trigger_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Resume Trigger Runtime

### Example


```python
import amesh_client
from amesh_client.models.trigger_action_request import TriggerActionRequest
from amesh_client.models.trigger_runtime_state import TriggerRuntimeState
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
    api_instance = amesh_client.TriggersApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    trigger_id = 'trigger_id_example' # str |
    trigger_action_request = amesh_client.TriggerActionRequest() # TriggerActionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Resume Trigger Runtime
        api_response = api_instance.resume_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_resume_post(namespace, flow_id, trigger_id, trigger_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of TriggersApi->resume_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_resume_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->resume_trigger_runtime_api_v1_triggers_namespace_flow_id_trigger_id_resume_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **trigger_id** | **str**|  |
 **trigger_action_request** | [**TriggerActionRequest**](TriggerActionRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**TriggerRuntimeState**](TriggerRuntimeState.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **trigger_webhook_api_v1_webhooks_namespace_flow_id_trigger_id_post**
> ExecutionDetail trigger_webhook_api_v1_webhooks_namespace_flow_id_trigger_id_post(namespace, flow_id, trigger_id, runner=runner, prefer=prefer, idempotency_key=idempotency_key, x_event_id=x_event_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Trigger Webhook

### Example


```python
import amesh_client
from amesh_client.models.execution_detail import ExecutionDetail
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
    api_instance = amesh_client.TriggersApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    trigger_id = 'trigger_id_example' # str |
    runner = amesh_client.RunnerMode() # RunnerMode |  (optional)
    prefer = 'prefer_example' # str |  (optional)
    idempotency_key = 'idempotency_key_example' # str |  (optional)
    x_event_id = 'x_event_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Trigger Webhook
        api_response = api_instance.trigger_webhook_api_v1_webhooks_namespace_flow_id_trigger_id_post(namespace, flow_id, trigger_id, runner=runner, prefer=prefer, idempotency_key=idempotency_key, x_event_id=x_event_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of TriggersApi->trigger_webhook_api_v1_webhooks_namespace_flow_id_trigger_id_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TriggersApi->trigger_webhook_api_v1_webhooks_namespace_flow_id_trigger_id_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **trigger_id** | **str**|  |
 **runner** | [**RunnerMode**](.md)|  | [optional]
 **prefer** | **str**|  | [optional]
 **idempotency_key** | **str**|  | [optional]
 **x_event_id** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**202** | Webhook execution persisted and accepted for asynchronous processing |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
