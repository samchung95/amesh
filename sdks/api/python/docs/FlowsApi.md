# amesh_client.FlowsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apply_flow_api_v1_flows_put**](FlowsApi.md#apply_flow_api_v1_flows_put) | **PUT** /api/v1/flows | Apply Flow
[**delete_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_delete**](FlowsApi.md#delete_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_delete) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision} | Delete Flow Revision
[**diff_flow_draft_api_v1_flows_namespace_flow_id_revisions_revision_diff_draft_post**](FlowsApi.md#diff_flow_draft_api_v1_flows_namespace_flow_id_revisions_revision_diff_draft_post) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/diff-draft | Diff Flow Draft
[**diff_flow_revisions_api_v1_flows_namespace_flow_id_revisions_diff_get**](FlowsApi.md#diff_flow_revisions_api_v1_flows_namespace_flow_id_revisions_diff_get) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions/diff | Diff Flow Revisions
[**export_flow_document_api_v1_flows_namespace_flow_id_document_get**](FlowsApi.md#export_flow_document_api_v1_flows_namespace_flow_id_document_get) | **GET** /api/v1/flows/{namespace}/{flow_id}/document | Export Flow Document
[**format_flow_api_v1_flows_format_post**](FlowsApi.md#format_flow_api_v1_flows_format_post) | **POST** /api/v1/flows/format | Format Flow
[**get_flow_data_contract_api_v1_flows_namespace_flow_id_data_contract_get**](FlowsApi.md#get_flow_data_contract_api_v1_flows_namespace_flow_id_data_contract_get) | **GET** /api/v1/flows/{namespace}/{flow_id}/data-contract | Get Flow Data Contract
[**get_flow_editor_schema_api_v1_flows_editor_schema_get**](FlowsApi.md#get_flow_editor_schema_api_v1_flows_editor_schema_get) | **GET** /api/v1/flows/editor/schema | Get Flow Editor Schema
[**get_flow_graph_api_v1_flows_namespace_flow_id_graph_get**](FlowsApi.md#get_flow_graph_api_v1_flows_namespace_flow_id_graph_get) | **GET** /api/v1/flows/{namespace}/{flow_id}/graph | Get Flow Graph
[**get_flow_metadata_api_v1_flows_namespace_flow_id_metadata_get**](FlowsApi.md#get_flow_metadata_api_v1_flows_namespace_flow_id_metadata_get) | **GET** /api/v1/flows/{namespace}/{flow_id}/metadata | Get Flow Metadata
[**list_flow_revisions_api_v1_flows_namespace_flow_id_revisions_get**](FlowsApi.md#list_flow_revisions_api_v1_flows_namespace_flow_id_revisions_get) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions | List Flow Revisions
[**list_flows_api_v1_flows_get**](FlowsApi.md#list_flows_api_v1_flows_get) | **GET** /api/v1/flows | List Flows
[**preview_flow_expression_api_v1_flows_expressions_preview_post**](FlowsApi.md#preview_flow_expression_api_v1_flows_expressions_preview_post) | **POST** /api/v1/flows/expressions/preview | Preview Flow Expression
[**promote_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_lifecycle_put**](FlowsApi.md#promote_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_lifecycle_put) | **PUT** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/lifecycle | Promote Flow Revision
[**restore_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_restore_post**](FlowsApi.md#restore_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_restore_post) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/restore | Restore Flow Revision
[**validate_flow_api_v1_flows_validate_post**](FlowsApi.md#validate_flow_api_v1_flows_validate_post) | **POST** /api/v1/flows/validate | Validate Flow


# **apply_flow_api_v1_flows_put**
> PersistedFlow apply_flow_api_v1_flows_put(if_match=if_match, x_amesh_source=x_amesh_source, x_amesh_commit=x_amesh_commit, x_amesh_environment=x_amesh_environment, x_amesh_deployment=x_amesh_deployment, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Apply Flow

### Example


```python
import amesh_client
from amesh_client.models.persisted_flow import PersistedFlow
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
    api_instance = amesh_client.FlowsApi(api_client)
    if_match = 'if_match_example' # str |  (optional)
    x_amesh_source = 'x_amesh_source_example' # str |  (optional)
    x_amesh_commit = 'x_amesh_commit_example' # str |  (optional)
    x_amesh_environment = 'x_amesh_environment_example' # str |  (optional)
    x_amesh_deployment = 'x_amesh_deployment_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Apply Flow
        api_response = api_instance.apply_flow_api_v1_flows_put(if_match=if_match, x_amesh_source=x_amesh_source, x_amesh_commit=x_amesh_commit, x_amesh_environment=x_amesh_environment, x_amesh_deployment=x_amesh_deployment, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->apply_flow_api_v1_flows_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->apply_flow_api_v1_flows_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **if_match** | **str**|  | [optional]
 **x_amesh_source** | **str**|  | [optional]
 **x_amesh_commit** | **str**|  | [optional]
 **x_amesh_environment** | **str**|  | [optional]
 **x_amesh_deployment** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PersistedFlow**](PersistedFlow.md)

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

# **delete_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_delete**
> delete_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_delete(namespace, flow_id, revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Delete Flow Revision

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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    revision = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Delete Flow Revision
        api_instance.delete_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_delete(namespace, flow_id, revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling FlowsApi->delete_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **revision** | **int**|  |
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

# **diff_flow_draft_api_v1_flows_namespace_flow_id_revisions_revision_diff_draft_post**
> FlowRevisionDiff diff_flow_draft_api_v1_flows_namespace_flow_id_revisions_revision_diff_draft_post(namespace, flow_id, revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Diff Flow Draft

### Example


```python
import amesh_client
from amesh_client.models.flow_revision_diff import FlowRevisionDiff
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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    revision = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Diff Flow Draft
        api_response = api_instance.diff_flow_draft_api_v1_flows_namespace_flow_id_revisions_revision_diff_draft_post(namespace, flow_id, revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->diff_flow_draft_api_v1_flows_namespace_flow_id_revisions_revision_diff_draft_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->diff_flow_draft_api_v1_flows_namespace_flow_id_revisions_revision_diff_draft_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **revision** | **int**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**FlowRevisionDiff**](FlowRevisionDiff.md)

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

# **diff_flow_revisions_api_v1_flows_namespace_flow_id_revisions_diff_get**
> FlowRevisionDiff diff_flow_revisions_api_v1_flows_namespace_flow_id_revisions_diff_get(namespace, flow_id, var_from, to, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Diff Flow Revisions

### Example


```python
import amesh_client
from amesh_client.models.flow_revision_diff import FlowRevisionDiff
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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    var_from = 56 # int |
    to = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Diff Flow Revisions
        api_response = api_instance.diff_flow_revisions_api_v1_flows_namespace_flow_id_revisions_diff_get(namespace, flow_id, var_from, to, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->diff_flow_revisions_api_v1_flows_namespace_flow_id_revisions_diff_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->diff_flow_revisions_api_v1_flows_namespace_flow_id_revisions_diff_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **var_from** | **int**|  |
 **to** | **int**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**FlowRevisionDiff**](FlowRevisionDiff.md)

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

# **export_flow_document_api_v1_flows_namespace_flow_id_document_get**
> FlowDocumentExport export_flow_document_api_v1_flows_namespace_flow_id_document_get(namespace, flow_id, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Export Flow Document

### Example


```python
import amesh_client
from amesh_client.models.flow_document_export import FlowDocumentExport
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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    revision = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Export Flow Document
        api_response = api_instance.export_flow_document_api_v1_flows_namespace_flow_id_document_get(namespace, flow_id, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->export_flow_document_api_v1_flows_namespace_flow_id_document_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->export_flow_document_api_v1_flows_namespace_flow_id_document_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **revision** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**FlowDocumentExport**](FlowDocumentExport.md)

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

# **format_flow_api_v1_flows_format_post**
> FlowFormatResponse format_flow_api_v1_flows_format_post()

Format Flow

### Example


```python
import amesh_client
from amesh_client.models.flow_format_response import FlowFormatResponse
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
    api_instance = amesh_client.FlowsApi(api_client)

    try:
        # Format Flow
        api_response = api_instance.format_flow_api_v1_flows_format_post()
        print("The response of FlowsApi->format_flow_api_v1_flows_format_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->format_flow_api_v1_flows_format_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**FlowFormatResponse**](FlowFormatResponse.md)

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

# **get_flow_data_contract_api_v1_flows_namespace_flow_id_data_contract_get**
> FlowDataContract get_flow_data_contract_api_v1_flows_namespace_flow_id_data_contract_get(namespace, flow_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Flow Data Contract

### Example


```python
import amesh_client
from amesh_client.models.flow_data_contract import FlowDataContract
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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Flow Data Contract
        api_response = api_instance.get_flow_data_contract_api_v1_flows_namespace_flow_id_data_contract_get(namespace, flow_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->get_flow_data_contract_api_v1_flows_namespace_flow_id_data_contract_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->get_flow_data_contract_api_v1_flows_namespace_flow_id_data_contract_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**FlowDataContract**](FlowDataContract.md)

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

# **get_flow_editor_schema_api_v1_flows_editor_schema_get**
> FlowEditorSchemaResponse get_flow_editor_schema_api_v1_flows_editor_schema_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Flow Editor Schema

### Example


```python
import amesh_client
from amesh_client.models.flow_editor_schema_response import FlowEditorSchemaResponse
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
    api_instance = amesh_client.FlowsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Flow Editor Schema
        api_response = api_instance.get_flow_editor_schema_api_v1_flows_editor_schema_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->get_flow_editor_schema_api_v1_flows_editor_schema_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->get_flow_editor_schema_api_v1_flows_editor_schema_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**FlowEditorSchemaResponse**](FlowEditorSchemaResponse.md)

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

# **get_flow_graph_api_v1_flows_namespace_flow_id_graph_get**
> FlowGraph get_flow_graph_api_v1_flows_namespace_flow_id_graph_get(namespace, flow_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Flow Graph

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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Flow Graph
        api_response = api_instance.get_flow_graph_api_v1_flows_namespace_flow_id_graph_get(namespace, flow_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->get_flow_graph_api_v1_flows_namespace_flow_id_graph_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->get_flow_graph_api_v1_flows_namespace_flow_id_graph_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
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

# **get_flow_metadata_api_v1_flows_namespace_flow_id_metadata_get**
> FlowMetadataResponse get_flow_metadata_api_v1_flows_namespace_flow_id_metadata_get(namespace, flow_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Flow Metadata

### Example


```python
import amesh_client
from amesh_client.models.flow_metadata_response import FlowMetadataResponse
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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Flow Metadata
        api_response = api_instance.get_flow_metadata_api_v1_flows_namespace_flow_id_metadata_get(namespace, flow_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->get_flow_metadata_api_v1_flows_namespace_flow_id_metadata_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->get_flow_metadata_api_v1_flows_namespace_flow_id_metadata_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**FlowMetadataResponse**](FlowMetadataResponse.md)

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

# **list_flow_revisions_api_v1_flows_namespace_flow_id_revisions_get**
> List[FlowRevisionRecord] list_flow_revisions_api_v1_flows_namespace_flow_id_revisions_get(namespace, flow_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Flow Revisions

### Example


```python
import amesh_client
from amesh_client.models.flow_revision_record import FlowRevisionRecord
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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Flow Revisions
        api_response = api_instance.list_flow_revisions_api_v1_flows_namespace_flow_id_revisions_get(namespace, flow_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->list_flow_revisions_api_v1_flows_namespace_flow_id_revisions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->list_flow_revisions_api_v1_flows_namespace_flow_id_revisions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[FlowRevisionRecord]**](FlowRevisionRecord.md)

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

# **list_flows_api_v1_flows_get**
> List[PersistedFlow] list_flows_api_v1_flows_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Flows

### Example


```python
import amesh_client
from amesh_client.models.persisted_flow import PersistedFlow
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
    api_instance = amesh_client.FlowsApi(api_client)
    cursor = 'cursor_example' # str | Opaque cursor from the prior page (optional)
    limit = 56 # int |  (optional)
    filter = ['filter_example'] # List[str] | Repeatable top-level equality filter in field=value form (optional)
    sort = 'sort_example' # str | Comma-separated top-level fields; prefix descending fields with - (optional)
    fields = 'fields_example' # str | Comma-separated top-level response fields (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Flows
        api_response = api_instance.list_flows_api_v1_flows_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->list_flows_api_v1_flows_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->list_flows_api_v1_flows_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **str**| Opaque cursor from the prior page | [optional]
 **limit** | **int**|  | [optional]
 **filter** | [**List[str]**](str.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional]
 **sort** | **str**| Comma-separated top-level fields; prefix descending fields with - | [optional]
 **fields** | **str**| Comma-separated top-level response fields | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[PersistedFlow]**](PersistedFlow.md)

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

# **preview_flow_expression_api_v1_flows_expressions_preview_post**
> ExpressionPreviewResponse preview_flow_expression_api_v1_flows_expressions_preview_post(expression_preview_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Flow Expression

### Example


```python
import amesh_client
from amesh_client.models.expression_preview_request import ExpressionPreviewRequest
from amesh_client.models.expression_preview_response import ExpressionPreviewResponse
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
    api_instance = amesh_client.FlowsApi(api_client)
    expression_preview_request = amesh_client.ExpressionPreviewRequest() # ExpressionPreviewRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Flow Expression
        api_response = api_instance.preview_flow_expression_api_v1_flows_expressions_preview_post(expression_preview_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->preview_flow_expression_api_v1_flows_expressions_preview_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->preview_flow_expression_api_v1_flows_expressions_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **expression_preview_request** | [**ExpressionPreviewRequest**](ExpressionPreviewRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ExpressionPreviewResponse**](ExpressionPreviewResponse.md)

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

# **promote_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_lifecycle_put**
> PersistedFlow promote_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_lifecycle_put(namespace, flow_id, revision, flow_revision_lifecycle_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Promote Flow Revision

### Example


```python
import amesh_client
from amesh_client.models.flow_revision_lifecycle_request import FlowRevisionLifecycleRequest
from amesh_client.models.persisted_flow import PersistedFlow
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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    revision = 56 # int |
    flow_revision_lifecycle_request = amesh_client.FlowRevisionLifecycleRequest() # FlowRevisionLifecycleRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Promote Flow Revision
        api_response = api_instance.promote_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_lifecycle_put(namespace, flow_id, revision, flow_revision_lifecycle_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->promote_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_lifecycle_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->promote_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_lifecycle_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **revision** | **int**|  |
 **flow_revision_lifecycle_request** | [**FlowRevisionLifecycleRequest**](FlowRevisionLifecycleRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PersistedFlow**](PersistedFlow.md)

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

# **restore_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_restore_post**
> PersistedFlow restore_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_restore_post(namespace, flow_id, revision, flow_revision_restore_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Restore Flow Revision

### Example


```python
import amesh_client
from amesh_client.models.flow_revision_restore_request import FlowRevisionRestoreRequest
from amesh_client.models.persisted_flow import PersistedFlow
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
    api_instance = amesh_client.FlowsApi(api_client)
    namespace = 'namespace_example' # str |
    flow_id = 'flow_id_example' # str |
    revision = 56 # int |
    flow_revision_restore_request = amesh_client.FlowRevisionRestoreRequest() # FlowRevisionRestoreRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Restore Flow Revision
        api_response = api_instance.restore_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_restore_post(namespace, flow_id, revision, flow_revision_restore_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of FlowsApi->restore_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_restore_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->restore_flow_revision_api_v1_flows_namespace_flow_id_revisions_revision_restore_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **flow_id** | **str**|  |
 **revision** | **int**|  |
 **flow_revision_restore_request** | [**FlowRevisionRestoreRequest**](FlowRevisionRestoreRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PersistedFlow**](PersistedFlow.md)

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

# **validate_flow_api_v1_flows_validate_post**
> FlowValidationResult validate_flow_api_v1_flows_validate_post()

Validate Flow

### Example


```python
import amesh_client
from amesh_client.models.flow_validation_result import FlowValidationResult
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
    api_instance = amesh_client.FlowsApi(api_client)

    try:
        # Validate Flow
        api_response = api_instance.validate_flow_api_v1_flows_validate_post()
        print("The response of FlowsApi->validate_flow_api_v1_flows_validate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FlowsApi->validate_flow_api_v1_flows_validate_post: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**FlowValidationResult**](FlowValidationResult.md)

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
