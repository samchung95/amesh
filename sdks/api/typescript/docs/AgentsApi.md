# AgentsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet**](AgentsApi.md#compareagentdefinitionrevisionsapiv1namespacesnamespaceagentdefinitionskeycompareget) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/compare | Compare Agent Definition Revisions |
| [**createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost**](AgentsApi.md#createagentmcpconnectionrevisionapiv1namespacesnamespaceagentmcpconnectionspost) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections | Create Agent Mcp Connection Revision |
| [**createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost**](AgentsApi.md#createagentresourcerevisionapiv1namespacesnamespaceagentresourcespost) | **POST** /api/v1/namespaces/{namespace}/agent/resources | Create Agent Resource Revision |
| [**deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete**](AgentsApi.md#deleteagentmemoryentryapiv1namespacesnamespaceagentmemoryentryiddelete) | **DELETE** /api/v1/namespaces/{namespace}/agent/memory/{entry_id} | Delete Agent Memory Entry |
| [**diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet**](AgentsApi.md#diagnosemodelpolicymigrationapiv1namespacesnamespaceagentmodelpolicieskeymigrationget) | **GET** /api/v1/namespaces/{namespace}/agent/model-policies/{key}/migration | Diagnose Model Policy Migration |
| [**discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost**](AgentsApi.md#discoveragentmcpconnectionapiv1namespacesnamespaceagentmcpconnectionsdiscoverpost) | **POST** /api/v1/namespaces/{namespace}/agent/mcp-connections/discover | Discover Agent Mcp Connection |
| [**getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet**](AgentsApi.md#getagentmcpconnectionapiv1namespacesnamespaceagentmcpconnectionskeyget) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key} | Get Agent Mcp Connection |
| [**getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet**](AgentsApi.md#getagentresourceapiv1namespacesnamespaceagentresourceskindkeyget) | **GET** /api/v1/namespaces/{namespace}/agent/resources/{kind}/{key} | Get Agent Resource |
| [**listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet**](AgentsApi.md#listagentmcpconnectiontoolsapiv1namespacesnamespaceagentmcpconnectionskeytoolsget) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections/{key}/tools | List Agent Mcp Connection Tools |
| [**listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet**](AgentsApi.md#listagentmcpconnectionsapiv1namespacesnamespaceagentmcpconnectionsget) | **GET** /api/v1/namespaces/{namespace}/agent/mcp-connections | List Agent Mcp Connections |
| [**listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet**](AgentsApi.md#listagentmemorymetadataapiv1namespacesnamespaceagentmemoryget) | **GET** /api/v1/namespaces/{namespace}/agent/memory | List Agent Memory Metadata |
| [**listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet**](AgentsApi.md#listagentresourcesapiv1namespacesnamespaceagentresourcesget) | **GET** /api/v1/namespaces/{namespace}/agent/resources | List Agent Resources |
| [**previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet**](AgentsApi.md#previewagentdefinitionapiv1namespacesnamespaceagentdefinitionskeypreviewget) | **GET** /api/v1/namespaces/{namespace}/agent/definitions/{key}/preview | Preview Agent Definition |
| [**previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet**](AgentsApi.md#previewagentevaluationfixtureapiv1namespacesnamespaceagentevaluationskeyfixturesfixturekeypreviewget) | **GET** /api/v1/namespaces/{namespace}/agent/evaluations/{key}/fixtures/{fixture_key}/preview | Preview Agent Evaluation Fixture |
| [**previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost**](AgentsApi.md#previewagentmeshrouteapiv1namespacesnamespaceagentmeshroutespreviewpost) | **POST** /api/v1/namespaces/{namespace}/agent/mesh/routes/preview | Preview Agent Mesh Route |
| [**resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost**](AgentsApi.md#resolveagentdefinitionapiv1namespacesnamespaceagentdefinitionskeyresolvepost) | **POST** /api/v1/namespaces/{namespace}/agent/definitions/{key}/resolve | Resolve Agent Definition |



## compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet

> AgentRevisionComparison compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant)

Compare Agent Definition Revisions

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // number
    fromRevision: 56,
    // number
    toRevision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CompareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGetRequest;

  try {
    const data = await api.compareAgentDefinitionRevisionsApiV1NamespacesNamespaceAgentDefinitionsKeyCompareGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **key** | `string` |  | [Defaults to `undefined`] |
| **fromRevision** | `number` |  | [Defaults to `undefined`] |
| **toRevision** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AgentRevisionComparison**](AgentRevisionComparison.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost

> McpConnectionRevision createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost(namespace, mcpConnectionSpec, authorization, xAmeshCSRF, xAmeshTenant)

Create Agent Mcp Connection Revision

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // McpConnectionSpec
    mcpConnectionSpec: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPostRequest;

  try {
    const data = await api.createAgentMcpConnectionRevisionApiV1NamespacesNamespaceAgentMcpConnectionsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **mcpConnectionSpec** | [McpConnectionSpec](McpConnectionSpec.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**McpConnectionRevision**](McpConnectionRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost

> AgentResourceRevision createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost(namespace, spec, authorization, xAmeshCSRF, xAmeshTenant)

Create Agent Resource Revision

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // Spec
    spec: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPostRequest;

  try {
    const data = await api.createAgentResourceRevisionApiV1NamespacesNamespaceAgentResourcesPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **spec** | [Spec](Spec.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AgentResourceRevision**](AgentResourceRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete

> AgentMemoryMetadata deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete(namespace, entryId, authorization, xAmeshCSRF, xAmeshTenant)

Delete Agent Memory Entry

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { DeleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    entryId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDeleteRequest;

  try {
    const data = await api.deleteAgentMemoryEntryApiV1NamespacesNamespaceAgentMemoryEntryIdDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **entryId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AgentMemoryMetadata**](AgentMemoryMetadata.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet

> ProviderMigrationDiagnostic diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet(namespace, key, fromRevision, toRevision, authorization, xAmeshCSRF, xAmeshTenant)

Diagnose Model Policy Migration

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // number
    fromRevision: 56,
    // number
    toRevision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DiagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGetRequest;

  try {
    const data = await api.diagnoseModelPolicyMigrationApiV1NamespacesNamespaceAgentModelPoliciesKeyMigrationGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **key** | `string` |  | [Defaults to `undefined`] |
| **fromRevision** | `number` |  | [Defaults to `undefined`] |
| **toRevision** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ProviderMigrationDiagnostic**](ProviderMigrationDiagnostic.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost

> McpDiscoveryResult discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost(namespace, mcpConnectionDiscoveryRequest, authorization, xAmeshCSRF, xAmeshTenant)

Discover Agent Mcp Connection

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // McpConnectionDiscoveryRequest
    mcpConnectionDiscoveryRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DiscoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPostRequest;

  try {
    const data = await api.discoverAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsDiscoverPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **mcpConnectionDiscoveryRequest** | [McpConnectionDiscoveryRequest](McpConnectionDiscoveryRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**McpDiscoveryResult**](McpDiscoveryResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet

> McpConnectionRevision getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Mcp Connection

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // number (optional)
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGetRequest;

  try {
    const data = await api.getAgentMcpConnectionApiV1NamespacesNamespaceAgentMcpConnectionsKeyGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **key** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**McpConnectionRevision**](McpConnectionRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet

> AgentResourceRevision getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet(namespace, kind, key, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Resource

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // AgentResourceKind
    kind: ...,
    // string
    key: key_example,
    // number (optional)
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGetRequest;

  try {
    const data = await api.getAgentResourceApiV1NamespacesNamespaceAgentResourcesKindKeyGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **kind** | `AgentResourceKind` |  | [Defaults to `undefined`] [Enum: PROMPT, SKILL, MODEL_POLICY, EVALUATION, AGENT] |
| **key** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AgentResourceRevision**](AgentResourceRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet

> Array&lt;{ [key: string]: any; }&gt; listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet(namespace, key, revision, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Mcp Connection Tools

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // number (optional)
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGetRequest;

  try {
    const data = await api.listAgentMcpConnectionToolsApiV1NamespacesNamespaceAgentMcpConnectionsKeyToolsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **key** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array<{ [key: string]: any; }>**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet

> Array&lt;McpConnectionRevision&gt; listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Mcp Connections

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGetRequest;

  try {
    const data = await api.listAgentMcpConnectionsApiV1NamespacesNamespaceAgentMcpConnectionsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;McpConnectionRevision&gt;**](McpConnectionRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet

> Array&lt;AgentMemoryMetadata&gt; listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet(namespace, agentKey, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Memory Metadata

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { ListAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string (optional)
    agentKey: agentKey_example,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGetRequest;

  try {
    const data = await api.listAgentMemoryMetadataApiV1NamespacesNamespaceAgentMemoryGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **agentKey** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;AgentMemoryMetadata&gt;**](AgentMemoryMetadata.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet

> Array&lt;AgentResourceRevision&gt; listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet(namespace, kind, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Resources

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // AgentResourceKind (optional)
    kind: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAgentResourcesApiV1NamespacesNamespaceAgentResourcesGetRequest;

  try {
    const data = await api.listAgentResourcesApiV1NamespacesNamespaceAgentResourcesGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **kind** | `AgentResourceKind` |  | [Optional] [Defaults to `undefined`] [Enum: PROMPT, SKILL, MODEL_POLICY, EVALUATION, AGENT] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;AgentResourceRevision&gt;**](AgentResourceRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet

> AgentEnvelopePreview previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet(namespace, key, agentRevision, authorization, xAmeshCSRF, xAmeshTenant)

Preview Agent Definition

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { PreviewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // number
    agentRevision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PreviewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGetRequest;

  try {
    const data = await api.previewAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyPreviewGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **key** | `string` |  | [Defaults to `undefined`] |
| **agentRevision** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AgentEnvelopePreview**](AgentEnvelopePreview.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet

> AgentEvaluationPreview previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet(namespace, key, fixtureKey, revision, authorization, xAmeshCSRF, xAmeshTenant)

Preview Agent Evaluation Fixture

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { PreviewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // string
    fixtureKey: fixtureKey_example,
    // number
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PreviewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGetRequest;

  try {
    const data = await api.previewAgentEvaluationFixtureApiV1NamespacesNamespaceAgentEvaluationsKeyFixturesFixtureKeyPreviewGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **key** | `string` |  | [Defaults to `undefined`] |
| **fixtureKey** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AgentEvaluationPreview**](AgentEvaluationPreview.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost

> AgentRouteDecision previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost(namespace, agentRouteRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Agent Mesh Route

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { PreviewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // AgentRouteRequest
    agentRouteRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PreviewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPostRequest;

  try {
    const data = await api.previewAgentMeshRouteApiV1NamespacesNamespaceAgentMeshRoutesPreviewPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **agentRouteRequest** | [AgentRouteRequest](AgentRouteRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AgentRouteDecision**](AgentRouteDecision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost

> AgentCapabilityPin resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost(namespace, key, agentResolutionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resolve Agent Definition

### Example

```ts
import {
  Configuration,
  AgentsApi,
} from '@amesh/client';
import type { ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // AgentResolutionRequest
    agentResolutionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ResolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePostRequest;

  try {
    const data = await api.resolveAgentDefinitionApiV1NamespacesNamespaceAgentDefinitionsKeyResolvePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **key** | `string` |  | [Defaults to `undefined`] |
| **agentResolutionRequest** | [AgentResolutionRequest](AgentResolutionRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AgentCapabilityPin**](AgentCapabilityPin.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
