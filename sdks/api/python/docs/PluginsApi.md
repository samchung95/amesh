# amesh_client.PluginsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_plugin_policy_rule_api_v1_plugin_policy_rules_post**](PluginsApi.md#create_plugin_policy_rule_api_v1_plugin_policy_rules_post) | **POST** /api/v1/plugin-policy/rules | Create Plugin Policy Rule
[**delete_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_delete**](PluginsApi.md#delete_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_delete) | **DELETE** /api/v1/plugin-policy/rules/{rule_id} | Delete Plugin Policy Rule
[**download_plugin_registry_bundle_api_v1_plugin_registry_blobs_digest_get**](PluginsApi.md#download_plugin_registry_bundle_api_v1_plugin_registry_blobs_digest_get) | **GET** /api/v1/plugin-registry/blobs/{digest} | Download Plugin Registry Bundle
[**evaluate_flow_plugin_policy_api_v1_plugin_policy_evaluate_post**](PluginsApi.md#evaluate_flow_plugin_policy_api_v1_plugin_policy_evaluate_post) | **POST** /api/v1/plugin-policy/evaluate | Evaluate Flow Plugin Policy
[**export_plugin_registry_api_v1_plugin_registry_offline_export_get**](PluginsApi.md#export_plugin_registry_api_v1_plugin_registry_offline_export_get) | **GET** /api/v1/plugin-registry/offline-export | Export Plugin Registry
[**get_effective_plugin_policy_api_v1_plugin_policy_effective_get**](PluginsApi.md#get_effective_plugin_policy_api_v1_plugin_policy_effective_get) | **GET** /api/v1/plugin-policy/effective | Get Effective Plugin Policy
[**get_plugin_registry_index_api_v1_plugin_registry_index_get**](PluginsApi.md#get_plugin_registry_index_api_v1_plugin_registry_index_get) | **GET** /api/v1/plugin-registry/index | Get Plugin Registry Index
[**get_plugin_registry_package_api_v1_plugin_registry_packages_name_version_get**](PluginsApi.md#get_plugin_registry_package_api_v1_plugin_registry_packages_name_version_get) | **GET** /api/v1/plugin-registry/packages/{name}/{version} | Get Plugin Registry Package
[**import_plugin_registry_api_v1_plugin_registry_offline_import_post**](PluginsApi.md#import_plugin_registry_api_v1_plugin_registry_offline_import_post) | **POST** /api/v1/plugin-registry/offline-import | Import Plugin Registry
[**install_plugin_bundle_api_v1_plugins_install_post**](PluginsApi.md#install_plugin_bundle_api_v1_plugins_install_post) | **POST** /api/v1/plugins/install | Install Plugin Bundle
[**isolated_plugin_runtime_status_api_v1_plugins_isolated_runtime_get**](PluginsApi.md#isolated_plugin_runtime_status_api_v1_plugins_isolated_runtime_get) | **GET** /api/v1/plugins/isolated-runtime | Isolated Plugin Runtime Status
[**list_plugin_policy_decisions_api_v1_plugin_policy_decisions_get**](PluginsApi.md#list_plugin_policy_decisions_api_v1_plugin_policy_decisions_get) | **GET** /api/v1/plugin-policy/decisions | List Plugin Policy Decisions
[**list_plugins_api_v1_plugins_get**](PluginsApi.md#list_plugins_api_v1_plugins_get) | **GET** /api/v1/plugins | List Plugins
[**preview_plugin_quarantine_api_v1_plugin_policy_quarantines_preview_post**](PluginsApi.md#preview_plugin_quarantine_api_v1_plugin_policy_quarantines_preview_post) | **POST** /api/v1/plugin-policy/quarantines/preview | Preview Plugin Quarantine
[**publish_plugin_registry_package_api_v1_plugin_registry_packages_post**](PluginsApi.md#publish_plugin_registry_package_api_v1_plugin_registry_packages_post) | **POST** /api/v1/plugin-registry/packages | Publish Plugin Registry Package
[**quarantine_plugin_version_api_v1_plugin_policy_quarantines_post**](PluginsApi.md#quarantine_plugin_version_api_v1_plugin_policy_quarantines_post) | **POST** /api/v1/plugin-policy/quarantines | Quarantine Plugin Version
[**refresh_plugins_api_v1_plugins_refresh_post**](PluginsApi.md#refresh_plugins_api_v1_plugins_refresh_post) | **POST** /api/v1/plugins/refresh | Refresh Plugins
[**release_plugin_quarantine_api_v1_plugin_policy_quarantines_quarantine_id_release_post**](PluginsApi.md#release_plugin_quarantine_api_v1_plugin_policy_quarantines_quarantine_id_release_post) | **POST** /api/v1/plugin-policy/quarantines/{quarantine_id}/release | Release Plugin Quarantine
[**trusted_plugin_runtime_status_api_v1_plugins_trusted_runtime_get**](PluginsApi.md#trusted_plugin_runtime_status_api_v1_plugins_trusted_runtime_get) | **GET** /api/v1/plugins/trusted-runtime | Trusted Plugin Runtime Status
[**update_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_put**](PluginsApi.md#update_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_put) | **PUT** /api/v1/plugin-policy/rules/{rule_id} | Update Plugin Policy Rule
[**yank_plugin_registry_package_api_v1_plugin_registry_packages_name_version_yank_post**](PluginsApi.md#yank_plugin_registry_package_api_v1_plugin_registry_packages_name_version_yank_post) | **POST** /api/v1/plugin-registry/packages/{name}/{version}/yank | Yank Plugin Registry Package


# **create_plugin_policy_rule_api_v1_plugin_policy_rules_post**
> PluginPolicyRule create_plugin_policy_rule_api_v1_plugin_policy_rules_post(plugin_policy_rule_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Plugin Policy Rule

### Example


```python
import amesh_client
from amesh_client.models.plugin_policy_rule import PluginPolicyRule
from amesh_client.models.plugin_policy_rule_create import PluginPolicyRuleCreate
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
    plugin_policy_rule_create = amesh_client.PluginPolicyRuleCreate() # PluginPolicyRuleCreate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Plugin Policy Rule
        api_response = api_instance.create_plugin_policy_rule_api_v1_plugin_policy_rules_post(plugin_policy_rule_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->create_plugin_policy_rule_api_v1_plugin_policy_rules_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->create_plugin_policy_rule_api_v1_plugin_policy_rules_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_policy_rule_create** | [**PluginPolicyRuleCreate**](PluginPolicyRuleCreate.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginPolicyRule**](PluginPolicyRule.md)

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

# **delete_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_delete**
> delete_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_delete(rule_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Delete Plugin Policy Rule

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
    rule_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Delete Plugin Policy Rule
        api_instance.delete_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_delete(rule_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
    except Exception as e:
        print("Exception when calling PluginsApi->delete_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **UUID**|  |
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

# **evaluate_flow_plugin_policy_api_v1_plugin_policy_evaluate_post**
> PluginPolicyDecision evaluate_flow_plugin_policy_api_v1_plugin_policy_evaluate_post(stage=stage, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Evaluate Flow Plugin Policy

### Example


```python
import amesh_client
from amesh_client.models.plugin_policy_decision import PluginPolicyDecision
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
    stage = amesh_client.PluginPolicyStage() # PluginPolicyStage |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Evaluate Flow Plugin Policy
        api_response = api_instance.evaluate_flow_plugin_policy_api_v1_plugin_policy_evaluate_post(stage=stage, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->evaluate_flow_plugin_policy_api_v1_plugin_policy_evaluate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->evaluate_flow_plugin_policy_api_v1_plugin_policy_evaluate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **stage** | [**PluginPolicyStage**](.md)|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginPolicyDecision**](PluginPolicyDecision.md)

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

# **get_effective_plugin_policy_api_v1_plugin_policy_effective_get**
> EffectivePluginPolicy get_effective_plugin_policy_api_v1_plugin_policy_effective_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Effective Plugin Policy

### Example


```python
import amesh_client
from amesh_client.models.effective_plugin_policy import EffectivePluginPolicy
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
    namespace = 'namespace_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Effective Plugin Policy
        api_response = api_instance.get_effective_plugin_policy_api_v1_plugin_policy_effective_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->get_effective_plugin_policy_api_v1_plugin_policy_effective_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->get_effective_plugin_policy_api_v1_plugin_policy_effective_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**EffectivePluginPolicy**](EffectivePluginPolicy.md)

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

# **list_plugin_policy_decisions_api_v1_plugin_policy_decisions_get**
> List[PluginPolicyDecision] list_plugin_policy_decisions_api_v1_plugin_policy_decisions_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Plugin Policy Decisions

### Example


```python
import amesh_client
from amesh_client.models.plugin_policy_decision import PluginPolicyDecision
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
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Plugin Policy Decisions
        api_response = api_instance.list_plugin_policy_decisions_api_v1_plugin_policy_decisions_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->list_plugin_policy_decisions_api_v1_plugin_policy_decisions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->list_plugin_policy_decisions_api_v1_plugin_policy_decisions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[PluginPolicyDecision]**](PluginPolicyDecision.md)

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

# **preview_plugin_quarantine_api_v1_plugin_policy_quarantines_preview_post**
> PluginPolicyImpactPreview preview_plugin_quarantine_api_v1_plugin_policy_quarantines_preview_post(plugin_quarantine_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Plugin Quarantine

### Example


```python
import amesh_client
from amesh_client.models.plugin_policy_impact_preview import PluginPolicyImpactPreview
from amesh_client.models.plugin_quarantine_create import PluginQuarantineCreate
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
    plugin_quarantine_create = amesh_client.PluginQuarantineCreate() # PluginQuarantineCreate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Plugin Quarantine
        api_response = api_instance.preview_plugin_quarantine_api_v1_plugin_policy_quarantines_preview_post(plugin_quarantine_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->preview_plugin_quarantine_api_v1_plugin_policy_quarantines_preview_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->preview_plugin_quarantine_api_v1_plugin_policy_quarantines_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_quarantine_create** | [**PluginQuarantineCreate**](PluginQuarantineCreate.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginPolicyImpactPreview**](PluginPolicyImpactPreview.md)

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

# **quarantine_plugin_version_api_v1_plugin_policy_quarantines_post**
> PluginQuarantine quarantine_plugin_version_api_v1_plugin_policy_quarantines_post(plugin_quarantine_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Quarantine Plugin Version

### Example


```python
import amesh_client
from amesh_client.models.plugin_quarantine import PluginQuarantine
from amesh_client.models.plugin_quarantine_create import PluginQuarantineCreate
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
    plugin_quarantine_create = amesh_client.PluginQuarantineCreate() # PluginQuarantineCreate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Quarantine Plugin Version
        api_response = api_instance.quarantine_plugin_version_api_v1_plugin_policy_quarantines_post(plugin_quarantine_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->quarantine_plugin_version_api_v1_plugin_policy_quarantines_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->quarantine_plugin_version_api_v1_plugin_policy_quarantines_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **plugin_quarantine_create** | [**PluginQuarantineCreate**](PluginQuarantineCreate.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginQuarantine**](PluginQuarantine.md)

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

# **release_plugin_quarantine_api_v1_plugin_policy_quarantines_quarantine_id_release_post**
> PluginQuarantine release_plugin_quarantine_api_v1_plugin_policy_quarantines_quarantine_id_release_post(quarantine_id, reason, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Release Plugin Quarantine

### Example


```python
import amesh_client
from amesh_client.models.plugin_quarantine import PluginQuarantine
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
    quarantine_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    reason = 'reason_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Release Plugin Quarantine
        api_response = api_instance.release_plugin_quarantine_api_v1_plugin_policy_quarantines_quarantine_id_release_post(quarantine_id, reason, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->release_plugin_quarantine_api_v1_plugin_policy_quarantines_quarantine_id_release_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->release_plugin_quarantine_api_v1_plugin_policy_quarantines_quarantine_id_release_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **quarantine_id** | **UUID**|  |
 **reason** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginQuarantine**](PluginQuarantine.md)

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

# **update_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_put**
> PluginPolicyRule update_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_put(rule_id, plugin_policy_rule_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Update Plugin Policy Rule

### Example


```python
import amesh_client
from amesh_client.models.plugin_policy_rule import PluginPolicyRule
from amesh_client.models.plugin_policy_rule_create import PluginPolicyRuleCreate
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
    rule_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    plugin_policy_rule_create = amesh_client.PluginPolicyRuleCreate() # PluginPolicyRuleCreate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Update Plugin Policy Rule
        api_response = api_instance.update_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_put(rule_id, plugin_policy_rule_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PluginsApi->update_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PluginsApi->update_plugin_policy_rule_api_v1_plugin_policy_rules_rule_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **UUID**|  |
 **plugin_policy_rule_create** | [**PluginPolicyRuleCreate**](PluginPolicyRuleCreate.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PluginPolicyRule**](PluginPolicyRule.md)

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
