# amesh_client.HumanTasksApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**act_on_human_task_api_v1_human_tasks_human_task_id_actions_post**](HumanTasksApi.md#act_on_human_task_api_v1_human_tasks_human_task_id_actions_post) | **POST** /api/v1/human-tasks/{human_task_id}/actions | Act On Human Task
[**list_human_task_notifications_api_v1_human_task_notifications_get**](HumanTasksApi.md#list_human_task_notifications_api_v1_human_task_notifications_get) | **GET** /api/v1/human-task-notifications | List Human Task Notifications
[**list_human_tasks_api_v1_human_tasks_get**](HumanTasksApi.md#list_human_tasks_api_v1_human_tasks_get) | **GET** /api/v1/human-tasks | List Human Tasks


# **act_on_human_task_api_v1_human_tasks_human_task_id_actions_post**
> HumanTask act_on_human_task_api_v1_human_tasks_human_task_id_actions_post(human_task_id, human_task_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Act On Human Task

### Example


```python
import amesh_client
from amesh_client.models.human_task import HumanTask
from amesh_client.models.human_task_action_request import HumanTaskActionRequest
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
    api_instance = amesh_client.HumanTasksApi(api_client)
    human_task_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    human_task_action_request = amesh_client.HumanTaskActionRequest() # HumanTaskActionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Act On Human Task
        api_response = api_instance.act_on_human_task_api_v1_human_tasks_human_task_id_actions_post(human_task_id, human_task_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of HumanTasksApi->act_on_human_task_api_v1_human_tasks_human_task_id_actions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HumanTasksApi->act_on_human_task_api_v1_human_tasks_human_task_id_actions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **human_task_id** | **UUID**|  |
 **human_task_action_request** | [**HumanTaskActionRequest**](HumanTaskActionRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**HumanTask**](HumanTask.md)

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

# **list_human_task_notifications_api_v1_human_task_notifications_get**
> List[HumanTaskNotification] list_human_task_notifications_api_v1_human_task_notifications_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Human Task Notifications

### Example


```python
import amesh_client
from amesh_client.models.human_task_notification import HumanTaskNotification
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
    api_instance = amesh_client.HumanTasksApi(api_client)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Human Task Notifications
        api_response = api_instance.list_human_task_notifications_api_v1_human_task_notifications_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of HumanTasksApi->list_human_task_notifications_api_v1_human_task_notifications_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HumanTasksApi->list_human_task_notifications_api_v1_human_task_notifications_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[HumanTaskNotification]**](HumanTaskNotification.md)

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

# **list_human_tasks_api_v1_human_tasks_get**
> List[HumanTask] list_human_tasks_api_v1_human_tasks_get(namespace=namespace, include_closed=include_closed, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Human Tasks

### Example


```python
import amesh_client
from amesh_client.models.human_task import HumanTask
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
    api_instance = amesh_client.HumanTasksApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    include_closed = False # bool |  (optional) (default to False)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Human Tasks
        api_response = api_instance.list_human_tasks_api_v1_human_tasks_get(namespace=namespace, include_closed=include_closed, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of HumanTasksApi->list_human_tasks_api_v1_human_tasks_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HumanTasksApi->list_human_tasks_api_v1_human_tasks_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **include_closed** | **bool**|  | [optional] [default to False]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[HumanTask]**](HumanTask.md)

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
