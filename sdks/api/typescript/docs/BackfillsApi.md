# BackfillsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**cancelBackfillApiV1BackfillsBackfillIdCancelPost**](BackfillsApi.md#cancelbackfillapiv1backfillsbackfillidcancelpost) | **POST** /api/v1/backfills/{backfill_id}/cancel | Cancel Backfill |
| [**createBackfillApiV1BackfillsPost**](BackfillsApi.md#createbackfillapiv1backfillspost) | **POST** /api/v1/backfills | Create Backfill |
| [**getBackfillApiV1BackfillsBackfillIdGet**](BackfillsApi.md#getbackfillapiv1backfillsbackfillidget) | **GET** /api/v1/backfills/{backfill_id} | Get Backfill |
| [**listBackfillsApiV1BackfillsGet**](BackfillsApi.md#listbackfillsapiv1backfillsget) | **GET** /api/v1/backfills | List Backfills |
| [**pauseBackfillApiV1BackfillsBackfillIdPausePost**](BackfillsApi.md#pausebackfillapiv1backfillsbackfillidpausepost) | **POST** /api/v1/backfills/{backfill_id}/pause | Pause Backfill |
| [**previewBackfillApiV1BackfillsPreviewPost**](BackfillsApi.md#previewbackfillapiv1backfillspreviewpost) | **POST** /api/v1/backfills/preview | Preview Backfill |
| [**resumeBackfillApiV1BackfillsBackfillIdResumePost**](BackfillsApi.md#resumebackfillapiv1backfillsbackfillidresumepost) | **POST** /api/v1/backfills/{backfill_id}/resume | Resume Backfill |



## cancelBackfillApiV1BackfillsBackfillIdCancelPost

> BackfillRecord cancelBackfillApiV1BackfillsBackfillIdCancelPost(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Cancel Backfill

### Example

```ts
import {
  Configuration,
  BackfillsApi,
} from '@amesh/client';
import type { CancelBackfillApiV1BackfillsBackfillIdCancelPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BackfillsApi();

  const body = {
    // string
    backfillId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // BackfillActionRequest
    backfillActionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CancelBackfillApiV1BackfillsBackfillIdCancelPostRequest;

  try {
    const data = await api.cancelBackfillApiV1BackfillsBackfillIdCancelPost(body);
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
| **backfillId** | `string` |  | [Defaults to `undefined`] |
| **backfillActionRequest** | BackfillActionRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**BackfillRecord**

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


## createBackfillApiV1BackfillsPost

> BackfillRecord createBackfillApiV1BackfillsPost(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant)

Create Backfill

### Example

```ts
import {
  Configuration,
  BackfillsApi,
} from '@amesh/client';
import type { CreateBackfillApiV1BackfillsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BackfillsApi();

  const body = {
    // BackfillSpec
    backfillSpec: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateBackfillApiV1BackfillsPostRequest;

  try {
    const data = await api.createBackfillApiV1BackfillsPost(body);
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
| **backfillSpec** | BackfillSpec |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**BackfillRecord**

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


## getBackfillApiV1BackfillsBackfillIdGet

> BackfillRecord getBackfillApiV1BackfillsBackfillIdGet(backfillId, authorization, xAmeshCSRF, xAmeshTenant)

Get Backfill

### Example

```ts
import {
  Configuration,
  BackfillsApi,
} from '@amesh/client';
import type { GetBackfillApiV1BackfillsBackfillIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BackfillsApi();

  const body = {
    // string
    backfillId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetBackfillApiV1BackfillsBackfillIdGetRequest;

  try {
    const data = await api.getBackfillApiV1BackfillsBackfillIdGet(body);
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
| **backfillId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**BackfillRecord**

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


## listBackfillsApiV1BackfillsGet

> Array&lt;BackfillRecord&gt; listBackfillsApiV1BackfillsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Backfills

### Example

```ts
import {
  Configuration,
  BackfillsApi,
} from '@amesh/client';
import type { ListBackfillsApiV1BackfillsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BackfillsApi();

  const body = {
    // string | Opaque cursor from the prior page (optional)
    cursor: cursor_example,
    // number (optional)
    limit: 56,
    // Array<string> | Repeatable top-level equality filter in field=value form (optional)
    filter: ...,
    // string | Comma-separated top-level fields; prefix descending fields with - (optional)
    sort: sort_example,
    // string | Comma-separated top-level response fields (optional)
    fields: fields_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListBackfillsApiV1BackfillsGetRequest;

  try {
    const data = await api.listBackfillsApiV1BackfillsGet(body);
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
| **cursor** | `string` | Opaque cursor from the prior page | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **filter** | `Array<string>` | Repeatable top-level equality filter in field&#x3D;value form | [Optional] |
| **sort** | `string` | Comma-separated top-level fields; prefix descending fields with - | [Optional] [Defaults to `undefined`] |
| **fields** | `string` | Comma-separated top-level response fields | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;BackfillRecord&gt;**

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


## pauseBackfillApiV1BackfillsBackfillIdPausePost

> BackfillRecord pauseBackfillApiV1BackfillsBackfillIdPausePost(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Pause Backfill

### Example

```ts
import {
  Configuration,
  BackfillsApi,
} from '@amesh/client';
import type { PauseBackfillApiV1BackfillsBackfillIdPausePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BackfillsApi();

  const body = {
    // string
    backfillId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // BackfillActionRequest
    backfillActionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PauseBackfillApiV1BackfillsBackfillIdPausePostRequest;

  try {
    const data = await api.pauseBackfillApiV1BackfillsBackfillIdPausePost(body);
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
| **backfillId** | `string` |  | [Defaults to `undefined`] |
| **backfillActionRequest** | BackfillActionRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**BackfillRecord**

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


## previewBackfillApiV1BackfillsPreviewPost

> BackfillPreview previewBackfillApiV1BackfillsPreviewPost(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant)

Preview Backfill

### Example

```ts
import {
  Configuration,
  BackfillsApi,
} from '@amesh/client';
import type { PreviewBackfillApiV1BackfillsPreviewPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BackfillsApi();

  const body = {
    // BackfillSpec
    backfillSpec: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PreviewBackfillApiV1BackfillsPreviewPostRequest;

  try {
    const data = await api.previewBackfillApiV1BackfillsPreviewPost(body);
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
| **backfillSpec** | BackfillSpec |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**BackfillPreview**

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


## resumeBackfillApiV1BackfillsBackfillIdResumePost

> BackfillRecord resumeBackfillApiV1BackfillsBackfillIdResumePost(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resume Backfill

### Example

```ts
import {
  Configuration,
  BackfillsApi,
} from '@amesh/client';
import type { ResumeBackfillApiV1BackfillsBackfillIdResumePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BackfillsApi();

  const body = {
    // string
    backfillId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // BackfillActionRequest
    backfillActionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ResumeBackfillApiV1BackfillsBackfillIdResumePostRequest;

  try {
    const data = await api.resumeBackfillApiV1BackfillsBackfillIdResumePost(body);
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
| **backfillId** | `string` |  | [Defaults to `undefined`] |
| **backfillActionRequest** | BackfillActionRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**BackfillRecord**

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
