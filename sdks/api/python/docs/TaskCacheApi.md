# amesh_client.TaskCacheApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**list_task_cache_entries_api_v1_task_cache_get**](TaskCacheApi.md#list_task_cache_entries_api_v1_task_cache_get) | **GET** /api/v1/task-cache | List Task Cache Entries
[**purge_task_cache_entries_api_v1_task_cache_purge_post**](TaskCacheApi.md#purge_task_cache_entries_api_v1_task_cache_purge_post) | **POST** /api/v1/task-cache/purge | Purge Task Cache Entries


# **list_task_cache_entries_api_v1_task_cache_get**
> List[TaskCacheEntry] list_task_cache_entries_api_v1_task_cache_get(key_prefix=key_prefix, namespace=namespace, flow_id=flow_id, task_id=task_id, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Task Cache Entries

### Example


```python
import amesh_client
from amesh_client.models.task_cache_entry import TaskCacheEntry
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
    api_instance = amesh_client.TaskCacheApi(api_client)
    key_prefix = 'key_prefix_example' # str |  (optional)
    namespace = 'namespace_example' # str |  (optional)
    flow_id = 'flow_id_example' # str |  (optional)
    task_id = 'task_id_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Task Cache Entries
        api_response = api_instance.list_task_cache_entries_api_v1_task_cache_get(key_prefix=key_prefix, namespace=namespace, flow_id=flow_id, task_id=task_id, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of TaskCacheApi->list_task_cache_entries_api_v1_task_cache_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TaskCacheApi->list_task_cache_entries_api_v1_task_cache_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key_prefix** | **str**|  | [optional]
 **namespace** | **str**|  | [optional]
 **flow_id** | **str**|  | [optional]
 **task_id** | **str**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[TaskCacheEntry]**](TaskCacheEntry.md)

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

# **purge_task_cache_entries_api_v1_task_cache_purge_post**
> TaskCachePurgeResult purge_task_cache_entries_api_v1_task_cache_purge_post(task_cache_purge_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Purge Task Cache Entries

### Example


```python
import amesh_client
from amesh_client.models.task_cache_purge_request import TaskCachePurgeRequest
from amesh_client.models.task_cache_purge_result import TaskCachePurgeResult
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
    api_instance = amesh_client.TaskCacheApi(api_client)
    task_cache_purge_request = amesh_client.TaskCachePurgeRequest() # TaskCachePurgeRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Purge Task Cache Entries
        api_response = api_instance.purge_task_cache_entries_api_v1_task_cache_purge_post(task_cache_purge_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of TaskCacheApi->purge_task_cache_entries_api_v1_task_cache_purge_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TaskCacheApi->purge_task_cache_entries_api_v1_task_cache_purge_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **task_cache_purge_request** | **TaskCachePurgeRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**TaskCachePurgeResult**

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
