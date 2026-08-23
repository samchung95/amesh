# amesh_client.DashboardsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_dashboard_api_v1_dashboards_dashboard_id_delete**](DashboardsApi.md#delete_dashboard_api_v1_dashboards_dashboard_id_delete) | **DELETE** /api/v1/dashboards/{dashboard_id} | Delete Dashboard
[**execute_dashboard_query_api_v1_dashboard_queries_post**](DashboardsApi.md#execute_dashboard_query_api_v1_dashboard_queries_post) | **POST** /api/v1/dashboard-queries | Execute Dashboard Query
[**export_dashboard_api_v1_dashboards_dashboard_id_export_get**](DashboardsApi.md#export_dashboard_api_v1_dashboards_dashboard_id_export_get) | **GET** /api/v1/dashboards/{dashboard_id}/export | Export Dashboard
[**get_dashboard_api_v1_dashboards_dashboard_id_get**](DashboardsApi.md#get_dashboard_api_v1_dashboards_dashboard_id_get) | **GET** /api/v1/dashboards/{dashboard_id} | Get Dashboard
[**list_dashboards_api_v1_dashboards_get**](DashboardsApi.md#list_dashboards_api_v1_dashboards_get) | **GET** /api/v1/dashboards | List Dashboards
[**put_dashboard_api_v1_dashboards_dashboard_id_put**](DashboardsApi.md#put_dashboard_api_v1_dashboards_dashboard_id_put) | **PUT** /api/v1/dashboards/{dashboard_id} | Put Dashboard
[**render_dashboard_api_v1_dashboards_dashboard_id_render_post**](DashboardsApi.md#render_dashboard_api_v1_dashboards_dashboard_id_render_post) | **POST** /api/v1/dashboards/{dashboard_id}/render | Render Dashboard


# **delete_dashboard_api_v1_dashboards_dashboard_id_delete**
> delete_dashboard_api_v1_dashboards_dashboard_id_delete(dashboard_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Delete Dashboard

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
    api_instance = amesh_client.DashboardsApi(api_client)
    dashboard_id = 'dashboard_id_example' # str |
    expected_version = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Delete Dashboard
        api_instance.delete_dashboard_api_v1_dashboards_dashboard_id_delete(dashboard_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling DashboardsApi->delete_dashboard_api_v1_dashboards_dashboard_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboard_id** | **str**|  |
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

# **execute_dashboard_query_api_v1_dashboard_queries_post**
> DashboardQueryResult execute_dashboard_query_api_v1_dashboard_queries_post(dashboard_query, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Execute Dashboard Query

### Example


```python
import amesh_client
from amesh_client.models.dashboard_query import DashboardQuery
from amesh_client.models.dashboard_query_result import DashboardQueryResult
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
    api_instance = amesh_client.DashboardsApi(api_client)
    dashboard_query = amesh_client.DashboardQuery() # DashboardQuery |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Execute Dashboard Query
        api_response = api_instance.execute_dashboard_query_api_v1_dashboard_queries_post(dashboard_query, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of DashboardsApi->execute_dashboard_query_api_v1_dashboard_queries_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardsApi->execute_dashboard_query_api_v1_dashboard_queries_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboard_query** | [**DashboardQuery**](DashboardQuery.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**DashboardQueryResult**](DashboardQueryResult.md)

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

# **export_dashboard_api_v1_dashboards_dashboard_id_export_get**
> object export_dashboard_api_v1_dashboards_dashboard_id_export_get(dashboard_id, format=format, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Export Dashboard

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
    api_instance = amesh_client.DashboardsApi(api_client)
    dashboard_id = 'dashboard_id_example' # str |
    format = 'yaml' # str |  (optional) (default to 'yaml')
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Export Dashboard
        api_response = api_instance.export_dashboard_api_v1_dashboards_dashboard_id_export_get(dashboard_id, format=format, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of DashboardsApi->export_dashboard_api_v1_dashboards_dashboard_id_export_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardsApi->export_dashboard_api_v1_dashboards_dashboard_id_export_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboard_id** | **str**|  |
 **format** | **str**|  | [optional] [default to &#39;yaml&#39;]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**object**

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

# **get_dashboard_api_v1_dashboards_dashboard_id_get**
> DashboardDefinition get_dashboard_api_v1_dashboards_dashboard_id_get(dashboard_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Dashboard

### Example


```python
import amesh_client
from amesh_client.models.dashboard_definition import DashboardDefinition
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
    api_instance = amesh_client.DashboardsApi(api_client)
    dashboard_id = 'dashboard_id_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Dashboard
        api_response = api_instance.get_dashboard_api_v1_dashboards_dashboard_id_get(dashboard_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of DashboardsApi->get_dashboard_api_v1_dashboards_dashboard_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardsApi->get_dashboard_api_v1_dashboards_dashboard_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboard_id** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**DashboardDefinition**](DashboardDefinition.md)

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

# **list_dashboards_api_v1_dashboards_get**
> List[DashboardDefinition] list_dashboards_api_v1_dashboards_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Dashboards

### Example


```python
import amesh_client
from amesh_client.models.dashboard_definition import DashboardDefinition
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
    api_instance = amesh_client.DashboardsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Dashboards
        api_response = api_instance.list_dashboards_api_v1_dashboards_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of DashboardsApi->list_dashboards_api_v1_dashboards_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardsApi->list_dashboards_api_v1_dashboards_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[DashboardDefinition]**](DashboardDefinition.md)

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

# **put_dashboard_api_v1_dashboards_dashboard_id_put**
> DashboardDefinition put_dashboard_api_v1_dashboards_dashboard_id_put(dashboard_id, dashboard_spec, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Put Dashboard

### Example


```python
import amesh_client
from amesh_client.models.dashboard_definition import DashboardDefinition
from amesh_client.models.dashboard_spec import DashboardSpec
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
    api_instance = amesh_client.DashboardsApi(api_client)
    dashboard_id = 'dashboard_id_example' # str |
    dashboard_spec = amesh_client.DashboardSpec() # DashboardSpec |
    expected_version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Put Dashboard
        api_response = api_instance.put_dashboard_api_v1_dashboards_dashboard_id_put(dashboard_id, dashboard_spec, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of DashboardsApi->put_dashboard_api_v1_dashboards_dashboard_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardsApi->put_dashboard_api_v1_dashboards_dashboard_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboard_id** | **str**|  |
 **dashboard_spec** | [**DashboardSpec**](DashboardSpec.md)|  |
 **expected_version** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**DashboardDefinition**](DashboardDefinition.md)

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

# **render_dashboard_api_v1_dashboards_dashboard_id_render_post**
> DashboardRender render_dashboard_api_v1_dashboards_dashboard_id_render_post(dashboard_id, dashboard_filters, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Render Dashboard

### Example


```python
import amesh_client
from amesh_client.models.dashboard_filters import DashboardFilters
from amesh_client.models.dashboard_render import DashboardRender
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
    api_instance = amesh_client.DashboardsApi(api_client)
    dashboard_id = 'dashboard_id_example' # str |
    dashboard_filters = amesh_client.DashboardFilters() # DashboardFilters |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Render Dashboard
        api_response = api_instance.render_dashboard_api_v1_dashboards_dashboard_id_render_post(dashboard_id, dashboard_filters, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of DashboardsApi->render_dashboard_api_v1_dashboards_dashboard_id_render_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DashboardsApi->render_dashboard_api_v1_dashboards_dashboard_id_render_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboard_id** | **str**|  |
 **dashboard_filters** | [**DashboardFilters**](DashboardFilters.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**DashboardRender**](DashboardRender.md)

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
