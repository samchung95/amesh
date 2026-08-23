# DashboardsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteDashboardApiV1DashboardsDashboardIdDelete**](DashboardsApi.md#deletedashboardapiv1dashboardsdashboardiddelete) | **DELETE** /api/v1/dashboards/{dashboard_id} | Delete Dashboard |
| [**executeDashboardQueryApiV1DashboardQueriesPost**](DashboardsApi.md#executedashboardqueryapiv1dashboardqueriespost) | **POST** /api/v1/dashboard-queries | Execute Dashboard Query |
| [**exportDashboardApiV1DashboardsDashboardIdExportGet**](DashboardsApi.md#exportdashboardapiv1dashboardsdashboardidexportget) | **GET** /api/v1/dashboards/{dashboard_id}/export | Export Dashboard |
| [**getDashboardApiV1DashboardsDashboardIdGet**](DashboardsApi.md#getdashboardapiv1dashboardsdashboardidget) | **GET** /api/v1/dashboards/{dashboard_id} | Get Dashboard |
| [**listDashboardsApiV1DashboardsGet**](DashboardsApi.md#listdashboardsapiv1dashboardsget) | **GET** /api/v1/dashboards | List Dashboards |
| [**putDashboardApiV1DashboardsDashboardIdPut**](DashboardsApi.md#putdashboardapiv1dashboardsdashboardidput) | **PUT** /api/v1/dashboards/{dashboard_id} | Put Dashboard |
| [**renderDashboardApiV1DashboardsDashboardIdRenderPost**](DashboardsApi.md#renderdashboardapiv1dashboardsdashboardidrenderpost) | **POST** /api/v1/dashboards/{dashboard_id}/render | Render Dashboard |



## deleteDashboardApiV1DashboardsDashboardIdDelete

> deleteDashboardApiV1DashboardsDashboardIdDelete(dashboardId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Delete Dashboard

### Example

```ts
import {
  Configuration,
  DashboardsApi,
} from '@amesh/client';
import type { DeleteDashboardApiV1DashboardsDashboardIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new DashboardsApi();

  const body = {
    // string
    dashboardId: dashboardId_example,
    // number
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeleteDashboardApiV1DashboardsDashboardIdDeleteRequest;

  try {
    const data = await api.deleteDashboardApiV1DashboardsDashboardIdDelete(body);
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
| **dashboardId** | `string` |  | [Defaults to `undefined`] |
| **expectedVersion** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## executeDashboardQueryApiV1DashboardQueriesPost

> DashboardQueryResult executeDashboardQueryApiV1DashboardQueriesPost(dashboardQuery, authorization, xAmeshCSRF, xAmeshTenant)

Execute Dashboard Query

### Example

```ts
import {
  Configuration,
  DashboardsApi,
} from '@amesh/client';
import type { ExecuteDashboardQueryApiV1DashboardQueriesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new DashboardsApi();

  const body = {
    // DashboardQuery
    dashboardQuery: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExecuteDashboardQueryApiV1DashboardQueriesPostRequest;

  try {
    const data = await api.executeDashboardQueryApiV1DashboardQueriesPost(body);
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
| **dashboardQuery** | [DashboardQuery](DashboardQuery.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**DashboardQueryResult**](DashboardQueryResult.md)

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


## exportDashboardApiV1DashboardsDashboardIdExportGet

> any exportDashboardApiV1DashboardsDashboardIdExportGet(dashboardId, format, authorization, xAmeshCSRF, xAmeshTenant)

Export Dashboard

### Example

```ts
import {
  Configuration,
  DashboardsApi,
} from '@amesh/client';
import type { ExportDashboardApiV1DashboardsDashboardIdExportGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new DashboardsApi();

  const body = {
    // string
    dashboardId: dashboardId_example,
    // 'yaml' | 'json' (optional)
    format: format_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExportDashboardApiV1DashboardsDashboardIdExportGetRequest;

  try {
    const data = await api.exportDashboardApiV1DashboardsDashboardIdExportGet(body);
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
| **dashboardId** | `string` |  | [Defaults to `undefined`] |
| **format** | `yaml`, `json` |  | [Optional] [Defaults to `&#39;yaml&#39;`] [Enum: yaml, json] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

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


## getDashboardApiV1DashboardsDashboardIdGet

> DashboardDefinition getDashboardApiV1DashboardsDashboardIdGet(dashboardId, authorization, xAmeshCSRF, xAmeshTenant)

Get Dashboard

### Example

```ts
import {
  Configuration,
  DashboardsApi,
} from '@amesh/client';
import type { GetDashboardApiV1DashboardsDashboardIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new DashboardsApi();

  const body = {
    // string
    dashboardId: dashboardId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetDashboardApiV1DashboardsDashboardIdGetRequest;

  try {
    const data = await api.getDashboardApiV1DashboardsDashboardIdGet(body);
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
| **dashboardId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**DashboardDefinition**](DashboardDefinition.md)

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


## listDashboardsApiV1DashboardsGet

> Array&lt;DashboardDefinition&gt; listDashboardsApiV1DashboardsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Dashboards

### Example

```ts
import {
  Configuration,
  DashboardsApi,
} from '@amesh/client';
import type { ListDashboardsApiV1DashboardsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new DashboardsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListDashboardsApiV1DashboardsGetRequest;

  try {
    const data = await api.listDashboardsApiV1DashboardsGet(body);
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

[**Array&lt;DashboardDefinition&gt;**](DashboardDefinition.md)

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


## putDashboardApiV1DashboardsDashboardIdPut

> DashboardDefinition putDashboardApiV1DashboardsDashboardIdPut(dashboardId, dashboardSpec, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Put Dashboard

### Example

```ts
import {
  Configuration,
  DashboardsApi,
} from '@amesh/client';
import type { PutDashboardApiV1DashboardsDashboardIdPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new DashboardsApi();

  const body = {
    // string
    dashboardId: dashboardId_example,
    // DashboardSpec
    dashboardSpec: ...,
    // number (optional)
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PutDashboardApiV1DashboardsDashboardIdPutRequest;

  try {
    const data = await api.putDashboardApiV1DashboardsDashboardIdPut(body);
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
| **dashboardId** | `string` |  | [Defaults to `undefined`] |
| **dashboardSpec** | [DashboardSpec](DashboardSpec.md) |  | |
| **expectedVersion** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**DashboardDefinition**](DashboardDefinition.md)

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


## renderDashboardApiV1DashboardsDashboardIdRenderPost

> DashboardRender renderDashboardApiV1DashboardsDashboardIdRenderPost(dashboardId, dashboardFilters, authorization, xAmeshCSRF, xAmeshTenant)

Render Dashboard

### Example

```ts
import {
  Configuration,
  DashboardsApi,
} from '@amesh/client';
import type { RenderDashboardApiV1DashboardsDashboardIdRenderPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new DashboardsApi();

  const body = {
    // string
    dashboardId: dashboardId_example,
    // DashboardFilters
    dashboardFilters: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies RenderDashboardApiV1DashboardsDashboardIdRenderPostRequest;

  try {
    const data = await api.renderDashboardApiV1DashboardsDashboardIdRenderPost(body);
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
| **dashboardId** | `string` |  | [Defaults to `undefined`] |
| **dashboardFilters** | [DashboardFilters](DashboardFilters.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**DashboardRender**](DashboardRender.md)

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
