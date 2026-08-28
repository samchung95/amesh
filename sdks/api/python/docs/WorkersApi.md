# amesh_client.WorkersApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**drain_worker_api_v1_workers_worker_id_drain_post**](WorkersApi.md#drain_worker_api_v1_workers_worker_id_drain_post) | **POST** /api/v1/workers/{worker_id}/drain | Drain Worker
[**list_runner_capabilities_api_v1_runners_capabilities_get**](WorkersApi.md#list_runner_capabilities_api_v1_runners_capabilities_get) | **GET** /api/v1/runners/capabilities | List Runner Capabilities
[**list_workers_api_v1_workers_get**](WorkersApi.md#list_workers_api_v1_workers_get) | **GET** /api/v1/workers | List Workers


# **drain_worker_api_v1_workers_worker_id_drain_post**
> WorkerInventory drain_worker_api_v1_workers_worker_id_drain_post(worker_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Drain Worker

### Example


```python
import amesh_client
from amesh_client.models.worker_inventory import WorkerInventory
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
    api_instance = amesh_client.WorkersApi(api_client)
    worker_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    expected_version = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Drain Worker
        api_response = api_instance.drain_worker_api_v1_workers_worker_id_drain_post(worker_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of WorkersApi->drain_worker_api_v1_workers_worker_id_drain_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkersApi->drain_worker_api_v1_workers_worker_id_drain_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **worker_id** | **UUID**|  |
 **expected_version** | **int**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**WorkerInventory**

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

# **list_runner_capabilities_api_v1_runners_capabilities_get**
> List[RunnerCapabilities] list_runner_capabilities_api_v1_runners_capabilities_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Runner Capabilities

### Example


```python
import amesh_client
from amesh_client.models.runner_capabilities import RunnerCapabilities
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
    api_instance = amesh_client.WorkersApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Runner Capabilities
        api_response = api_instance.list_runner_capabilities_api_v1_runners_capabilities_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of WorkersApi->list_runner_capabilities_api_v1_runners_capabilities_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkersApi->list_runner_capabilities_api_v1_runners_capabilities_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[RunnerCapabilities]**](RunnerCapabilities.md)

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

# **list_workers_api_v1_workers_get**
> List[WorkerInventory] list_workers_api_v1_workers_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Workers

### Example


```python
import amesh_client
from amesh_client.models.worker_inventory import WorkerInventory
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
    api_instance = amesh_client.WorkersApi(api_client)
    cursor = 'cursor_example' # str | Opaque cursor from the prior page (optional)
    limit = 56 # int |  (optional)
    filter = ['filter_example'] # List[str] | Repeatable top-level equality filter in field=value form (optional)
    sort = 'sort_example' # str | Comma-separated top-level fields; prefix descending fields with - (optional)
    fields = 'fields_example' # str | Comma-separated top-level response fields (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Workers
        api_response = api_instance.list_workers_api_v1_workers_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of WorkersApi->list_workers_api_v1_workers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WorkersApi->list_workers_api_v1_workers_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **str**| Opaque cursor from the prior page | [optional]
 **limit** | **int**|  | [optional]
 **filter** | [**List[str]**](str.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional]
 **sort** | **str**| Comma-separated top-level fields; prefix descending fields with - | [optional]
 **fields** | **str**| Comma-separated top-level response fields | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[WorkerInventory]**](WorkerInventory.md)

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
