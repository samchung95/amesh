# CompatibilityApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost**](CompatibilityApi.md#createkestraexecutionapiv1executionsnamespaceflowidpost) | **POST** /api/v1/executions/{namespace}/{flow_id} | Create Kestra Execution |
| [**getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet**](CompatibilityApi.md#getkestracompatibilitymanifestapiv1compatibilitykestramanifestget) | **GET** /api/v1/compatibility/kestra/manifest | Get Kestra Compatibility Manifest |
| [**validateKestraFlowApiV1MainFlowsValidatePost**](CompatibilityApi.md#validatekestraflowapiv1mainflowsvalidatepost) | **POST** /api/v1/main/flows/validate | Validate Kestra Flow |



## createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost

> ExecutionDetail createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost(namespace, flowId, kestraExecutionRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant)

Create Kestra Execution

### Example

```ts
import {
  Configuration,
  CompatibilityApi,
} from '@amesh/client';
import type { CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new CompatibilityApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // KestraExecutionRequest
    kestraExecutionRequest: ...,
    // string (optional)
    prefer: prefer_example,
    // string (optional)
    idempotencyKey: idempotencyKey_example,
    // string (optional)
    xCorrelationID: xCorrelationID_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateKestraExecutionApiV1ExecutionsNamespaceFlowIdPostRequest;

  try {
    const data = await api.createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost(body);
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
| **kestraExecutionRequest** | [KestraExecutionRequest](KestraExecutionRequest.md) |  | |
| **prefer** | `string` |  | [Optional] [Defaults to `undefined`] |
| **idempotencyKey** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xCorrelationID** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **202** | Execution persisted and accepted for asynchronous processing |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet

> { [key: string]: any | null; } getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet()

Get Kestra Compatibility Manifest

### Example

```ts
import {
  Configuration,
  CompatibilityApi,
} from '@amesh/client';
import type { GetKestraCompatibilityManifestApiV1CompatibilityKestraManifestGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new CompatibilityApi();

  try {
    const data = await api.getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

**{ [key: string]: any | null; }**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## validateKestraFlowApiV1MainFlowsValidatePost

> KestraFlowImport validateKestraFlowApiV1MainFlowsValidatePost()

Validate Kestra Flow

### Example

```ts
import {
  Configuration,
  CompatibilityApi,
} from '@amesh/client';
import type { ValidateKestraFlowApiV1MainFlowsValidatePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new CompatibilityApi();

  try {
    const data = await api.validateKestraFlowApiV1MainFlowsValidatePost();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**KestraFlowImport**](KestraFlowImport.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
