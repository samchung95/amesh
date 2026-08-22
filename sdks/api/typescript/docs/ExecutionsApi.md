# ExecutionsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost**](ExecutionsApi.md#applyexecutioncontrolapiv1executionsexecutionidinterventionspost) | **POST** /api/v1/executions/{execution_id}/interventions | Apply Execution Control |
| [**createExecutionApiV1ExecutionsPost**](ExecutionsApi.md#createexecutionapiv1executionspost) | **POST** /api/v1/executions | Create Execution |
| [**createExecutionsBulkApiV1ExecutionsBulkPost**](ExecutionsApi.md#createexecutionsbulkapiv1executionsbulkpost) | **POST** /api/v1/executions/bulk | Create Executions Bulk |
| [**downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet**](ExecutionsApi.md#downloadexecutionfileapiv1executionsexecutionidfilesartifactidget) | **GET** /api/v1/executions/{execution_id}/files/{artifact_id} | Download Execution File |
| [**getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet**](ExecutionsApi.md#getexecutionadmissionapiv1executionsexecutionidadmissionget) | **GET** /api/v1/executions/{execution_id}/admission | Get Execution Admission |
| [**getExecutionApiV1ExecutionsExecutionIdGet**](ExecutionsApi.md#getexecutionapiv1executionsexecutionidget) | **GET** /api/v1/executions/{execution_id} | Get Execution |
| [**getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet**](ExecutionsApi.md#getexecutionevidenceapiv1executionsexecutionidevidenceget) | **GET** /api/v1/executions/{execution_id}/evidence | Get Execution Evidence |
| [**getExecutionGraphApiV1ExecutionsExecutionIdGraphGet**](ExecutionsApi.md#getexecutiongraphapiv1executionsexecutionidgraphget) | **GET** /api/v1/executions/{execution_id}/graph | Get Execution Graph |
| [**getExecutionLogsApiV1ExecutionsExecutionIdLogsGet**](ExecutionsApi.md#getexecutionlogsapiv1executionsexecutionidlogsget) | **GET** /api/v1/executions/{execution_id}/logs | Get Execution Logs |
| [**getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet**](ExecutionsApi.md#getexecutionparentsubflowapiv1executionsexecutionidparentsubflowget) | **GET** /api/v1/executions/{execution_id}/parent-subflow | Get Execution Parent Subflow |
| [**getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet**](ExecutionsApi.md#gettaskadmissionapiv1taskrunstaskrunidadmissionget) | **GET** /api/v1/task-runs/{task_run_id}/admission | Get Task Admission |
| [**listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet**](ExecutionsApi.md#listexecutioncontrolhistoryapiv1executionsexecutionidinterventionsget) | **GET** /api/v1/executions/{execution_id}/interventions | List Execution Control History |
| [**listExecutionFilesApiV1ExecutionsExecutionIdFilesGet**](ExecutionsApi.md#listexecutionfilesapiv1executionsexecutionidfilesget) | **GET** /api/v1/executions/{execution_id}/files | List Execution Files |
| [**listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet**](ExecutionsApi.md#listexecutionsubflowsapiv1executionsexecutionidsubflowsget) | **GET** /api/v1/executions/{execution_id}/subflows | List Execution Subflows |
| [**listExecutionsApiV1ExecutionsGet**](ExecutionsApi.md#listexecutionsapiv1executionsget) | **GET** /api/v1/executions | List Executions |
| [**previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost**](ExecutionsApi.md#previewexecutioncontrolapiv1executionsexecutionidinterventionspreviewpost) | **POST** /api/v1/executions/{execution_id}/interventions/preview | Preview Execution Control |
| [**reduceExecutionEventsApiV1ExecutionsReducePost**](ExecutionsApi.md#reduceexecutioneventsapiv1executionsreducepost) | **POST** /api/v1/executions/reduce | Reduce Execution Events |
| [**resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost**](ExecutionsApi.md#resumetaskrunapiv1executionsexecutionidtaskrunstaskrunidresumepost) | **POST** /api/v1/executions/{execution_id}/task-runs/{task_run_id}/resume | Resume Task Run |
| [**streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet**](ExecutionsApi.md#streamexecutionevidenceapiv1executionsexecutionidevidencestreamget) | **GET** /api/v1/executions/{execution_id}/evidence/stream | Stream Execution Evidence |
| [**streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet**](ExecutionsApi.md#streamexecutionlogsapiv1executionsexecutionidlogsstreamget) | **GET** /api/v1/executions/{execution_id}/logs/stream | Stream Execution Logs |



## applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost

> ExecutionDetail applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost(executionId, executionInterventionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Apply Execution Control

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // ExecutionInterventionRequest
    executionInterventionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPostRequest;

  try {
    const data = await api.applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **executionInterventionRequest** | [ExecutionInterventionRequest](ExecutionInterventionRequest.md) |  | |
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


## createExecutionApiV1ExecutionsPost

> ExecutionDetail createExecutionApiV1ExecutionsPost(createExecutionRequest, prefer, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant)

Create Execution

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { CreateExecutionApiV1ExecutionsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // CreateExecutionRequest
    createExecutionRequest: ...,
    // string (optional)
    prefer: prefer_example,
    // string (optional)
    idempotencyKey: idempotencyKey_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateExecutionApiV1ExecutionsPostRequest;

  try {
    const data = await api.createExecutionApiV1ExecutionsPost(body);
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
| **createExecutionRequest** | [CreateExecutionRequest](CreateExecutionRequest.md) |  | |
| **prefer** | `string` |  | [Optional] [Defaults to `undefined`] |
| **idempotencyKey** | `string` |  | [Optional] [Defaults to `undefined`] |
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
| **202** | Execution persisted and accepted for asynchronous processing |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createExecutionsBulkApiV1ExecutionsBulkPost

> Array&lt;BulkExecutionItemResult&gt; createExecutionsBulkApiV1ExecutionsBulkPost(bulkExecutionRequest, prefer, authorization, xAmeshCSRF, xAmeshTenant)

Create Executions Bulk

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { CreateExecutionsBulkApiV1ExecutionsBulkPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // BulkExecutionRequest
    bulkExecutionRequest: ...,
    // string (optional)
    prefer: prefer_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateExecutionsBulkApiV1ExecutionsBulkPostRequest;

  try {
    const data = await api.createExecutionsBulkApiV1ExecutionsBulkPost(body);
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
| **bulkExecutionRequest** | [BulkExecutionRequest](BulkExecutionRequest.md) |  | |
| **prefer** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;BulkExecutionItemResult&gt;**](BulkExecutionItemResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **207** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet

> downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet(executionId, artifactId, authorization, xAmeshCSRF, xAmeshTenant)

Download Execution File

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { DownloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string
    artifactId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DownloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGetRequest;

  try {
    const data = await api.downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **artifactId** | `string` |  | [Defaults to `undefined`] |
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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet

> AdmissionDecision getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Admission

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGetRequest;

  try {
    const data = await api.getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AdmissionDecision**](AdmissionDecision.md)

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


## getExecutionApiV1ExecutionsExecutionIdGet

> ExecutionDetail getExecutionApiV1ExecutionsExecutionIdGet(executionId, taskOffset, taskLimit, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { GetExecutionApiV1ExecutionsExecutionIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number (optional)
    taskOffset: 56,
    // number (optional)
    taskLimit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetExecutionApiV1ExecutionsExecutionIdGetRequest;

  try {
    const data = await api.getExecutionApiV1ExecutionsExecutionIdGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **taskOffset** | `number` |  | [Optional] [Defaults to `0`] |
| **taskLimit** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

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


## getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet

> ExecutionEvidencePage getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet(executionId, cursor, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Evidence

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string | Opaque reconnect cursor (optional)
    cursor: cursor_example,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGetRequest;

  try {
    const data = await api.getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **cursor** | `string` | Opaque reconnect cursor | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `500`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ExecutionEvidencePage**](ExecutionEvidencePage.md)

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


## getExecutionGraphApiV1ExecutionsExecutionIdGraphGet

> FlowGraph getExecutionGraphApiV1ExecutionsExecutionIdGraphGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Graph

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { GetExecutionGraphApiV1ExecutionsExecutionIdGraphGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetExecutionGraphApiV1ExecutionsExecutionIdGraphGetRequest;

  try {
    const data = await api.getExecutionGraphApiV1ExecutionsExecutionIdGraphGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**FlowGraph**](FlowGraph.md)

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


## getExecutionLogsApiV1ExecutionsExecutionIdLogsGet

> Array&lt;TaskLog&gt; getExecutionLogsApiV1ExecutionsExecutionIdLogsGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Logs

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { GetExecutionLogsApiV1ExecutionsExecutionIdLogsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetExecutionLogsApiV1ExecutionsExecutionIdLogsGetRequest;

  try {
    const data = await api.getExecutionLogsApiV1ExecutionsExecutionIdLogsGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;TaskLog&gt;**](TaskLog.md)

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


## getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet

> PersistedSubflow getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Parent Subflow

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGetRequest;

  try {
    const data = await api.getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PersistedSubflow**](PersistedSubflow.md)

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


## getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet

> AdmissionDecision getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet(taskRunId, authorization, xAmeshCSRF, xAmeshTenant)

Get Task Admission

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    taskRunId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGetRequest;

  try {
    const data = await api.getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet(body);
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
| **taskRunId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AdmissionDecision**](AdmissionDecision.md)

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


## listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet

> Array&lt;ExecutionInterventionRecord&gt; listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

List Execution Control History

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGetRequest;

  try {
    const data = await api.listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;ExecutionInterventionRecord&gt;**](ExecutionInterventionRecord.md)

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


## listExecutionFilesApiV1ExecutionsExecutionIdFilesGet

> Array&lt;ExecutionArtifact&gt; listExecutionFilesApiV1ExecutionsExecutionIdFilesGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

List Execution Files

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { ListExecutionFilesApiV1ExecutionsExecutionIdFilesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListExecutionFilesApiV1ExecutionsExecutionIdFilesGetRequest;

  try {
    const data = await api.listExecutionFilesApiV1ExecutionsExecutionIdFilesGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;ExecutionArtifact&gt;**](ExecutionArtifact.md)

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


## listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet

> Array&lt;PersistedSubflow&gt; listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

List Execution Subflows

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGetRequest;

  try {
    const data = await api.listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;PersistedSubflow&gt;**](PersistedSubflow.md)

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


## listExecutionsApiV1ExecutionsGet

> Array&lt;PersistedExecution&gt; listExecutionsApiV1ExecutionsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Executions

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { ListExecutionsApiV1ExecutionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

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
  } satisfies ListExecutionsApiV1ExecutionsGetRequest;

  try {
    const data = await api.listExecutionsApiV1ExecutionsGet(body);
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

[**Array&lt;PersistedExecution&gt;**](PersistedExecution.md)

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


## previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost

> ExecutionInterventionPreview previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost(executionId, executionInterventionPreviewRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Execution Control

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // ExecutionInterventionPreviewRequest
    executionInterventionPreviewRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPostRequest;

  try {
    const data = await api.previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **executionInterventionPreviewRequest** | [ExecutionInterventionPreviewRequest](ExecutionInterventionPreviewRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ExecutionInterventionPreview**](ExecutionInterventionPreview.md)

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


## reduceExecutionEventsApiV1ExecutionsReducePost

> ReduceExecutionResponse reduceExecutionEventsApiV1ExecutionsReducePost(reduceExecutionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Reduce Execution Events

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { ReduceExecutionEventsApiV1ExecutionsReducePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // ReduceExecutionRequest
    reduceExecutionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ReduceExecutionEventsApiV1ExecutionsReducePostRequest;

  try {
    const data = await api.reduceExecutionEventsApiV1ExecutionsReducePost(body);
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
| **reduceExecutionRequest** | [ReduceExecutionRequest](ReduceExecutionRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ReduceExecutionResponse**](ReduceExecutionResponse.md)

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


## resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost

> PersistedTaskRun resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost(executionId, taskRunId, resumeTaskRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resume Task Run

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string
    taskRunId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // ResumeTaskRequest
    resumeTaskRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePostRequest;

  try {
    const data = await api.resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **taskRunId** | `string` |  | [Defaults to `undefined`] |
| **resumeTaskRequest** | [ResumeTaskRequest](ResumeTaskRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PersistedTaskRun**](PersistedTaskRun.md)

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


## streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet

> streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet(executionId, cursor, authorization, xAmeshCSRF, xAmeshTenant)

Stream Execution Evidence

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { StreamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string | Opaque reconnect cursor (optional)
    cursor: cursor_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies StreamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGetRequest;

  try {
    const data = await api.streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **cursor** | `string` | Opaque reconnect cursor | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/x-ndjson`, `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Evidence events streamed as newline-delimited JSON |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet

> streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Stream Execution Logs

### Example

```ts
import {
  Configuration,
  ExecutionsApi,
} from '@amesh/client';
import type { StreamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ExecutionsApi();

  const body = {
    // string
    executionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies StreamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGetRequest;

  try {
    const data = await api.streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet(body);
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
| **executionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/x-ndjson`, `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Task logs streamed as newline-delimited JSON |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
