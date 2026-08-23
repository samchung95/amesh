# AppsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getWorkflowAppApiV1AppsNamespaceAppIdGet**](AppsApi.md#getworkflowappapiv1appsnamespaceappidget) | **GET** /api/v1/apps/{namespace}/{app_id} | Get Workflow App |
| [**launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost**](AppsApi.md#launchworkflowappapiv1appsnamespaceappidlaunchpost) | **POST** /api/v1/apps/{namespace}/{app_id}/launch | Launch Workflow App |
| [**listWorkflowAppsApiV1AppsGet**](AppsApi.md#listworkflowappsapiv1appsget) | **GET** /api/v1/apps | List Workflow Apps |
| [**upsertWorkflowAppApiV1AppsNamespaceAppIdPut**](AppsApi.md#upsertworkflowappapiv1appsnamespaceappidput) | **PUT** /api/v1/apps/{namespace}/{app_id} | Upsert Workflow App |



## getWorkflowAppApiV1AppsNamespaceAppIdGet

> WorkflowApp getWorkflowAppApiV1AppsNamespaceAppIdGet(namespace, appId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Workflow App

### Example

```ts
import {
  Configuration,
  AppsApi,
} from '@amesh/client';
import type { GetWorkflowAppApiV1AppsNamespaceAppIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AppsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    appId: appId_example,
    // number (optional)
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetWorkflowAppApiV1AppsNamespaceAppIdGetRequest;

  try {
    const data = await api.getWorkflowAppApiV1AppsNamespaceAppIdGet(body);
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
| **appId** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**WorkflowApp**](WorkflowApp.md)

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


## launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost

> ExecutionDetail launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost(namespace, appId, workflowAppLaunchRequest, authorization, xAmeshCSRF, xAmeshTenant)

Launch Workflow App

### Example

```ts
import {
  Configuration,
  AppsApi,
} from '@amesh/client';
import type { LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AppsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    appId: appId_example,
    // WorkflowAppLaunchRequest
    workflowAppLaunchRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies LaunchWorkflowAppApiV1AppsNamespaceAppIdLaunchPostRequest;

  try {
    const data = await api.launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost(body);
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
| **appId** | `string` |  | [Defaults to `undefined`] |
| **workflowAppLaunchRequest** | [WorkflowAppLaunchRequest](WorkflowAppLaunchRequest.md) |  | |
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
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listWorkflowAppsApiV1AppsGet

> Array&lt;WorkflowApp&gt; listWorkflowAppsApiV1AppsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Workflow Apps

### Example

```ts
import {
  Configuration,
  AppsApi,
} from '@amesh/client';
import type { ListWorkflowAppsApiV1AppsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AppsApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListWorkflowAppsApiV1AppsGetRequest;

  try {
    const data = await api.listWorkflowAppsApiV1AppsGet(body);
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

[**Array&lt;WorkflowApp&gt;**](WorkflowApp.md)

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


## upsertWorkflowAppApiV1AppsNamespaceAppIdPut

> WorkflowApp upsertWorkflowAppApiV1AppsNamespaceAppIdPut(namespace, appId, workflowAppUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Upsert Workflow App

### Example

```ts
import {
  Configuration,
  AppsApi,
} from '@amesh/client';
import type { UpsertWorkflowAppApiV1AppsNamespaceAppIdPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AppsApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    appId: appId_example,
    // WorkflowAppUpsertRequest
    workflowAppUpsertRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies UpsertWorkflowAppApiV1AppsNamespaceAppIdPutRequest;

  try {
    const data = await api.upsertWorkflowAppApiV1AppsNamespaceAppIdPut(body);
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
| **appId** | `string` |  | [Defaults to `undefined`] |
| **workflowAppUpsertRequest** | [WorkflowAppUpsertRequest](WorkflowAppUpsertRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**WorkflowApp**](WorkflowApp.md)

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
