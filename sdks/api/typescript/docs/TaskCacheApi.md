# TaskCacheApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**listTaskCacheEntriesApiV1TaskCacheGet**](TaskCacheApi.md#listtaskcacheentriesapiv1taskcacheget) | **GET** /api/v1/task-cache | List Task Cache Entries |
| [**purgeTaskCacheEntriesApiV1TaskCachePurgePost**](TaskCacheApi.md#purgetaskcacheentriesapiv1taskcachepurgepost) | **POST** /api/v1/task-cache/purge | Purge Task Cache Entries |



## listTaskCacheEntriesApiV1TaskCacheGet

> Array&lt;TaskCacheEntry&gt; listTaskCacheEntriesApiV1TaskCacheGet(keyPrefix, namespace, flowId, taskId, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Task Cache Entries

### Example

```ts
import {
  Configuration,
  TaskCacheApi,
} from '@amesh/client';
import type { ListTaskCacheEntriesApiV1TaskCacheGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TaskCacheApi();

  const body = {
    // string (optional)
    keyPrefix: keyPrefix_example,
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    flowId: flowId_example,
    // string (optional)
    taskId: taskId_example,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListTaskCacheEntriesApiV1TaskCacheGetRequest;

  try {
    const data = await api.listTaskCacheEntriesApiV1TaskCacheGet(body);
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
| **keyPrefix** | `string` |  | [Optional] [Defaults to `undefined`] |
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **flowId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **taskId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;TaskCacheEntry&gt;**](TaskCacheEntry.md)

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


## purgeTaskCacheEntriesApiV1TaskCachePurgePost

> TaskCachePurgeResult purgeTaskCacheEntriesApiV1TaskCachePurgePost(taskCachePurgeRequest, authorization, xAmeshCSRF, xAmeshTenant)

Purge Task Cache Entries

### Example

```ts
import {
  Configuration,
  TaskCacheApi,
} from '@amesh/client';
import type { PurgeTaskCacheEntriesApiV1TaskCachePurgePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TaskCacheApi();

  const body = {
    // TaskCachePurgeRequest
    taskCachePurgeRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PurgeTaskCacheEntriesApiV1TaskCachePurgePostRequest;

  try {
    const data = await api.purgeTaskCacheEntriesApiV1TaskCachePurgePost(body);
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
| **taskCachePurgeRequest** | [TaskCachePurgeRequest](TaskCachePurgeRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TaskCachePurgeResult**](TaskCachePurgeResult.md)

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
