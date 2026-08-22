# amesh_client.BackfillsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**cancel_backfill_api_v1_backfills_backfill_id_cancel_post**](BackfillsApi.md#cancel_backfill_api_v1_backfills_backfill_id_cancel_post) | **POST** /api/v1/backfills/{backfill_id}/cancel | Cancel Backfill
[**create_backfill_api_v1_backfills_post**](BackfillsApi.md#create_backfill_api_v1_backfills_post) | **POST** /api/v1/backfills | Create Backfill
[**get_backfill_api_v1_backfills_backfill_id_get**](BackfillsApi.md#get_backfill_api_v1_backfills_backfill_id_get) | **GET** /api/v1/backfills/{backfill_id} | Get Backfill
[**list_backfills_api_v1_backfills_get**](BackfillsApi.md#list_backfills_api_v1_backfills_get) | **GET** /api/v1/backfills | List Backfills
[**pause_backfill_api_v1_backfills_backfill_id_pause_post**](BackfillsApi.md#pause_backfill_api_v1_backfills_backfill_id_pause_post) | **POST** /api/v1/backfills/{backfill_id}/pause | Pause Backfill
[**preview_backfill_api_v1_backfills_preview_post**](BackfillsApi.md#preview_backfill_api_v1_backfills_preview_post) | **POST** /api/v1/backfills/preview | Preview Backfill
[**resume_backfill_api_v1_backfills_backfill_id_resume_post**](BackfillsApi.md#resume_backfill_api_v1_backfills_backfill_id_resume_post) | **POST** /api/v1/backfills/{backfill_id}/resume | Resume Backfill


# **cancel_backfill_api_v1_backfills_backfill_id_cancel_post**
> BackfillRecord cancel_backfill_api_v1_backfills_backfill_id_cancel_post(backfill_id, backfill_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Cancel Backfill

### Example


```python
import amesh_client
from amesh_client.models.backfill_action_request import BackfillActionRequest
from amesh_client.models.backfill_record import BackfillRecord
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
    api_instance = amesh_client.BackfillsApi(api_client)
    backfill_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    backfill_action_request = amesh_client.BackfillActionRequest() # BackfillActionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Cancel Backfill
        api_response = api_instance.cancel_backfill_api_v1_backfills_backfill_id_cancel_post(backfill_id, backfill_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BackfillsApi->cancel_backfill_api_v1_backfills_backfill_id_cancel_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackfillsApi->cancel_backfill_api_v1_backfills_backfill_id_cancel_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfill_id** | **UUID**|  |
 **backfill_action_request** | [**BackfillActionRequest**](BackfillActionRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**BackfillRecord**](BackfillRecord.md)

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

# **create_backfill_api_v1_backfills_post**
> BackfillRecord create_backfill_api_v1_backfills_post(backfill_spec, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Backfill

### Example


```python
import amesh_client
from amesh_client.models.backfill_record import BackfillRecord
from amesh_client.models.backfill_spec import BackfillSpec
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
    api_instance = amesh_client.BackfillsApi(api_client)
    backfill_spec = amesh_client.BackfillSpec() # BackfillSpec |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Backfill
        api_response = api_instance.create_backfill_api_v1_backfills_post(backfill_spec, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BackfillsApi->create_backfill_api_v1_backfills_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackfillsApi->create_backfill_api_v1_backfills_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfill_spec** | [**BackfillSpec**](BackfillSpec.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**BackfillRecord**](BackfillRecord.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_backfill_api_v1_backfills_backfill_id_get**
> BackfillRecord get_backfill_api_v1_backfills_backfill_id_get(backfill_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Backfill

### Example


```python
import amesh_client
from amesh_client.models.backfill_record import BackfillRecord
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
    api_instance = amesh_client.BackfillsApi(api_client)
    backfill_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Backfill
        api_response = api_instance.get_backfill_api_v1_backfills_backfill_id_get(backfill_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BackfillsApi->get_backfill_api_v1_backfills_backfill_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackfillsApi->get_backfill_api_v1_backfills_backfill_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfill_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**BackfillRecord**](BackfillRecord.md)

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

# **list_backfills_api_v1_backfills_get**
> List[BackfillRecord] list_backfills_api_v1_backfills_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Backfills

### Example


```python
import amesh_client
from amesh_client.models.backfill_record import BackfillRecord
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
    api_instance = amesh_client.BackfillsApi(api_client)
    cursor = 'cursor_example' # str | Opaque cursor from the prior page (optional)
    limit = 100 # int |  (optional) (default to 100)
    filter = ['filter_example'] # List[str] | Repeatable top-level equality filter in field=value form (optional)
    sort = 'sort_example' # str | Comma-separated top-level fields; prefix descending fields with - (optional)
    fields = 'fields_example' # str | Comma-separated top-level response fields (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Backfills
        api_response = api_instance.list_backfills_api_v1_backfills_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BackfillsApi->list_backfills_api_v1_backfills_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackfillsApi->list_backfills_api_v1_backfills_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **str**| Opaque cursor from the prior page | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **filter** | [**List[str]**](str.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional]
 **sort** | **str**| Comma-separated top-level fields; prefix descending fields with - | [optional]
 **fields** | **str**| Comma-separated top-level response fields | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[BackfillRecord]**](BackfillRecord.md)

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

# **pause_backfill_api_v1_backfills_backfill_id_pause_post**
> BackfillRecord pause_backfill_api_v1_backfills_backfill_id_pause_post(backfill_id, backfill_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Pause Backfill

### Example


```python
import amesh_client
from amesh_client.models.backfill_action_request import BackfillActionRequest
from amesh_client.models.backfill_record import BackfillRecord
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
    api_instance = amesh_client.BackfillsApi(api_client)
    backfill_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    backfill_action_request = amesh_client.BackfillActionRequest() # BackfillActionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Pause Backfill
        api_response = api_instance.pause_backfill_api_v1_backfills_backfill_id_pause_post(backfill_id, backfill_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BackfillsApi->pause_backfill_api_v1_backfills_backfill_id_pause_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackfillsApi->pause_backfill_api_v1_backfills_backfill_id_pause_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfill_id** | **UUID**|  |
 **backfill_action_request** | [**BackfillActionRequest**](BackfillActionRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**BackfillRecord**](BackfillRecord.md)

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

# **preview_backfill_api_v1_backfills_preview_post**
> BackfillPreview preview_backfill_api_v1_backfills_preview_post(backfill_spec, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Backfill

### Example


```python
import amesh_client
from amesh_client.models.backfill_preview import BackfillPreview
from amesh_client.models.backfill_spec import BackfillSpec
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
    api_instance = amesh_client.BackfillsApi(api_client)
    backfill_spec = amesh_client.BackfillSpec() # BackfillSpec |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Backfill
        api_response = api_instance.preview_backfill_api_v1_backfills_preview_post(backfill_spec, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BackfillsApi->preview_backfill_api_v1_backfills_preview_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackfillsApi->preview_backfill_api_v1_backfills_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfill_spec** | [**BackfillSpec**](BackfillSpec.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**BackfillPreview**](BackfillPreview.md)

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

# **resume_backfill_api_v1_backfills_backfill_id_resume_post**
> BackfillRecord resume_backfill_api_v1_backfills_backfill_id_resume_post(backfill_id, backfill_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Resume Backfill

### Example


```python
import amesh_client
from amesh_client.models.backfill_action_request import BackfillActionRequest
from amesh_client.models.backfill_record import BackfillRecord
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
    api_instance = amesh_client.BackfillsApi(api_client)
    backfill_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    backfill_action_request = amesh_client.BackfillActionRequest() # BackfillActionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Resume Backfill
        api_response = api_instance.resume_backfill_api_v1_backfills_backfill_id_resume_post(backfill_id, backfill_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BackfillsApi->resume_backfill_api_v1_backfills_backfill_id_resume_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BackfillsApi->resume_backfill_api_v1_backfills_backfill_id_resume_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfill_id** | **UUID**|  |
 **backfill_action_request** | [**BackfillActionRequest**](BackfillActionRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**BackfillRecord**](BackfillRecord.md)

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
