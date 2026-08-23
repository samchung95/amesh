# PoliciesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createAdmissionPolicyApiV1PoliciesPost**](PoliciesApi.md#createadmissionpolicyapiv1policiespost) | **POST** /api/v1/policies | Create Admission Policy |
| [**evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost**](PoliciesApi.md#evaluateadmissionpoliciesapiv1policiesevaluatepost) | **POST** /api/v1/policies/evaluate | Evaluate Admission Policies |
| [**getAdmissionPolicyApiV1PoliciesPolicyKeyGet**](PoliciesApi.md#getadmissionpolicyapiv1policiespolicykeyget) | **GET** /api/v1/policies/{policy_key} | Get Admission Policy |
| [**listAdmissionPoliciesApiV1PoliciesGet**](PoliciesApi.md#listadmissionpoliciesapiv1policiesget) | **GET** /api/v1/policies | List Admission Policies |
| [**listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet**](PoliciesApi.md#listadmissionpolicydecisionsapiv1policiesdecisionsget) | **GET** /api/v1/policies/decisions | List Admission Policy Decisions |
| [**testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost**](PoliciesApi.md#testadmissionpolicyapiv1policiespolicykeytestpost) | **POST** /api/v1/policies/{policy_key}/test | Test Admission Policy |
| [**updateAdmissionPolicyApiV1PoliciesPolicyKeyPut**](PoliciesApi.md#updateadmissionpolicyapiv1policiespolicykeyput) | **PUT** /api/v1/policies/{policy_key} | Update Admission Policy |
| [**validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost**](PoliciesApi.md#validateflowadmissionpolicyapiv1policiesflowsvalidatepost) | **POST** /api/v1/policies/flows/validate | Validate Flow Admission Policy |



## createAdmissionPolicyApiV1PoliciesPost

> PolicyRevision createAdmissionPolicyApiV1PoliciesPost(policyDocument, authorization, xAmeshCSRF, xAmeshTenant)

Create Admission Policy

### Example

```ts
import {
  Configuration,
  PoliciesApi,
} from '@amesh/client';
import type { CreateAdmissionPolicyApiV1PoliciesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PoliciesApi();

  const body = {
    // PolicyDocument
    policyDocument: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateAdmissionPolicyApiV1PoliciesPostRequest;

  try {
    const data = await api.createAdmissionPolicyApiV1PoliciesPost(body);
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
| **policyDocument** | [PolicyDocument](PolicyDocument.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PolicyRevision**](PolicyRevision.md)

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


## evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost

> PolicyDecision evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost(policyEvaluationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Evaluate Admission Policies

### Example

```ts
import {
  Configuration,
  PoliciesApi,
} from '@amesh/client';
import type { EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PoliciesApi();

  const body = {
    // PolicyEvaluationRequest
    policyEvaluationRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePostRequest;

  try {
    const data = await api.evaluateAdmissionPoliciesApiV1PoliciesEvaluatePost(body);
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
| **policyEvaluationRequest** | [PolicyEvaluationRequest](PolicyEvaluationRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PolicyDecision**](PolicyDecision.md)

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


## getAdmissionPolicyApiV1PoliciesPolicyKeyGet

> PolicyRevision getAdmissionPolicyApiV1PoliciesPolicyKeyGet(policyKey, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Admission Policy

### Example

```ts
import {
  Configuration,
  PoliciesApi,
} from '@amesh/client';
import type { GetAdmissionPolicyApiV1PoliciesPolicyKeyGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PoliciesApi();

  const body = {
    // string
    policyKey: policyKey_example,
    // number (optional)
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAdmissionPolicyApiV1PoliciesPolicyKeyGetRequest;

  try {
    const data = await api.getAdmissionPolicyApiV1PoliciesPolicyKeyGet(body);
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
| **policyKey** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PolicyRevision**](PolicyRevision.md)

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


## listAdmissionPoliciesApiV1PoliciesGet

> Array&lt;PolicyRevision&gt; listAdmissionPoliciesApiV1PoliciesGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Admission Policies

### Example

```ts
import {
  Configuration,
  PoliciesApi,
} from '@amesh/client';
import type { ListAdmissionPoliciesApiV1PoliciesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PoliciesApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAdmissionPoliciesApiV1PoliciesGetRequest;

  try {
    const data = await api.listAdmissionPoliciesApiV1PoliciesGet(body);
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
| **namespace** | `string` |  | [Optional] [Defaults to `&#39;default&#39;`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;PolicyRevision&gt;**](PolicyRevision.md)

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


## listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet

> Array&lt;PolicyDecision&gt; listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Admission Policy Decisions

### Example

```ts
import {
  Configuration,
  PoliciesApi,
} from '@amesh/client';
import type { ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PoliciesApi();

  const body = {
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGetRequest;

  try {
    const data = await api.listAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet(body);
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

[**Array&lt;PolicyDecision&gt;**](PolicyDecision.md)

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


## testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost

> PolicyFixtureResult testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost(policyKey, policyFixture, revision, authorization, xAmeshCSRF, xAmeshTenant)

Test Admission Policy

### Example

```ts
import {
  Configuration,
  PoliciesApi,
} from '@amesh/client';
import type { TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PoliciesApi();

  const body = {
    // string
    policyKey: policyKey_example,
    // PolicyFixture
    policyFixture: ...,
    // number (optional)
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPostRequest;

  try {
    const data = await api.testAdmissionPolicyApiV1PoliciesPolicyKeyTestPost(body);
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
| **policyKey** | `string` |  | [Defaults to `undefined`] |
| **policyFixture** | [PolicyFixture](PolicyFixture.md) |  | |
| **revision** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PolicyFixtureResult**](PolicyFixtureResult.md)

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


## updateAdmissionPolicyApiV1PoliciesPolicyKeyPut

> PolicyRevision updateAdmissionPolicyApiV1PoliciesPolicyKeyPut(policyKey, policyDocument, authorization, xAmeshCSRF, xAmeshTenant)

Update Admission Policy

### Example

```ts
import {
  Configuration,
  PoliciesApi,
} from '@amesh/client';
import type { UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PoliciesApi();

  const body = {
    // string
    policyKey: policyKey_example,
    // PolicyDocument
    policyDocument: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPutRequest;

  try {
    const data = await api.updateAdmissionPolicyApiV1PoliciesPolicyKeyPut(body);
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
| **policyKey** | `string` |  | [Defaults to `undefined`] |
| **policyDocument** | [PolicyDocument](PolicyDocument.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PolicyRevision**](PolicyRevision.md)

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


## validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost

> PolicyDecision validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost(authorization, xAmeshCSRF, xAmeshTenant)

Validate Flow Admission Policy

### Example

```ts
import {
  Configuration,
  PoliciesApi,
} from '@amesh/client';
import type { ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PoliciesApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePostRequest;

  try {
    const data = await api.validateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost(body);
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

[**PolicyDecision**](PolicyDecision.md)

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
