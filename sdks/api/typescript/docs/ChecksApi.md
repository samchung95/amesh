# ChecksApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getCheckComplianceApiV1CheckComplianceGet**](ChecksApi.md#getcheckcomplianceapiv1checkcomplianceget) | **GET** /api/v1/check-compliance | Get Check Compliance |
| [**listCheckEvaluationsApiV1CheckEvaluationsGet**](ChecksApi.md#listcheckevaluationsapiv1checkevaluationsget) | **GET** /api/v1/check-evaluations | List Check Evaluations |
| [**listCheckPoliciesApiV1CheckPoliciesGet**](ChecksApi.md#listcheckpoliciesapiv1checkpoliciesget) | **GET** /api/v1/check-policies | List Check Policies |
| [**upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut**](ChecksApi.md#upsertcheckpolicyapiv1checkpoliciesnamespacepolicykeyput) | **PUT** /api/v1/check-policies/{namespace}/{policy_key} | Upsert Check Policy |



## getCheckComplianceApiV1CheckComplianceGet

> Array&lt;CheckComplianceSummary&gt; getCheckComplianceApiV1CheckComplianceGet(groupBy, fromTime, toTime, namespace, flowId, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Check Compliance

### Example

```ts
import {
  Configuration,
  ChecksApi,
} from '@amesh/client';
import type { GetCheckComplianceApiV1CheckComplianceGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ChecksApi();

  const body = {
    // string (optional)
    groupBy: groupBy_example,
    // Date (optional)
    fromTime: 2013-10-20T19:20:30+01:00,
    // Date (optional)
    toTime: 2013-10-20T19:20:30+01:00,
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    flowId: flowId_example,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetCheckComplianceApiV1CheckComplianceGetRequest;

  try {
    const data = await api.getCheckComplianceApiV1CheckComplianceGet(body);
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
| **groupBy** | `string` |  | [Optional] [Defaults to `&#39;flow&#39;`] |
| **fromTime** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **toTime** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **flowId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;CheckComplianceSummary&gt;**

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


## listCheckEvaluationsApiV1CheckEvaluationsGet

> Array&lt;CheckEvaluation&gt; listCheckEvaluationsApiV1CheckEvaluationsGet(namespace, flowId, executionId, outcome, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Check Evaluations

### Example

```ts
import {
  Configuration,
  ChecksApi,
} from '@amesh/client';
import type { ListCheckEvaluationsApiV1CheckEvaluationsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ChecksApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    flowId: flowId_example,
    // string (optional)
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // CheckOutcome (optional)
    outcome: ...,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListCheckEvaluationsApiV1CheckEvaluationsGetRequest;

  try {
    const data = await api.listCheckEvaluationsApiV1CheckEvaluationsGet(body);
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
| **flowId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **executionId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **outcome** | `CheckOutcome` |  | [Optional] [Defaults to `undefined`] [Enum: PASS, WARN, FAIL, ERROR] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;CheckEvaluation&gt;**

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


## listCheckPoliciesApiV1CheckPoliciesGet

> Array&lt;NamespaceCheckPolicy&gt; listCheckPoliciesApiV1CheckPoliciesGet(namespace, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Check Policies

### Example

```ts
import {
  Configuration,
  ChecksApi,
} from '@amesh/client';
import type { ListCheckPoliciesApiV1CheckPoliciesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ChecksApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListCheckPoliciesApiV1CheckPoliciesGetRequest;

  try {
    const data = await api.listCheckPoliciesApiV1CheckPoliciesGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;NamespaceCheckPolicy&gt;**

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


## upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut

> NamespaceCheckPolicy upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut(namespace, policyKey, checkPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Upsert Check Policy

### Example

```ts
import {
  Configuration,
  ChecksApi,
} from '@amesh/client';
import type { UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ChecksApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    policyKey: policyKey_example,
    // CheckPolicyUpsertRequest
    checkPolicyUpsertRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPutRequest;

  try {
    const data = await api.upsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut(body);
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
| **policyKey** | `string` |  | [Defaults to `undefined`] |
| **checkPolicyUpsertRequest** | CheckPolicyUpsertRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**NamespaceCheckPolicy**

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
