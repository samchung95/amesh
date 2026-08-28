# TriggersApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**listTriggerOccurrencesApiV1TriggerOccurrencesGet**](TriggersApi.md#listtriggeroccurrencesapiv1triggeroccurrencesget) | **GET** /api/v1/trigger-occurrences | List Trigger Occurrences |
| [**listTriggerRuntimeStatesApiV1TriggersGet**](TriggersApi.md#listtriggerruntimestatesapiv1triggersget) | **GET** /api/v1/triggers | List Trigger Runtime States |
| [**pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost**](TriggersApi.md#pausetriggerruntimeapiv1triggersnamespaceflowidtriggeridpausepost) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/pause | Pause Trigger Runtime |
| [**previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet**](TriggersApi.md#previewscheduleapiv1flowsnamespaceflowidschedulestriggeridpreviewget) | **GET** /api/v1/flows/{namespace}/{flow_id}/schedules/{trigger_id}/preview | Preview Schedule |
| [**replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost**](TriggersApi.md#replaytriggeroccurrenceapiv1triggeroccurrencesoccurrenceidreplaypost) | **POST** /api/v1/trigger-occurrences/{occurrence_id}/replay | Replay Trigger Occurrence |
| [**resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost**](TriggersApi.md#resumetriggerruntimeapiv1triggersnamespaceflowidtriggeridresumepost) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/resume | Resume Trigger Runtime |
| [**triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost**](TriggersApi.md#triggerwebhookapiv1webhooksnamespaceflowidtriggeridpost) | **POST** /api/v1/webhooks/{namespace}/{flow_id}/{trigger_id} | Trigger Webhook |



## listTriggerOccurrencesApiV1TriggerOccurrencesGet

> Array&lt;TriggerOccurrence&gt; listTriggerOccurrencesApiV1TriggerOccurrencesGet(namespace, flowId, triggerId, state, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Trigger Occurrences

### Example

```ts
import {
  Configuration,
  TriggersApi,
} from '@amesh/client';
import type { ListTriggerOccurrencesApiV1TriggerOccurrencesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TriggersApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    flowId: flowId_example,
    // string (optional)
    triggerId: triggerId_example,
    // TriggerOccurrenceState (optional)
    state: ...,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListTriggerOccurrencesApiV1TriggerOccurrencesGetRequest;

  try {
    const data = await api.listTriggerOccurrencesApiV1TriggerOccurrencesGet(body);
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
| **flowId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **triggerId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **state** | `TriggerOccurrenceState` |  | [Optional] [Defaults to `undefined`] [Enum: ACCEPTED, DEFERRED, PROCESSING, RETRY_WAIT, SUCCEEDED, DEAD_LETTERED] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;TriggerOccurrence&gt;**

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


## listTriggerRuntimeStatesApiV1TriggersGet

> Array&lt;TriggerRuntimeState&gt; listTriggerRuntimeStatesApiV1TriggersGet(namespace, flowId, triggerId, active, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Trigger Runtime States

### Example

```ts
import {
  Configuration,
  TriggersApi,
} from '@amesh/client';
import type { ListTriggerRuntimeStatesApiV1TriggersGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TriggersApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    flowId: flowId_example,
    // string (optional)
    triggerId: triggerId_example,
    // boolean (optional)
    active: true,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListTriggerRuntimeStatesApiV1TriggersGetRequest;

  try {
    const data = await api.listTriggerRuntimeStatesApiV1TriggersGet(body);
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
| **flowId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **triggerId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **active** | `boolean` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;TriggerRuntimeState&gt;**

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


## pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost

> TriggerRuntimeState pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Pause Trigger Runtime

### Example

```ts
import {
  Configuration,
  TriggersApi,
} from '@amesh/client';
import type { PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TriggersApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // string
    triggerId: triggerId_example,
    // TriggerActionRequest
    triggerActionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePostRequest;

  try {
    const data = await api.pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost(body);
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
| **triggerId** | `string` |  | [Defaults to `undefined`] |
| **triggerActionRequest** | TriggerActionRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**TriggerRuntimeState**

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


## previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet

> SchedulePreview previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet(namespace, flowId, triggerId, after, count, authorization, xAmeshCSRF, xAmeshTenant)

Preview Schedule

### Example

```ts
import {
  Configuration,
  TriggersApi,
} from '@amesh/client';
import type { PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TriggersApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // string
    triggerId: triggerId_example,
    // Date (optional)
    after: 2013-10-20T19:20:30+01:00,
    // number (optional)
    count: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PreviewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGetRequest;

  try {
    const data = await api.previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet(body);
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
| **triggerId** | `string` |  | [Defaults to `undefined`] |
| **after** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **count** | `number` |  | [Optional] [Defaults to `5`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**SchedulePreview**

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


## replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost

> TriggerOccurrence replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost(occurrenceId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Replay Trigger Occurrence

### Example

```ts
import {
  Configuration,
  TriggersApi,
} from '@amesh/client';
import type { ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TriggersApi();

  const body = {
    // string
    occurrenceId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // TriggerActionRequest
    triggerActionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ReplayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPostRequest;

  try {
    const data = await api.replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost(body);
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
| **occurrenceId** | `string` |  | [Defaults to `undefined`] |
| **triggerActionRequest** | TriggerActionRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**TriggerOccurrence**

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


## resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost

> TriggerRuntimeState resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resume Trigger Runtime

### Example

```ts
import {
  Configuration,
  TriggersApi,
} from '@amesh/client';
import type { ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TriggersApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // string
    triggerId: triggerId_example,
    // TriggerActionRequest
    triggerActionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ResumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePostRequest;

  try {
    const data = await api.resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost(body);
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
| **triggerId** | `string` |  | [Defaults to `undefined`] |
| **triggerActionRequest** | TriggerActionRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**TriggerRuntimeState**

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


## triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost

> ExecutionDetail triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost(namespace, flowId, triggerId, runner, prefer, idempotencyKey, xEventId, authorization, xAmeshCSRF, xAmeshTenant)

Trigger Webhook

### Example

```ts
import {
  Configuration,
  TriggersApi,
} from '@amesh/client';
import type { TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TriggersApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    flowId: flowId_example,
    // string
    triggerId: triggerId_example,
    // RunnerMode (optional)
    runner: ...,
    // string (optional)
    prefer: prefer_example,
    // string (optional)
    idempotencyKey: idempotencyKey_example,
    // string (optional)
    xEventId: xEventId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies TriggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPostRequest;

  try {
    const data = await api.triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost(body);
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
| **triggerId** | `string` |  | [Defaults to `undefined`] |
| **runner** | `RunnerMode` |  | [Optional] [Defaults to `undefined`] [Enum: local, docker, kubernetes] |
| **prefer** | `string` |  | [Optional] [Defaults to `undefined`] |
| **idempotencyKey** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xEventId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ExecutionDetail**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **202** | Webhook execution persisted and accepted for asynchronous processing |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
