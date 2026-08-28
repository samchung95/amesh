# amesh_client.AgentSessionsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**control_agent_session_api_v1_agent_sessions_service_session_id_action_post**](AgentSessionsApi.md#control_agent_session_api_v1_agent_sessions_service_session_id_action_post) | **POST** /api/v1/agent-sessions/{service_session_id}/{action} | Control Agent Session
[**create_agent_session_api_v1_agent_sessions_post**](AgentSessionsApi.md#create_agent_session_api_v1_agent_sessions_post) | **POST** /api/v1/agent-sessions | Create Agent Session
[**get_agent_session_api_v1_agent_sessions_service_session_id_get**](AgentSessionsApi.md#get_agent_session_api_v1_agent_sessions_service_session_id_get) | **GET** /api/v1/agent-sessions/{service_session_id} | Get Agent Session
[**get_agent_session_events_api_v1_agent_sessions_service_session_id_events_get**](AgentSessionsApi.md#get_agent_session_events_api_v1_agent_sessions_service_session_id_events_get) | **GET** /api/v1/agent-sessions/{service_session_id}/events | Get Agent Session Events
[**get_agent_session_messages_api_v1_agent_sessions_service_session_id_messages_get**](AgentSessionsApi.md#get_agent_session_messages_api_v1_agent_sessions_service_session_id_messages_get) | **GET** /api/v1/agent-sessions/{service_session_id}/messages | Get Agent Session Messages
[**get_agent_session_result_api_v1_agent_sessions_service_session_id_result_get**](AgentSessionsApi.md#get_agent_session_result_api_v1_agent_sessions_service_session_id_result_get) | **GET** /api/v1/agent-sessions/{service_session_id}/result | Get Agent Session Result
[**list_agent_session_harnesses_api_v1_agent_sessions_harnesses_get**](AgentSessionsApi.md#list_agent_session_harnesses_api_v1_agent_sessions_harnesses_get) | **GET** /api/v1/agent-sessions/harnesses | List Agent Session Harnesses
[**list_agent_sessions_api_v1_agent_sessions_get**](AgentSessionsApi.md#list_agent_sessions_api_v1_agent_sessions_get) | **GET** /api/v1/agent-sessions | List Agent Sessions
[**openai_chat_completions_v1_chat_completions_post**](AgentSessionsApi.md#openai_chat_completions_v1_chat_completions_post) | **POST** /v1/chat/completions | Openai Chat Completions
[**openai_responses_v1_responses_post**](AgentSessionsApi.md#openai_responses_v1_responses_post) | **POST** /v1/responses | Openai Responses
[**post_agent_session_message_api_v1_agent_sessions_service_session_id_messages_post**](AgentSessionsApi.md#post_agent_session_message_api_v1_agent_sessions_service_session_id_messages_post) | **POST** /api/v1/agent-sessions/{service_session_id}/messages | Post Agent Session Message
[**stream_agent_session_events_api_v1_agent_sessions_service_session_id_events_stream_get**](AgentSessionsApi.md#stream_agent_session_events_api_v1_agent_sessions_service_session_id_events_stream_get) | **GET** /api/v1/agent-sessions/{service_session_id}/events/stream | Stream Agent Session Events


# **control_agent_session_api_v1_agent_sessions_service_session_id_action_post**
> AgentSessionLaunchResponse control_agent_session_api_v1_agent_sessions_service_session_id_action_post(service_session_id, action, agent_session_control_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Control Agent Session

### Example


```python
import amesh_client
from amesh_client.models.agent_session_control_request import AgentSessionControlRequest
from amesh_client.models.agent_session_launch_response import AgentSessionLaunchResponse
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    service_session_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    action = 'action_example' # str |
    agent_session_control_request = amesh_client.AgentSessionControlRequest() # AgentSessionControlRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Control Agent Session
        api_response = api_instance.control_agent_session_api_v1_agent_sessions_service_session_id_action_post(service_session_id, action, agent_session_control_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->control_agent_session_api_v1_agent_sessions_service_session_id_action_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->control_agent_session_api_v1_agent_sessions_service_session_id_action_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_session_id** | **UUID**|  |
 **action** | **str**|  |
 **agent_session_control_request** | **AgentSessionControlRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionLaunchResponse**

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

# **create_agent_session_api_v1_agent_sessions_post**
> AgentSessionLaunchResponse create_agent_session_api_v1_agent_sessions_post(agent_session_create_request, prefer=prefer, idempotency_key=idempotency_key, x_correlation_id=x_correlation_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Agent Session

### Example


```python
import amesh_client
from amesh_client.models.agent_session_create_request import AgentSessionCreateRequest
from amesh_client.models.agent_session_launch_response import AgentSessionLaunchResponse
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    agent_session_create_request = amesh_client.AgentSessionCreateRequest() # AgentSessionCreateRequest |
    prefer = 'prefer_example' # str |  (optional)
    idempotency_key = 'idempotency_key_example' # str |  (optional)
    x_correlation_id = 'x_correlation_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Agent Session
        api_response = api_instance.create_agent_session_api_v1_agent_sessions_post(agent_session_create_request, prefer=prefer, idempotency_key=idempotency_key, x_correlation_id=x_correlation_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->create_agent_session_api_v1_agent_sessions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->create_agent_session_api_v1_agent_sessions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_session_create_request** | **AgentSessionCreateRequest**|  |
 **prefer** | **str**|  | [optional]
 **idempotency_key** | **str**|  | [optional]
 **x_correlation_id** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionLaunchResponse**

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

# **get_agent_session_api_v1_agent_sessions_service_session_id_get**
> AgentSessionServiceDetailResponse get_agent_session_api_v1_agent_sessions_service_session_id_get(service_session_id, after_event_index=after_event_index, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Agent Session

### Example


```python
import amesh_client
from amesh_client.models.agent_session_service_detail_response import AgentSessionServiceDetailResponse
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    service_session_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    after_event_index = 0 # int |  (optional) (default to 0)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Agent Session
        api_response = api_instance.get_agent_session_api_v1_agent_sessions_service_session_id_get(service_session_id, after_event_index=after_event_index, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->get_agent_session_api_v1_agent_sessions_service_session_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->get_agent_session_api_v1_agent_sessions_service_session_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_session_id** | **UUID**|  |
 **after_event_index** | **int**|  | [optional] [default to 0]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionServiceDetailResponse**

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

# **get_agent_session_events_api_v1_agent_sessions_service_session_id_events_get**
> AgentSessionServiceDetailResponse get_agent_session_events_api_v1_agent_sessions_service_session_id_events_get(service_session_id, after_event_index=after_event_index, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Agent Session Events

### Example


```python
import amesh_client
from amesh_client.models.agent_session_service_detail_response import AgentSessionServiceDetailResponse
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    service_session_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    after_event_index = 0 # int |  (optional) (default to 0)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Agent Session Events
        api_response = api_instance.get_agent_session_events_api_v1_agent_sessions_service_session_id_events_get(service_session_id, after_event_index=after_event_index, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->get_agent_session_events_api_v1_agent_sessions_service_session_id_events_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->get_agent_session_events_api_v1_agent_sessions_service_session_id_events_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_session_id** | **UUID**|  |
 **after_event_index** | **int**|  | [optional] [default to 0]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionServiceDetailResponse**

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

# **get_agent_session_messages_api_v1_agent_sessions_service_session_id_messages_get**
> AgentSessionServiceDetailResponse get_agent_session_messages_api_v1_agent_sessions_service_session_id_messages_get(service_session_id, after_event_index=after_event_index, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Agent Session Messages

### Example


```python
import amesh_client
from amesh_client.models.agent_session_service_detail_response import AgentSessionServiceDetailResponse
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    service_session_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    after_event_index = 0 # int |  (optional) (default to 0)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Agent Session Messages
        api_response = api_instance.get_agent_session_messages_api_v1_agent_sessions_service_session_id_messages_get(service_session_id, after_event_index=after_event_index, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->get_agent_session_messages_api_v1_agent_sessions_service_session_id_messages_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->get_agent_session_messages_api_v1_agent_sessions_service_session_id_messages_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_session_id** | **UUID**|  |
 **after_event_index** | **int**|  | [optional] [default to 0]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionServiceDetailResponse**

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

# **get_agent_session_result_api_v1_agent_sessions_service_session_id_result_get**
> AgentSessionResultResponse get_agent_session_result_api_v1_agent_sessions_service_session_id_result_get(service_session_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Agent Session Result

### Example


```python
import amesh_client
from amesh_client.models.agent_session_result_response import AgentSessionResultResponse
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    service_session_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Agent Session Result
        api_response = api_instance.get_agent_session_result_api_v1_agent_sessions_service_session_id_result_get(service_session_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->get_agent_session_result_api_v1_agent_sessions_service_session_id_result_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->get_agent_session_result_api_v1_agent_sessions_service_session_id_result_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_session_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionResultResponse**

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

# **list_agent_session_harnesses_api_v1_agent_sessions_harnesses_get**
> Dict[str, AgentSessionHarnessCatalogEntry] list_agent_session_harnesses_api_v1_agent_sessions_harnesses_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Agent Session Harnesses

Return registered harness provenance without exposing worker details.

### Example


```python
import amesh_client
from amesh_client.models.agent_session_harness_catalog_entry import AgentSessionHarnessCatalogEntry
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Agent Session Harnesses
        api_response = api_instance.list_agent_session_harnesses_api_v1_agent_sessions_harnesses_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->list_agent_session_harnesses_api_v1_agent_sessions_harnesses_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->list_agent_session_harnesses_api_v1_agent_sessions_harnesses_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**Dict[str, AgentSessionHarnessCatalogEntry]**](AgentSessionHarnessCatalogEntry.md)

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

# **list_agent_sessions_api_v1_agent_sessions_get**
> List[AgentSessionServiceItem] list_agent_sessions_api_v1_agent_sessions_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Agent Sessions

### Example


```python
import amesh_client
from amesh_client.models.agent_session_service_item import AgentSessionServiceItem
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Agent Sessions
        api_response = api_instance.list_agent_sessions_api_v1_agent_sessions_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->list_agent_sessions_api_v1_agent_sessions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->list_agent_sessions_api_v1_agent_sessions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[AgentSessionServiceItem]**](AgentSessionServiceItem.md)

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

# **openai_chat_completions_v1_chat_completions_post**
> OpenAIChatCompletionResponse openai_chat_completions_v1_chat_completions_post(open_ai_chat_completion_request, idempotency_key=idempotency_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Openai Chat Completions

### Example


```python
import amesh_client
from amesh_client.models.open_ai_chat_completion_request import OpenAIChatCompletionRequest
from amesh_client.models.open_ai_chat_completion_response import OpenAIChatCompletionResponse
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    open_ai_chat_completion_request = amesh_client.OpenAIChatCompletionRequest() # OpenAIChatCompletionRequest |
    idempotency_key = 'idempotency_key_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Openai Chat Completions
        api_response = api_instance.openai_chat_completions_v1_chat_completions_post(open_ai_chat_completion_request, idempotency_key=idempotency_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->openai_chat_completions_v1_chat_completions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->openai_chat_completions_v1_chat_completions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **open_ai_chat_completion_request** | **OpenAIChatCompletionRequest**|  |
 **idempotency_key** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**OpenAIChatCompletionResponse**

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

# **openai_responses_v1_responses_post**
> OpenAIResponse openai_responses_v1_responses_post(open_ai_response_request, idempotency_key=idempotency_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Openai Responses

### Example


```python
import amesh_client
from amesh_client.models.open_ai_response import OpenAIResponse
from amesh_client.models.open_ai_response_request import OpenAIResponseRequest
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    open_ai_response_request = amesh_client.OpenAIResponseRequest() # OpenAIResponseRequest |
    idempotency_key = 'idempotency_key_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Openai Responses
        api_response = api_instance.openai_responses_v1_responses_post(open_ai_response_request, idempotency_key=idempotency_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionsApi->openai_responses_v1_responses_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->openai_responses_v1_responses_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **open_ai_response_request** | **OpenAIResponseRequest**|  |
 **idempotency_key** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**OpenAIResponse**

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

# **post_agent_session_message_api_v1_agent_sessions_service_session_id_messages_post**
> post_agent_session_message_api_v1_agent_sessions_service_session_id_messages_post(service_session_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Post Agent Session Message

Reject follow-up turns until the durable turn mapping is implemented.

### Example


```python
import amesh_client
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    service_session_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Post Agent Session Message
        api_instance.post_agent_session_message_api_v1_agent_sessions_service_session_id_messages_post(service_session_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->post_agent_session_message_api_v1_agent_sessions_service_session_id_messages_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_session_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**409** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stream_agent_session_events_api_v1_agent_sessions_service_session_id_events_stream_get**
> stream_agent_session_events_api_v1_agent_sessions_service_session_id_events_stream_get(service_session_id, after_event_index=after_event_index, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Stream Agent Session Events

Stream durable redacted events with a bounded reconnectable poll window.

### Example


```python
import amesh_client
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
    api_instance = amesh_client.AgentSessionsApi(api_client)
    service_session_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    after_event_index = 0 # int |  (optional) (default to 0)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Stream Agent Session Events
        api_instance.stream_agent_session_events_api_v1_agent_sessions_service_session_id_events_stream_get(service_session_id, after_event_index=after_event_index, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling AgentSessionsApi->stream_agent_session_events_api_v1_agent_sessions_service_session_id_events_stream_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **service_session_id** | **UUID**|  |
 **after_event_index** | **int**|  | [optional] [default to 0]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

void (empty response body)

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
