# ExternalOrchestrationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getExternalOrchestrationProfileApiV1OrchestrationProfileGet**](ExternalOrchestrationApi.md#getexternalorchestrationprofileapiv1orchestrationprofileget) | **GET** /api/v1/orchestration/profile | Get External Orchestration Profile |



## getExternalOrchestrationProfileApiV1OrchestrationProfileGet

> ExternalOrchestrationProfile getExternalOrchestrationProfileApiV1OrchestrationProfileGet()

Get External Orchestration Profile

Publish the client-neutral contract without exposing tenant data.

### Example

```ts
import {
  Configuration,
  ExternalOrchestrationApi,
} from '@amesh/client';
import type { GetExternalOrchestrationProfileApiV1OrchestrationProfileGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExternalOrchestrationApi();

  try {
    const data = await api.getExternalOrchestrationProfileApiV1OrchestrationProfileGet();
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

[**ExternalOrchestrationProfile**](ExternalOrchestrationProfile.md)

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
