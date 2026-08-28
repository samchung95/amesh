# amesh_client.OperationsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**activate_operational_control_api_v1_operational_controls_post**](OperationsApi.md#activate_operational_control_api_v1_operational_controls_post) | **POST** /api/v1/operational-controls | Activate Operational Control
[**change_operational_control_api_v1_operational_controls_control_id_actions_post**](OperationsApi.md#change_operational_control_api_v1_operational_controls_control_id_actions_post) | **POST** /api/v1/operational-controls/{control_id}/actions | Change Operational Control
[**deactivate_announcement_api_v1_announcements_announcement_id_delete**](OperationsApi.md#deactivate_announcement_api_v1_announcements_announcement_id_delete) | **DELETE** /api/v1/announcements/{announcement_id} | Deactivate Announcement
[**drain_service_instance_api_v1_operations_services_instance_id_drain_post**](OperationsApi.md#drain_service_instance_api_v1_operations_services_instance_id_drain_post) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance
[**get_admission_diagnostics_api_v1_admissions_diagnostics_get**](OperationsApi.md#get_admission_diagnostics_api_v1_admissions_diagnostics_get) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics
[**get_network_diagnostics_api_v1_operations_network_diagnostics_get**](OperationsApi.md#get_network_diagnostics_api_v1_operations_network_diagnostics_get) | **GET** /api/v1/operations/network-diagnostics | Get Network Diagnostics
[**get_reconciliation_api_v1_reconciliations_run_id_get**](OperationsApi.md#get_reconciliation_api_v1_reconciliations_run_id_get) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation
[**get_service_topology_api_v1_operations_topology_get**](OperationsApi.md#get_service_topology_api_v1_operations_topology_get) | **GET** /api/v1/operations/topology | Get Service Topology
[**list_announcements_api_v1_announcements_get**](OperationsApi.md#list_announcements_api_v1_announcements_get) | **GET** /api/v1/announcements | List Announcements
[**list_operational_control_events_api_v1_operational_control_events_get**](OperationsApi.md#list_operational_control_events_api_v1_operational_control_events_get) | **GET** /api/v1/operational-control-events | List Operational Control Events
[**list_operational_controls_api_v1_operational_controls_get**](OperationsApi.md#list_operational_controls_api_v1_operational_controls_get) | **GET** /api/v1/operational-controls | List Operational Controls
[**list_reconciliations_api_v1_reconciliations_get**](OperationsApi.md#list_reconciliations_api_v1_reconciliations_get) | **GET** /api/v1/reconciliations | List Reconciliations
[**publish_announcement_api_v1_announcements_post**](OperationsApi.md#publish_announcement_api_v1_announcements_post) | **POST** /api/v1/announcements | Publish Announcement
[**reconcile_admissions_api_v1_admissions_reconcile_post**](OperationsApi.md#reconcile_admissions_api_v1_admissions_reconcile_post) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions
[**run_reconciliation_api_v1_reconciliations_post**](OperationsApi.md#run_reconciliation_api_v1_reconciliations_post) | **POST** /api/v1/reconciliations | Run Reconciliation


# **activate_operational_control_api_v1_operational_controls_post**
> OperationalControl activate_operational_control_api_v1_operational_controls_post(operational_control_create_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Activate Operational Control

### Example


```python
import amesh_client
from amesh_client.models.operational_control import OperationalControl
from amesh_client.models.operational_control_create_request import OperationalControlCreateRequest
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
    operational_control_create_request = amesh_client.OperationalControlCreateRequest() # OperationalControlCreateRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Activate Operational Control
        api_response = api_instance.activate_operational_control_api_v1_operational_controls_post(operational_control_create_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->activate_operational_control_api_v1_operational_controls_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->activate_operational_control_api_v1_operational_controls_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **operational_control_create_request** | **OperationalControlCreateRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**OperationalControl**

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

# **change_operational_control_api_v1_operational_controls_control_id_actions_post**
> OperationalControl change_operational_control_api_v1_operational_controls_control_id_actions_post(control_id, operational_control_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Change Operational Control

### Example


```python
import amesh_client
from amesh_client.models.operational_control import OperationalControl
from amesh_client.models.operational_control_action_request import OperationalControlActionRequest
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
    control_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    operational_control_action_request = amesh_client.OperationalControlActionRequest() # OperationalControlActionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Change Operational Control
        api_response = api_instance.change_operational_control_api_v1_operational_controls_control_id_actions_post(control_id, operational_control_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->change_operational_control_api_v1_operational_controls_control_id_actions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->change_operational_control_api_v1_operational_controls_control_id_actions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **control_id** | **UUID**|  |
 **operational_control_action_request** | **OperationalControlActionRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**OperationalControl**

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

# **deactivate_announcement_api_v1_announcements_announcement_id_delete**
> Announcement deactivate_announcement_api_v1_announcements_announcement_id_delete(announcement_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Deactivate Announcement

### Example


```python
import amesh_client
from amesh_client.models.announcement import Announcement
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
    announcement_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    expected_version = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Deactivate Announcement
        api_response = api_instance.deactivate_announcement_api_v1_announcements_announcement_id_delete(announcement_id, expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->deactivate_announcement_api_v1_announcements_announcement_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->deactivate_announcement_api_v1_announcements_announcement_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **announcement_id** | **UUID**|  |
 **expected_version** | **int**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**Announcement**

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
 **service_drain_request** | **ServiceDrainRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**ServiceInstance**

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

**AdmissionDiagnostics**

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

# **get_network_diagnostics_api_v1_operations_network_diagnostics_get**
> NetworkDiagnosticBundle get_network_diagnostics_api_v1_operations_network_diagnostics_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Network Diagnostics

### Example


```python
import amesh_client
from amesh_client.models.network_diagnostic_bundle import NetworkDiagnosticBundle
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
        # Get Network Diagnostics
        api_response = api_instance.get_network_diagnostics_api_v1_operations_network_diagnostics_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->get_network_diagnostics_api_v1_operations_network_diagnostics_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->get_network_diagnostics_api_v1_operations_network_diagnostics_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**NetworkDiagnosticBundle**

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

**ReconciliationRun**

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

**ServiceTopology**

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

# **list_announcements_api_v1_announcements_get**
> List[Announcement] list_announcements_api_v1_announcements_get(namespace=namespace, include_inactive=include_inactive, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Announcements

### Example


```python
import amesh_client
from amesh_client.models.announcement import Announcement
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
    namespace = 'namespace_example' # str |  (optional)
    include_inactive = False # bool |  (optional) (default to False)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Announcements
        api_response = api_instance.list_announcements_api_v1_announcements_get(namespace=namespace, include_inactive=include_inactive, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->list_announcements_api_v1_announcements_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->list_announcements_api_v1_announcements_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **include_inactive** | **bool**|  | [optional] [default to False]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[Announcement]**](Announcement.md)

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

# **list_operational_control_events_api_v1_operational_control_events_get**
> List[OperationalControlEvent] list_operational_control_events_api_v1_operational_control_events_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Operational Control Events

### Example


```python
import amesh_client
from amesh_client.models.operational_control_event import OperationalControlEvent
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
    limit = 200 # int |  (optional) (default to 200)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Operational Control Events
        api_response = api_instance.list_operational_control_events_api_v1_operational_control_events_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->list_operational_control_events_api_v1_operational_control_events_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->list_operational_control_events_api_v1_operational_control_events_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 200]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[OperationalControlEvent]**](OperationalControlEvent.md)

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

# **list_operational_controls_api_v1_operational_controls_get**
> List[OperationalControl] list_operational_controls_api_v1_operational_controls_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Operational Controls

### Example


```python
import amesh_client
from amesh_client.models.operational_control import OperationalControl
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
        # List Operational Controls
        api_response = api_instance.list_operational_controls_api_v1_operational_controls_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->list_operational_controls_api_v1_operational_controls_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->list_operational_controls_api_v1_operational_controls_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[OperationalControl]**](OperationalControl.md)

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

# **publish_announcement_api_v1_announcements_post**
> Announcement publish_announcement_api_v1_announcements_post(announcement_create_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Publish Announcement

### Example


```python
import amesh_client
from amesh_client.models.announcement import Announcement
from amesh_client.models.announcement_create_request import AnnouncementCreateRequest
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
    announcement_create_request = amesh_client.AnnouncementCreateRequest() # AnnouncementCreateRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Publish Announcement
        api_response = api_instance.publish_announcement_api_v1_announcements_post(announcement_create_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of OperationsApi->publish_announcement_api_v1_announcements_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OperationsApi->publish_announcement_api_v1_announcements_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **announcement_create_request** | **AnnouncementCreateRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**Announcement**

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
 **reconciliation_request** | **ReconciliationRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**ReconciliationRun**

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
