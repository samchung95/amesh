# amesh_client.UiApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_ui_session_api_v1_ui_session_get**](UiApi.md#get_ui_session_api_v1_ui_session_get) | **GET** /api/v1/ui/session | Get Ui Session


# **get_ui_session_api_v1_ui_session_get**
> UiSessionResponse get_ui_session_api_v1_ui_session_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Ui Session

### Example


```python
import amesh_client
from amesh_client.models.ui_session_response import UiSessionResponse
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
    api_instance = amesh_client.UiApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Ui Session
        api_response = api_instance.get_ui_session_api_v1_ui_session_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of UiApi->get_ui_session_api_v1_ui_session_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UiApi->get_ui_session_api_v1_ui_session_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**UiSessionResponse**](UiSessionResponse.md)

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
