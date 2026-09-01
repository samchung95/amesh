# amesh_client.ModelEnginesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**account_login_start_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_login_post**](ModelEnginesApi.md#account_login_start_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_login_post) | **POST** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/login | Account Login Start
[**account_logout_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_logout_post**](ModelEnginesApi.md#account_logout_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_logout_post) | **POST** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/logout | Account Logout
[**account_status_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_status_get**](ModelEnginesApi.md#account_status_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_status_get) | **GET** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/status | Account Status
[**catalog_api_v1_namespaces_namespace_model_engines_catalog_get**](ModelEnginesApi.md#catalog_api_v1_namespaces_namespace_model_engines_catalog_get) | **GET** /api/v1/namespaces/{namespace}/model-engines/catalog | Catalog


# **account_login_start_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_login_post**
> ModelEngineLoginStartResponse account_login_start_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_login_post(namespace, adapter, engine_ref, model_engine_login_request, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Account Login Start

### Example


```python
import amesh_client
from amesh_client.models.model_engine_login_request import ModelEngineLoginRequest
from amesh_client.models.model_engine_login_start_response import ModelEngineLoginStartResponse
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
    api_instance = amesh_client.ModelEnginesApi(api_client)
    namespace = 'namespace_example' # str |
    adapter = 'adapter_example' # str |
    engine_ref = 'engine_ref_example' # str |
    model_engine_login_request = amesh_client.ModelEngineLoginRequest() # ModelEngineLoginRequest |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Account Login Start
        api_response = api_instance.account_login_start_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_login_post(namespace, adapter, engine_ref, model_engine_login_request, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ModelEnginesApi->account_login_start_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_login_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelEnginesApi->account_login_start_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_login_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **adapter** | **str**|  |
 **engine_ref** | **str**|  |
 **model_engine_login_request** | **ModelEngineLoginRequest**|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**ModelEngineLoginStartResponse**

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

# **account_logout_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_logout_post**
> ModelEngineLogoutResponse account_logout_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_logout_post(namespace, adapter, engine_ref, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Account Logout

### Example


```python
import amesh_client
from amesh_client.models.model_engine_logout_response import ModelEngineLogoutResponse
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
    api_instance = amesh_client.ModelEnginesApi(api_client)
    namespace = 'namespace_example' # str |
    adapter = 'adapter_example' # str |
    engine_ref = 'engine_ref_example' # str |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Account Logout
        api_response = api_instance.account_logout_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_logout_post(namespace, adapter, engine_ref, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ModelEnginesApi->account_logout_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_logout_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelEnginesApi->account_logout_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_logout_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **adapter** | **str**|  |
 **engine_ref** | **str**|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**ModelEngineLogoutResponse**

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

# **account_status_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_status_get**
> ModelEngineAccountStatusResponse account_status_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_status_get(namespace, adapter, engine_ref, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Account Status

### Example


```python
import amesh_client
from amesh_client.models.model_engine_account_status_response import ModelEngineAccountStatusResponse
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
    api_instance = amesh_client.ModelEnginesApi(api_client)
    namespace = 'namespace_example' # str |
    adapter = 'adapter_example' # str |
    engine_ref = 'engine_ref_example' # str |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Account Status
        api_response = api_instance.account_status_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_status_get(namespace, adapter, engine_ref, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ModelEnginesApi->account_status_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelEnginesApi->account_status_api_v1_namespaces_namespace_model_engines_adapter_engine_ref_status_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **adapter** | **str**|  |
 **engine_ref** | **str**|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**ModelEngineAccountStatusResponse**

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

# **catalog_api_v1_namespaces_namespace_model_engines_catalog_get**
> ModelEngineCatalog catalog_api_v1_namespaces_namespace_model_engines_catalog_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Catalog

### Example


```python
import amesh_client
from amesh_client.models.model_engine_catalog import ModelEngineCatalog
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
    api_instance = amesh_client.ModelEnginesApi(api_client)
    namespace = 'namespace_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Catalog
        api_response = api_instance.catalog_api_v1_namespaces_namespace_model_engines_catalog_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ModelEnginesApi->catalog_api_v1_namespaces_namespace_model_engines_catalog_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelEnginesApi->catalog_api_v1_namespaces_namespace_model_engines_catalog_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**ModelEngineCatalog**

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
