# HumanTasksApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost**](HumanTasksApi.md#actonhumantaskapiv1humantaskshumantaskidactionspost) | **POST** /api/v1/human-tasks/{human_task_id}/actions | Act On Human Task |
| [**listHumanTaskNotificationsApiV1HumanTaskNotificationsGet**](HumanTasksApi.md#listhumantasknotificationsapiv1humantasknotificationsget) | **GET** /api/v1/human-task-notifications | List Human Task Notifications |
| [**listHumanTasksApiV1HumanTasksGet**](HumanTasksApi.md#listhumantasksapiv1humantasksget) | **GET** /api/v1/human-tasks | List Human Tasks |



## actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost

> HumanTask actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost(humanTaskId, humanTaskActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Act On Human Task

### Example

```ts
import {
  Configuration,
  HumanTasksApi,
} from '@amesh/client';
import type { ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new HumanTasksApi();

  const body = {
    // string
    humanTaskId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // HumanTaskActionRequest
    humanTaskActionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ActOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPostRequest;

  try {
    const data = await api.actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost(body);
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
| **humanTaskId** | `string` |  | [Defaults to `undefined`] |
| **humanTaskActionRequest** | HumanTaskActionRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**HumanTask**

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


## listHumanTaskNotificationsApiV1HumanTaskNotificationsGet

> Array&lt;HumanTaskNotification&gt; listHumanTaskNotificationsApiV1HumanTaskNotificationsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Human Task Notifications

### Example

```ts
import {
  Configuration,
  HumanTasksApi,
} from '@amesh/client';
import type { ListHumanTaskNotificationsApiV1HumanTaskNotificationsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new HumanTasksApi();

  const body = {
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListHumanTaskNotificationsApiV1HumanTaskNotificationsGetRequest;

  try {
    const data = await api.listHumanTaskNotificationsApiV1HumanTaskNotificationsGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;HumanTaskNotification&gt;**

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


## listHumanTasksApiV1HumanTasksGet

> Array&lt;HumanTask&gt; listHumanTasksApiV1HumanTasksGet(namespace, includeClosed, authorization, xAmeshCSRF, xAmeshTenant)

List Human Tasks

### Example

```ts
import {
  Configuration,
  HumanTasksApi,
} from '@amesh/client';
import type { ListHumanTasksApiV1HumanTasksGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new HumanTasksApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // boolean (optional)
    includeClosed: true,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListHumanTasksApiV1HumanTasksGetRequest;

  try {
    const data = await api.listHumanTasksApiV1HumanTasksGet(body);
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
| **includeClosed** | `boolean` |  | [Optional] [Defaults to `false`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;HumanTask&gt;**

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
