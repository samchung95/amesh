# WorkersApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**drainWorkerApiV1WorkersWorkerIdDrainPost**](WorkersApi.md#drainworkerapiv1workersworkeriddrainpost) | **POST** /api/v1/workers/{worker_id}/drain | Drain Worker |
| [**listRunnerCapabilitiesApiV1RunnersCapabilitiesGet**](WorkersApi.md#listrunnercapabilitiesapiv1runnerscapabilitiesget) | **GET** /api/v1/runners/capabilities | List Runner Capabilities |
| [**listWorkersApiV1WorkersGet**](WorkersApi.md#listworkersapiv1workersget) | **GET** /api/v1/workers | List Workers |



## drainWorkerApiV1WorkersWorkerIdDrainPost

> WorkerInventory drainWorkerApiV1WorkersWorkerIdDrainPost(workerId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Drain Worker

### Example

```ts
import {
  Configuration,
  WorkersApi,
} from '@amesh/client';
import type { DrainWorkerApiV1WorkersWorkerIdDrainPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new WorkersApi();

  const body = {
    // string
    workerId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DrainWorkerApiV1WorkersWorkerIdDrainPostRequest;

  try {
    const data = await api.drainWorkerApiV1WorkersWorkerIdDrainPost(body);
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
| **workerId** | `string` |  | [Defaults to `undefined`] |
| **expectedVersion** | `number` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**WorkerInventory**

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


## listRunnerCapabilitiesApiV1RunnersCapabilitiesGet

> Array&lt;RunnerCapabilities&gt; listRunnerCapabilitiesApiV1RunnersCapabilitiesGet(authorization, xAmeshCSRF, xAmeshTenant)

List Runner Capabilities

### Example

```ts
import {
  Configuration,
  WorkersApi,
} from '@amesh/client';
import type { ListRunnerCapabilitiesApiV1RunnersCapabilitiesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new WorkersApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListRunnerCapabilitiesApiV1RunnersCapabilitiesGetRequest;

  try {
    const data = await api.listRunnerCapabilitiesApiV1RunnersCapabilitiesGet(body);
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

**Array&lt;RunnerCapabilities&gt;**

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


## listWorkersApiV1WorkersGet

> Array&lt;WorkerInventory&gt; listWorkersApiV1WorkersGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Workers

### Example

```ts
import {
  Configuration,
  WorkersApi,
} from '@amesh/client';
import type { ListWorkersApiV1WorkersGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new WorkersApi();

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
  } satisfies ListWorkersApiV1WorkersGetRequest;

  try {
    const data = await api.listWorkersApiV1WorkersGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `undefined`] |
| **filter** | `Array<string>` | Repeatable top-level equality filter in field&#x3D;value form | [Optional] |
| **sort** | `string` | Comma-separated top-level fields; prefix descending fields with - | [Optional] [Defaults to `undefined`] |
| **fields** | `string` | Comma-separated top-level response fields | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;WorkerInventory&gt;**

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
