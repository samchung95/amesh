# amesh_client.AgentsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**compare_agent_definition_revisions_api_v1_namespaces_namespace_agent_definitions_key_compare_get**](AgentsApi.md#compare_agent_definition_revisions_api_v1_namespaces_namespace_agent_definitions_key_compare_get) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/compare | Compare Agent Definition Revisions
[**create_agent_mcp_connection_revision_api_v1_namespaces_namespace_agent_mcp_connections_post**](AgentsApi.md#create_agent_mcp_connection_revision_api_v1_namespaces_namespace_agent_mcp_connections_post) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections | Create Agent Mcp Connection Revision
[**create_agent_resource_revision_api_v1_namespaces_namespace_agent_resources_post**](AgentsApi.md#create_agent_resource_revision_api_v1_namespaces_namespace_agent_resources_post) | **POST** /api/v1/namespaces/{namespace}/agent/resources | Create Agent Resource Revision
[**delete_agent_memory_entry_api_v1_namespaces_namespace_agent_memory_entry_id_delete**](AgentsApi.md#delete_agent_memory_entry_api_v1_namespaces_namespace_agent_memory_entry_id_delete) | **DELETE** /api/v1/namespaces/{namespace}/agent/memory/{entry_id} | Delete Agent Memory Entry
[**diagnose_model_policy_migration_api_v1_namespaces_namespace_agent_model_policies_key_migration_get**](AgentsApi.md#diagnose_model_policy_migration_api_v1_namespaces_namespace_agent_model_policies_key_migration_get) | **GET** /api/v1/namespaces/{namespace}/agent/model-policies/{key}/migration | Diagnose Model Policy Migration
[**discover_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_discover_post**](AgentsApi.md#discover_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_discover_post) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections/discover | Discover Agent Mcp Connection
[**get_agent_capability_catalog_api_v1_namespaces_namespace_agent_capabilities_catalog_get**](AgentsApi.md#get_agent_capability_catalog_api_v1_namespaces_namespace_agent_capabilities_catalog_get) | **GET** /api/v1/namespaces/{namespace}/agent/capabilities/catalog | Get Agent Capability Catalog
[**get_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_get**](AgentsApi.md#get_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_get) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key} | Get Agent Mcp Connection
[**get_agent_resource_api_v1_namespaces_namespace_agent_resources_kind_key_get**](AgentsApi.md#get_agent_resource_api_v1_namespaces_namespace_agent_resources_kind_key_get) | **GET** /api/v1/namespaces/{namespace}/agent/resources/{kind}/{key} | Get Agent Resource
[**list_agent_mcp_connection_tools_api_v1_namespaces_namespace_agent_mcp_connections_key_tools_get**](AgentsApi.md#list_agent_mcp_connection_tools_api_v1_namespaces_namespace_agent_mcp_connections_key_tools_get) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools | List Agent Mcp Connection Tools
[**list_agent_mcp_connections_api_v1_namespaces_namespace_agent_mcp_connections_get**](AgentsApi.md#list_agent_mcp_connections_api_v1_namespaces_namespace_agent_mcp_connections_get) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections | List Agent Mcp Connections
[**list_agent_memory_metadata_api_v1_namespaces_namespace_agent_memory_get**](AgentsApi.md#list_agent_memory_metadata_api_v1_namespaces_namespace_agent_memory_get) | **GET** /api/v1/namespaces/{namespace}/agent/memory | List Agent Memory Metadata
[**list_agent_resources_api_v1_namespaces_namespace_agent_resources_get**](AgentsApi.md#list_agent_resources_api_v1_namespaces_namespace_agent_resources_get) | **GET** /api/v1/namespaces/{namespace}/agent/resources | List Agent Resources
[**preview_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_preview_get**](AgentsApi.md#preview_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_preview_get) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/preview | Preview Agent Definition
[**preview_agent_evaluation_fixture_api_v1_namespaces_namespace_agent_evaluations_key_fixtures_fixture_key_preview_get**](AgentsApi.md#preview_agent_evaluation_fixture_api_v1_namespaces_namespace_agent_evaluations_key_fixtures_fixture_key_preview_get) | **GET** /api/v1/namespaces/{namespace}/agent/evaluations/{key}/fixtures/{fixture_key}/preview | Preview Agent Evaluation Fixture
[**preview_agent_mesh_route_api_v1_namespaces_namespace_agent_mesh_routes_preview_post**](AgentsApi.md#preview_agent_mesh_route_api_v1_namespaces_namespace_agent_mesh_routes_preview_post) | **POST** /api/v1/namespaces/{namespace}/agent/mesh/routes/preview | Preview Agent Mesh Route
[**resolve_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_resolve_post**](AgentsApi.md#resolve_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_resolve_post) | **POST** /api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve | Resolve Agent Definition
[**test_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_test_post**](AgentsApi.md#test_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_test_post) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/test | Test Agent Mcp Connection


# **compare_agent_definition_revisions_api_v1_namespaces_namespace_agent_definitions_key_compare_get**
> AgentRevisionComparison compare_agent_definition_revisions_api_v1_namespaces_namespace_agent_definitions_key_compare_get(namespace, key, from_revision, to_revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Compare Agent Definition Revisions

### Example


```python
import amesh_client
from amesh_client.models.agent_revision_comparison import AgentRevisionComparison
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    from_revision = 56 # int |
    to_revision = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Compare Agent Definition Revisions
        api_response = api_instance.compare_agent_definition_revisions_api_v1_namespaces_namespace_agent_definitions_key_compare_get(namespace, key, from_revision, to_revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->compare_agent_definition_revisions_api_v1_namespaces_namespace_agent_definitions_key_compare_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->compare_agent_definition_revisions_api_v1_namespaces_namespace_agent_definitions_key_compare_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **from_revision** | **int**|  |
 **to_revision** | **int**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentRevisionComparison**

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

# **create_agent_mcp_connection_revision_api_v1_namespaces_namespace_agent_mcp_connections_post**
> McpConnectionRevision create_agent_mcp_connection_revision_api_v1_namespaces_namespace_agent_mcp_connections_post(namespace, mcp_connection_spec, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Agent Mcp Connection Revision

### Example


```python
import amesh_client
from amesh_client.models.mcp_connection_revision import McpConnectionRevision
from amesh_client.models.mcp_connection_spec import McpConnectionSpec
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    mcp_connection_spec = amesh_client.McpConnectionSpec() # McpConnectionSpec |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Agent Mcp Connection Revision
        api_response = api_instance.create_agent_mcp_connection_revision_api_v1_namespaces_namespace_agent_mcp_connections_post(namespace, mcp_connection_spec, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->create_agent_mcp_connection_revision_api_v1_namespaces_namespace_agent_mcp_connections_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->create_agent_mcp_connection_revision_api_v1_namespaces_namespace_agent_mcp_connections_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **mcp_connection_spec** | **McpConnectionSpec**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**McpConnectionRevision**

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

# **create_agent_resource_revision_api_v1_namespaces_namespace_agent_resources_post**
> AgentResourceRevisionOutput create_agent_resource_revision_api_v1_namespaces_namespace_agent_resources_post(namespace, spec, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Agent Resource Revision

### Example


```python
import amesh_client
from amesh_client.models.agent_resource_revision_output import AgentResourceRevisionOutput
from amesh_client.models.spec import Spec
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    spec = amesh_client.Spec() # Spec |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Agent Resource Revision
        api_response = api_instance.create_agent_resource_revision_api_v1_namespaces_namespace_agent_resources_post(namespace, spec, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->create_agent_resource_revision_api_v1_namespaces_namespace_agent_resources_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->create_agent_resource_revision_api_v1_namespaces_namespace_agent_resources_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **spec** | **Spec**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentResourceRevisionOutput**

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

# **delete_agent_memory_entry_api_v1_namespaces_namespace_agent_memory_entry_id_delete**
> AgentMemoryMetadata delete_agent_memory_entry_api_v1_namespaces_namespace_agent_memory_entry_id_delete(namespace, entry_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Delete Agent Memory Entry

### Example


```python
import amesh_client
from amesh_client.models.agent_memory_metadata import AgentMemoryMetadata
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    entry_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Delete Agent Memory Entry
        api_response = api_instance.delete_agent_memory_entry_api_v1_namespaces_namespace_agent_memory_entry_id_delete(namespace, entry_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->delete_agent_memory_entry_api_v1_namespaces_namespace_agent_memory_entry_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->delete_agent_memory_entry_api_v1_namespaces_namespace_agent_memory_entry_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **entry_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentMemoryMetadata**

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

# **diagnose_model_policy_migration_api_v1_namespaces_namespace_agent_model_policies_key_migration_get**
> ProviderMigrationDiagnostic diagnose_model_policy_migration_api_v1_namespaces_namespace_agent_model_policies_key_migration_get(namespace, key, from_revision, to_revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Diagnose Model Policy Migration

### Example


```python
import amesh_client
from amesh_client.models.provider_migration_diagnostic import ProviderMigrationDiagnostic
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    from_revision = 56 # int |
    to_revision = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Diagnose Model Policy Migration
        api_response = api_instance.diagnose_model_policy_migration_api_v1_namespaces_namespace_agent_model_policies_key_migration_get(namespace, key, from_revision, to_revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->diagnose_model_policy_migration_api_v1_namespaces_namespace_agent_model_policies_key_migration_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->diagnose_model_policy_migration_api_v1_namespaces_namespace_agent_model_policies_key_migration_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **from_revision** | **int**|  |
 **to_revision** | **int**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**ProviderMigrationDiagnostic**

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

# **discover_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_discover_post**
> McpDiscoveryResult discover_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_discover_post(namespace, mcp_connection_discovery_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Discover Agent Mcp Connection

### Example


```python
import amesh_client
from amesh_client.models.mcp_connection_discovery_request import McpConnectionDiscoveryRequest
from amesh_client.models.mcp_discovery_result import McpDiscoveryResult
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    mcp_connection_discovery_request = amesh_client.McpConnectionDiscoveryRequest() # McpConnectionDiscoveryRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Discover Agent Mcp Connection
        api_response = api_instance.discover_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_discover_post(namespace, mcp_connection_discovery_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->discover_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_discover_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->discover_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_discover_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **mcp_connection_discovery_request** | **McpConnectionDiscoveryRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**McpDiscoveryResult**

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

# **get_agent_capability_catalog_api_v1_namespaces_namespace_agent_capabilities_catalog_get**
> CapabilityCatalog get_agent_capability_catalog_api_v1_namespaces_namespace_agent_capabilities_catalog_get(namespace, q=q, kind=kind, status=status, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Agent Capability Catalog

### Example


```python
import amesh_client
from amesh_client.models.capability_catalog import CapabilityCatalog
from amesh_client.models.capability_kind import CapabilityKind
from amesh_client.models.capability_status import CapabilityStatus
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    q = 'q_example' # str |  (optional)
    kind = [amesh_client.CapabilityKind()] # List[CapabilityKind] |  (optional)
    status = [amesh_client.CapabilityStatus()] # List[CapabilityStatus] |  (optional)
    limit = 200 # int |  (optional) (default to 200)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Agent Capability Catalog
        api_response = api_instance.get_agent_capability_catalog_api_v1_namespaces_namespace_agent_capabilities_catalog_get(namespace, q=q, kind=kind, status=status, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->get_agent_capability_catalog_api_v1_namespaces_namespace_agent_capabilities_catalog_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->get_agent_capability_catalog_api_v1_namespaces_namespace_agent_capabilities_catalog_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **q** | **str**|  | [optional]
 **kind** | [**List[CapabilityKind]**](CapabilityKind.md)|  | [optional]
 **status** | [**List[CapabilityStatus]**](CapabilityStatus.md)|  | [optional]
 **limit** | **int**|  | [optional] [default to 200]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**CapabilityCatalog**

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

# **get_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_get**
> McpConnectionRevision get_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_get(namespace, key, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Agent Mcp Connection

### Example


```python
import amesh_client
from amesh_client.models.mcp_connection_revision import McpConnectionRevision
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    revision = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Agent Mcp Connection
        api_response = api_instance.get_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_get(namespace, key, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->get_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->get_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **revision** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**McpConnectionRevision**

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

# **get_agent_resource_api_v1_namespaces_namespace_agent_resources_kind_key_get**
> AgentResourceRevisionOutput get_agent_resource_api_v1_namespaces_namespace_agent_resources_kind_key_get(namespace, kind, key, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Agent Resource

### Example


```python
import amesh_client
from amesh_client.models.agent_resource_kind import AgentResourceKind
from amesh_client.models.agent_resource_revision_output import AgentResourceRevisionOutput
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    kind = amesh_client.AgentResourceKind() # AgentResourceKind |
    key = 'key_example' # str |
    revision = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Agent Resource
        api_response = api_instance.get_agent_resource_api_v1_namespaces_namespace_agent_resources_kind_key_get(namespace, kind, key, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->get_agent_resource_api_v1_namespaces_namespace_agent_resources_kind_key_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->get_agent_resource_api_v1_namespaces_namespace_agent_resources_kind_key_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **kind** | **AgentResourceKind**|  |
 **key** | **str**|  |
 **revision** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentResourceRevisionOutput**

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

# **list_agent_mcp_connection_tools_api_v1_namespaces_namespace_agent_mcp_connections_key_tools_get**
> List[Dict[str, object]] list_agent_mcp_connection_tools_api_v1_namespaces_namespace_agent_mcp_connections_key_tools_get(namespace, key, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Agent Mcp Connection Tools

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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    revision = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Agent Mcp Connection Tools
        api_response = api_instance.list_agent_mcp_connection_tools_api_v1_namespaces_namespace_agent_mcp_connections_key_tools_get(namespace, key, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->list_agent_mcp_connection_tools_api_v1_namespaces_namespace_agent_mcp_connections_key_tools_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->list_agent_mcp_connection_tools_api_v1_namespaces_namespace_agent_mcp_connections_key_tools_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **revision** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**List[Dict[str, object]]**

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

# **list_agent_mcp_connections_api_v1_namespaces_namespace_agent_mcp_connections_get**
> List[McpConnectionRevision] list_agent_mcp_connections_api_v1_namespaces_namespace_agent_mcp_connections_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Agent Mcp Connections

### Example


```python
import amesh_client
from amesh_client.models.mcp_connection_revision import McpConnectionRevision
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Agent Mcp Connections
        api_response = api_instance.list_agent_mcp_connections_api_v1_namespaces_namespace_agent_mcp_connections_get(namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->list_agent_mcp_connections_api_v1_namespaces_namespace_agent_mcp_connections_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->list_agent_mcp_connections_api_v1_namespaces_namespace_agent_mcp_connections_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[McpConnectionRevision]**](McpConnectionRevision.md)

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

# **list_agent_memory_metadata_api_v1_namespaces_namespace_agent_memory_get**
> List[AgentMemoryMetadata] list_agent_memory_metadata_api_v1_namespaces_namespace_agent_memory_get(namespace, agent_key=agent_key, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Agent Memory Metadata

### Example


```python
import amesh_client
from amesh_client.models.agent_memory_metadata import AgentMemoryMetadata
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    agent_key = 'agent_key_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Agent Memory Metadata
        api_response = api_instance.list_agent_memory_metadata_api_v1_namespaces_namespace_agent_memory_get(namespace, agent_key=agent_key, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->list_agent_memory_metadata_api_v1_namespaces_namespace_agent_memory_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->list_agent_memory_metadata_api_v1_namespaces_namespace_agent_memory_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **agent_key** | **str**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[AgentMemoryMetadata]**](AgentMemoryMetadata.md)

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

# **list_agent_resources_api_v1_namespaces_namespace_agent_resources_get**
> List[AgentResourceRevisionOutput] list_agent_resources_api_v1_namespaces_namespace_agent_resources_get(namespace, kind=kind, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Agent Resources

### Example


```python
import amesh_client
from amesh_client.models.agent_resource_revision_output import AgentResourceRevisionOutput
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    kind = amesh_client.AgentResourceKind() # AgentResourceKind |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Agent Resources
        api_response = api_instance.list_agent_resources_api_v1_namespaces_namespace_agent_resources_get(namespace, kind=kind, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->list_agent_resources_api_v1_namespaces_namespace_agent_resources_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->list_agent_resources_api_v1_namespaces_namespace_agent_resources_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **kind** | **AgentResourceKind**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[AgentResourceRevisionOutput]**](AgentResourceRevisionOutput.md)

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

# **preview_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_preview_get**
> AgentEnvelopePreview preview_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_preview_get(namespace, key, agent_revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Agent Definition

### Example


```python
import amesh_client
from amesh_client.models.agent_envelope_preview import AgentEnvelopePreview
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    agent_revision = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Agent Definition
        api_response = api_instance.preview_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_preview_get(namespace, key, agent_revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->preview_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_preview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->preview_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_preview_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **agent_revision** | **int**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentEnvelopePreview**

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

# **preview_agent_evaluation_fixture_api_v1_namespaces_namespace_agent_evaluations_key_fixtures_fixture_key_preview_get**
> AgentEvaluationPreview preview_agent_evaluation_fixture_api_v1_namespaces_namespace_agent_evaluations_key_fixtures_fixture_key_preview_get(namespace, key, fixture_key, revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Agent Evaluation Fixture

### Example


```python
import amesh_client
from amesh_client.models.agent_evaluation_preview import AgentEvaluationPreview
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    fixture_key = 'fixture_key_example' # str |
    revision = 56 # int |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Agent Evaluation Fixture
        api_response = api_instance.preview_agent_evaluation_fixture_api_v1_namespaces_namespace_agent_evaluations_key_fixtures_fixture_key_preview_get(namespace, key, fixture_key, revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->preview_agent_evaluation_fixture_api_v1_namespaces_namespace_agent_evaluations_key_fixtures_fixture_key_preview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->preview_agent_evaluation_fixture_api_v1_namespaces_namespace_agent_evaluations_key_fixtures_fixture_key_preview_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **fixture_key** | **str**|  |
 **revision** | **int**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentEvaluationPreview**

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

# **preview_agent_mesh_route_api_v1_namespaces_namespace_agent_mesh_routes_preview_post**
> AgentRouteDecision preview_agent_mesh_route_api_v1_namespaces_namespace_agent_mesh_routes_preview_post(namespace, agent_route_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Agent Mesh Route

### Example


```python
import amesh_client
from amesh_client.models.agent_route_decision import AgentRouteDecision
from amesh_client.models.agent_route_request import AgentRouteRequest
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    agent_route_request = amesh_client.AgentRouteRequest() # AgentRouteRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Agent Mesh Route
        api_response = api_instance.preview_agent_mesh_route_api_v1_namespaces_namespace_agent_mesh_routes_preview_post(namespace, agent_route_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->preview_agent_mesh_route_api_v1_namespaces_namespace_agent_mesh_routes_preview_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->preview_agent_mesh_route_api_v1_namespaces_namespace_agent_mesh_routes_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **agent_route_request** | **AgentRouteRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentRouteDecision**

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

# **resolve_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_resolve_post**
> AgentCapabilityPinOutput resolve_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_resolve_post(namespace, key, agent_resolution_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Resolve Agent Definition

### Example


```python
import amesh_client
from amesh_client.models.agent_capability_pin_output import AgentCapabilityPinOutput
from amesh_client.models.agent_resolution_request import AgentResolutionRequest
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    agent_resolution_request = amesh_client.AgentResolutionRequest() # AgentResolutionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Resolve Agent Definition
        api_response = api_instance.resolve_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_resolve_post(namespace, key, agent_resolution_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->resolve_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_resolve_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->resolve_agent_definition_api_v1_namespaces_namespace_agent_definitions_key_resolve_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **agent_resolution_request** | **AgentResolutionRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentCapabilityPinOutput**

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

# **test_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_test_post**
> McpConnectionTestResponse test_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_test_post(namespace, key, mcp_connection_test_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Test Agent Mcp Connection

### Example


```python
import amesh_client
from amesh_client.models.mcp_connection_test_request import McpConnectionTestRequest
from amesh_client.models.mcp_connection_test_response import McpConnectionTestResponse
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
    api_instance = amesh_client.AgentsApi(api_client)
    namespace = 'namespace_example' # str |
    key = 'key_example' # str |
    mcp_connection_test_request = amesh_client.McpConnectionTestRequest() # McpConnectionTestRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Test Agent Mcp Connection
        api_response = api_instance.test_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_test_post(namespace, key, mcp_connection_test_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentsApi->test_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_test_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentsApi->test_agent_mcp_connection_api_v1_namespaces_namespace_agent_mcp_connections_key_test_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **key** | **str**|  |
 **mcp_connection_test_request** | **McpConnectionTestRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**McpConnectionTestResponse**

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
