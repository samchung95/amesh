# amesh_client.AppsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_workflow_app_api_v1_apps_namespace_app_id_get**](AppsApi.md#get_workflow_app_api_v1_apps_namespace_app_id_get) | **GET** /api/v1/apps/{namespace}/{app_id} | Get Workflow App
[**launch_workflow_app_api_v1_apps_namespace_app_id_launch_post**](AppsApi.md#launch_workflow_app_api_v1_apps_namespace_app_id_launch_post) | **POST** /api/v1/apps/{namespace}/{app_id}/launch | Launch Workflow App
[**list_workflow_apps_api_v1_apps_get**](AppsApi.md#list_workflow_apps_api_v1_apps_get) | **GET** /api/v1/apps | List Workflow Apps
[**upsert_workflow_app_api_v1_apps_namespace_app_id_put**](AppsApi.md#upsert_workflow_app_api_v1_apps_namespace_app_id_put) | **PUT** /api/v1/apps/{namespace}/{app_id} | Upsert Workflow App


# **get_workflow_app_api_v1_apps_namespace_app_id_get**
> WorkflowApp get_workflow_app_api_v1_apps_namespace_app_id_get(namespace, app_id, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Workflow App

### Example


```python
import amesh_client
from amesh_client.models.workflow_app import WorkflowApp
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
    api_instance = amesh_client.AppsApi(api_client)
    namespace = 'namespace_example' # str |
    app_id = 'app_id_example' # str |
    revision = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Workflow App
        api_response = api_instance.get_workflow_app_api_v1_apps_namespace_app_id_get(namespace, app_id, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AppsApi->get_workflow_app_api_v1_apps_namespace_app_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppsApi->get_workflow_app_api_v1_apps_namespace_app_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **app_id** | **str**|  |
 **revision** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**WorkflowApp**

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

# **launch_workflow_app_api_v1_apps_namespace_app_id_launch_post**
> ExecutionDetail launch_workflow_app_api_v1_apps_namespace_app_id_launch_post(namespace, app_id, workflow_app_launch_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Launch Workflow App

### Example


```python
import amesh_client
from amesh_client.models.execution_detail import ExecutionDetail
from amesh_client.models.workflow_app_launch_request import WorkflowAppLaunchRequest
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
    api_instance = amesh_client.AppsApi(api_client)
    namespace = 'namespace_example' # str |
    app_id = 'app_id_example' # str |
    workflow_app_launch_request = amesh_client.WorkflowAppLaunchRequest() # WorkflowAppLaunchRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Launch Workflow App
        api_response = api_instance.launch_workflow_app_api_v1_apps_namespace_app_id_launch_post(namespace, app_id, workflow_app_launch_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AppsApi->launch_workflow_app_api_v1_apps_namespace_app_id_launch_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppsApi->launch_workflow_app_api_v1_apps_namespace_app_id_launch_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **app_id** | **str**|  |
 **workflow_app_launch_request** | **WorkflowAppLaunchRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**ExecutionDetail**

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

# **list_workflow_apps_api_v1_apps_get**
> List[WorkflowApp] list_workflow_apps_api_v1_apps_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Workflow Apps

### Example


```python
import amesh_client
from amesh_client.models.workflow_app import WorkflowApp
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
    api_instance = amesh_client.AppsApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Workflow Apps
        api_response = api_instance.list_workflow_apps_api_v1_apps_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AppsApi->list_workflow_apps_api_v1_apps_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppsApi->list_workflow_apps_api_v1_apps_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[WorkflowApp]**](WorkflowApp.md)

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

# **upsert_workflow_app_api_v1_apps_namespace_app_id_put**
> WorkflowApp upsert_workflow_app_api_v1_apps_namespace_app_id_put(namespace, app_id, workflow_app_upsert_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Upsert Workflow App

### Example


```python
import amesh_client
from amesh_client.models.workflow_app import WorkflowApp
from amesh_client.models.workflow_app_upsert_request import WorkflowAppUpsertRequest
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
    api_instance = amesh_client.AppsApi(api_client)
    namespace = 'namespace_example' # str |
    app_id = 'app_id_example' # str |
    workflow_app_upsert_request = amesh_client.WorkflowAppUpsertRequest() # WorkflowAppUpsertRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Upsert Workflow App
        api_response = api_instance.upsert_workflow_app_api_v1_apps_namespace_app_id_put(namespace, app_id, workflow_app_upsert_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AppsApi->upsert_workflow_app_api_v1_apps_namespace_app_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AppsApi->upsert_workflow_app_api_v1_apps_namespace_app_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **app_id** | **str**|  |
 **workflow_app_upsert_request** | **WorkflowAppUpsertRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**WorkflowApp**

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
