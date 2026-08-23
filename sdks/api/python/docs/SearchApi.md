# amesh_client.SearchApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**control_search_projection_api_v1_search_control_post**](SearchApi.md#control_search_projection_api_v1_search_control_post) | **POST** /api/v1/search/control | Control Search Projection
[**get_search_status_api_v1_search_status_get**](SearchApi.md#get_search_status_api_v1_search_status_get) | **GET** /api/v1/search/status | Get Search Status
[**rebuild_search_projection_api_v1_search_rebuild_post**](SearchApi.md#rebuild_search_projection_api_v1_search_rebuild_post) | **POST** /api/v1/search/rebuild | Rebuild Search Projection
[**search_resources_api_v1_search_post**](SearchApi.md#search_resources_api_v1_search_post) | **POST** /api/v1/search | Search Resources
[**verify_search_projection_api_v1_search_verify_get**](SearchApi.md#verify_search_projection_api_v1_search_verify_get) | **GET** /api/v1/search/verify | Verify Search Projection


# **control_search_projection_api_v1_search_control_post**
> SearchProjectionStatus control_search_projection_api_v1_search_control_post(search_projection_control_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Control Search Projection

### Example


```python
import amesh_client
from amesh_client.models.search_projection_control_request import SearchProjectionControlRequest
from amesh_client.models.search_projection_status import SearchProjectionStatus
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
    api_instance = amesh_client.SearchApi(api_client)
    search_projection_control_request = amesh_client.SearchProjectionControlRequest() # SearchProjectionControlRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Control Search Projection
        api_response = api_instance.control_search_projection_api_v1_search_control_post(search_projection_control_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of SearchApi->control_search_projection_api_v1_search_control_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SearchApi->control_search_projection_api_v1_search_control_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_projection_control_request** | [**SearchProjectionControlRequest**](SearchProjectionControlRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**SearchProjectionStatus**](SearchProjectionStatus.md)

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

# **get_search_status_api_v1_search_status_get**
> SearchProjectionStatus get_search_status_api_v1_search_status_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Search Status

### Example


```python
import amesh_client
from amesh_client.models.search_projection_status import SearchProjectionStatus
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
    api_instance = amesh_client.SearchApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Search Status
        api_response = api_instance.get_search_status_api_v1_search_status_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of SearchApi->get_search_status_api_v1_search_status_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SearchApi->get_search_status_api_v1_search_status_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**SearchProjectionStatus**](SearchProjectionStatus.md)

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

# **rebuild_search_projection_api_v1_search_rebuild_post**
> SearchProjectionStatus rebuild_search_projection_api_v1_search_rebuild_post(search_rebuild_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Rebuild Search Projection

### Example


```python
import amesh_client
from amesh_client.models.search_projection_status import SearchProjectionStatus
from amesh_client.models.search_rebuild_request import SearchRebuildRequest
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
    api_instance = amesh_client.SearchApi(api_client)
    search_rebuild_request = amesh_client.SearchRebuildRequest() # SearchRebuildRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Rebuild Search Projection
        api_response = api_instance.rebuild_search_projection_api_v1_search_rebuild_post(search_rebuild_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of SearchApi->rebuild_search_projection_api_v1_search_rebuild_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SearchApi->rebuild_search_projection_api_v1_search_rebuild_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_rebuild_request** | [**SearchRebuildRequest**](SearchRebuildRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**SearchProjectionStatus**](SearchProjectionStatus.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**202** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_resources_api_v1_search_post**
> SearchResponse search_resources_api_v1_search_post(search_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Search Resources

### Example


```python
import amesh_client
from amesh_client.models.search_request import SearchRequest
from amesh_client.models.search_response import SearchResponse
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
    api_instance = amesh_client.SearchApi(api_client)
    search_request = amesh_client.SearchRequest() # SearchRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Search Resources
        api_response = api_instance.search_resources_api_v1_search_post(search_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of SearchApi->search_resources_api_v1_search_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SearchApi->search_resources_api_v1_search_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_request** | [**SearchRequest**](SearchRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**SearchResponse**](SearchResponse.md)

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

# **verify_search_projection_api_v1_search_verify_get**
> SearchProjectionVerification verify_search_projection_api_v1_search_verify_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Verify Search Projection

### Example


```python
import amesh_client
from amesh_client.models.search_projection_verification import SearchProjectionVerification
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
    api_instance = amesh_client.SearchApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Verify Search Projection
        api_response = api_instance.verify_search_projection_api_v1_search_verify_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of SearchApi->verify_search_projection_api_v1_search_verify_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SearchApi->verify_search_projection_api_v1_search_verify_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**SearchProjectionVerification**](SearchProjectionVerification.md)

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
