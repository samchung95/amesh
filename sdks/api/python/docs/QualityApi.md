# amesh_client.QualityApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_differential_api_v1_namespaces_namespace_differentials_idempotency_key_get**](QualityApi.md#get_differential_api_v1_namespaces_namespace_differentials_idempotency_key_get) | **GET** /api/v1/namespaces/{namespace}/differentials/{idempotency_key} | Get Differential
[**run_differential_api_v1_namespaces_namespace_differentials_post**](QualityApi.md#run_differential_api_v1_namespaces_namespace_differentials_post) | **POST** /api/v1/namespaces/{namespace}/differentials | Run Differential


# **get_differential_api_v1_namespaces_namespace_differentials_idempotency_key_get**
> ComparisonReport get_differential_api_v1_namespaces_namespace_differentials_idempotency_key_get(namespace, idempotency_key, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Get Differential

### Example


```python
import amesh_client
from amesh_client.models.comparison_report import ComparisonReport
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
    api_instance = amesh_client.QualityApi(api_client)
    namespace = 'namespace_example' # str |
    idempotency_key = 'idempotency_key_example' # str |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Get Differential
        api_response = api_instance.get_differential_api_v1_namespaces_namespace_differentials_idempotency_key_get(namespace, idempotency_key, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of QualityApi->get_differential_api_v1_namespaces_namespace_differentials_idempotency_key_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QualityApi->get_differential_api_v1_namespaces_namespace_differentials_idempotency_key_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **idempotency_key** | **str**|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**ComparisonReport**](ComparisonReport.md)

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

# **run_differential_api_v1_namespaces_namespace_differentials_post**
> ComparisonReport run_differential_api_v1_namespaces_namespace_differentials_post(namespace, differential_spec, idempotency_key=idempotency_key, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Run Differential

### Example


```python
import amesh_client
from amesh_client.models.comparison_report import ComparisonReport
from amesh_client.models.differential_spec import DifferentialSpec
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
    api_instance = amesh_client.QualityApi(api_client)
    namespace = 'namespace_example' # str |
    differential_spec = amesh_client.DifferentialSpec() # DifferentialSpec |
    idempotency_key = 'idempotency_key_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Run Differential
        api_response = api_instance.run_differential_api_v1_namespaces_namespace_differentials_post(namespace, differential_spec, idempotency_key=idempotency_key, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of QualityApi->run_differential_api_v1_namespaces_namespace_differentials_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling QualityApi->run_differential_api_v1_namespaces_namespace_differentials_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **differential_spec** | [**DifferentialSpec**](DifferentialSpec.md)|  |
 **idempotency_key** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**ComparisonReport**](ComparisonReport.md)

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
