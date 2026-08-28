# FlowTestsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete**](FlowTestsApi.md#deleteflowtestapiv1flowsnamespaceflowidteststestiddelete) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/tests/{test_id} | Delete Flow Test |
| [**getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet**](FlowTestsApi.md#getflowtestgateapiv1namespacesnamespaceflowtestgateget) | **GET** /api/v1/namespaces/{namespace}/flow-test-gate | Get Flow Test Gate |
| [**listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet**](FlowTestsApi.md#listflowtestrunsapiv1flowsnamespaceflowidtestsrunsget) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests/runs | List Flow Test Runs |
| [**listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet**](FlowTestsApi.md#listflowtestsapiv1flowsnamespaceflowidtestsget) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests | List Flow Tests |
| [**runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost**](FlowTestsApi.md#runflowtestsapiv1flowsnamespaceflowidtestsrunspost) | **POST** /api/v1/flows/{namespace}/{flow_id}/tests/runs | Run Flow Tests |
| [**saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut**](FlowTestsApi.md#saveflowtestapiv1flowsnamespaceflowidtestsput) | **PUT** /api/v1/flows/{namespace}/{flow_id}/tests | Save Flow Test |
| [**updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut**](FlowTestsApi.md#updateflowtestgateapiv1namespacesnamespaceflowtestgateput) | **PUT** /api/v1/namespaces/{namespace}/flow-test-gate | Update Flow Test Gate |



## deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete

> deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete(namespace, flowId, testId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Delete Flow Test

### Example

```ts
import {
  Configuration,
  FlowTestsApi,
} from '@amesh/client';
import type { DeleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowTestsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // string
    testId: testId_example,
    // number
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDeleteRequest;

  try {
    const data = await api.deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete(body);
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
| **testId** | `string` |  | [Defaults to `undefined`] |
| **expectedVersion** | `number` |  | [Defaults to `undefined`] |
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


## getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet

> FlowTestQualityGate getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Test Gate

### Example

```ts
import {
  Configuration,
  FlowTestsApi,
} from '@amesh/client';
import type { GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowTestsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGetRequest;

  try {
    const data = await api.getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet(body);
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

**FlowTestQualityGate**

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


## listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet

> Array&lt;FlowTestRunResult&gt; listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet(namespace, flowId, revision, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Flow Test Runs

### Example

```ts
import {
  Configuration,
  FlowTestsApi,
} from '@amesh/client';
import type { ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowTestsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // number (optional)
    revision: 56,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGetRequest;

  try {
    const data = await api.listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `50`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;FlowTestRunResult&gt;**

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


## listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet

> Array&lt;FlowTestDefinition&gt; listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

List Flow Tests

### Example

```ts
import {
  Configuration,
  FlowTestsApi,
} from '@amesh/client';
import type { ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowTestsApi();

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
  } satisfies ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGetRequest;

  try {
    const data = await api.listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet(body);
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

**Array&lt;FlowTestDefinition&gt;**

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


## runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost

> FlowTestRunResult runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost(namespace, flowId, revision, flowTestRunRequest, authorization, xAmeshCSRF, xAmeshTenant)

Run Flow Tests

### Example

```ts
import {
  Configuration,
  FlowTestsApi,
} from '@amesh/client';
import type { RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowTestsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // number
    revision: 56,
    // FlowTestRunRequest
    flowTestRunRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPostRequest;

  try {
    const data = await api.runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost(body);
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
| **flowTestRunRequest** | FlowTestRunRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**FlowTestRunResult**

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


## saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut

> FlowTestDefinition saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut(namespace, flowId, flowTestDefinitionCreateRequest, authorization, xAmeshCSRF, xAmeshTenant)

Save Flow Test

### Example

```ts
import {
  Configuration,
  FlowTestsApi,
} from '@amesh/client';
import type { SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowTestsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // FlowTestDefinitionCreateRequest
    flowTestDefinitionCreateRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPutRequest;

  try {
    const data = await api.saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut(body);
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
| **flowTestDefinitionCreateRequest** | FlowTestDefinitionCreateRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**FlowTestDefinition**

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


## updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut

> FlowTestQualityGate updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut(namespace, flowTestQualityGateUpdate, authorization, xAmeshCSRF, xAmeshTenant)

Update Flow Test Gate

### Example

```ts
import {
  Configuration,
  FlowTestsApi,
} from '@amesh/client';
import type { UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new FlowTestsApi();

  const body = {
    // string
    namespace: namespace_example,
    // FlowTestQualityGateUpdate
    flowTestQualityGateUpdate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePutRequest;

  try {
    const data = await api.updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut(body);
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
| **flowTestQualityGateUpdate** | FlowTestQualityGateUpdate |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**FlowTestQualityGate**

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
