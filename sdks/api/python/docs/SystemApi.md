# amesh_client.SystemApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health_health_get**](SystemApi.md#health_health_get) | **GET** /health | Health
[**ready_ready_get**](SystemApi.md#ready_ready_get) | **GET** /ready | Ready


# **health_health_get**
> HealthResponse health_health_get()

Health

### Example


```python
import amesh_client
from amesh_client.models.health_response import HealthResponse
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
    api_instance = amesh_client.SystemApi(api_client)

    try:
        # Health
        api_response = api_instance.health_health_get()
        print("The response of SystemApi->health_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SystemApi->health_health_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**HealthResponse**

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

# **ready_ready_get**
> ReadinessResponse ready_ready_get()

Ready

### Example


```python
import amesh_client
from amesh_client.models.readiness_response import ReadinessResponse
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
    api_instance = amesh_client.SystemApi(api_client)

    try:
        # Ready
        api_response = api_instance.ready_ready_get()
        print("The response of SystemApi->ready_ready_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SystemApi->ready_ready_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**ReadinessResponse**

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
