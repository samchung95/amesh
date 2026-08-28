# amesh_client.FlowTestsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_flow_test_api_v1_flows_namespace_flow_id_tests_test_id_delete**](FlowTestsApi.md#delete_flow_test_api_v1_flows_namespace_flow_id_tests_test_id_delete) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/tests/{test_id} | Delete Flow Test
[**get_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_get**](FlowTestsApi.md#get_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_get) | **GET** /api/v1/namespaces/{namespace}/flow-test-gate | Get Flow Test Gate
[**list_flow_test_runs_api_v1_flows_namespace_flow_id_tests_runs_get**](FlowTestsApi.md#list_flow_test_runs_api_v1_flows_namespace_flow_id_tests_runs_get) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests/runs | List Flow Test Runs
[**list_flow_tests_api_v1_flows_namespace_flow_id_tests_get**](FlowTestsApi.md#list_flow_tests_api_v1_flows_namespace_flow_id_tests_get) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests | List Flow Tests
[**run_flow_tests_api_v1_flows_namespace_flow_id_tests_runs_post**](FlowTestsApi.md#run_flow_tests_api_v1_flows_namespace_flow_id_tests_runs_post) | **POST** /api/v1/flows/{namespace}/{flow_id}/tests/runs | Run Flow Tests
[**save_flow_test_api_v1_flows_namespace_flow_id_tests_put**](FlowTestsApi.md#save_flow_test_api_v1_flows_namespace_flow_id_tests_put) | **PUT** /api/v1/flows/{namespace}/{flow_id}/tests | Save Flow Test
[**update_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_put**](FlowTestsApi.md#update_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_put) | **PUT** /api/v1/namespaces/{namespace}/flow-test-gate | Update Flow Test Gate


# **delete_flow_test_api_v1_flows_namespace_flow_id_tests_test_id_delete**
> delete_flow_test_api_v1_flows_namespace_flow_id_tests_test_id_delete(namespace, flow_id, test_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Delete Flow Test

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
    api_instance = amesh_client.FlowTestsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    test_id = 'test_id_example' # str |
    expected_version = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Delete Flow Test
        api_instance.delete_flow_test_api_v1_flows_namespace_flow_id_tests_test_id_delete(namespace, flow_id, test_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling FlowTestsApi->delete_flow_test_api_v1_flows_namespace_flow_id_tests_test_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **test_id** | **str**|  |
 **expected_version** | **int**|  |
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
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_get**
> FlowTestQualityGate get_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Flow Test Gate

### Example


```python
import amesh_client
from amesh_client.models.flow_test_quality_gate import FlowTestQualityGate
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
    api_instance = amesh_client.FlowTestsApi(api_client)
    namespace = 'namespace_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Flow Test Gate
        api_response = api_instance.get_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowTestsApi->get_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowTestsApi->get_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**FlowTestQualityGate**

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

# **list_flow_test_runs_api_v1_flows_namespace_flow_id_tests_runs_get**
> List[FlowTestRunResult] list_flow_test_runs_api_v1_flows_namespace_flow_id_tests_runs_get(namespace, flow_id, revision=revision, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Flow Test Runs

### Example


```python
import amesh_client
from amesh_client.models.flow_test_run_result import FlowTestRunResult
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
    api_instance = amesh_client.FlowTestsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    revision = 56 # int |  (optional)
    limit = 50 # int |  (optional) (default to 50)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Flow Test Runs
        api_response = api_instance.list_flow_test_runs_api_v1_flows_namespace_flow_id_tests_runs_get(namespace, flow_id, revision=revision, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowTestsApi->list_flow_test_runs_api_v1_flows_namespace_flow_id_tests_runs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowTestsApi->list_flow_test_runs_api_v1_flows_namespace_flow_id_tests_runs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **revision** | **int**|  | [optional]
 **limit** | **int**|  | [optional] [default to 50]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[FlowTestRunResult]**](FlowTestRunResult.md)

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

# **list_flow_tests_api_v1_flows_namespace_flow_id_tests_get**
> List[FlowTestDefinition] list_flow_tests_api_v1_flows_namespace_flow_id_tests_get(namespace, flow_id, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Flow Tests

### Example


```python
import amesh_client
from amesh_client.models.flow_test_definition import FlowTestDefinition
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
    api_instance = amesh_client.FlowTestsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    revision = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Flow Tests
        api_response = api_instance.list_flow_tests_api_v1_flows_namespace_flow_id_tests_get(namespace, flow_id, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowTestsApi->list_flow_tests_api_v1_flows_namespace_flow_id_tests_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowTestsApi->list_flow_tests_api_v1_flows_namespace_flow_id_tests_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **revision** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[FlowTestDefinition]**](FlowTestDefinition.md)

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

# **run_flow_tests_api_v1_flows_namespace_flow_id_tests_runs_post**
> FlowTestRunResult run_flow_tests_api_v1_flows_namespace_flow_id_tests_runs_post(namespace, flow_id, revision, flow_test_run_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Run Flow Tests

### Example


```python
import amesh_client
from amesh_client.models.flow_test_run_request import FlowTestRunRequest
from amesh_client.models.flow_test_run_result import FlowTestRunResult
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
    api_instance = amesh_client.FlowTestsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    revision = 56 # int |
    flow_test_run_request = amesh_client.FlowTestRunRequest() # FlowTestRunRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Run Flow Tests
        api_response = api_instance.run_flow_tests_api_v1_flows_namespace_flow_id_tests_runs_post(namespace, flow_id, revision, flow_test_run_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowTestsApi->run_flow_tests_api_v1_flows_namespace_flow_id_tests_runs_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowTestsApi->run_flow_tests_api_v1_flows_namespace_flow_id_tests_runs_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **revision** | **int**|  |
 **flow_test_run_request** | **FlowTestRunRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**FlowTestRunResult**

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

# **save_flow_test_api_v1_flows_namespace_flow_id_tests_put**
> FlowTestDefinition save_flow_test_api_v1_flows_namespace_flow_id_tests_put(namespace, flow_id, flow_test_definition_create_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Save Flow Test

### Example


```python
import amesh_client
from amesh_client.models.flow_test_definition import FlowTestDefinition
from amesh_client.models.flow_test_definition_create_request import FlowTestDefinitionCreateRequest
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
    api_instance = amesh_client.FlowTestsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    flow_test_definition_create_request = amesh_client.FlowTestDefinitionCreateRequest() # FlowTestDefinitionCreateRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Save Flow Test
        api_response = api_instance.save_flow_test_api_v1_flows_namespace_flow_id_tests_put(namespace, flow_id, flow_test_definition_create_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowTestsApi->save_flow_test_api_v1_flows_namespace_flow_id_tests_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowTestsApi->save_flow_test_api_v1_flows_namespace_flow_id_tests_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **flow_test_definition_create_request** | **FlowTestDefinitionCreateRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**FlowTestDefinition**

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

# **update_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_put**
> FlowTestQualityGate update_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_put(namespace, flow_test_quality_gate_update, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Update Flow Test Gate

### Example


```python
import amesh_client
from amesh_client.models.flow_test_quality_gate import FlowTestQualityGate
from amesh_client.models.flow_test_quality_gate_update import FlowTestQualityGateUpdate
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
    api_instance = amesh_client.FlowTestsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_test_quality_gate_update = amesh_client.FlowTestQualityGateUpdate() # FlowTestQualityGateUpdate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Update Flow Test Gate
        api_response = api_instance.update_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_put(namespace, flow_test_quality_gate_update, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowTestsApi->update_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowTestsApi->update_flow_test_gate_api_v1_namespaces_namespace_flow_test_gate_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_test_quality_gate_update** | **FlowTestQualityGateUpdate**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**FlowTestQualityGate**

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
