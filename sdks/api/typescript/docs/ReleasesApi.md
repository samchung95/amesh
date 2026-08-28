# ReleasesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost**](ReleasesApi.md#applypolicyapiv1releasespoliciespolicyidapplypost) | **POST** /api/v1/releases/policies/{policy_id}/apply | Apply Policy |
| [**createPolicyApiV1ReleasesPoliciesPost**](ReleasesApi.md#createpolicyapiv1releasespoliciespost) | **POST** /api/v1/releases/policies | Create Policy |
| [**killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost**](ReleasesApi.md#killswitchapiv1releasestargetkindtargetkeykillswitchpost) | **POST** /api/v1/releases/{target_kind}/{target_key}/kill-switch | Kill Switch |
| [**previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost**](ReleasesApi.md#previewpolicyapiv1releasespoliciespolicyidpreviewpost) | **POST** /api/v1/releases/policies/{policy_id}/preview | Preview Policy |
| [**recordEvidenceApiV1ReleasesEvidencePost**](ReleasesApi.md#recordevidenceapiv1releasesevidencepost) | **POST** /api/v1/releases/evidence | Record Evidence |
| [**rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost**](ReleasesApi.md#rollbackapiv1releasestargetkindtargetkeyrollbackpost) | **POST** /api/v1/releases/{target_kind}/{target_key}/rollback | Rollback |
| [**targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet**](ReleasesApi.md#targethistoryapiv1releasestargetkindtargetkeyhistoryget) | **GET** /api/v1/releases/{target_kind}/{target_key}/history | Target History |
| [**targetStateApiV1ReleasesTargetKindTargetKeyGet**](ReleasesApi.md#targetstateapiv1releasestargetkindtargetkeyget) | **GET** /api/v1/releases/{target_kind}/{target_key} | Target State |



## applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost

> any applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost(policyId, promotionApplyRequest, xAmeshTenant, authorization, xAmeshCSRF)

Apply Policy

### Example

```ts
import {
  Configuration,
  ReleasesApi,
} from '@amesh/client';
import type { ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ReleasesApi();

  const body = {
    // string
    policyId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // PromotionApplyRequest
    promotionApplyRequest: ...,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPostRequest;

  try {
    const data = await api.applyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost(body);
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
| **policyId** | `string` |  | [Defaults to `undefined`] |
| **promotionApplyRequest** | PromotionApplyRequest |  | |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

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


## createPolicyApiV1ReleasesPoliciesPost

> PromotionPolicyOutput createPolicyApiV1ReleasesPoliciesPost(promotionPolicyInput, xAmeshTenant, authorization, xAmeshCSRF)

Create Policy

### Example

```ts
import {
  Configuration,
  ReleasesApi,
} from '@amesh/client';
import type { CreatePolicyApiV1ReleasesPoliciesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ReleasesApi();

  const body = {
    // PromotionPolicyInput
    promotionPolicyInput: ...,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies CreatePolicyApiV1ReleasesPoliciesPostRequest;

  try {
    const data = await api.createPolicyApiV1ReleasesPoliciesPost(body);
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
| **promotionPolicyInput** | PromotionPolicyInput |  | |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**PromotionPolicyOutput**

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


## killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost

> any killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost(targetKind, targetKey, promotionKillSwitchRequest, xAmeshTenant, authorization, xAmeshCSRF)

Kill Switch

### Example

```ts
import {
  Configuration,
  ReleasesApi,
} from '@amesh/client';
import type { KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ReleasesApi();

  const body = {
    // PromotionTargetKind
    targetKind: ...,
    // string
    targetKey: targetKey_example,
    // PromotionKillSwitchRequest
    promotionKillSwitchRequest: ...,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPostRequest;

  try {
    const data = await api.killSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost(body);
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
| **targetKind** | `PromotionTargetKind` |  | [Defaults to `undefined`] [Enum: WORKFLOW, AGENT] |
| **targetKey** | `string` |  | [Defaults to `undefined`] |
| **promotionKillSwitchRequest** | PromotionKillSwitchRequest |  | |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

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


## previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost

> any previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost(policyId, xAmeshTenant, authorization, xAmeshCSRF, promotionPreviewRequest)

Preview Policy

### Example

```ts
import {
  Configuration,
  ReleasesApi,
} from '@amesh/client';
import type { PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ReleasesApi();

  const body = {
    // string
    policyId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // PromotionPreviewRequest (optional)
    promotionPreviewRequest: ...,
  } satisfies PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPostRequest;

  try {
    const data = await api.previewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost(body);
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
| **policyId** | `string` |  | [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **promotionPreviewRequest** | PromotionPreviewRequest |  | [Optional] |

### Return type

**any**

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


## recordEvidenceApiV1ReleasesEvidencePost

> EvidenceArtifact recordEvidenceApiV1ReleasesEvidencePost(evidenceArtifact, xAmeshTenant, authorization, xAmeshCSRF)

Record Evidence

### Example

```ts
import {
  Configuration,
  ReleasesApi,
} from '@amesh/client';
import type { RecordEvidenceApiV1ReleasesEvidencePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ReleasesApi();

  const body = {
    // EvidenceArtifact
    evidenceArtifact: ...,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RecordEvidenceApiV1ReleasesEvidencePostRequest;

  try {
    const data = await api.recordEvidenceApiV1ReleasesEvidencePost(body);
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
| **evidenceArtifact** | EvidenceArtifact |  | |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**EvidenceArtifact**

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


## rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost

> any rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost(targetKind, targetKey, promotionRollbackRequest, xAmeshTenant, authorization, xAmeshCSRF)

Rollback

### Example

```ts
import {
  Configuration,
  ReleasesApi,
} from '@amesh/client';
import type { RollbackApiV1ReleasesTargetKindTargetKeyRollbackPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ReleasesApi();

  const body = {
    // PromotionTargetKind
    targetKind: ...,
    // string
    targetKey: targetKey_example,
    // PromotionRollbackRequest
    promotionRollbackRequest: ...,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RollbackApiV1ReleasesTargetKindTargetKeyRollbackPostRequest;

  try {
    const data = await api.rollbackApiV1ReleasesTargetKindTargetKeyRollbackPost(body);
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
| **targetKind** | `PromotionTargetKind` |  | [Defaults to `undefined`] [Enum: WORKFLOW, AGENT] |
| **targetKey** | `string` |  | [Defaults to `undefined`] |
| **promotionRollbackRequest** | PromotionRollbackRequest |  | |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**any**

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


## targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet

> any targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF)

Target History

### Example

```ts
import {
  Configuration,
  ReleasesApi,
} from '@amesh/client';
import type { TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ReleasesApi();

  const body = {
    // PromotionTargetKind
    targetKind: ...,
    // string
    targetKey: targetKey_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGetRequest;

  try {
    const data = await api.targetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet(body);
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
| **targetKind** | `PromotionTargetKind` |  | [Defaults to `undefined`] [Enum: WORKFLOW, AGENT] |
| **targetKey** | `string` |  | [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## targetStateApiV1ReleasesTargetKindTargetKeyGet

> any targetStateApiV1ReleasesTargetKindTargetKeyGet(targetKind, targetKey, xAmeshTenant, authorization, xAmeshCSRF)

Target State

### Example

```ts
import {
  Configuration,
  ReleasesApi,
} from '@amesh/client';
import type { TargetStateApiV1ReleasesTargetKindTargetKeyGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ReleasesApi();

  const body = {
    // PromotionTargetKind
    targetKind: ...,
    // string
    targetKey: targetKey_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies TargetStateApiV1ReleasesTargetKindTargetKeyGetRequest;

  try {
    const data = await api.targetStateApiV1ReleasesTargetKindTargetKeyGet(body);
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
| **targetKind** | `PromotionTargetKind` |  | [Defaults to `undefined`] [Enum: WORKFLOW, AGENT] |
| **targetKey** | `string` |  | [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

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
