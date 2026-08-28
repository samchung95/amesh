# amesh_client.NamespacesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_get**](NamespacesApi.md#get_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_get) | **GET** /api/v1/namespaces/{namespace}/workflow-metadata | Get Namespace Workflow Metadata
[**upsert_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_put**](NamespacesApi.md#upsert_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_put) | **PUT** /api/v1/namespaces/{namespace}/workflow-metadata | Upsert Namespace Workflow Metadata


# **get_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_get**
> NamespaceWorkflowMetadataView get_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Namespace Workflow Metadata

### Example


```python
import amesh_client
from amesh_client.models.namespace_workflow_metadata_view import NamespaceWorkflowMetadataView
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
    api_instance = amesh_client.NamespacesApi(api_client)
    namespace = 'namespace_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Namespace Workflow Metadata
        api_response = api_instance.get_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespacesApi->get_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespacesApi->get_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**NamespaceWorkflowMetadataView**

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

# **upsert_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_put**
> NamespaceWorkflowMetadata upsert_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_put(namespace, namespace_workflow_metadata_update, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Upsert Namespace Workflow Metadata

### Example


```python
import amesh_client
from amesh_client.models.namespace_workflow_metadata import NamespaceWorkflowMetadata
from amesh_client.models.namespace_workflow_metadata_update import NamespaceWorkflowMetadataUpdate
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
    api_instance = amesh_client.NamespacesApi(api_client)
    namespace = 'namespace_example' # str |
    namespace_workflow_metadata_update = amesh_client.NamespaceWorkflowMetadataUpdate() # NamespaceWorkflowMetadataUpdate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Upsert Namespace Workflow Metadata
        api_response = api_instance.upsert_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_put(namespace, namespace_workflow_metadata_update, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespacesApi->upsert_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespacesApi->upsert_namespace_workflow_metadata_api_v1_namespaces_namespace_workflow_metadata_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **namespace_workflow_metadata_update** | **NamespaceWorkflowMetadataUpdate**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**NamespaceWorkflowMetadata**

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
