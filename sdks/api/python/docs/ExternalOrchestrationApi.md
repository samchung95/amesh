# amesh_client.ExternalOrchestrationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_external_orchestration_profile_api_v1_orchestration_profile_get**](ExternalOrchestrationApi.md#get_external_orchestration_profile_api_v1_orchestration_profile_get) | **GET** /api/v1/orchestration/profile | Get External Orchestration Profile


# **get_external_orchestration_profile_api_v1_orchestration_profile_get**
> ExternalOrchestrationProfile get_external_orchestration_profile_api_v1_orchestration_profile_get()

Get External Orchestration Profile

Publish the client-neutral contract without exposing tenant data.

### Example


```python
import amesh_client
from amesh_client.models.external_orchestration_profile import ExternalOrchestrationProfile
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
    api_instance = amesh_client.ExternalOrchestrationApi(api_client)

    try:
        # Get External Orchestration Profile
        api_response = api_instance.get_external_orchestration_profile_api_v1_orchestration_profile_get()
        print("The response of ExternalOrchestrationApi->get_external_orchestration_profile_api_v1_orchestration_profile_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExternalOrchestrationApi->get_external_orchestration_profile_api_v1_orchestration_profile_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**ExternalOrchestrationProfile**

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
