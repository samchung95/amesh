# FlowsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyFlowApiV1FlowsPut**](FlowsApi.md#applyflowapiv1flowsput) | **PUT** /api/v1/flows | Apply Flow |
| [**deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete**](FlowsApi.md#deleteflowrevisionapiv1flowsnamespaceflowidrevisionsrevisiondelete) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision} | Delete Flow Revision |
| [**diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet**](FlowsApi.md#diffflowrevisionsapiv1flowsnamespaceflowidrevisionsdiffget) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions/diff | Diff Flow Revisions |
| [**exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet**](FlowsApi.md#exportflowdocumentapiv1flowsnamespaceflowiddocumentget) | **GET** /api/v1/flows/{namespace}/{flow_id}/document | Export Flow Document |
| [**getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet**](FlowsApi.md#getflowdatacontractapiv1flowsnamespaceflowiddatacontractget) | **GET** /api/v1/flows/{namespace}/{flow_id}/data-contract | Get Flow Data Contract |
| [**getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet**](FlowsApi.md#getflowgraphapiv1flowsnamespaceflowidgraphget) | **GET** /api/v1/flows/{namespace}/{flow_id}/graph | Get Flow Graph |
| [**getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet**](FlowsApi.md#getflowmetadataapiv1flowsnamespaceflowidmetadataget) | **GET** /api/v1/flows/{namespace}/{flow_id}/metadata | Get Flow Metadata |
| [**listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet**](FlowsApi.md#listflowrevisionsapiv1flowsnamespaceflowidrevisionsget) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions | List Flow Revisions |
| [**listFlowsApiV1FlowsGet**](FlowsApi.md#listflowsapiv1flowsget) | **GET** /api/v1/flows | List Flows |
| [**promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut**](FlowsApi.md#promoteflowrevisionapiv1flowsnamespaceflowidrevisionsrevisionlifecycleput) | **PUT** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/lifecycle | Promote Flow Revision |
| [**restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost**](FlowsApi.md#restoreflowrevisionapiv1flowsnamespaceflowidrevisionsrevisionrestorepost) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/restore | Restore Flow Revision |
| [**validateFlowApiV1FlowsValidatePost**](FlowsApi.md#validateflowapiv1flowsvalidatepost) | **POST** /api/v1/flows/validate | Validate Flow |



## applyFlowApiV1FlowsPut

> PersistedFlow applyFlowApiV1FlowsPut(ifMatch, xAMESHSource, xAMESHCommit, xAMESHEnvironment, xAMESHDeployment, authorization, xAmeshCSRF, xAmeshTenant)

Apply Flow

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { ApplyFlowApiV1FlowsPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string (optional)
    ifMatch: ifMatch_example,
    // string (optional)
    xAMESHSource: xAMESHSource_example,
    // string (optional)
    xAMESHCommit: xAMESHCommit_example,
    // string (optional)
    xAMESHEnvironment: xAMESHEnvironment_example,
    // string (optional)
    xAMESHDeployment: xAMESHDeployment_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ApplyFlowApiV1FlowsPutRequest;

  try {
    const data = await api.applyFlowApiV1FlowsPut(body);
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
| **ifMatch** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAMESHSource** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAMESHCommit** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAMESHEnvironment** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAMESHDeployment** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PersistedFlow**](PersistedFlow.md)

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


## deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete

> deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Delete Flow Revision

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { DeleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // number
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDeleteRequest;

  try {
    const data = await api.deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete(body);
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
| **flowId** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet

> FlowRevisionDiff diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet(namespace, flowId, from, to, authorization, xAmeshCSRF, xAmeshTenant)

Diff Flow Revisions

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // number
    from: 56,
    // number
    to: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DiffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGetRequest;

  try {
    const data = await api.diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet(body);
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
| **flowId** | `string` |  | [Defaults to `undefined`] |
| **from** | `number` |  | [Defaults to `undefined`] |
| **to** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**FlowRevisionDiff**](FlowRevisionDiff.md)

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


## exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet

> FlowDocumentExport exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Export Flow Document

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // number (optional)
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGetRequest;

  try {
    const data = await api.exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet(body);
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
| **flowId** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**FlowDocumentExport**](FlowDocumentExport.md)

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


## getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet

> FlowDataContract getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Data Contract

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGetRequest;

  try {
    const data = await api.getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet(body);
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
| **flowId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**FlowDataContract**](FlowDataContract.md)

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


## getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet

> FlowGraph getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Graph

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetFlowGraphApiV1FlowsNamespaceFlowIdGraphGetRequest;

  try {
    const data = await api.getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet(body);
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
| **flowId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**FlowGraph**](FlowGraph.md)

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


## getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet

> FlowMetadataResponse getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Metadata

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGetRequest;

  try {
    const data = await api.getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet(body);
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
| **flowId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**FlowMetadataResponse**](FlowMetadataResponse.md)

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


## listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet

> Array&lt;FlowRevisionRecord&gt; listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

List Flow Revisions

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGetRequest;

  try {
    const data = await api.listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet(body);
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
| **flowId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;FlowRevisionRecord&gt;**](FlowRevisionRecord.md)

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


## listFlowsApiV1FlowsGet

> Array&lt;PersistedFlow&gt; listFlowsApiV1FlowsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Flows

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { ListFlowsApiV1FlowsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string | Opaque cursor from the prior page (optional)
    cursor: cursor_example,
    // number (optional)
    limit: 56,
    // Array<string> | Repeatable top-level equality filter in field=value form (optional)
    filter: ...,
    // string | Comma-separated top-level fields; prefix descending fields with - (optional)
    sort: sort_example,
    // string | Comma-separated top-level response fields (optional)
    fields: fields_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListFlowsApiV1FlowsGetRequest;

  try {
    const data = await api.listFlowsApiV1FlowsGet(body);
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
| **cursor** | `string` | Opaque cursor from the prior page | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `undefined`] |
| **filter** | `Array<string>` | Repeatable top-level equality filter in field&#x3D;value form | [Optional] |
| **sort** | `string` | Comma-separated top-level fields; prefix descending fields with - | [Optional] [Defaults to `undefined`] |
| **fields** | `string` | Comma-separated top-level response fields | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;PersistedFlow&gt;**](PersistedFlow.md)

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


## promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut

> PersistedFlow promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut(namespace, flowId, revision, flowRevisionLifecycleRequest, authorization, xAmeshCSRF, xAmeshTenant)

Promote Flow Revision

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // number
    revision: 56,
    // FlowRevisionLifecycleRequest
    flowRevisionLifecycleRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PromoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePutRequest;

  try {
    const data = await api.promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut(body);
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
| **flowId** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Defaults to `undefined`] |
| **flowRevisionLifecycleRequest** | [FlowRevisionLifecycleRequest](FlowRevisionLifecycleRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PersistedFlow**](PersistedFlow.md)

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


## restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost

> PersistedFlow restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost(namespace, flowId, revision, flowRevisionRestoreRequest, authorization, xAmeshCSRF, xAmeshTenant)

Restore Flow Revision

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // number
    revision: 56,
    // FlowRevisionRestoreRequest
    flowRevisionRestoreRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies RestoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePostRequest;

  try {
    const data = await api.restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost(body);
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
| **flowId** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Defaults to `undefined`] |
| **flowRevisionRestoreRequest** | [FlowRevisionRestoreRequest](FlowRevisionRestoreRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PersistedFlow**](PersistedFlow.md)

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


## validateFlowApiV1FlowsValidatePost

> FlowValidationResult validateFlowApiV1FlowsValidatePost()

Validate Flow

### Example

```ts
import {
  Configuration,
  FlowsApi,
} from '@amesh/client';
import type { ValidateFlowApiV1FlowsValidatePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowsApi();

  try {
    const data = await api.validateFlowApiV1FlowsValidatePost();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**FlowValidationResult**](FlowValidationResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
