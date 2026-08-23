# amesh_client.SimulationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**compare_flow_simulations_api_v1_flows_namespace_flow_id_simulations_compare_post**](SimulationsApi.md#compare_flow_simulations_api_v1_flows_namespace_flow_id_simulations_compare_post) | **POST** /api/v1/flows/{namespace}/{flow_id}/simulations/compare | Compare Flow Simulations
[**simulate_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_simulate_post**](SimulationsApi.md#simulate_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_simulate_post) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/simulate | Simulate Flow Revision


# **compare_flow_simulations_api_v1_flows_namespace_flow_id_simulations_compare_post**
> SimulationComparison compare_flow_simulations_api_v1_flows_namespace_flow_id_simulations_compare_post(namespace, flow_id, var_from, to, simulation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Compare Flow Simulations

### Example


```python
import amesh_client
from amesh_client.models.simulation_comparison import SimulationComparison
from amesh_client.models.simulation_request import SimulationRequest
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
    api_instance = amesh_client.SimulationsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    var_from = 56 # int |
    to = 56 # int |
    simulation_request = amesh_client.SimulationRequest() # SimulationRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Compare Flow Simulations
        api_response = api_instance.compare_flow_simulations_api_v1_flows_namespace_flow_id_simulations_compare_post(namespace, flow_id, var_from, to, simulation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of SimulationsApi->compare_flow_simulations_api_v1_flows_namespace_flow_id_simulations_compare_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SimulationsApi->compare_flow_simulations_api_v1_flows_namespace_flow_id_simulations_compare_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **var_from** | **int**|  |
 **to** | **int**|  |
 **simulation_request** | [**SimulationRequest**](SimulationRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**SimulationComparison**](SimulationComparison.md)

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

# **simulate_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_simulate_post**
> SimulationPlan simulate_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_simulate_post(namespace, flow_id, revision, simulation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Simulate Flow Revision

### Example


```python
import amesh_client
from amesh_client.models.simulation_plan import SimulationPlan
from amesh_client.models.simulation_request import SimulationRequest
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
    api_instance = amesh_client.SimulationsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    revision = 56 # int |
    simulation_request = amesh_client.SimulationRequest() # SimulationRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Simulate Flow Revision
        api_response = api_instance.simulate_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_simulate_post(namespace, flow_id, revision, simulation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of SimulationsApi->simulate_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_simulate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SimulationsApi->simulate_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_simulate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **revision** | **int**|  |
 **simulation_request** | [**SimulationRequest**](SimulationRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**SimulationPlan**](SimulationPlan.md)

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
