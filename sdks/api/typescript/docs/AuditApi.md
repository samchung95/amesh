# AuditApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createAuditLegalHoldApiV1AuditLegalHoldsPost**](AuditApi.md#createauditlegalholdapiv1auditlegalholdspost) | **POST** /api/v1/audit-legal-holds | Create Audit Legal Hold |
| [**createComplianceEvidenceApiV1ComplianceEvidencePost**](AuditApi.md#createcomplianceevidenceapiv1complianceevidencepost) | **POST** /api/v1/compliance-evidence | Create Compliance Evidence |
| [**createObjectAuditExportApiV1AuditExportsPost**](AuditApi.md#createobjectauditexportapiv1auditexportspost) | **POST** /api/v1/audit-exports | Create Object Audit Export |
| [**createObjectCompliancePackageApiV1CompliancePackagesPost**](AuditApi.md#createobjectcompliancepackageapiv1compliancepackagespost) | **POST** /api/v1/compliance-packages | Create Object Compliance Package |
| [**downloadAuditExportApiV1AuditEventsExportGet**](AuditApi.md#downloadauditexportapiv1auditeventsexportget) | **GET** /api/v1/audit-events/export | Download Audit Export |
| [**downloadCompliancePackageApiV1CompliancePackagesExportGet**](AuditApi.md#downloadcompliancepackageapiv1compliancepackagesexportget) | **GET** /api/v1/compliance-packages/export | Download Compliance Package |
| [**getAuditPolicyApiV1AuditPolicyGet**](AuditApi.md#getauditpolicyapiv1auditpolicyget) | **GET** /api/v1/audit-policy | Get Audit Policy |
| [**listAuditEventsApiV1AuditEventsGet**](AuditApi.md#listauditeventsapiv1auditeventsget) | **GET** /api/v1/audit-events | List Audit Events |
| [**listAuditLegalHoldsApiV1AuditLegalHoldsGet**](AuditApi.md#listauditlegalholdsapiv1auditlegalholdsget) | **GET** /api/v1/audit-legal-holds | List Audit Legal Holds |
| [**listComplianceEvidenceApiV1ComplianceEvidenceGet**](AuditApi.md#listcomplianceevidenceapiv1complianceevidenceget) | **GET** /api/v1/compliance-evidence | List Compliance Evidence |
| [**purgeAuditRetentionApiV1AuditRetentionPurgePost**](AuditApi.md#purgeauditretentionapiv1auditretentionpurgepost) | **POST** /api/v1/audit-retention/purge | Purge Audit Retention |
| [**releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete**](AuditApi.md#releaseauditlegalholdapiv1auditlegalholdsholdiddelete) | **DELETE** /api/v1/audit-legal-holds/{hold_id} | Release Audit Legal Hold |
| [**updateAuditPolicyApiV1AuditPolicyPut**](AuditApi.md#updateauditpolicyapiv1auditpolicyput) | **PUT** /api/v1/audit-policy | Update Audit Policy |
| [**verifyAuditIntegrityApiV1AuditEventsIntegrityGet**](AuditApi.md#verifyauditintegrityapiv1auditeventsintegrityget) | **GET** /api/v1/audit-events/integrity | Verify Audit Integrity |



## createAuditLegalHoldApiV1AuditLegalHoldsPost

> AuditLegalHold createAuditLegalHoldApiV1AuditLegalHoldsPost(auditLegalHoldCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Audit Legal Hold

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { CreateAuditLegalHoldApiV1AuditLegalHoldsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // AuditLegalHoldCreate
    auditLegalHoldCreate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateAuditLegalHoldApiV1AuditLegalHoldsPostRequest;

  try {
    const data = await api.createAuditLegalHoldApiV1AuditLegalHoldsPost(body);
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
| **auditLegalHoldCreate** | AuditLegalHoldCreate |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AuditLegalHold**

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


## createComplianceEvidenceApiV1ComplianceEvidencePost

> ComplianceEvidenceRecord createComplianceEvidenceApiV1ComplianceEvidencePost(complianceEvidenceCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Compliance Evidence

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { CreateComplianceEvidenceApiV1ComplianceEvidencePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // ComplianceEvidenceCreate
    complianceEvidenceCreate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateComplianceEvidenceApiV1ComplianceEvidencePostRequest;

  try {
    const data = await api.createComplianceEvidenceApiV1ComplianceEvidencePost(body);
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
| **complianceEvidenceCreate** | ComplianceEvidenceCreate |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ComplianceEvidenceRecord**

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


## createObjectAuditExportApiV1AuditExportsPost

> AuditExportReceipt createObjectAuditExportApiV1AuditExportsPost(auditExportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Create Object Audit Export

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { CreateObjectAuditExportApiV1AuditExportsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // AuditExportRequest
    auditExportRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateObjectAuditExportApiV1AuditExportsPostRequest;

  try {
    const data = await api.createObjectAuditExportApiV1AuditExportsPost(body);
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
| **auditExportRequest** | AuditExportRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AuditExportReceipt**

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


## createObjectCompliancePackageApiV1CompliancePackagesPost

> AuditExportReceipt createObjectCompliancePackageApiV1CompliancePackagesPost(compliancePackageRequest, authorization, xAmeshCSRF, xAmeshTenant)

Create Object Compliance Package

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { CreateObjectCompliancePackageApiV1CompliancePackagesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // CompliancePackageRequest
    compliancePackageRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateObjectCompliancePackageApiV1CompliancePackagesPostRequest;

  try {
    const data = await api.createObjectCompliancePackageApiV1CompliancePackagesPost(body);
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
| **compliancePackageRequest** | CompliancePackageRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AuditExportReceipt**

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


## downloadAuditExportApiV1AuditEventsExportGet

> any downloadAuditExportApiV1AuditEventsExportGet(format, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant)

Download Audit Export

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { DownloadAuditExportApiV1AuditEventsExportGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // AuditExportFormat (optional)
    format: ...,
    // number (optional)
    limit: 56,
    // string (optional)
    action: action_example,
    // string (optional)
    resourceType: resourceType_example,
    // string (optional)
    outcome: outcome_example,
    // Date (optional)
    occurredFrom: 2013-10-20T19:20:30+01:00,
    // Date (optional)
    occurredTo: 2013-10-20T19:20:30+01:00,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DownloadAuditExportApiV1AuditEventsExportGetRequest;

  try {
    const data = await api.downloadAuditExportApiV1AuditEventsExportGet(body);
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
| **format** | `AuditExportFormat` |  | [Optional] [Defaults to `undefined`] [Enum: JSON, NDJSON] |
| **limit** | `number` |  | [Optional] [Defaults to `10000`] |
| **action** | `string` |  | [Optional] [Defaults to `undefined`] |
| **resourceType** | `string` |  | [Optional] [Defaults to `undefined`] |
| **outcome** | `string` |  | [Optional] [Defaults to `undefined`] |
| **occurredFrom** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **occurredTo** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

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


## downloadCompliancePackageApiV1CompliancePackagesExportGet

> any downloadCompliancePackageApiV1CompliancePackagesExportGet(occurredFrom, occurredTo, maxAuditEvents, authorization, xAmeshCSRF, xAmeshTenant)

Download Compliance Package

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { DownloadCompliancePackageApiV1CompliancePackagesExportGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // Date (optional)
    occurredFrom: 2013-10-20T19:20:30+01:00,
    // Date (optional)
    occurredTo: 2013-10-20T19:20:30+01:00,
    // number (optional)
    maxAuditEvents: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DownloadCompliancePackageApiV1CompliancePackagesExportGetRequest;

  try {
    const data = await api.downloadCompliancePackageApiV1CompliancePackagesExportGet(body);
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
| **occurredFrom** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **occurredTo** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **maxAuditEvents** | `number` |  | [Optional] [Defaults to `10000`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

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


## getAuditPolicyApiV1AuditPolicyGet

> AuditRetentionPolicy getAuditPolicyApiV1AuditPolicyGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Audit Policy

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { GetAuditPolicyApiV1AuditPolicyGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAuditPolicyApiV1AuditPolicyGetRequest;

  try {
    const data = await api.getAuditPolicyApiV1AuditPolicyGet(body);
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

**AuditRetentionPolicy**

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


## listAuditEventsApiV1AuditEventsGet

> AuditEventPage listAuditEventsApiV1AuditEventsGet(cursor, limit, action, resourceType, outcome, occurredFrom, occurredTo, authorization, xAmeshCSRF, xAmeshTenant)

List Audit Events

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { ListAuditEventsApiV1AuditEventsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // number (optional)
    cursor: 56,
    // number (optional)
    limit: 56,
    // string (optional)
    action: action_example,
    // string (optional)
    resourceType: resourceType_example,
    // string (optional)
    outcome: outcome_example,
    // Date (optional)
    occurredFrom: 2013-10-20T19:20:30+01:00,
    // Date (optional)
    occurredTo: 2013-10-20T19:20:30+01:00,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAuditEventsApiV1AuditEventsGetRequest;

  try {
    const data = await api.listAuditEventsApiV1AuditEventsGet(body);
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
| **cursor** | `number` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **action** | `string` |  | [Optional] [Defaults to `undefined`] |
| **resourceType** | `string` |  | [Optional] [Defaults to `undefined`] |
| **outcome** | `string` |  | [Optional] [Defaults to `undefined`] |
| **occurredFrom** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **occurredTo** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AuditEventPage**

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


## listAuditLegalHoldsApiV1AuditLegalHoldsGet

> Array&lt;AuditLegalHold&gt; listAuditLegalHoldsApiV1AuditLegalHoldsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Audit Legal Holds

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { ListAuditLegalHoldsApiV1AuditLegalHoldsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAuditLegalHoldsApiV1AuditLegalHoldsGetRequest;

  try {
    const data = await api.listAuditLegalHoldsApiV1AuditLegalHoldsGet(body);
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

**Array&lt;AuditLegalHold&gt;**

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


## listComplianceEvidenceApiV1ComplianceEvidenceGet

> Array&lt;ComplianceEvidenceRecord&gt; listComplianceEvidenceApiV1ComplianceEvidenceGet(authorization, xAmeshCSRF, xAmeshTenant)

List Compliance Evidence

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { ListComplianceEvidenceApiV1ComplianceEvidenceGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListComplianceEvidenceApiV1ComplianceEvidenceGetRequest;

  try {
    const data = await api.listComplianceEvidenceApiV1ComplianceEvidenceGet(body);
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

**Array&lt;ComplianceEvidenceRecord&gt;**

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


## purgeAuditRetentionApiV1AuditRetentionPurgePost

> AuditRetentionResult purgeAuditRetentionApiV1AuditRetentionPurgePost(authorization, xAmeshCSRF, xAmeshTenant)

Purge Audit Retention

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { PurgeAuditRetentionApiV1AuditRetentionPurgePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PurgeAuditRetentionApiV1AuditRetentionPurgePostRequest;

  try {
    const data = await api.purgeAuditRetentionApiV1AuditRetentionPurgePost(body);
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

**AuditRetentionResult**

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


## releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete

> AuditLegalHold releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete(holdId, authorization, xAmeshCSRF, xAmeshTenant)

Release Audit Legal Hold

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // string
    holdId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDeleteRequest;

  try {
    const data = await api.releaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete(body);
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
| **holdId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AuditLegalHold**

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


## updateAuditPolicyApiV1AuditPolicyPut

> AuditRetentionPolicy updateAuditPolicyApiV1AuditPolicyPut(auditRetentionPolicyUpdate, authorization, xAmeshCSRF, xAmeshTenant)

Update Audit Policy

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { UpdateAuditPolicyApiV1AuditPolicyPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // AuditRetentionPolicyUpdate
    auditRetentionPolicyUpdate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies UpdateAuditPolicyApiV1AuditPolicyPutRequest;

  try {
    const data = await api.updateAuditPolicyApiV1AuditPolicyPut(body);
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
| **auditRetentionPolicyUpdate** | AuditRetentionPolicyUpdate |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AuditRetentionPolicy**

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


## verifyAuditIntegrityApiV1AuditEventsIntegrityGet

> AuditIntegrityReport verifyAuditIntegrityApiV1AuditEventsIntegrityGet(authorization, xAmeshCSRF, xAmeshTenant)

Verify Audit Integrity

### Example

```ts
import {
  Configuration,
  AuditApi,
} from '@amesh/client';
import type { VerifyAuditIntegrityApiV1AuditEventsIntegrityGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuditApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies VerifyAuditIntegrityApiV1AuditEventsIntegrityGetRequest;

  try {
    const data = await api.verifyAuditIntegrityApiV1AuditEventsIntegrityGet(body);
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

**AuditIntegrityReport**

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
