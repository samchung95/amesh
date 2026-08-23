# amesh_client.BlueprintsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_blueprint_version_api_v1_blueprints_blueprint_id_version_get**](BlueprintsApi.md#get_blueprint_version_api_v1_blueprints_blueprint_id_version_get) | **GET** /api/v1/blueprints/{blueprint_id}/{version} | Get Blueprint Version
[**get_blueprints_api_v1_blueprints_get**](BlueprintsApi.md#get_blueprints_api_v1_blueprints_get) | **GET** /api/v1/blueprints | Get Blueprints
[**instantiate_blueprint_draft_api_v1_blueprints_blueprint_id_version_instantiate_post**](BlueprintsApi.md#instantiate_blueprint_draft_api_v1_blueprints_blueprint_id_version_instantiate_post) | **POST** /api/v1/blueprints/{blueprint_id}/{version}/instantiate | Instantiate Blueprint Draft
[**simulate_playground_api_v1_playground_simulate_post**](BlueprintsApi.md#simulate_playground_api_v1_playground_simulate_post) | **POST** /api/v1/playground/simulate | Simulate Playground


# **get_blueprint_version_api_v1_blueprints_blueprint_id_version_get**
> BlueprintDefinition get_blueprint_version_api_v1_blueprints_blueprint_id_version_get(blueprint_id, version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Blueprint Version

### Example


```python
import amesh_client
from amesh_client.models.blueprint_definition import BlueprintDefinition
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
    api_instance = amesh_client.BlueprintsApi(api_client)
    blueprint_id = 'blueprint_id_example' # str |
    version = 'version_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Blueprint Version
        api_response = api_instance.get_blueprint_version_api_v1_blueprints_blueprint_id_version_get(blueprint_id, version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BlueprintsApi->get_blueprint_version_api_v1_blueprints_blueprint_id_version_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BlueprintsApi->get_blueprint_version_api_v1_blueprints_blueprint_id_version_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **blueprint_id** | **str**|  |
 **version** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**BlueprintDefinition**](BlueprintDefinition.md)

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

# **get_blueprints_api_v1_blueprints_get**
> List[BlueprintSummary] get_blueprints_api_v1_blueprints_get(q=q, source=source, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Blueprints

### Example


```python
import amesh_client
from amesh_client.models.blueprint_summary import BlueprintSummary
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
    api_instance = amesh_client.BlueprintsApi(api_client)
    q = 'q_example' # str |  (optional)
    source = amesh_client.BlueprintCatalogSource() # BlueprintCatalogSource |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Blueprints
        api_response = api_instance.get_blueprints_api_v1_blueprints_get(q=q, source=source, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BlueprintsApi->get_blueprints_api_v1_blueprints_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BlueprintsApi->get_blueprints_api_v1_blueprints_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **str**|  | [optional]
 **source** | [**BlueprintCatalogSource**](.md)|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[BlueprintSummary]**](BlueprintSummary.md)

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

# **instantiate_blueprint_draft_api_v1_blueprints_blueprint_id_version_instantiate_post**
> BlueprintDraftResponse instantiate_blueprint_draft_api_v1_blueprints_blueprint_id_version_instantiate_post(blueprint_id, version, blueprint_instantiation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Instantiate Blueprint Draft

### Example


```python
import amesh_client
from amesh_client.models.blueprint_draft_response import BlueprintDraftResponse
from amesh_client.models.blueprint_instantiation_request import BlueprintInstantiationRequest
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
    api_instance = amesh_client.BlueprintsApi(api_client)
    blueprint_id = 'blueprint_id_example' # str |
    version = 'version_example' # str |
    blueprint_instantiation_request = amesh_client.BlueprintInstantiationRequest() # BlueprintInstantiationRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Instantiate Blueprint Draft
        api_response = api_instance.instantiate_blueprint_draft_api_v1_blueprints_blueprint_id_version_instantiate_post(blueprint_id, version, blueprint_instantiation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BlueprintsApi->instantiate_blueprint_draft_api_v1_blueprints_blueprint_id_version_instantiate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BlueprintsApi->instantiate_blueprint_draft_api_v1_blueprints_blueprint_id_version_instantiate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **blueprint_id** | **str**|  |
 **version** | **str**|  |
 **blueprint_instantiation_request** | [**BlueprintInstantiationRequest**](BlueprintInstantiationRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**BlueprintDraftResponse**](BlueprintDraftResponse.md)

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

# **simulate_playground_api_v1_playground_simulate_post**
> PlaygroundSimulationResponse simulate_playground_api_v1_playground_simulate_post(playground_simulation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Simulate Playground

### Example


```python
import amesh_client
from amesh_client.models.playground_simulation_request import PlaygroundSimulationRequest
from amesh_client.models.playground_simulation_response import PlaygroundSimulationResponse
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
    api_instance = amesh_client.BlueprintsApi(api_client)
    playground_simulation_request = amesh_client.PlaygroundSimulationRequest() # PlaygroundSimulationRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Simulate Playground
        api_response = api_instance.simulate_playground_api_v1_playground_simulate_post(playground_simulation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of BlueprintsApi->simulate_playground_api_v1_playground_simulate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling BlueprintsApi->simulate_playground_api_v1_playground_simulate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **playground_simulation_request** | [**PlaygroundSimulationRequest**](PlaygroundSimulationRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PlaygroundSimulationResponse**](PlaygroundSimulationResponse.md)

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
