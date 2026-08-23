# SearchApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getSearchStatusApiV1SearchStatusGet**](SearchApi.md#getsearchstatusapiv1searchstatusget) | **GET** /api/v1/search/status | Get Search Status |
| [**rebuildSearchProjectionApiV1SearchRebuildPost**](SearchApi.md#rebuildsearchprojectionapiv1searchrebuildpost) | **POST** /api/v1/search/rebuild | Rebuild Search Projection |
| [**searchResourcesApiV1SearchPost**](SearchApi.md#searchresourcesapiv1searchpost) | **POST** /api/v1/search | Search Resources |



## getSearchStatusApiV1SearchStatusGet

> SearchProjectionStatus getSearchStatusApiV1SearchStatusGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Search Status

### Example

```ts
import {
  Configuration,
  SearchApi,
} from '@amesh/client';
import type { GetSearchStatusApiV1SearchStatusGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new SearchApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetSearchStatusApiV1SearchStatusGetRequest;

  try {
    const data = await api.getSearchStatusApiV1SearchStatusGet(body);
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

[**SearchProjectionStatus**](SearchProjectionStatus.md)

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


## rebuildSearchProjectionApiV1SearchRebuildPost

> SearchProjectionStatus rebuildSearchProjectionApiV1SearchRebuildPost(searchRebuildRequest, authorization, xAmeshCSRF, xAmeshTenant)

Rebuild Search Projection

### Example

```ts
import {
  Configuration,
  SearchApi,
} from '@amesh/client';
import type { RebuildSearchProjectionApiV1SearchRebuildPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new SearchApi();

  const body = {
    // SearchRebuildRequest
    searchRebuildRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies RebuildSearchProjectionApiV1SearchRebuildPostRequest;

  try {
    const data = await api.rebuildSearchProjectionApiV1SearchRebuildPost(body);
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
| **searchRebuildRequest** | [SearchRebuildRequest](SearchRebuildRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**SearchProjectionStatus**](SearchProjectionStatus.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## searchResourcesApiV1SearchPost

> SearchResponse searchResourcesApiV1SearchPost(searchRequest, authorization, xAmeshCSRF, xAmeshTenant)

Search Resources

### Example

```ts
import {
  Configuration,
  SearchApi,
} from '@amesh/client';
import type { SearchResourcesApiV1SearchPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new SearchApi();

  const body = {
    // SearchRequest
    searchRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies SearchResourcesApiV1SearchPostRequest;

  try {
    const data = await api.searchResourcesApiV1SearchPost(body);
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
| **searchRequest** | [SearchRequest](SearchRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**SearchResponse**](SearchResponse.md)

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
