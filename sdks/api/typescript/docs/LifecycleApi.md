# LifecycleApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost**](LifecycleApi.md#createlifecyclelegalholdapiv1lifecyclelegalholdspost) | **POST** /api/v1/lifecycle/legal-holds | Create Lifecycle Legal Hold |
| [**createLifecyclePolicyApiV1LifecyclePoliciesPost**](LifecycleApi.md#createlifecyclepolicyapiv1lifecyclepoliciespost) | **POST** /api/v1/lifecycle/policies | Create Lifecycle Policy |
| [**executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost**](LifecycleApi.md#executelifecyclejobapiv1lifecyclejobsjobidexecutepost) | **POST** /api/v1/lifecycle/jobs/{job_id}/execute | Execute Lifecycle Job |
| [**getLifecycleJobApiV1LifecycleJobsJobIdGet**](LifecycleApi.md#getlifecyclejobapiv1lifecyclejobsjobidget) | **GET** /api/v1/lifecycle/jobs/{job_id} | Get Lifecycle Job |
| [**listLifecycleJobsApiV1LifecycleJobsGet**](LifecycleApi.md#listlifecyclejobsapiv1lifecyclejobsget) | **GET** /api/v1/lifecycle/jobs | List Lifecycle Jobs |
| [**listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet**](LifecycleApi.md#listlifecyclelegalholdsapiv1lifecyclelegalholdsget) | **GET** /api/v1/lifecycle/legal-holds | List Lifecycle Legal Holds |
| [**listLifecyclePoliciesApiV1LifecyclePoliciesGet**](LifecycleApi.md#listlifecyclepoliciesapiv1lifecyclepoliciesget) | **GET** /api/v1/lifecycle/policies | List Lifecycle Policies |
| [**previewLifecyclePurgeApiV1LifecyclePreviewsPost**](LifecycleApi.md#previewlifecyclepurgeapiv1lifecyclepreviewspost) | **POST** /api/v1/lifecycle/previews | Preview Lifecycle Purge |
| [**releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost**](LifecycleApi.md#releaselifecyclelegalholdapiv1lifecyclelegalholdsholdidreleasepost) | **POST** /api/v1/lifecycle/legal-holds/{hold_id}/release | Release Lifecycle Legal Hold |
| [**resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost**](LifecycleApi.md#resumelifecyclejobapiv1lifecyclejobsjobidresumepost) | **POST** /api/v1/lifecycle/jobs/{job_id}/resume | Resume Lifecycle Job |
| [**updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut**](LifecycleApi.md#updatelifecyclepolicyapiv1lifecyclepoliciespolicyidput) | **PUT** /api/v1/lifecycle/policies/{policy_id} | Update Lifecycle Policy |



## createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost

> LifecycleLegalHold createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost(lifecycleLegalHoldDraft, authorization, xAmeshCSRF, xAmeshTenant)

Create Lifecycle Legal Hold

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // LifecycleLegalHoldDraft
    lifecycleLegalHoldDraft: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPostRequest;

  try {
    const data = await api.createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost(body);
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
| **lifecycleLegalHoldDraft** | [LifecycleLegalHoldDraft](LifecycleLegalHoldDraft.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**LifecycleLegalHold**](LifecycleLegalHold.md)

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


## createLifecyclePolicyApiV1LifecyclePoliciesPost

> LifecyclePolicy createLifecyclePolicyApiV1LifecyclePoliciesPost(lifecyclePolicyDraft, authorization, xAmeshCSRF, xAmeshTenant)

Create Lifecycle Policy

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { CreateLifecyclePolicyApiV1LifecyclePoliciesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // LifecyclePolicyDraft
    lifecyclePolicyDraft: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateLifecyclePolicyApiV1LifecyclePoliciesPostRequest;

  try {
    const data = await api.createLifecyclePolicyApiV1LifecyclePoliciesPost(body);
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
| **lifecyclePolicyDraft** | [LifecyclePolicyDraft](LifecyclePolicyDraft.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**LifecyclePolicy**](LifecyclePolicy.md)

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


## executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost

> LifecycleJob executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost(jobId, lifecycleExecuteRequest, authorization, xAmeshCSRF, xAmeshTenant)

Execute Lifecycle Job

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // string
    jobId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // LifecycleExecuteRequest
    lifecycleExecuteRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePostRequest;

  try {
    const data = await api.executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost(body);
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
| **jobId** | `string` |  | [Defaults to `undefined`] |
| **lifecycleExecuteRequest** | [LifecycleExecuteRequest](LifecycleExecuteRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**LifecycleJob**](LifecycleJob.md)

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


## getLifecycleJobApiV1LifecycleJobsJobIdGet

> LifecycleJob getLifecycleJobApiV1LifecycleJobsJobIdGet(jobId, authorization, xAmeshCSRF, xAmeshTenant)

Get Lifecycle Job

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { GetLifecycleJobApiV1LifecycleJobsJobIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // string
    jobId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetLifecycleJobApiV1LifecycleJobsJobIdGetRequest;

  try {
    const data = await api.getLifecycleJobApiV1LifecycleJobsJobIdGet(body);
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
| **jobId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**LifecycleJob**](LifecycleJob.md)

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


## listLifecycleJobsApiV1LifecycleJobsGet

> Array&lt;LifecycleJob&gt; listLifecycleJobsApiV1LifecycleJobsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Lifecycle Jobs

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { ListLifecycleJobsApiV1LifecycleJobsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListLifecycleJobsApiV1LifecycleJobsGetRequest;

  try {
    const data = await api.listLifecycleJobsApiV1LifecycleJobsGet(body);
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

[**Array&lt;LifecycleJob&gt;**](LifecycleJob.md)

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


## listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet

> Array&lt;LifecycleLegalHold&gt; listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Lifecycle Legal Holds

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGetRequest;

  try {
    const data = await api.listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet(body);
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

[**Array&lt;LifecycleLegalHold&gt;**](LifecycleLegalHold.md)

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


## listLifecyclePoliciesApiV1LifecyclePoliciesGet

> Array&lt;LifecyclePolicy&gt; listLifecyclePoliciesApiV1LifecyclePoliciesGet(authorization, xAmeshCSRF, xAmeshTenant)

List Lifecycle Policies

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { ListLifecyclePoliciesApiV1LifecyclePoliciesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListLifecyclePoliciesApiV1LifecyclePoliciesGetRequest;

  try {
    const data = await api.listLifecyclePoliciesApiV1LifecyclePoliciesGet(body);
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

[**Array&lt;LifecyclePolicy&gt;**](LifecyclePolicy.md)

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


## previewLifecyclePurgeApiV1LifecyclePreviewsPost

> LifecycleJob previewLifecyclePurgeApiV1LifecyclePreviewsPost(lifecyclePreviewRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Lifecycle Purge

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { PreviewLifecyclePurgeApiV1LifecyclePreviewsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // LifecyclePreviewRequest
    lifecyclePreviewRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PreviewLifecyclePurgeApiV1LifecyclePreviewsPostRequest;

  try {
    const data = await api.previewLifecyclePurgeApiV1LifecyclePreviewsPost(body);
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
| **lifecyclePreviewRequest** | [LifecyclePreviewRequest](LifecyclePreviewRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**LifecycleJob**](LifecycleJob.md)

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


## releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost

> LifecycleLegalHold releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost(holdId, authorization, xAmeshCSRF, xAmeshTenant)

Release Lifecycle Legal Hold

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // string
    holdId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePostRequest;

  try {
    const data = await api.releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost(body);
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

[**LifecycleLegalHold**](LifecycleLegalHold.md)

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


## resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost

> LifecycleJob resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost(jobId, authorization, xAmeshCSRF, xAmeshTenant)

Resume Lifecycle Job

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // string
    jobId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePostRequest;

  try {
    const data = await api.resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost(body);
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
| **jobId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**LifecycleJob**](LifecycleJob.md)

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


## updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut

> LifecyclePolicy updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut(policyId, lifecyclePolicyDraft, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Update Lifecycle Policy

### Example

```ts
import {
  Configuration,
  LifecycleApi,
} from '@amesh/client';
import type { UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new LifecycleApi();

  const body = {
    // string
    policyId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // LifecyclePolicyDraft
    lifecyclePolicyDraft: ...,
    // number (optional)
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPutRequest;

  try {
    const data = await api.updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut(body);
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
| **lifecyclePolicyDraft** | [LifecyclePolicyDraft](LifecyclePolicyDraft.md) |  | |
| **expectedVersion** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**LifecyclePolicy**](LifecyclePolicy.md)

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
