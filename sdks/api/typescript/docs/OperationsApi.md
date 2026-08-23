# OperationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**activateOperationalControlApiV1OperationalControlsPost**](OperationsApi.md#activateoperationalcontrolapiv1operationalcontrolspost) | **POST** /api/v1/operational-controls | Activate Operational Control |
| [**changeOperationalControlApiV1OperationalControlsControlIdActionsPost**](OperationsApi.md#changeoperationalcontrolapiv1operationalcontrolscontrolidactionspost) | **POST** /api/v1/operational-controls/{control_id}/actions | Change Operational Control |
| [**deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete**](OperationsApi.md#deactivateannouncementapiv1announcementsannouncementiddelete) | **DELETE** /api/v1/announcements/{announcement_id} | Deactivate Announcement |
| [**drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost**](OperationsApi.md#drainserviceinstanceapiv1operationsservicesinstanceiddrainpost) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance |
| [**getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet**](OperationsApi.md#getadmissiondiagnosticsapiv1admissionsdiagnosticsget) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics |
| [**getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet**](OperationsApi.md#getnetworkdiagnosticsapiv1operationsnetworkdiagnosticsget) | **GET** /api/v1/operations/network-diagnostics | Get Network Diagnostics |
| [**getReconciliationApiV1ReconciliationsRunIdGet**](OperationsApi.md#getreconciliationapiv1reconciliationsrunidget) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation |
| [**getServiceTopologyApiV1OperationsTopologyGet**](OperationsApi.md#getservicetopologyapiv1operationstopologyget) | **GET** /api/v1/operations/topology | Get Service Topology |
| [**listAnnouncementsApiV1AnnouncementsGet**](OperationsApi.md#listannouncementsapiv1announcementsget) | **GET** /api/v1/announcements | List Announcements |
| [**listOperationalControlEventsApiV1OperationalControlEventsGet**](OperationsApi.md#listoperationalcontroleventsapiv1operationalcontroleventsget) | **GET** /api/v1/operational-control-events | List Operational Control Events |
| [**listOperationalControlsApiV1OperationalControlsGet**](OperationsApi.md#listoperationalcontrolsapiv1operationalcontrolsget) | **GET** /api/v1/operational-controls | List Operational Controls |
| [**listReconciliationsApiV1ReconciliationsGet**](OperationsApi.md#listreconciliationsapiv1reconciliationsget) | **GET** /api/v1/reconciliations | List Reconciliations |
| [**publishAnnouncementApiV1AnnouncementsPost**](OperationsApi.md#publishannouncementapiv1announcementspost) | **POST** /api/v1/announcements | Publish Announcement |
| [**reconcileAdmissionsApiV1AdmissionsReconcilePost**](OperationsApi.md#reconcileadmissionsapiv1admissionsreconcilepost) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions |
| [**runReconciliationApiV1ReconciliationsPost**](OperationsApi.md#runreconciliationapiv1reconciliationspost) | **POST** /api/v1/reconciliations | Run Reconciliation |



## activateOperationalControlApiV1OperationalControlsPost

> OperationalControl activateOperationalControlApiV1OperationalControlsPost(operationalControlCreateRequest, authorization, xAmeshCSRF, xAmeshTenant)

Activate Operational Control

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { ActivateOperationalControlApiV1OperationalControlsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // OperationalControlCreateRequest
    operationalControlCreateRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ActivateOperationalControlApiV1OperationalControlsPostRequest;

  try {
    const data = await api.activateOperationalControlApiV1OperationalControlsPost(body);
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
| **operationalControlCreateRequest** | [OperationalControlCreateRequest](OperationalControlCreateRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**OperationalControl**](OperationalControl.md)

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


## changeOperationalControlApiV1OperationalControlsControlIdActionsPost

> OperationalControl changeOperationalControlApiV1OperationalControlsControlIdActionsPost(controlId, operationalControlActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Change Operational Control

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { ChangeOperationalControlApiV1OperationalControlsControlIdActionsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // string
    controlId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // OperationalControlActionRequest
    operationalControlActionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ChangeOperationalControlApiV1OperationalControlsControlIdActionsPostRequest;

  try {
    const data = await api.changeOperationalControlApiV1OperationalControlsControlIdActionsPost(body);
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
| **controlId** | `string` |  | [Defaults to `undefined`] |
| **operationalControlActionRequest** | [OperationalControlActionRequest](OperationalControlActionRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**OperationalControl**](OperationalControl.md)

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


## deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete

> Announcement deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete(announcementId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Deactivate Announcement

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { DeactivateAnnouncementApiV1AnnouncementsAnnouncementIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // string
    announcementId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeactivateAnnouncementApiV1AnnouncementsAnnouncementIdDeleteRequest;

  try {
    const data = await api.deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete(body);
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
| **announcementId** | `string` |  | [Defaults to `undefined`] |
| **expectedVersion** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Announcement**](Announcement.md)

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


## getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet

> NetworkDiagnosticBundle getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Network Diagnostics

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { GetNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGetRequest } from '@amesh/client';

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
  } satisfies GetNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGetRequest;

  try {
    const data = await api.getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet(body);
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

[**NetworkDiagnosticBundle**](NetworkDiagnosticBundle.md)

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


## listAnnouncementsApiV1AnnouncementsGet

> Array&lt;Announcement&gt; listAnnouncementsApiV1AnnouncementsGet(namespace, includeInactive, authorization, xAmeshCSRF, xAmeshTenant)

List Announcements

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { ListAnnouncementsApiV1AnnouncementsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // boolean (optional)
    includeInactive: true,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAnnouncementsApiV1AnnouncementsGetRequest;

  try {
    const data = await api.listAnnouncementsApiV1AnnouncementsGet(body);
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
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **includeInactive** | `boolean` |  | [Optional] [Defaults to `false`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;Announcement&gt;**](Announcement.md)

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


## listOperationalControlEventsApiV1OperationalControlEventsGet

> Array&lt;OperationalControlEvent&gt; listOperationalControlEventsApiV1OperationalControlEventsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Operational Control Events

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { ListOperationalControlEventsApiV1OperationalControlEventsGetRequest } from '@amesh/client';

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
  } satisfies ListOperationalControlEventsApiV1OperationalControlEventsGetRequest;

  try {
    const data = await api.listOperationalControlEventsApiV1OperationalControlEventsGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `200`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;OperationalControlEvent&gt;**](OperationalControlEvent.md)

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


## listOperationalControlsApiV1OperationalControlsGet

> Array&lt;OperationalControl&gt; listOperationalControlsApiV1OperationalControlsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Operational Controls

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { ListOperationalControlsApiV1OperationalControlsGetRequest } from '@amesh/client';

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
  } satisfies ListOperationalControlsApiV1OperationalControlsGetRequest;

  try {
    const data = await api.listOperationalControlsApiV1OperationalControlsGet(body);
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

[**Array&lt;OperationalControl&gt;**](OperationalControl.md)

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


## publishAnnouncementApiV1AnnouncementsPost

> Announcement publishAnnouncementApiV1AnnouncementsPost(announcementCreateRequest, authorization, xAmeshCSRF, xAmeshTenant)

Publish Announcement

### Example

```ts
import {
  Configuration,
  OperationsApi,
} from '@amesh/client';
import type { PublishAnnouncementApiV1AnnouncementsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new OperationsApi();

  const body = {
    // AnnouncementCreateRequest
    announcementCreateRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PublishAnnouncementApiV1AnnouncementsPostRequest;

  try {
    const data = await api.publishAnnouncementApiV1AnnouncementsPost(body);
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
| **announcementCreateRequest** | [AnnouncementCreateRequest](AnnouncementCreateRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Announcement**](Announcement.md)

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
