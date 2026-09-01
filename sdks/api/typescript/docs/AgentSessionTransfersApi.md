# AgentSessionTransfersApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet**](AgentSessionTransfersApi.md#exportagentprofiletransferapiv1adminagentsessiontransfersprofilesnamespaceagentkeyexportget) | **GET** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer |
| [**exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost**](AgentSessionTransfersApi.md#exportagentprofiletransferapiv1adminagentsessiontransfersprofilesnamespaceagentkeyexportpost) | **POST** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer |
| [**exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost**](AgentSessionTransfersApi.md#exportagentsessiontransferapiv1adminagentsessiontransferssessionssessionidexportpost) | **POST** /api/v1/admin/agent-session-transfers/sessions/{session_id}/export | Export Agent Session Transfer |
| [**importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost**](AgentSessionTransfersApi.md#importagentprofiletransferapiv1adminagentsessiontransfersprofilesimportpost) | **POST** /api/v1/admin/agent-session-transfers/profiles/import | Import Agent Profile Transfer |
| [**importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost**](AgentSessionTransfersApi.md#importagentsessiontransferapiv1adminagentsessiontransferssessionsimportpost) | **POST** /api/v1/admin/agent-session-transfers/sessions/import | Import Agent Session Transfer |
| [**planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost**](AgentSessionTransfersApi.md#planagentprofiletransferapiv1adminagentsessiontransfersprofilesplanpost) | **POST** /api/v1/admin/agent-session-transfers/profiles/plan | Plan Agent Profile Transfer |
| [**planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost**](AgentSessionTransfersApi.md#planagentsessiontransferapiv1adminagentsessiontransferssessionsplanpost) | **POST** /api/v1/admin/agent-session-transfers/sessions/plan | Plan Agent Session Transfer |



## exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet

> ProfileBundleOutput exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant)

Export Agent Profile Transfer

### Example

```ts
import {
  Configuration,
  AgentSessionTransfersApi,
} from '@amesh/client';
import type { ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionTransfersApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    agentKey: agentKey_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGetRequest;

  try {
    const data = await api.exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet(body);
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
| **agentKey** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ProfileBundleOutput**

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


## exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost

> ProfileBundleOutput exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant)

Export Agent Profile Transfer

### Example

```ts
import {
  Configuration,
  AgentSessionTransfersApi,
} from '@amesh/client';
import type { ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionTransfersApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    agentKey: agentKey_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPostRequest;

  try {
    const data = await api.exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost(body);
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
| **agentKey** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ProfileBundleOutput**

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


## exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost

> SessionTransferBundleOutput exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost(sessionId, agentSessionTransferSessionExportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Export Agent Session Transfer

### Example

```ts
import {
  Configuration,
  AgentSessionTransfersApi,
} from '@amesh/client';
import type { ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionTransfersApi();

  const body = {
    // string
    sessionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // AgentSessionTransferSessionExportRequest
    agentSessionTransferSessionExportRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPostRequest;

  try {
    const data = await api.exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost(body);
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
| **sessionId** | `string` |  | [Defaults to `undefined`] |
| **agentSessionTransferSessionExportRequest** | AgentSessionTransferSessionExportRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**SessionTransferBundleOutput**

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


## importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost

> ProfileImportResult importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost(agentSessionTransferProfileImportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Import Agent Profile Transfer

### Example

```ts
import {
  Configuration,
  AgentSessionTransfersApi,
} from '@amesh/client';
import type { ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionTransfersApi();

  const body = {
    // AgentSessionTransferProfileImportRequest
    agentSessionTransferProfileImportRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPostRequest;

  try {
    const data = await api.importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost(body);
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
| **agentSessionTransferProfileImportRequest** | AgentSessionTransferProfileImportRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ProfileImportResult**

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


## importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost

> SessionTransferImportResult importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost(agentSessionTransferSessionImportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Import Agent Session Transfer

### Example

```ts
import {
  Configuration,
  AgentSessionTransfersApi,
} from '@amesh/client';
import type { ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionTransfersApi();

  const body = {
    // AgentSessionTransferSessionImportRequest
    agentSessionTransferSessionImportRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPostRequest;

  try {
    const data = await api.importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost(body);
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
| **agentSessionTransferSessionImportRequest** | AgentSessionTransferSessionImportRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**SessionTransferImportResult**

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


## planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost

> ProfileCompatibilityReport planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost(agentSessionTransferProfilePlanRequest, authorization, xAmeshCSRF, xAmeshTenant)

Plan Agent Profile Transfer

### Example

```ts
import {
  Configuration,
  AgentSessionTransfersApi,
} from '@amesh/client';
import type { PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionTransfersApi();

  const body = {
    // AgentSessionTransferProfilePlanRequest
    agentSessionTransferProfilePlanRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPostRequest;

  try {
    const data = await api.planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost(body);
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
| **agentSessionTransferProfilePlanRequest** | AgentSessionTransferProfilePlanRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ProfileCompatibilityReport**

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


## planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost

> SessionTransferCompatibilityReport planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost(agentSessionTransferSessionPlanRequest, authorization, xAmeshCSRF, xAmeshTenant)

Plan Agent Session Transfer

### Example

```ts
import {
  Configuration,
  AgentSessionTransfersApi,
} from '@amesh/client';
import type { PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionTransfersApi();

  const body = {
    // AgentSessionTransferSessionPlanRequest
    agentSessionTransferSessionPlanRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPostRequest;

  try {
    const data = await api.planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost(body);
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
| **agentSessionTransferSessionPlanRequest** | AgentSessionTransferSessionPlanRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**SessionTransferCompatibilityReport**

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
