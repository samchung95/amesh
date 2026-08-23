# amesh_client.CompatibilityApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_kestra_execution_api_v1_executions_namespace_flow_id_post**](CompatibilityApi.md#create_kestra_execution_api_v1_executions_namespace_flow_id_post) | **POST** /api/v1/executions/{namespace}/{flow_id} | Create Kestra Execution
[**get_kestra_compatibility_manifest_api_v1_compatibility_kestra_manifest_get**](CompatibilityApi.md#get_kestra_compatibility_manifest_api_v1_compatibility_kestra_manifest_get) | **GET** /api/v1/compatibility/kestra/manifest | Get Kestra Compatibility Manifest
[**validate_kestra_flow_api_v1_main_flows_validate_post**](CompatibilityApi.md#validate_kestra_flow_api_v1_main_flows_validate_post) | **POST** /api/v1/main/flows/validate | Validate Kestra Flow


# **create_kestra_execution_api_v1_executions_namespace_flow_id_post**
> ExecutionDetail create_kestra_execution_api_v1_executions_namespace_flow_id_post(namespace, flow_id, kestra_execution_request, prefer=prefer, idempotency_key=idempotency_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Kestra Execution

### Example


```python
import amesh_client
from amesh_client.models.execution_detail import ExecutionDetail
from amesh_client.models.kestra_execution_request import KestraExecutionRequest
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
    api_instance = amesh_client.CompatibilityApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    kestra_execution_request = amesh_client.KestraExecutionRequest() # KestraExecutionRequest |
    prefer = 'prefer_example' # str |  (optional)
    idempotency_key = 'idempotency_key_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Kestra Execution
        api_response = api_instance.create_kestra_execution_api_v1_executions_namespace_flow_id_post(namespace, flow_id, kestra_execution_request, prefer=prefer, idempotency_key=idempotency_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of CompatibilityApi->create_kestra_execution_api_v1_executions_namespace_flow_id_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CompatibilityApi->create_kestra_execution_api_v1_executions_namespace_flow_id_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **kestra_execution_request** | [**KestraExecutionRequest**](KestraExecutionRequest.md)|  |
 **prefer** | **str**|  | [optional]
 **idempotency_key** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**202** | Execution persisted and accepted for asynchronous processing |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_kestra_compatibility_manifest_api_v1_compatibility_kestra_manifest_get**
> Dict[str, Optional[object]] get_kestra_compatibility_manifest_api_v1_compatibility_kestra_manifest_get()

Get Kestra Compatibility Manifest

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
    api_instance = amesh_client.CompatibilityApi(api_client)

    try:
        # Get Kestra Compatibility Manifest
        api_response = api_instance.get_kestra_compatibility_manifest_api_v1_compatibility_kestra_manifest_get()
        print("The response of CompatibilityApi->get_kestra_compatibility_manifest_api_v1_compatibility_kestra_manifest_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CompatibilityApi->get_kestra_compatibility_manifest_api_v1_compatibility_kestra_manifest_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**Dict[str, Optional[object]]**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **validate_kestra_flow_api_v1_main_flows_validate_post**
> KestraFlowImport validate_kestra_flow_api_v1_main_flows_validate_post()

Validate Kestra Flow

### Example


```python
import amesh_client
from amesh_client.models.kestra_flow_import import KestraFlowImport
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
    api_instance = amesh_client.CompatibilityApi(api_client)

    try:
        # Validate Kestra Flow
        api_response = api_instance.validate_kestra_flow_api_v1_main_flows_validate_post()
        print("The response of CompatibilityApi->validate_kestra_flow_api_v1_main_flows_validate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CompatibilityApi->validate_kestra_flow_api_v1_main_flows_validate_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**KestraFlowImport**](KestraFlowImport.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
