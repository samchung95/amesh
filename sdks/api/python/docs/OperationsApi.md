# amesh_client.OperationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**drain_service_instance_api_v1_operations_services_instance_id_drain_post**](OperationsApi.md#drain_service_instance_api_v1_operations_services_instance_id_drain_post) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance
[**get_admission_diagnostics_api_v1_admissions_diagnostics_get**](OperationsApi.md#get_admission_diagnostics_api_v1_admissions_diagnostics_get) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics
[**get_reconciliation_api_v1_reconciliations_run_id_get**](OperationsApi.md#get_reconciliation_api_v1_reconciliations_run_id_get) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation
[**get_service_topology_api_v1_operations_topology_get**](OperationsApi.md#get_service_topology_api_v1_operations_topology_get) | **GET** /api/v1/operations/topology | Get Service Topology
[**list_reconciliations_api_v1_reconciliations_get**](OperationsApi.md#list_reconciliations_api_v1_reconciliations_get) | **GET** /api/v1/reconciliations | List Reconciliations
[**reconcile_admissions_api_v1_admissions_reconcile_post**](OperationsApi.md#reconcile_admissions_api_v1_admissions_reconcile_post) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions
[**run_reconciliation_api_v1_reconciliations_post**](OperationsApi.md#run_reconciliation_api_v1_reconciliations_post) | **POST** /api/v1/reconciliations | Run Reconciliation


# **drain_service_instance_api_v1_operations_services_instance_id_drain_post**
> ServiceInstance drain_service_instance_api_v1_operations_services_instance_id_drain_post(instance_id, service_drain_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Drain Service Instance

### Example


```python
import amesh_client
from amesh_client.models.service_drain_request import ServiceDrainRequest
from amesh_client.models.service_instance import ServiceInstance
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
    api_instance = amesh_client.OperationsApi(api_client)
    instance_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    service_drain_request = amesh_client.ServiceDrainRequest() # ServiceDrainRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Drain Service Instance
        api_response = api_instance.drain_service_instance_api_v1_operations_services_instance_id_drain_post(instance_id, service_drain_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of OperationsApi->drain_service_instance_api_v1_operations_services_instance_id_drain_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->drain_service_instance_api_v1_operations_services_instance_id_drain_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **instance_id** | **UUID**|  |
 **service_drain_request** | [**ServiceDrainRequest**](ServiceDrainRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**ServiceInstance**](ServiceInstance.md)

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

# **get_admission_diagnostics_api_v1_admissions_diagnostics_get**
> AdmissionDiagnostics get_admission_diagnostics_api_v1_admissions_diagnostics_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Admission Diagnostics

### Example


```python
import amesh_client
from amesh_client.models.admission_diagnostics import AdmissionDiagnostics
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
    api_instance = amesh_client.OperationsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Admission Diagnostics
        api_response = api_instance.get_admission_diagnostics_api_v1_admissions_diagnostics_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->get_admission_diagnostics_api_v1_admissions_diagnostics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->get_admission_diagnostics_api_v1_admissions_diagnostics_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AdmissionDiagnostics**](AdmissionDiagnostics.md)

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

# **get_reconciliation_api_v1_reconciliations_run_id_get**
> ReconciliationRun get_reconciliation_api_v1_reconciliations_run_id_get(run_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Reconciliation

### Example


```python
import amesh_client
from amesh_client.models.reconciliation_run import ReconciliationRun
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
    api_instance = amesh_client.OperationsApi(api_client)
    run_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Reconciliation
        api_response = api_instance.get_reconciliation_api_v1_reconciliations_run_id_get(run_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->get_reconciliation_api_v1_reconciliations_run_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->get_reconciliation_api_v1_reconciliations_run_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **run_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ReconciliationRun**](ReconciliationRun.md)

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

# **get_service_topology_api_v1_operations_topology_get**
> ServiceTopology get_service_topology_api_v1_operations_topology_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Get Service Topology

### Example


```python
import amesh_client
from amesh_client.models.service_topology import ServiceTopology
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
    api_instance = amesh_client.OperationsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Get Service Topology
        api_response = api_instance.get_service_topology_api_v1_operations_topology_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of OperationsApi->get_service_topology_api_v1_operations_topology_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->get_service_topology_api_v1_operations_topology_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**ServiceTopology**](ServiceTopology.md)

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

# **list_reconciliations_api_v1_reconciliations_get**
> List[ReconciliationRun] list_reconciliations_api_v1_reconciliations_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Reconciliations

### Example


```python
import amesh_client
from amesh_client.models.reconciliation_run import ReconciliationRun
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
    api_instance = amesh_client.OperationsApi(api_client)
    limit = 50 # int |  (optional) (default to 50)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Reconciliations
        api_response = api_instance.list_reconciliations_api_v1_reconciliations_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->list_reconciliations_api_v1_reconciliations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->list_reconciliations_api_v1_reconciliations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 50]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[ReconciliationRun]**](ReconciliationRun.md)

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

# **reconcile_admissions_api_v1_admissions_reconcile_post**
> Dict[str, int] reconcile_admissions_api_v1_admissions_reconcile_post(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Reconcile Admissions

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
    api_instance = amesh_client.OperationsApi(api_client)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Reconcile Admissions
        api_response = api_instance.reconcile_admissions_api_v1_admissions_reconcile_post(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->reconcile_admissions_api_v1_admissions_reconcile_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->reconcile_admissions_api_v1_admissions_reconcile_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**Dict[str, int]**

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

# **run_reconciliation_api_v1_reconciliations_post**
> ReconciliationRun run_reconciliation_api_v1_reconciliations_post(reconciliation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Run Reconciliation

### Example


```python
import amesh_client
from amesh_client.models.reconciliation_request import ReconciliationRequest
from amesh_client.models.reconciliation_run import ReconciliationRun
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
    api_instance = amesh_client.OperationsApi(api_client)
    reconciliation_request = amesh_client.ReconciliationRequest() # ReconciliationRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Run Reconciliation
        api_response = api_instance.run_reconciliation_api_v1_reconciliations_post(reconciliation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->run_reconciliation_api_v1_reconciliations_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->run_reconciliation_api_v1_reconciliations_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reconciliation_request** | [**ReconciliationRequest**](ReconciliationRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ReconciliationRun**](ReconciliationRun.md)

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
