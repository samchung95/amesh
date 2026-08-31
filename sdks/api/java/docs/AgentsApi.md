# AgentsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet**](AgentsApi.md#compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/compare | Compare Agent Definition Revisions |
| [**compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGetWithHttpInfo**](AgentsApi.md#compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/compare | Compare Agent Definition Revisions |
| [**createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost**](AgentsApi.md#createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections | Create Agent Mcp Connection Revision |
| [**createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPostWithHttpInfo**](AgentsApi.md#createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPostWithHttpInfo) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections | Create Agent Mcp Connection Revision |
| [**createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost**](AgentsApi.md#createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost) | **POST** /api/v1/namespaces/{namespace}/agent/resources | Create Agent Resource Revision |
| [**createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPostWithHttpInfo**](AgentsApi.md#createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPostWithHttpInfo) | **POST** /api/v1/namespaces/{namespace}/agent/resources | Create Agent Resource Revision |
| [**deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete**](AgentsApi.md#deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete) | **DELETE** /api/v1/namespaces/{namespace}/agent/memory/{entry_id} | Delete Agent Memory Entry |
| [**deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDeleteWithHttpInfo**](AgentsApi.md#deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDeleteWithHttpInfo) | **DELETE** /api/v1/namespaces/{namespace}/agent/memory/{entry_id} | Delete Agent Memory Entry |
| [**diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet**](AgentsApi.md#diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet) | **GET** /api/v1/namespaces/{namespace}/agent/model-policies/{key}/migration | Diagnose Model Policy Migration |
| [**diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGetWithHttpInfo**](AgentsApi.md#diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/model-policies/{key}/migration | Diagnose Model Policy Migration |
| [**discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost**](AgentsApi.md#discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections/discover | Discover Agent Mcp Connection |
| [**discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPostWithHttpInfo**](AgentsApi.md#discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPostWithHttpInfo) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections/discover | Discover Agent Mcp Connection |
| [**getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGet**](AgentsApi.md#getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGet) | **GET** /api/v1/namespaces/{namespace}/agent/capabilities/catalog | Get Agent Capability Catalog |
| [**getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGetWithHttpInfo**](AgentsApi.md#getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/capabilities/catalog | Get Agent Capability Catalog |
| [**getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet**](AgentsApi.md#getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key} | Get Agent Mcp Connection |
| [**getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGetWithHttpInfo**](AgentsApi.md#getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key} | Get Agent Mcp Connection |
| [**getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet**](AgentsApi.md#getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet) | **GET** /api/v1/namespaces/{namespace}/agent/resources/{kind}/{key} | Get Agent Resource |
| [**getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGetWithHttpInfo**](AgentsApi.md#getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/resources/{kind}/{key} | Get Agent Resource |
| [**listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet**](AgentsApi.md#listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools | List Agent Mcp Connection Tools |
| [**listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGetWithHttpInfo**](AgentsApi.md#listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools | List Agent Mcp Connection Tools |
| [**listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet**](AgentsApi.md#listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections | List Agent Mcp Connections |
| [**listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGetWithHttpInfo**](AgentsApi.md#listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections | List Agent Mcp Connections |
| [**listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet**](AgentsApi.md#listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet) | **GET** /api/v1/namespaces/{namespace}/agent/memory | List Agent Memory Metadata |
| [**listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGetWithHttpInfo**](AgentsApi.md#listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/memory | List Agent Memory Metadata |
| [**listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet**](AgentsApi.md#listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet) | **GET** /api/v1/namespaces/{namespace}/agent/resources | List Agent Resources |
| [**listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGetWithHttpInfo**](AgentsApi.md#listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/resources | List Agent Resources |
| [**previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet**](AgentsApi.md#previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/preview | Preview Agent Definition |
| [**previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGetWithHttpInfo**](AgentsApi.md#previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/preview | Preview Agent Definition |
| [**previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet**](AgentsApi.md#previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet) | **GET** /api/v1/namespaces/{namespace}/agent/evaluations/{key}/fixtures/{fixture_key}/preview | Preview Agent Evaluation Fixture |
| [**previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGetWithHttpInfo**](AgentsApi.md#previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/agent/evaluations/{key}/fixtures/{fixture_key}/preview | Preview Agent Evaluation Fixture |
| [**previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost**](AgentsApi.md#previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost) | **POST** /api/v1/namespaces/{namespace}/agent/mesh/routes/preview | Preview Agent Mesh Route |
| [**previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPostWithHttpInfo**](AgentsApi.md#previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPostWithHttpInfo) | **POST** /api/v1/namespaces/{namespace}/agent/mesh/routes/preview | Preview Agent Mesh Route |
| [**resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost**](AgentsApi.md#resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost) | **POST** /api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve | Resolve Agent Definition |
| [**resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePostWithHttpInfo**](AgentsApi.md#resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePostWithHttpInfo) | **POST** /api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve | Resolve Agent Definition |
| [**testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPost**](AgentsApi.md#testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPost) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/test | Test Agent Mcp Connection |
| [**testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPostWithHttpInfo**](AgentsApi.md#testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPostWithHttpInfo) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/test | Test Agent Mcp Connection |



## compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet

> AgentRevisionComparison compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant)

Compare Agent Definition Revisions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer fromRevision = 56; // Integer |
        Integer toRevision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentRevisionComparison result = apiInstance.compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **fromRevision** | **Integer**|  | |
| **toRevision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGetWithHttpInfo

> ApiResponse<AgentRevisionComparison> compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGetWithHttpInfo(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant)

Compare Agent Definition Revisions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer fromRevision = 56; // Integer |
        Integer toRevision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentRevisionComparison> response = apiInstance.compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGetWithHttpInfo(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **fromRevision** | **Integer**|  | |
| **toRevision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentRevisionComparison**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost

> McpConnectionRevision createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost(namespace, mcpConnectionSpec, authorization, xAmeshCSRF, xAmeshTenant)

Create Agent Mcp Connection Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        McpConnectionSpec mcpConnectionSpec = new McpConnectionSpec(); // McpConnectionSpec |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            McpConnectionRevision result = apiInstance.createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost(namespace, mcpConnectionSpec, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **mcpConnectionSpec** | **McpConnectionSpec**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPostWithHttpInfo

> ApiResponse<McpConnectionRevision> createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPostWithHttpInfo(namespace, mcpConnectionSpec, authorization, xAmeshCSRF, xAmeshTenant)

Create Agent Mcp Connection Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        McpConnectionSpec mcpConnectionSpec = new McpConnectionSpec(); // McpConnectionSpec |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<McpConnectionRevision> response = apiInstance.createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPostWithHttpInfo(namespace, mcpConnectionSpec, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **mcpConnectionSpec** | **McpConnectionSpec**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**McpConnectionRevision**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost

> AgentResourceRevisionOutput createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost(namespace, spec, authorization, xAmeshCSRF, xAmeshTenant)

Create Agent Resource Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        Spec spec = new Spec(); // Spec |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentResourceRevisionOutput result = apiInstance.createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost(namespace, spec, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **spec** | **Spec**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPostWithHttpInfo

> ApiResponse<AgentResourceRevisionOutput> createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPostWithHttpInfo(namespace, spec, authorization, xAmeshCSRF, xAmeshTenant)

Create Agent Resource Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        Spec spec = new Spec(); // Spec |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentResourceRevisionOutput> response = apiInstance.createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPostWithHttpInfo(namespace, spec, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **spec** | **Spec**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentResourceRevisionOutput**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete

> AgentMemoryMetadata deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete(namespace, entryId, authorization, xAmeshCSRF, xAmeshTenant)

Delete Agent Memory Entry

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        UUID entryId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentMemoryMetadata result = apiInstance.deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete(namespace, entryId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **entryId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDeleteWithHttpInfo

> ApiResponse<AgentMemoryMetadata> deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDeleteWithHttpInfo(namespace, entryId, authorization, xAmeshCSRF, xAmeshTenant)

Delete Agent Memory Entry

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        UUID entryId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentMemoryMetadata> response = apiInstance.deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDeleteWithHttpInfo(namespace, entryId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **entryId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentMemoryMetadata**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet

> ProviderMigrationDiagnostic diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant)

Diagnose Model Policy Migration

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer fromRevision = 56; // Integer |
        Integer toRevision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ProviderMigrationDiagnostic result = apiInstance.diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **fromRevision** | **Integer**|  | |
| **toRevision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGetWithHttpInfo

> ApiResponse<ProviderMigrationDiagnostic> diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGetWithHttpInfo(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant)

Diagnose Model Policy Migration

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer fromRevision = 56; // Integer |
        Integer toRevision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ProviderMigrationDiagnostic> response = apiInstance.diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGetWithHttpInfo(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **fromRevision** | **Integer**|  | |
| **toRevision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**ProviderMigrationDiagnostic**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost

> McpDiscoveryResult discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost(namespace, mcpConnectionDiscoveryRequest, authorization, xAmeshCSRF, xAmeshTenant)

Discover Agent Mcp Connection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        McpConnectionDiscoveryRequest mcpConnectionDiscoveryRequest = new McpConnectionDiscoveryRequest(); // McpConnectionDiscoveryRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            McpDiscoveryResult result = apiInstance.discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost(namespace, mcpConnectionDiscoveryRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **mcpConnectionDiscoveryRequest** | **McpConnectionDiscoveryRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPostWithHttpInfo

> ApiResponse<McpDiscoveryResult> discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPostWithHttpInfo(namespace, mcpConnectionDiscoveryRequest, authorization, xAmeshCSRF, xAmeshTenant)

Discover Agent Mcp Connection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        McpConnectionDiscoveryRequest mcpConnectionDiscoveryRequest = new McpConnectionDiscoveryRequest(); // McpConnectionDiscoveryRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<McpDiscoveryResult> response = apiInstance.discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPostWithHttpInfo(namespace, mcpConnectionDiscoveryRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **mcpConnectionDiscoveryRequest** | **McpConnectionDiscoveryRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**McpDiscoveryResult**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGet

> CapabilityCatalog getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGet(namespace, q, kind, status, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Capability Catalog

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String q = "q_example"; // String |
        List<CapabilityKind> kind = Arrays.asList(); // List<CapabilityKind> |
        List<CapabilityStatus> status = Arrays.asList(); // List<CapabilityStatus> |
        Integer limit = 200; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            CapabilityCatalog result = apiInstance.getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGet(namespace, q, kind, status, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **q** | **String**|  | [optional] |
| **kind** | **List&lt;CapabilityKind&gt;**|  | [optional] |
| **status** | **List&lt;CapabilityStatus&gt;**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 200] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGetWithHttpInfo

> ApiResponse<CapabilityCatalog> getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGetWithHttpInfo(namespace, q, kind, status, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Capability Catalog

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String q = "q_example"; // String |
        List<CapabilityKind> kind = Arrays.asList(); // List<CapabilityKind> |
        List<CapabilityStatus> status = Arrays.asList(); // List<CapabilityStatus> |
        Integer limit = 200; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<CapabilityCatalog> response = apiInstance.getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGetWithHttpInfo(namespace, q, kind, status, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#getAgentCapabilityCatalogApiV1NamespacesNamespaceAgentCapabilitiesCatalogGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **q** | **String**|  | [optional] |
| **kind** | **List&lt;CapabilityKind&gt;**|  | [optional] |
| **status** | **List&lt;CapabilityStatus&gt;**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 200] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**CapabilityCatalog**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet

> McpConnectionRevision getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Mcp Connection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            McpConnectionRevision result = apiInstance.getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGetWithHttpInfo

> ApiResponse<McpConnectionRevision> getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGetWithHttpInfo(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Mcp Connection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<McpConnectionRevision> response = apiInstance.getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGetWithHttpInfo(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**McpConnectionRevision**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet

> AgentResourceRevisionOutput getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet(namespace, kind, key, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Resource

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        AgentResourceKind kind = AgentResourceKind.fromValue("PROMPT"); // AgentResourceKind |
        String key = "key_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentResourceRevisionOutput result = apiInstance.getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet(namespace, kind, key, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **kind** | **AgentResourceKind**|  | [enum: PROMPT, SKILL, MODEL_POLICY, EVALUATION, AGENT] |
| **key** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGetWithHttpInfo

> ApiResponse<AgentResourceRevisionOutput> getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGetWithHttpInfo(namespace, kind, key, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Resource

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        AgentResourceKind kind = AgentResourceKind.fromValue("PROMPT"); // AgentResourceKind |
        String key = "key_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentResourceRevisionOutput> response = apiInstance.getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGetWithHttpInfo(namespace, kind, key, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **kind** | **AgentResourceKind**|  | [enum: PROMPT, SKILL, MODEL_POLICY, EVALUATION, AGENT] |
| **key** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentResourceRevisionOutput**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet

> List<Map<String, Object>> listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Mcp Connection Tools

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<Map<String, Object>> result = apiInstance.listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;Map&lt;String, Object&gt;&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGetWithHttpInfo

> ApiResponse<List<Map<String, Object>>> listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGetWithHttpInfo(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Mcp Connection Tools

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<Map<String, Object>>> response = apiInstance.listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGetWithHttpInfo(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;Map&lt;String, Object&gt;&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet

> List<McpConnectionRevision> listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Mcp Connections

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<McpConnectionRevision> result = apiInstance.listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;McpConnectionRevision&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGetWithHttpInfo

> ApiResponse<List<McpConnectionRevision>> listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Mcp Connections

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<McpConnectionRevision>> response = apiInstance.listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;McpConnectionRevision&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet

> List<AgentMemoryMetadata> listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet(namespace, agentKey, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Memory Metadata

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String agentKey = "agentKey_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<AgentMemoryMetadata> result = apiInstance.listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet(namespace, agentKey, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **agentKey** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;AgentMemoryMetadata&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGetWithHttpInfo

> ApiResponse<List<AgentMemoryMetadata>> listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGetWithHttpInfo(namespace, agentKey, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Memory Metadata

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String agentKey = "agentKey_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<AgentMemoryMetadata>> response = apiInstance.listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGetWithHttpInfo(namespace, agentKey, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **agentKey** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;AgentMemoryMetadata&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet

> List<AgentResourceRevisionOutput> listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet(namespace, kind, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Resources

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        AgentResourceKind kind = AgentResourceKind.fromValue("PROMPT"); // AgentResourceKind |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<AgentResourceRevisionOutput> result = apiInstance.listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet(namespace, kind, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **kind** | **AgentResourceKind**|  | [optional] [enum: PROMPT, SKILL, MODEL_POLICY, EVALUATION, AGENT] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;AgentResourceRevisionOutput&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGetWithHttpInfo

> ApiResponse<List<AgentResourceRevisionOutput>> listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGetWithHttpInfo(namespace, kind, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Resources

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        AgentResourceKind kind = AgentResourceKind.fromValue("PROMPT"); // AgentResourceKind |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<AgentResourceRevisionOutput>> response = apiInstance.listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGetWithHttpInfo(namespace, kind, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **kind** | **AgentResourceKind**|  | [optional] [enum: PROMPT, SKILL, MODEL_POLICY, EVALUATION, AGENT] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;AgentResourceRevisionOutput&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet

> AgentEnvelopePreview previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet(namespace, key, agentRevision, authorization, xAmeshCSRF, xAmeshTenant)

Preview Agent Definition

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer agentRevision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentEnvelopePreview result = apiInstance.previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet(namespace, key, agentRevision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **agentRevision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGetWithHttpInfo

> ApiResponse<AgentEnvelopePreview> previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGetWithHttpInfo(namespace, key, agentRevision, authorization, xAmeshCSRF, xAmeshTenant)

Preview Agent Definition

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        Integer agentRevision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentEnvelopePreview> response = apiInstance.previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGetWithHttpInfo(namespace, key, agentRevision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **agentRevision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentEnvelopePreview**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet

> AgentEvaluationPreview previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet(namespace, key, fixtureKey, revision, authorization, xAmeshCSRF, xAmeshTenant)

Preview Agent Evaluation Fixture

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        String fixtureKey = "fixtureKey_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentEvaluationPreview result = apiInstance.previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet(namespace, key, fixtureKey, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **fixtureKey** | **String**|  | |
| **revision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGetWithHttpInfo

> ApiResponse<AgentEvaluationPreview> previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGetWithHttpInfo(namespace, key, fixtureKey, revision, authorization, xAmeshCSRF, xAmeshTenant)

Preview Agent Evaluation Fixture

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        String fixtureKey = "fixtureKey_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentEvaluationPreview> response = apiInstance.previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGetWithHttpInfo(namespace, key, fixtureKey, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **fixtureKey** | **String**|  | |
| **revision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentEvaluationPreview**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost

> AgentRouteDecision previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost(namespace, agentRouteRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Agent Mesh Route

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        AgentRouteRequest agentRouteRequest = new AgentRouteRequest(); // AgentRouteRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentRouteDecision result = apiInstance.previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost(namespace, agentRouteRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **agentRouteRequest** | **AgentRouteRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPostWithHttpInfo

> ApiResponse<AgentRouteDecision> previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPostWithHttpInfo(namespace, agentRouteRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Agent Mesh Route

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        AgentRouteRequest agentRouteRequest = new AgentRouteRequest(); // AgentRouteRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentRouteDecision> response = apiInstance.previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPostWithHttpInfo(namespace, agentRouteRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **agentRouteRequest** | **AgentRouteRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentRouteDecision**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost

> AgentCapabilityPinOutput resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost(namespace, key, agentResolutionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resolve Agent Definition

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        AgentResolutionRequest agentResolutionRequest = new AgentResolutionRequest(); // AgentResolutionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentCapabilityPinOutput result = apiInstance.resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost(namespace, key, agentResolutionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **agentResolutionRequest** | **AgentResolutionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePostWithHttpInfo

> ApiResponse<AgentCapabilityPinOutput> resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePostWithHttpInfo(namespace, key, agentResolutionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resolve Agent Definition

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        AgentResolutionRequest agentResolutionRequest = new AgentResolutionRequest(); // AgentResolutionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentCapabilityPinOutput> response = apiInstance.resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePostWithHttpInfo(namespace, key, agentResolutionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **agentResolutionRequest** | **AgentResolutionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentCapabilityPinOutput**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPost

> McpConnectionTestResponse testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPost(namespace, key, mcpConnectionTestRequest, authorization, xAmeshCSRF, xAmeshTenant)

Test Agent Mcp Connection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        McpConnectionTestRequest mcpConnectionTestRequest = new McpConnectionTestRequest(); // McpConnectionTestRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            McpConnectionTestResponse result = apiInstance.testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPost(namespace, key, mcpConnectionTestRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **mcpConnectionTestRequest** | **McpConnectionTestRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPostWithHttpInfo

> ApiResponse<McpConnectionTestResponse> testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPostWithHttpInfo(namespace, key, mcpConnectionTestRequest, authorization, xAmeshCSRF, xAmeshTenant)

Test Agent Mcp Connection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentsApi apiInstance = new AgentsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String key = "key_example"; // String |
        McpConnectionTestRequest mcpConnectionTestRequest = new McpConnectionTestRequest(); // McpConnectionTestRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<McpConnectionTestResponse> response = apiInstance.testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPostWithHttpInfo(namespace, key, mcpConnectionTestRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentsApi#testAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyTestPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **key** | **String**|  | |
| **mcpConnectionTestRequest** | **McpConnectionTestRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**McpConnectionTestResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |
