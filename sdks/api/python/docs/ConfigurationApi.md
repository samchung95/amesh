# amesh_client.ConfigurationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**evaluate_feature_flag_api_v1_feature_flags_key_evaluate_get**](ConfigurationApi.md#evaluate_feature_flag_api_v1_feature_flags_key_evaluate_get) | **GET** /api/v1/feature-flags/{key}/evaluate | Evaluate Feature Flag
[**get_configuration_diagnostics_api_v1_configuration_diagnostics_get**](ConfigurationApi.md#get_configuration_diagnostics_api_v1_configuration_diagnostics_get) | **GET** /api/v1/configuration/diagnostics | Get Configuration Diagnostics
[**get_effective_configuration_api_v1_configuration_get**](ConfigurationApi.md#get_effective_configuration_api_v1_configuration_get) | **GET** /api/v1/configuration | Get Effective Configuration
[**list_feature_flags_api_v1_feature_flags_get**](ConfigurationApi.md#list_feature_flags_api_v1_feature_flags_get) | **GET** /api/v1/feature-flags | List Feature Flags
[**put_feature_flag_api_v1_feature_flags_key_put**](ConfigurationApi.md#put_feature_flag_api_v1_feature_flags_key_put) | **PUT** /api/v1/feature-flags/{key} | Put Feature Flag
[**reload_configuration_api_v1_configuration_reload_post**](ConfigurationApi.md#reload_configuration_api_v1_configuration_reload_post) | **POST** /api/v1/configuration/reload | Reload Configuration


# **evaluate_feature_flag_api_v1_feature_flags_key_evaluate_get**
> FeatureFlagDecision evaluate_feature_flag_api_v1_feature_flags_key_evaluate_get(key, namespace=namespace, default=default, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Evaluate Feature Flag

### Example


```python
import amesh_client
from amesh_client.models.feature_flag_decision import FeatureFlagDecision
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
    api_instance = amesh_client.ConfigurationApi(api_client)
    key = 'key_example' # str |
    namespace = 'namespace_example' # str |  (optional)
    default = False # bool |  (optional) (default to False)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Evaluate Feature Flag
        api_response = api_instance.evaluate_feature_flag_api_v1_feature_flags_key_evaluate_get(key, namespace=namespace, default=default, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ConfigurationApi->evaluate_feature_flag_api_v1_feature_flags_key_evaluate_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigurationApi->evaluate_feature_flag_api_v1_feature_flags_key_evaluate_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**|  |
 **namespace** | **str**|  | [optional]
 **default** | **bool**|  | [optional] [default to False]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**FeatureFlagDecision**](FeatureFlagDecision.md)

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

# **get_configuration_diagnostics_api_v1_configuration_diagnostics_get**
> ConfigurationDiagnosticBundle get_configuration_diagnostics_api_v1_configuration_diagnostics_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Configuration Diagnostics

### Example


```python
import amesh_client
from amesh_client.models.configuration_diagnostic_bundle import ConfigurationDiagnosticBundle
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
    api_instance = amesh_client.ConfigurationApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Configuration Diagnostics
        api_response = api_instance.get_configuration_diagnostics_api_v1_configuration_diagnostics_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ConfigurationApi->get_configuration_diagnostics_api_v1_configuration_diagnostics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigurationApi->get_configuration_diagnostics_api_v1_configuration_diagnostics_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ConfigurationDiagnosticBundle**](ConfigurationDiagnosticBundle.md)

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

# **get_effective_configuration_api_v1_configuration_get**
> ConfigurationSnapshot get_effective_configuration_api_v1_configuration_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Get Effective Configuration

### Example


```python
import amesh_client
from amesh_client.models.configuration_snapshot import ConfigurationSnapshot
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
    api_instance = amesh_client.ConfigurationApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Get Effective Configuration
        api_response = api_instance.get_effective_configuration_api_v1_configuration_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ConfigurationApi->get_effective_configuration_api_v1_configuration_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigurationApi->get_effective_configuration_api_v1_configuration_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**ConfigurationSnapshot**](ConfigurationSnapshot.md)

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

# **list_feature_flags_api_v1_feature_flags_get**
> List[FeatureFlag] list_feature_flags_api_v1_feature_flags_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Feature Flags

### Example


```python
import amesh_client
from amesh_client.models.feature_flag import FeatureFlag
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
    api_instance = amesh_client.ConfigurationApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Feature Flags
        api_response = api_instance.list_feature_flags_api_v1_feature_flags_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ConfigurationApi->list_feature_flags_api_v1_feature_flags_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigurationApi->list_feature_flags_api_v1_feature_flags_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[FeatureFlag]**](FeatureFlag.md)

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

# **put_feature_flag_api_v1_feature_flags_key_put**
> FeatureFlag put_feature_flag_api_v1_feature_flags_key_put(key, feature_flag_upsert_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Put Feature Flag

### Example


```python
import amesh_client
from amesh_client.models.feature_flag import FeatureFlag
from amesh_client.models.feature_flag_upsert_request import FeatureFlagUpsertRequest
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
    api_instance = amesh_client.ConfigurationApi(api_client)
    key = 'key_example' # str |
    feature_flag_upsert_request = amesh_client.FeatureFlagUpsertRequest() # FeatureFlagUpsertRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Put Feature Flag
        api_response = api_instance.put_feature_flag_api_v1_feature_flags_key_put(key, feature_flag_upsert_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ConfigurationApi->put_feature_flag_api_v1_feature_flags_key_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigurationApi->put_feature_flag_api_v1_feature_flags_key_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | **str**|  |
 **feature_flag_upsert_request** | [**FeatureFlagUpsertRequest**](FeatureFlagUpsertRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**FeatureFlag**](FeatureFlag.md)

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

# **reload_configuration_api_v1_configuration_reload_post**
> ConfigurationSnapshot reload_configuration_api_v1_configuration_reload_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Reload Configuration

### Example


```python
import amesh_client
from amesh_client.models.configuration_snapshot import ConfigurationSnapshot
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
    api_instance = amesh_client.ConfigurationApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Reload Configuration
        api_response = api_instance.reload_configuration_api_v1_configuration_reload_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ConfigurationApi->reload_configuration_api_v1_configuration_reload_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ConfigurationApi->reload_configuration_api_v1_configuration_reload_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**ConfigurationSnapshot**](ConfigurationSnapshot.md)

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
