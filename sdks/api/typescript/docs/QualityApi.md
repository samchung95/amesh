# QualityApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet**](QualityApi.md#getdifferentialapiv1namespacesnamespacedifferentialsidempotencykeyget) | **GET** /api/v1/namespaces/{namespace}/differentials/{idempotency_key} | Get Differential |
| [**runDifferentialApiV1NamespacesNamespaceDifferentialsPost**](QualityApi.md#rundifferentialapiv1namespacesnamespacedifferentialspost) | **POST** /api/v1/namespaces/{namespace}/differentials | Run Differential |



## getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet

> ComparisonReport getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet(namespace, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF)

Get Differential

### Example

```ts
import {
  Configuration,
  QualityApi,
} from '@amesh/client';
import type { GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new QualityApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    idempotencyKey: idempotencyKey_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGetRequest;

  try {
    const data = await api.getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet(body);
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
| **idempotencyKey** | `string` |  | [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ComparisonReport**

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


## runDifferentialApiV1NamespacesNamespaceDifferentialsPost

> ComparisonReport runDifferentialApiV1NamespacesNamespaceDifferentialsPost(namespace, differentialSpec, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF)

Run Differential

### Example

```ts
import {
  Configuration,
  QualityApi,
} from '@amesh/client';
import type { RunDifferentialApiV1NamespacesNamespaceDifferentialsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new QualityApi();

  const body = {
    // string
    namespace: namespace_example,
    // DifferentialSpec
    differentialSpec: ...,
    // string (optional)
    idempotencyKey: idempotencyKey_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RunDifferentialApiV1NamespacesNamespaceDifferentialsPostRequest;

  try {
    const data = await api.runDifferentialApiV1NamespacesNamespaceDifferentialsPost(body);
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
| **differentialSpec** | DifferentialSpec |  | |
| **idempotencyKey** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ComparisonReport**

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
