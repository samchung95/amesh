# SimulationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost**](SimulationsApi.md#compareflowsimulationsapiv1flowsnamespaceflowidsimulationscomparepost) | **POST** /api/v1/flows/{namespace}/{flow_id}/simulations/compare | Compare Flow Simulations |
| [**simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost**](SimulationsApi.md#simulateflowrevisionapiv1flowsnamespaceflowidrevisionsrevisionsimulatepost) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/simulate | Simulate Flow Revision |



## compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost

> SimulationComparison compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost(namespace, flowId, from, to, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Compare Flow Simulations

### Example

```ts
import {
  Configuration,
  SimulationsApi,
} from '@amesh/client';
import type { CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new SimulationsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // number
    from: 56,
    // number
    to: 56,
    // SimulationRequest
    simulationRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePostRequest;

  try {
    const data = await api.compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost(body);
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
| **simulationRequest** | [SimulationRequest](SimulationRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**SimulationComparison**](SimulationComparison.md)

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


## simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost

> SimulationPlan simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost(namespace, flowId, revision, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Simulate Flow Revision

### Example

```ts
import {
  Configuration,
  SimulationsApi,
} from '@amesh/client';
import type { SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new SimulationsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // number
    revision: 56,
    // SimulationRequest
    simulationRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePostRequest;

  try {
    const data = await api.simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost(body);
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
| **simulationRequest** | [SimulationRequest](SimulationRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**SimulationPlan**](SimulationPlan.md)

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
