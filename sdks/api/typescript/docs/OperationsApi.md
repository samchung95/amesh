# OperationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost**](OperationsApi.md#drainserviceinstanceapiv1operationsservicesinstanceiddrainpost) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance |
| [**getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet**](OperationsApi.md#getadmissiondiagnosticsapiv1admissionsdiagnosticsget) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics |
| [**getReconciliationApiV1ReconciliationsRunIdGet**](OperationsApi.md#getreconciliationapiv1reconciliationsrunidget) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation |
| [**getServiceTopologyApiV1OperationsTopologyGet**](OperationsApi.md#getservicetopologyapiv1operationstopologyget) | **GET** /api/v1/operations/topology | Get Service Topology |
| [**listReconciliationsApiV1ReconciliationsGet**](OperationsApi.md#listreconciliationsapiv1reconciliationsget) | **GET** /api/v1/reconciliations | List Reconciliations |
| [**reconcileAdmissionsApiV1AdmissionsReconcilePost**](OperationsApi.md#reconcileadmissionsapiv1admissionsreconcilepost) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions |
| [**runReconciliationApiV1ReconciliationsPost**](OperationsApi.md#runreconciliationapiv1reconciliationspost) | **POST** /api/v1/reconciliations | Run Reconciliation |



## drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost

> ServiceInstance drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost(instanceId, serviceDrainRequest, authorization, xAmeshCSRF)

Drain Service Instance

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // string
    instanceId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // ServiceDrainRequest
    serviceDrainRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostRequest;

  try {
    const data = await api.drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost(body);
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
| **instanceId** | `string` |  | [Defaults to `undefined`] |
| **serviceDrainRequest** | [ServiceDrainRequest](ServiceDrainRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ServiceInstance**](ServiceInstance.md)

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


## getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet

> AdmissionDiagnostics getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Admission Diagnostics

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetRequest;

  try {
    const data = await api.getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AdmissionDiagnostics**](AdmissionDiagnostics.md)

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


## getReconciliationApiV1ReconciliationsRunIdGet

> ReconciliationRun getReconciliationApiV1ReconciliationsRunIdGet(runId, authorization, xAmeshCSRF, xAmeshTenant)

Get Reconciliation

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { GetReconciliationApiV1ReconciliationsRunIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // string
    runId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetReconciliationApiV1ReconciliationsRunIdGetRequest;

  try {
    const data = await api.getReconciliationApiV1ReconciliationsRunIdGet(body);
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
| **runId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ReconciliationRun**](ReconciliationRun.md)

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


## getServiceTopologyApiV1OperationsTopologyGet

> ServiceTopology getServiceTopologyApiV1OperationsTopologyGet(authorization, xAmeshCSRF)

Get Service Topology

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { GetServiceTopologyApiV1OperationsTopologyGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies GetServiceTopologyApiV1OperationsTopologyGetRequest;

  try {
    const data = await api.getServiceTopologyApiV1OperationsTopologyGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ServiceTopology**](ServiceTopology.md)

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


## listReconciliationsApiV1ReconciliationsGet

> Array&lt;ReconciliationRun&gt; listReconciliationsApiV1ReconciliationsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Reconciliations

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { ListReconciliationsApiV1ReconciliationsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListReconciliationsApiV1ReconciliationsGetRequest;

  try {
    const data = await api.listReconciliationsApiV1ReconciliationsGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `50`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;ReconciliationRun&gt;**](ReconciliationRun.md)

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


## reconcileAdmissionsApiV1AdmissionsReconcilePost

> { [key: string]: number; } reconcileAdmissionsApiV1AdmissionsReconcilePost(limit, authorization, xAmeshCSRF, xAmeshTenant)

Reconcile Admissions

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { ReconcileAdmissionsApiV1AdmissionsReconcilePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ReconcileAdmissionsApiV1AdmissionsReconcilePostRequest;

  try {
    const data = await api.reconcileAdmissionsApiV1AdmissionsReconcilePost(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**{ [key: string]: number; }**

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


## runReconciliationApiV1ReconciliationsPost

> ReconciliationRun runReconciliationApiV1ReconciliationsPost(reconciliationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Run Reconciliation

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { RunReconciliationApiV1ReconciliationsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // ReconciliationRequest
    reconciliationRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies RunReconciliationApiV1ReconciliationsPostRequest;

  try {
    const data = await api.runReconciliationApiV1ReconciliationsPost(body);
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
| **reconciliationRequest** | [ReconciliationRequest](ReconciliationRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ReconciliationRun**](ReconciliationRun.md)

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
