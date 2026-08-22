# amesh_client.ExecutionsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apply_execution_control_api_v1_executions_execution_id_interventions_post**](ExecutionsApi.md#apply_execution_control_api_v1_executions_execution_id_interventions_post) | **POST** /api/v1/executions/{execution_id}/interventions | Apply Execution Control
[**create_execution_api_v1_executions_post**](ExecutionsApi.md#create_execution_api_v1_executions_post) | **POST** /api/v1/executions | Create Execution
[**create_executions_bulk_api_v1_executions_bulk_post**](ExecutionsApi.md#create_executions_bulk_api_v1_executions_bulk_post) | **POST** /api/v1/executions/bulk | Create Executions Bulk
[**download_execution_file_api_v1_executions_execution_id_files_artifact_id_get**](ExecutionsApi.md#download_execution_file_api_v1_executions_execution_id_files_artifact_id_get) | **GET** /api/v1/executions/{execution_id}/files/{artifact_id} | Download Execution File
[**get_execution_admission_api_v1_executions_execution_id_admission_get**](ExecutionsApi.md#get_execution_admission_api_v1_executions_execution_id_admission_get) | **GET** /api/v1/executions/{execution_id}/admission | Get Execution Admission
[**get_execution_api_v1_executions_execution_id_get**](ExecutionsApi.md#get_execution_api_v1_executions_execution_id_get) | **GET** /api/v1/executions/{execution_id} | Get Execution
[**get_execution_evidence_api_v1_executions_execution_id_evidence_get**](ExecutionsApi.md#get_execution_evidence_api_v1_executions_execution_id_evidence_get) | **GET** /api/v1/executions/{execution_id}/evidence | Get Execution Evidence
[**get_execution_graph_api_v1_executions_execution_id_graph_get**](ExecutionsApi.md#get_execution_graph_api_v1_executions_execution_id_graph_get) | **GET** /api/v1/executions/{execution_id}/graph | Get Execution Graph
[**get_execution_logs_api_v1_executions_execution_id_logs_get**](ExecutionsApi.md#get_execution_logs_api_v1_executions_execution_id_logs_get) | **GET** /api/v1/executions/{execution_id}/logs | Get Execution Logs
[**get_execution_parent_subflow_api_v1_executions_execution_id_parent_subflow_get**](ExecutionsApi.md#get_execution_parent_subflow_api_v1_executions_execution_id_parent_subflow_get) | **GET** /api/v1/executions/{execution_id}/parent-subflow | Get Execution Parent Subflow
[**get_task_admission_api_v1_task_runs_task_run_id_admission_get**](ExecutionsApi.md#get_task_admission_api_v1_task_runs_task_run_id_admission_get) | **GET** /api/v1/task-runs/{task_run_id}/admission | Get Task Admission
[**list_execution_control_history_api_v1_executions_execution_id_interventions_get**](ExecutionsApi.md#list_execution_control_history_api_v1_executions_execution_id_interventions_get) | **GET** /api/v1/executions/{execution_id}/interventions | List Execution Control History
[**list_execution_files_api_v1_executions_execution_id_files_get**](ExecutionsApi.md#list_execution_files_api_v1_executions_execution_id_files_get) | **GET** /api/v1/executions/{execution_id}/files | List Execution Files
[**list_execution_subflows_api_v1_executions_execution_id_subflows_get**](ExecutionsApi.md#list_execution_subflows_api_v1_executions_execution_id_subflows_get) | **GET** /api/v1/executions/{execution_id}/subflows | List Execution Subflows
[**list_executions_api_v1_executions_get**](ExecutionsApi.md#list_executions_api_v1_executions_get) | **GET** /api/v1/executions | List Executions
[**preview_execution_control_api_v1_executions_execution_id_interventions_preview_post**](ExecutionsApi.md#preview_execution_control_api_v1_executions_execution_id_interventions_preview_post) | **POST** /api/v1/executions/{execution_id}/interventions/preview | Preview Execution Control
[**reduce_execution_events_api_v1_executions_reduce_post**](ExecutionsApi.md#reduce_execution_events_api_v1_executions_reduce_post) | **POST** /api/v1/executions/reduce | Reduce Execution Events
[**resume_task_run_api_v1_executions_execution_id_task_runs_task_run_id_resume_post**](ExecutionsApi.md#resume_task_run_api_v1_executions_execution_id_task_runs_task_run_id_resume_post) | **POST** /api/v1/executions/{execution_id}/task-runs/{task_run_id}/resume | Resume Task Run
[**stream_execution_evidence_api_v1_executions_execution_id_evidence_stream_get**](ExecutionsApi.md#stream_execution_evidence_api_v1_executions_execution_id_evidence_stream_get) | **GET** /api/v1/executions/{execution_id}/evidence/stream | Stream Execution Evidence
[**stream_execution_logs_api_v1_executions_execution_id_logs_stream_get**](ExecutionsApi.md#stream_execution_logs_api_v1_executions_execution_id_logs_stream_get) | **GET** /api/v1/executions/{execution_id}/logs/stream | Stream Execution Logs


# **apply_execution_control_api_v1_executions_execution_id_interventions_post**
> ExecutionDetail apply_execution_control_api_v1_executions_execution_id_interventions_post(execution_id, execution_intervention_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Apply Execution Control

### Example


```python
import amesh_client
from amesh_client.models.execution_detail import ExecutionDetail
from amesh_client.models.execution_intervention_request import ExecutionInterventionRequest
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    execution_intervention_request = amesh_client.ExecutionInterventionRequest() # ExecutionInterventionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Apply Execution Control
        api_response = api_instance.apply_execution_control_api_v1_executions_execution_id_interventions_post(execution_id, execution_intervention_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->apply_execution_control_api_v1_executions_execution_id_interventions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->apply_execution_control_api_v1_executions_execution_id_interventions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **execution_intervention_request** | [**ExecutionInterventionRequest**](ExecutionInterventionRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

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

# **create_execution_api_v1_executions_post**
> ExecutionDetail create_execution_api_v1_executions_post(create_execution_request, prefer=prefer, idempotency_key=idempotency_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Execution

### Example


```python
import amesh_client
from amesh_client.models.create_execution_request import CreateExecutionRequest
from amesh_client.models.execution_detail import ExecutionDetail
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    create_execution_request = amesh_client.CreateExecutionRequest() # CreateExecutionRequest |
    prefer = 'prefer_example' # str |  (optional)
    idempotency_key = 'idempotency_key_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Execution
        api_response = api_instance.create_execution_api_v1_executions_post(create_execution_request, prefer=prefer, idempotency_key=idempotency_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->create_execution_api_v1_executions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->create_execution_api_v1_executions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_execution_request** | [**CreateExecutionRequest**](CreateExecutionRequest.md)|  |
 **prefer** | **str**|  | [optional]
 **idempotency_key** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**202** | Execution persisted and accepted for asynchronous processing |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_executions_bulk_api_v1_executions_bulk_post**
> List[BulkExecutionItemResult] create_executions_bulk_api_v1_executions_bulk_post(bulk_execution_request, prefer=prefer, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Executions Bulk

### Example


```python
import amesh_client
from amesh_client.models.bulk_execution_item_result import BulkExecutionItemResult
from amesh_client.models.bulk_execution_request import BulkExecutionRequest
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    bulk_execution_request = amesh_client.BulkExecutionRequest() # BulkExecutionRequest |
    prefer = 'prefer_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Executions Bulk
        api_response = api_instance.create_executions_bulk_api_v1_executions_bulk_post(bulk_execution_request, prefer=prefer, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->create_executions_bulk_api_v1_executions_bulk_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->create_executions_bulk_api_v1_executions_bulk_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bulk_execution_request** | [**BulkExecutionRequest**](BulkExecutionRequest.md)|  |
 **prefer** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[BulkExecutionItemResult]**](BulkExecutionItemResult.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**207** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **download_execution_file_api_v1_executions_execution_id_files_artifact_id_get**
> download_execution_file_api_v1_executions_execution_id_files_artifact_id_get(execution_id, artifact_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Download Execution File

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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    artifact_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Download Execution File
        api_instance.download_execution_file_api_v1_executions_execution_id_files_artifact_id_get(execution_id, artifact_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling ExecutionsApi->download_execution_file_api_v1_executions_execution_id_files_artifact_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **artifact_id** | **UUID**|  |
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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_execution_admission_api_v1_executions_execution_id_admission_get**
> AdmissionDecision get_execution_admission_api_v1_executions_execution_id_admission_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Execution Admission

### Example


```python
import amesh_client
from amesh_client.models.admission_decision import AdmissionDecision
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Execution Admission
        api_response = api_instance.get_execution_admission_api_v1_executions_execution_id_admission_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->get_execution_admission_api_v1_executions_execution_id_admission_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->get_execution_admission_api_v1_executions_execution_id_admission_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AdmissionDecision**](AdmissionDecision.md)

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

# **get_execution_api_v1_executions_execution_id_get**
> ExecutionDetail get_execution_api_v1_executions_execution_id_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Execution

### Example


```python
import amesh_client
from amesh_client.models.execution_detail import ExecutionDetail
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Execution
        api_response = api_instance.get_execution_api_v1_executions_execution_id_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->get_execution_api_v1_executions_execution_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->get_execution_api_v1_executions_execution_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

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

# **get_execution_evidence_api_v1_executions_execution_id_evidence_get**
> ExecutionEvidencePage get_execution_evidence_api_v1_executions_execution_id_evidence_get(execution_id, cursor=cursor, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Execution Evidence

### Example


```python
import amesh_client
from amesh_client.models.execution_evidence_page import ExecutionEvidencePage
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    cursor = 'cursor_example' # str | Opaque reconnect cursor (optional)
    limit = 500 # int |  (optional) (default to 500)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Execution Evidence
        api_response = api_instance.get_execution_evidence_api_v1_executions_execution_id_evidence_get(execution_id, cursor=cursor, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->get_execution_evidence_api_v1_executions_execution_id_evidence_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->get_execution_evidence_api_v1_executions_execution_id_evidence_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **cursor** | **str**| Opaque reconnect cursor | [optional]
 **limit** | **int**|  | [optional] [default to 500]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ExecutionEvidencePage**](ExecutionEvidencePage.md)

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

# **get_execution_graph_api_v1_executions_execution_id_graph_get**
> FlowGraph get_execution_graph_api_v1_executions_execution_id_graph_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Execution Graph

### Example


```python
import amesh_client
from amesh_client.models.flow_graph import FlowGraph
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Execution Graph
        api_response = api_instance.get_execution_graph_api_v1_executions_execution_id_graph_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->get_execution_graph_api_v1_executions_execution_id_graph_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->get_execution_graph_api_v1_executions_execution_id_graph_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**FlowGraph**](FlowGraph.md)

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

# **get_execution_logs_api_v1_executions_execution_id_logs_get**
> List[TaskLog] get_execution_logs_api_v1_executions_execution_id_logs_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Execution Logs

### Example


```python
import amesh_client
from amesh_client.models.task_log import TaskLog
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Execution Logs
        api_response = api_instance.get_execution_logs_api_v1_executions_execution_id_logs_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->get_execution_logs_api_v1_executions_execution_id_logs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->get_execution_logs_api_v1_executions_execution_id_logs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[TaskLog]**](TaskLog.md)

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

# **get_execution_parent_subflow_api_v1_executions_execution_id_parent_subflow_get**
> PersistedSubflow get_execution_parent_subflow_api_v1_executions_execution_id_parent_subflow_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Execution Parent Subflow

### Example


```python
import amesh_client
from amesh_client.models.persisted_subflow import PersistedSubflow
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Execution Parent Subflow
        api_response = api_instance.get_execution_parent_subflow_api_v1_executions_execution_id_parent_subflow_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->get_execution_parent_subflow_api_v1_executions_execution_id_parent_subflow_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->get_execution_parent_subflow_api_v1_executions_execution_id_parent_subflow_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PersistedSubflow**](PersistedSubflow.md)

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

# **get_task_admission_api_v1_task_runs_task_run_id_admission_get**
> AdmissionDecision get_task_admission_api_v1_task_runs_task_run_id_admission_get(task_run_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Task Admission

### Example


```python
import amesh_client
from amesh_client.models.admission_decision import AdmissionDecision
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    task_run_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Task Admission
        api_response = api_instance.get_task_admission_api_v1_task_runs_task_run_id_admission_get(task_run_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->get_task_admission_api_v1_task_runs_task_run_id_admission_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->get_task_admission_api_v1_task_runs_task_run_id_admission_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **task_run_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AdmissionDecision**](AdmissionDecision.md)

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

# **list_execution_control_history_api_v1_executions_execution_id_interventions_get**
> List[ExecutionInterventionRecord] list_execution_control_history_api_v1_executions_execution_id_interventions_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Execution Control History

### Example


```python
import amesh_client
from amesh_client.models.execution_intervention_record import ExecutionInterventionRecord
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Execution Control History
        api_response = api_instance.list_execution_control_history_api_v1_executions_execution_id_interventions_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->list_execution_control_history_api_v1_executions_execution_id_interventions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->list_execution_control_history_api_v1_executions_execution_id_interventions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[ExecutionInterventionRecord]**](ExecutionInterventionRecord.md)

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

# **list_execution_files_api_v1_executions_execution_id_files_get**
> List[ExecutionArtifact] list_execution_files_api_v1_executions_execution_id_files_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Execution Files

### Example


```python
import amesh_client
from amesh_client.models.execution_artifact import ExecutionArtifact
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Execution Files
        api_response = api_instance.list_execution_files_api_v1_executions_execution_id_files_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->list_execution_files_api_v1_executions_execution_id_files_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->list_execution_files_api_v1_executions_execution_id_files_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[ExecutionArtifact]**](ExecutionArtifact.md)

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

# **list_execution_subflows_api_v1_executions_execution_id_subflows_get**
> List[PersistedSubflow] list_execution_subflows_api_v1_executions_execution_id_subflows_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Execution Subflows

### Example


```python
import amesh_client
from amesh_client.models.persisted_subflow import PersistedSubflow
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Execution Subflows
        api_response = api_instance.list_execution_subflows_api_v1_executions_execution_id_subflows_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->list_execution_subflows_api_v1_executions_execution_id_subflows_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->list_execution_subflows_api_v1_executions_execution_id_subflows_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[PersistedSubflow]**](PersistedSubflow.md)

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

# **list_executions_api_v1_executions_get**
> List[PersistedExecution] list_executions_api_v1_executions_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Executions

### Example


```python
import amesh_client
from amesh_client.models.persisted_execution import PersistedExecution
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    cursor = 'cursor_example' # str | Opaque cursor from the prior page (optional)
    limit = 100 # int |  (optional) (default to 100)
    filter = ['filter_example'] # List[str] | Repeatable top-level equality filter in field=value form (optional)
    sort = 'sort_example' # str | Comma-separated top-level fields; prefix descending fields with - (optional)
    fields = 'fields_example' # str | Comma-separated top-level response fields (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Executions
        api_response = api_instance.list_executions_api_v1_executions_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->list_executions_api_v1_executions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->list_executions_api_v1_executions_get: %s\n" % e)
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

[**List[PersistedExecution]**](PersistedExecution.md)

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

# **preview_execution_control_api_v1_executions_execution_id_interventions_preview_post**
> ExecutionInterventionPreview preview_execution_control_api_v1_executions_execution_id_interventions_preview_post(execution_id, execution_intervention_preview_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Execution Control

### Example


```python
import amesh_client
from amesh_client.models.execution_intervention_preview import ExecutionInterventionPreview
from amesh_client.models.execution_intervention_preview_request import ExecutionInterventionPreviewRequest
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    execution_intervention_preview_request = amesh_client.ExecutionInterventionPreviewRequest() # ExecutionInterventionPreviewRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Execution Control
        api_response = api_instance.preview_execution_control_api_v1_executions_execution_id_interventions_preview_post(execution_id, execution_intervention_preview_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->preview_execution_control_api_v1_executions_execution_id_interventions_preview_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->preview_execution_control_api_v1_executions_execution_id_interventions_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **execution_intervention_preview_request** | [**ExecutionInterventionPreviewRequest**](ExecutionInterventionPreviewRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ExecutionInterventionPreview**](ExecutionInterventionPreview.md)

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

# **reduce_execution_events_api_v1_executions_reduce_post**
> ReduceExecutionResponse reduce_execution_events_api_v1_executions_reduce_post(reduce_execution_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Reduce Execution Events

### Example


```python
import amesh_client
from amesh_client.models.reduce_execution_request import ReduceExecutionRequest
from amesh_client.models.reduce_execution_response import ReduceExecutionResponse
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    reduce_execution_request = amesh_client.ReduceExecutionRequest() # ReduceExecutionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Reduce Execution Events
        api_response = api_instance.reduce_execution_events_api_v1_executions_reduce_post(reduce_execution_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->reduce_execution_events_api_v1_executions_reduce_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->reduce_execution_events_api_v1_executions_reduce_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reduce_execution_request** | [**ReduceExecutionRequest**](ReduceExecutionRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ReduceExecutionResponse**](ReduceExecutionResponse.md)

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

# **resume_task_run_api_v1_executions_execution_id_task_runs_task_run_id_resume_post**
> PersistedTaskRun resume_task_run_api_v1_executions_execution_id_task_runs_task_run_id_resume_post(execution_id, task_run_id, resume_task_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Resume Task Run

### Example


```python
import amesh_client
from amesh_client.models.persisted_task_run import PersistedTaskRun
from amesh_client.models.resume_task_request import ResumeTaskRequest
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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    task_run_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    resume_task_request = amesh_client.ResumeTaskRequest() # ResumeTaskRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Resume Task Run
        api_response = api_instance.resume_task_run_api_v1_executions_execution_id_task_runs_task_run_id_resume_post(execution_id, task_run_id, resume_task_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ExecutionsApi->resume_task_run_api_v1_executions_execution_id_task_runs_task_run_id_resume_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ExecutionsApi->resume_task_run_api_v1_executions_execution_id_task_runs_task_run_id_resume_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **task_run_id** | **UUID**|  |
 **resume_task_request** | [**ResumeTaskRequest**](ResumeTaskRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PersistedTaskRun**](PersistedTaskRun.md)

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

# **stream_execution_evidence_api_v1_executions_execution_id_evidence_stream_get**
> stream_execution_evidence_api_v1_executions_execution_id_evidence_stream_get(execution_id, cursor=cursor, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Stream Execution Evidence

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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    cursor = 'cursor_example' # str | Opaque reconnect cursor (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Stream Execution Evidence
        api_instance.stream_execution_evidence_api_v1_executions_execution_id_evidence_stream_get(execution_id, cursor=cursor, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling ExecutionsApi->stream_execution_evidence_api_v1_executions_execution_id_evidence_stream_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **cursor** | **str**| Opaque reconnect cursor | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/x-ndjson, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Evidence events streamed as newline-delimited JSON |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **stream_execution_logs_api_v1_executions_execution_id_logs_stream_get**
> stream_execution_logs_api_v1_executions_execution_id_logs_stream_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Stream Execution Logs

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
    api_instance = amesh_client.ExecutionsApi(api_client)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Stream Execution Logs
        api_instance.stream_execution_logs_api_v1_executions_execution_id_logs_stream_get(execution_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling ExecutionsApi->stream_execution_logs_api_v1_executions_execution_id_logs_stream_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **execution_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/x-ndjson, application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Task logs streamed as newline-delimited JSON |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
