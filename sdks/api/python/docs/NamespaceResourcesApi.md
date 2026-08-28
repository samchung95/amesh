# amesh_client.NamespaceResourcesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_namespace_file_api_v1_namespaces_namespace_files_path_delete**](NamespaceResourcesApi.md#delete_namespace_file_api_v1_namespaces_namespace_files_path_delete) | **DELETE** /api/v1/namespaces/{namespace}/files/{path} | Delete Namespace File
[**delete_namespace_key_value_api_v1_namespaces_namespace_key_values_key_delete**](NamespaceResourcesApi.md#delete_namespace_key_value_api_v1_namespaces_namespace_key_values_key_delete) | **DELETE** /api/v1/namespaces/{namespace}/key-values/{key} | Delete Namespace Key Value
[**delete_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_delete**](NamespaceResourcesApi.md#delete_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_delete) | **DELETE** /api/v1/namespaces/{namespace}/secret-bindings/{key} | Delete Namespace Secret Binding
[**download_namespace_file_api_v1_namespaces_namespace_files_path_get**](NamespaceResourcesApi.md#download_namespace_file_api_v1_namespaces_namespace_files_path_get) | **GET** /api/v1/namespaces/{namespace}/files/{path} | Download Namespace File
[**export_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_get**](NamespaceResourcesApi.md#export_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_get) | **GET** /api/v1/namespaces/{namespace}/resource-bundle | Export Namespace Resource Bundle
[**get_namespace_artifact_api_v1_namespaces_namespace_artifacts_path_get**](NamespaceResourcesApi.md#get_namespace_artifact_api_v1_namespaces_namespace_artifacts_path_get) | **GET** /api/v1/namespaces/{namespace}/artifacts/{path} | Get Namespace Artifact
[**get_namespace_key_value_api_v1_namespaces_namespace_key_values_key_get**](NamespaceResourcesApi.md#get_namespace_key_value_api_v1_namespaces_namespace_key_values_key_get) | **GET** /api/v1/namespaces/{namespace}/key-values/{key} | Get Namespace Key Value
[**import_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_post**](NamespaceResourcesApi.md#import_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_post) | **POST** /api/v1/namespaces/{namespace}/resource-bundle | Import Namespace Resource Bundle
[**list_namespace_artifacts_api_v1_namespaces_namespace_artifacts_get**](NamespaceResourcesApi.md#list_namespace_artifacts_api_v1_namespaces_namespace_artifacts_get) | **GET** /api/v1/namespaces/{namespace}/artifacts | List Namespace Artifacts
[**list_namespace_file_versions_api_v1_namespaces_namespace_files_path_versions_get**](NamespaceResourcesApi.md#list_namespace_file_versions_api_v1_namespaces_namespace_files_path_versions_get) | **GET** /api/v1/namespaces/{namespace}/files/{path}/versions | List Namespace File Versions
[**list_namespace_files_api_v1_namespaces_namespace_files_get**](NamespaceResourcesApi.md#list_namespace_files_api_v1_namespaces_namespace_files_get) | **GET** /api/v1/namespaces/{namespace}/files | List Namespace Files
[**list_namespace_key_value_changes_api_v1_namespaces_namespace_key_values_changes_get**](NamespaceResourcesApi.md#list_namespace_key_value_changes_api_v1_namespaces_namespace_key_values_changes_get) | **GET** /api/v1/namespaces/{namespace}/key-values/changes | List Namespace Key Value Changes
[**list_namespace_key_values_api_v1_namespaces_namespace_key_values_get**](NamespaceResourcesApi.md#list_namespace_key_values_api_v1_namespaces_namespace_key_values_get) | **GET** /api/v1/namespaces/{namespace}/key-values | List Namespace Key Values
[**list_namespace_secret_bindings_api_v1_namespaces_namespace_secret_bindings_get**](NamespaceResourcesApi.md#list_namespace_secret_bindings_api_v1_namespaces_namespace_secret_bindings_get) | **GET** /api/v1/namespaces/{namespace}/secret-bindings | List Namespace Secret Bindings
[**move_namespace_file_api_v1_namespaces_namespace_files_path_move_post**](NamespaceResourcesApi.md#move_namespace_file_api_v1_namespaces_namespace_files_path_move_post) | **POST** /api/v1/namespaces/{namespace}/files/{path}/move | Move Namespace File
[**put_namespace_key_value_api_v1_namespaces_namespace_key_values_key_put**](NamespaceResourcesApi.md#put_namespace_key_value_api_v1_namespaces_namespace_key_values_key_put) | **PUT** /api/v1/namespaces/{namespace}/key-values/{key} | Put Namespace Key Value
[**put_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_put**](NamespaceResourcesApi.md#put_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_put) | **PUT** /api/v1/namespaces/{namespace}/secret-bindings/{key} | Put Namespace Secret Binding
[**upload_namespace_file_api_v1_namespaces_namespace_files_path_put**](NamespaceResourcesApi.md#upload_namespace_file_api_v1_namespaces_namespace_files_path_put) | **PUT** /api/v1/namespaces/{namespace}/files/{path} | Upload Namespace File


# **delete_namespace_file_api_v1_namespaces_namespace_files_path_delete**
> Dict[str, int] delete_namespace_file_api_v1_namespaces_namespace_files_path_delete(namespace, path, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Delete Namespace File

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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    path = 'path_example' # str |
    expected_version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Delete Namespace File
        api_response = api_instance.delete_namespace_file_api_v1_namespaces_namespace_files_path_delete(namespace, path, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->delete_namespace_file_api_v1_namespaces_namespace_files_path_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->delete_namespace_file_api_v1_namespaces_namespace_files_path_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **path** | **str**|  |
 **expected_version** | **int**|  | [optional]
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

# **delete_namespace_key_value_api_v1_namespaces_namespace_key_values_key_delete**
> Dict[str, Optional[bool]] delete_namespace_key_value_api_v1_namespaces_namespace_key_values_key_delete(namespace, key, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Delete Namespace Key Value

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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    expected_version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Delete Namespace Key Value
        api_response = api_instance.delete_namespace_key_value_api_v1_namespaces_namespace_key_values_key_delete(namespace, key, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->delete_namespace_key_value_api_v1_namespaces_namespace_key_values_key_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->delete_namespace_key_value_api_v1_namespaces_namespace_key_values_key_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **expected_version** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**Dict[str, Optional[bool]]**

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

# **delete_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_delete**
> Dict[str, Optional[bool]] delete_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_delete(namespace, key, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Delete Namespace Secret Binding

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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    expected_version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Delete Namespace Secret Binding
        api_response = api_instance.delete_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_delete(namespace, key, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->delete_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->delete_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **expected_version** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**Dict[str, Optional[bool]]**

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

# **download_namespace_file_api_v1_namespaces_namespace_files_path_get**
> download_namespace_file_api_v1_namespaces_namespace_files_path_get(namespace, path, version=version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Download Namespace File

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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    path = 'path_example' # str |
    version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Download Namespace File
        api_instance.download_namespace_file_api_v1_namespaces_namespace_files_path_get(namespace, path, version=version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->download_namespace_file_api_v1_namespaces_namespace_files_path_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **path** | **str**|  |
 **version** | **int**|  | [optional]
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

# **export_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_get**
> NamespaceResourceBundle export_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Export Namespace Resource Bundle

### Example


```python
import amesh_client
from amesh_client.models.namespace_resource_bundle import NamespaceResourceBundle
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Export Namespace Resource Bundle
        api_response = api_instance.export_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->export_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->export_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**NamespaceResourceBundle**

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

# **get_namespace_artifact_api_v1_namespaces_namespace_artifacts_path_get**
> ArtifactRef get_namespace_artifact_api_v1_namespaces_namespace_artifacts_path_get(namespace, path, version=version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Namespace Artifact

### Example


```python
import amesh_client
from amesh_client.models.artifact_ref import ArtifactRef
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    path = 'path_example' # str |
    version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Namespace Artifact
        api_response = api_instance.get_namespace_artifact_api_v1_namespaces_namespace_artifacts_path_get(namespace, path, version=version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->get_namespace_artifact_api_v1_namespaces_namespace_artifacts_path_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->get_namespace_artifact_api_v1_namespaces_namespace_artifacts_path_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **path** | **str**|  |
 **version** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**ArtifactRef**

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

# **get_namespace_key_value_api_v1_namespaces_namespace_key_values_key_get**
> KeyValueEntry get_namespace_key_value_api_v1_namespaces_namespace_key_values_key_get(namespace, key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Namespace Key Value

### Example


```python
import amesh_client
from amesh_client.models.key_value_entry import KeyValueEntry
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Namespace Key Value
        api_response = api_instance.get_namespace_key_value_api_v1_namespaces_namespace_key_values_key_get(namespace, key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->get_namespace_key_value_api_v1_namespaces_namespace_key_values_key_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->get_namespace_key_value_api_v1_namespaces_namespace_key_values_key_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**KeyValueEntry**

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

# **import_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_post**
> NamespaceResourceImportResult import_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_post(namespace, namespace_resource_bundle, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Import Namespace Resource Bundle

### Example


```python
import amesh_client
from amesh_client.models.namespace_resource_bundle import NamespaceResourceBundle
from amesh_client.models.namespace_resource_import_result import NamespaceResourceImportResult
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    namespace_resource_bundle = amesh_client.NamespaceResourceBundle() # NamespaceResourceBundle |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Import Namespace Resource Bundle
        api_response = api_instance.import_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_post(namespace, namespace_resource_bundle, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->import_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->import_namespace_resource_bundle_api_v1_namespaces_namespace_resource_bundle_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **namespace_resource_bundle** | **NamespaceResourceBundle**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**NamespaceResourceImportResult**

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

# **list_namespace_artifacts_api_v1_namespaces_namespace_artifacts_get**
> List[ArtifactRef] list_namespace_artifacts_api_v1_namespaces_namespace_artifacts_get(namespace, inherited=inherited, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Namespace Artifacts

### Example


```python
import amesh_client
from amesh_client.models.artifact_ref import ArtifactRef
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    inherited = True # bool |  (optional) (default to True)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Namespace Artifacts
        api_response = api_instance.list_namespace_artifacts_api_v1_namespaces_namespace_artifacts_get(namespace, inherited=inherited, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->list_namespace_artifacts_api_v1_namespaces_namespace_artifacts_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->list_namespace_artifacts_api_v1_namespaces_namespace_artifacts_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **inherited** | **bool**|  | [optional] [default to True]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[ArtifactRef]**](ArtifactRef.md)

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

# **list_namespace_file_versions_api_v1_namespaces_namespace_files_path_versions_get**
> List[NamespaceFileVersion] list_namespace_file_versions_api_v1_namespaces_namespace_files_path_versions_get(namespace, path, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Namespace File Versions

### Example


```python
import amesh_client
from amesh_client.models.namespace_file_version import NamespaceFileVersion
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    path = 'path_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Namespace File Versions
        api_response = api_instance.list_namespace_file_versions_api_v1_namespaces_namespace_files_path_versions_get(namespace, path, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->list_namespace_file_versions_api_v1_namespaces_namespace_files_path_versions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->list_namespace_file_versions_api_v1_namespaces_namespace_files_path_versions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **path** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[NamespaceFileVersion]**](NamespaceFileVersion.md)

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

# **list_namespace_files_api_v1_namespaces_namespace_files_get**
> List[NamespaceFile] list_namespace_files_api_v1_namespaces_namespace_files_get(namespace, inherited=inherited, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Namespace Files

### Example


```python
import amesh_client
from amesh_client.models.namespace_file import NamespaceFile
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    inherited = True # bool |  (optional) (default to True)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Namespace Files
        api_response = api_instance.list_namespace_files_api_v1_namespaces_namespace_files_get(namespace, inherited=inherited, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->list_namespace_files_api_v1_namespaces_namespace_files_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->list_namespace_files_api_v1_namespaces_namespace_files_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **inherited** | **bool**|  | [optional] [default to True]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[NamespaceFile]**](NamespaceFile.md)

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

# **list_namespace_key_value_changes_api_v1_namespaces_namespace_key_values_changes_get**
> List[KeyValueChange] list_namespace_key_value_changes_api_v1_namespaces_namespace_key_values_changes_get(namespace, after=after, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Namespace Key Value Changes

### Example


```python
import amesh_client
from amesh_client.models.key_value_change import KeyValueChange
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    after = 0 # int |  (optional) (default to 0)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Namespace Key Value Changes
        api_response = api_instance.list_namespace_key_value_changes_api_v1_namespaces_namespace_key_values_changes_get(namespace, after=after, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->list_namespace_key_value_changes_api_v1_namespaces_namespace_key_values_changes_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->list_namespace_key_value_changes_api_v1_namespaces_namespace_key_values_changes_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **after** | **int**|  | [optional] [default to 0]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[KeyValueChange]**](KeyValueChange.md)

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

# **list_namespace_key_values_api_v1_namespaces_namespace_key_values_get**
> List[KeyValueEntry] list_namespace_key_values_api_v1_namespaces_namespace_key_values_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Namespace Key Values

### Example


```python
import amesh_client
from amesh_client.models.key_value_entry import KeyValueEntry
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Namespace Key Values
        api_response = api_instance.list_namespace_key_values_api_v1_namespaces_namespace_key_values_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->list_namespace_key_values_api_v1_namespaces_namespace_key_values_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->list_namespace_key_values_api_v1_namespaces_namespace_key_values_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[KeyValueEntry]**](KeyValueEntry.md)

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

# **list_namespace_secret_bindings_api_v1_namespaces_namespace_secret_bindings_get**
> List[SecretBinding] list_namespace_secret_bindings_api_v1_namespaces_namespace_secret_bindings_get(namespace, inherited=inherited, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Namespace Secret Bindings

### Example


```python
import amesh_client
from amesh_client.models.secret_binding import SecretBinding
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    inherited = True # bool |  (optional) (default to True)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Namespace Secret Bindings
        api_response = api_instance.list_namespace_secret_bindings_api_v1_namespaces_namespace_secret_bindings_get(namespace, inherited=inherited, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->list_namespace_secret_bindings_api_v1_namespaces_namespace_secret_bindings_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->list_namespace_secret_bindings_api_v1_namespaces_namespace_secret_bindings_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **inherited** | **bool**|  | [optional] [default to True]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[SecretBinding]**](SecretBinding.md)

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

# **move_namespace_file_api_v1_namespaces_namespace_files_path_move_post**
> NamespaceFile move_namespace_file_api_v1_namespaces_namespace_files_path_move_post(namespace, path, namespace_file_move_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Move Namespace File

### Example


```python
import amesh_client
from amesh_client.models.namespace_file import NamespaceFile
from amesh_client.models.namespace_file_move_request import NamespaceFileMoveRequest
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    path = 'path_example' # str |
    namespace_file_move_request = amesh_client.NamespaceFileMoveRequest() # NamespaceFileMoveRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Move Namespace File
        api_response = api_instance.move_namespace_file_api_v1_namespaces_namespace_files_path_move_post(namespace, path, namespace_file_move_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->move_namespace_file_api_v1_namespaces_namespace_files_path_move_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->move_namespace_file_api_v1_namespaces_namespace_files_path_move_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **path** | **str**|  |
 **namespace_file_move_request** | **NamespaceFileMoveRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**NamespaceFile**

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

# **put_namespace_key_value_api_v1_namespaces_namespace_key_values_key_put**
> KeyValueEntry put_namespace_key_value_api_v1_namespaces_namespace_key_values_key_put(namespace, key, key_value_write, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Put Namespace Key Value

### Example


```python
import amesh_client
from amesh_client.models.key_value_entry import KeyValueEntry
from amesh_client.models.key_value_write import KeyValueWrite
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    key_value_write = amesh_client.KeyValueWrite() # KeyValueWrite |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Put Namespace Key Value
        api_response = api_instance.put_namespace_key_value_api_v1_namespaces_namespace_key_values_key_put(namespace, key, key_value_write, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->put_namespace_key_value_api_v1_namespaces_namespace_key_values_key_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->put_namespace_key_value_api_v1_namespaces_namespace_key_values_key_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **key_value_write** | **KeyValueWrite**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**KeyValueEntry**

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

# **put_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_put**
> SecretBinding put_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_put(namespace, key, secret_binding_write, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Put Namespace Secret Binding

### Example


```python
import amesh_client
from amesh_client.models.secret_binding import SecretBinding
from amesh_client.models.secret_binding_write import SecretBindingWrite
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    secret_binding_write = amesh_client.SecretBindingWrite() # SecretBindingWrite |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Put Namespace Secret Binding
        api_response = api_instance.put_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_put(namespace, key, secret_binding_write, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->put_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->put_namespace_secret_binding_api_v1_namespaces_namespace_secret_bindings_key_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **secret_binding_write** | **SecretBindingWrite**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**SecretBinding**

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

# **upload_namespace_file_api_v1_namespaces_namespace_files_path_put**
> NamespaceFile upload_namespace_file_api_v1_namespaces_namespace_files_path_put(namespace, path, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Upload Namespace File

### Example


```python
import amesh_client
from amesh_client.models.namespace_file import NamespaceFile
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
    api_instance = amesh_client.NamespaceResourcesApi(api_client)
    namespace = 'namespace_example' # str |
    path = 'path_example' # str |
    expected_version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Upload Namespace File
        api_response = api_instance.upload_namespace_file_api_v1_namespaces_namespace_files_path_put(namespace, path, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of NamespaceResourcesApi->upload_namespace_file_api_v1_namespaces_namespace_files_path_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling NamespaceResourcesApi->upload_namespace_file_api_v1_namespaces_namespace_files_path_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **path** | **str**|  |
 **expected_version** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**NamespaceFile**

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
