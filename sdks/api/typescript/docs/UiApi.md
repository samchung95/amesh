# UiApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getUiSessionApiV1UiSessionGet**](UiApi.md#getuisessionapiv1uisessionget) | **GET** /api/v1/ui/session | Get Ui Session |



## getUiSessionApiV1UiSessionGet

> UiSessionResponse getUiSessionApiV1UiSessionGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Ui Session

### Example

```ts
import {
  Configuration,
  UiApi,
} from '@amesh/client';
import type { GetUiSessionApiV1UiSessionGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new UiApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetUiSessionApiV1UiSessionGetRequest;

  try {
    const data = await api.getUiSessionApiV1UiSessionGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**UiSessionResponse**](UiSessionResponse.md)

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
