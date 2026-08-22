# amesh_client.PluginsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**download_plugin_registry_bundle_api_v1_plugin_registry_blobs_digest_get**](PluginsApi.md#download_plugin_registry_bundle_api_v1_plugin_registry_blobs_digest_get) | **GET** /api/v1/plugin-registry/blobs/{digest} | Download Plugin Registry Bundle
[**export_plugin_registry_api_v1_plugin_registry_offline_export_get**](PluginsApi.md#export_plugin_registry_api_v1_plugin_registry_offline_export_get) | **GET** /api/v1/plugin-registry/offline-export | Export Plugin Registry
[**get_plugin_registry_index_api_v1_plugin_registry_index_get**](PluginsApi.md#get_plugin_registry_index_api_v1_plugin_registry_index_get) | **GET** /api/v1/plugin-registry/index | Get Plugin Registry Index
[**get_plugin_registry_package_api_v1_plugin_registry_packages_name_version_get**](PluginsApi.md#get_plugin_registry_package_api_v1_plugin_registry_packages_name_version_get) | **GET** /api/v1/plugin-registry/packages/{name}/{version} | Get Plugin Registry Package
[**import_plugin_registry_api_v1_plugin_registry_offline_import_post**](PluginsApi.md#import_plugin_registry_api_v1_plugin_registry_offline_import_post) | **POST** /api/v1/plugin-registry/offline-import | Import Plugin Registry
[**install_plugin_bundle_api_v1_plugins_install_post**](PluginsApi.md#install_plugin_bundle_api_v1_plugins_install_post) | **POST** /api/v1/plugins/install | Install Plugin Bundle
[**isolated_plugin_runtime_status_api_v1_plugins_isolated_runtime_get**](PluginsApi.md#isolated_plugin_runtime_status_api_v1_plugins_isolated_runtime_get) | **GET** /api/v1/plugins/isolated-runtime | Isolated Plugin Runtime Status
[**list_plugins_api_v1_plugins_get**](PluginsApi.md#list_plugins_api_v1_plugins_get) | **GET** /api/v1/plugins | List Plugins
[**publish_plugin_registry_package_api_v1_plugin_registry_packages_post**](PluginsApi.md#publish_plugin_registry_package_api_v1_plugin_registry_packages_post) | **POST** /api/v1/plugin-registry/packages | Publish Plugin Registry Package
[**refresh_plugins_api_v1_plugins_refresh_post**](PluginsApi.md#refresh_plugins_api_v1_plugins_refresh_post) | **POST** /api/v1/plugins/refresh | Refresh Plugins
[**trusted_plugin_runtime_status_api_v1_plugins_trusted_runtime_get**](PluginsApi.md#trusted_plugin_runtime_status_api_v1_plugins_trusted_runtime_get) | **GET** /api/v1/plugins/trusted-runtime | Trusted Plugin Runtime Status
[**yank_plugin_registry_package_api_v1_plugin_registry_packages_name_version_yank_post**](PluginsApi.md#yank_plugin_registry_package_api_v1_plugin_registry_packages_name_version_yank_post) | **POST** /api/v1/plugin-registry/packages/{name}/{version}/yank | Yank Plugin Registry Package


# **download_plugin_registry_bundle_api_v1_plugin_registry_blobs_digest_get**
> download_plugin_registry_bundle_api_v1_plugin_registry_blobs_digest_get(digest, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Download Plugin Registry Bundle

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
    api_instance = amesh_client.PluginsApi(api_client)
    digest = 'digest_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Download Plugin Registry Bundle
        api_instance.download_plugin_registry_bundle_api_v1_plugin_registry_blobs_digest_get(digest, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling PluginsApi->download_plugin_registry_bundle_api_v1_plugin_registry_blobs_digest_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **digest** | **str**|  |
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

# **export_plugin_registry_api_v1_plugin_registry_offline_export_get**
> export_plugin_registry_api_v1_plugin_registry_offline_export_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Export Plugin Registry

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
    api_instance = amesh_client.PluginsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Export Plugin Registry
        api_instance.export_plugin_registry_api_v1_plugin_registry_offline_export_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling PluginsApi->export_plugin_registry_api_v1_plugin_registry_offline_export_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
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

# **get_plugin_registry_index_api_v1_plugin_registry_index_get**
> PluginRegistryIndex get_plugin_registry_index_api_v1_plugin_registry_index_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Plugin Registry Index

### Example


```python
import amesh_client
from amesh_client.models.plugin_registry_index import PluginRegistryIndex
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
    api_instance = amesh_client.PluginsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Plugin Registry Index
        api_response = api_instance.get_plugin_registry_index_api_v1_plugin_registry_index_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->get_plugin_registry_index_api_v1_plugin_registry_index_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->get_plugin_registry_index_api_v1_plugin_registry_index_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginRegistryIndex**](PluginRegistryIndex.md)

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

# **get_plugin_registry_package_api_v1_plugin_registry_packages_name_version_get**
> PluginRegistryPackage get_plugin_registry_package_api_v1_plugin_registry_packages_name_version_get(name, version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Plugin Registry Package

### Example


```python
import amesh_client
from amesh_client.models.plugin_registry_package import PluginRegistryPackage
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
    api_instance = amesh_client.PluginsApi(api_client)
    name = 'name_example' # str |
    version = 'version_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Plugin Registry Package
        api_response = api_instance.get_plugin_registry_package_api_v1_plugin_registry_packages_name_version_get(name, version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->get_plugin_registry_package_api_v1_plugin_registry_packages_name_version_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->get_plugin_registry_package_api_v1_plugin_registry_packages_name_version_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  |
 **version** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)

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

# **import_plugin_registry_api_v1_plugin_registry_offline_import_post**
> PluginRegistryIndex import_plugin_registry_api_v1_plugin_registry_offline_import_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Import Plugin Registry

### Example


```python
import amesh_client
from amesh_client.models.plugin_registry_index import PluginRegistryIndex
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
    api_instance = amesh_client.PluginsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Import Plugin Registry
        api_response = api_instance.import_plugin_registry_api_v1_plugin_registry_offline_import_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->import_plugin_registry_api_v1_plugin_registry_offline_import_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->import_plugin_registry_api_v1_plugin_registry_offline_import_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginRegistryIndex**](PluginRegistryIndex.md)

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

# **install_plugin_bundle_api_v1_plugins_install_post**
> PluginCatalogSnapshot install_plugin_bundle_api_v1_plugins_install_post(content_digest, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Install Plugin Bundle

### Example


```python
import amesh_client
from amesh_client.models.plugin_catalog_snapshot import PluginCatalogSnapshot
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
    api_instance = amesh_client.PluginsApi(api_client)
    content_digest = 'content_digest_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Install Plugin Bundle
        api_response = api_instance.install_plugin_bundle_api_v1_plugins_install_post(content_digest, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->install_plugin_bundle_api_v1_plugins_install_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->install_plugin_bundle_api_v1_plugins_install_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **content_digest** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)

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

# **isolated_plugin_runtime_status_api_v1_plugins_isolated_runtime_get**
> IsolatedPluginRuntimeSnapshot isolated_plugin_runtime_status_api_v1_plugins_isolated_runtime_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Isolated Plugin Runtime Status

### Example


```python
import amesh_client
from amesh_client.models.isolated_plugin_runtime_snapshot import IsolatedPluginRuntimeSnapshot
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
    api_instance = amesh_client.PluginsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Isolated Plugin Runtime Status
        api_response = api_instance.isolated_plugin_runtime_status_api_v1_plugins_isolated_runtime_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->isolated_plugin_runtime_status_api_v1_plugins_isolated_runtime_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->isolated_plugin_runtime_status_api_v1_plugins_isolated_runtime_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**IsolatedPluginRuntimeSnapshot**](IsolatedPluginRuntimeSnapshot.md)

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

# **list_plugins_api_v1_plugins_get**
> PluginCatalogSnapshot list_plugins_api_v1_plugins_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Plugins

### Example


```python
import amesh_client
from amesh_client.models.plugin_catalog_snapshot import PluginCatalogSnapshot
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
    api_instance = amesh_client.PluginsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Plugins
        api_response = api_instance.list_plugins_api_v1_plugins_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->list_plugins_api_v1_plugins_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->list_plugins_api_v1_plugins_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)

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

# **publish_plugin_registry_package_api_v1_plugin_registry_packages_post**
> PluginRegistryPackage publish_plugin_registry_package_api_v1_plugin_registry_packages_post(plugin_registry_publish_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Publish Plugin Registry Package

### Example


```python
import amesh_client
from amesh_client.models.plugin_registry_package import PluginRegistryPackage
from amesh_client.models.plugin_registry_publish_request import PluginRegistryPublishRequest
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
    api_instance = amesh_client.PluginsApi(api_client)
    plugin_registry_publish_request = amesh_client.PluginRegistryPublishRequest() # PluginRegistryPublishRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Publish Plugin Registry Package
        api_response = api_instance.publish_plugin_registry_package_api_v1_plugin_registry_packages_post(plugin_registry_publish_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->publish_plugin_registry_package_api_v1_plugin_registry_packages_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->publish_plugin_registry_package_api_v1_plugin_registry_packages_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_registry_publish_request** | [**PluginRegistryPublishRequest**](PluginRegistryPublishRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)

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

# **refresh_plugins_api_v1_plugins_refresh_post**
> PluginCatalogSnapshot refresh_plugins_api_v1_plugins_refresh_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Refresh Plugins

### Example


```python
import amesh_client
from amesh_client.models.plugin_catalog_snapshot import PluginCatalogSnapshot
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
    api_instance = amesh_client.PluginsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Refresh Plugins
        api_response = api_instance.refresh_plugins_api_v1_plugins_refresh_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->refresh_plugins_api_v1_plugins_refresh_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->refresh_plugins_api_v1_plugins_refresh_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)

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

# **trusted_plugin_runtime_status_api_v1_plugins_trusted_runtime_get**
> TrustedPluginRuntimeSnapshot trusted_plugin_runtime_status_api_v1_plugins_trusted_runtime_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Trusted Plugin Runtime Status

### Example


```python
import amesh_client
from amesh_client.models.trusted_plugin_runtime_snapshot import TrustedPluginRuntimeSnapshot
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
    api_instance = amesh_client.PluginsApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Trusted Plugin Runtime Status
        api_response = api_instance.trusted_plugin_runtime_status_api_v1_plugins_trusted_runtime_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->trusted_plugin_runtime_status_api_v1_plugins_trusted_runtime_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->trusted_plugin_runtime_status_api_v1_plugins_trusted_runtime_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**TrustedPluginRuntimeSnapshot**](TrustedPluginRuntimeSnapshot.md)

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

# **yank_plugin_registry_package_api_v1_plugin_registry_packages_name_version_yank_post**
> PluginRegistryPackage yank_plugin_registry_package_api_v1_plugin_registry_packages_name_version_yank_post(name, version, plugin_registry_yank_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Yank Plugin Registry Package

### Example


```python
import amesh_client
from amesh_client.models.plugin_registry_package import PluginRegistryPackage
from amesh_client.models.plugin_registry_yank_request import PluginRegistryYankRequest
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
    api_instance = amesh_client.PluginsApi(api_client)
    name = 'name_example' # str |
    version = 'version_example' # str |
    plugin_registry_yank_request = amesh_client.PluginRegistryYankRequest() # PluginRegistryYankRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Yank Plugin Registry Package
        api_response = api_instance.yank_plugin_registry_package_api_v1_plugin_registry_packages_name_version_yank_post(name, version, plugin_registry_yank_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->yank_plugin_registry_package_api_v1_plugin_registry_packages_name_version_yank_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->yank_plugin_registry_package_api_v1_plugin_registry_packages_name_version_yank_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  |
 **version** | **str**|  |
 **plugin_registry_yank_request** | [**PluginRegistryYankRequest**](PluginRegistryYankRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)

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
