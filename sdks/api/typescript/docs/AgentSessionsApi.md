# AgentSessionsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost**](AgentSessionsApi.md#controlagentsessionapiv1agentsessionsservicesessionidactionpost) | **POST** /api/v1/agent-sessions/{service_session_id}/{action} | Control Agent Session |
| [**createAgentSessionApiV1AgentSessionsPost**](AgentSessionsApi.md#createagentsessionapiv1agentsessionspost) | **POST** /api/v1/agent-sessions | Create Agent Session |
| [**getAgentSessionApiV1AgentSessionsServiceSessionIdGet**](AgentSessionsApi.md#getagentsessionapiv1agentsessionsservicesessionidget) | **GET** /api/v1/agent-sessions/{service_session_id} | Get Agent Session |
| [**getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet**](AgentSessionsApi.md#getagentsessioneventsapiv1agentsessionsservicesessionideventsget) | **GET** /api/v1/agent-sessions/{service_session_id}/events | Get Agent Session Events |
| [**getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet**](AgentSessionsApi.md#getagentsessionmessagesapiv1agentsessionsservicesessionidmessagesget) | **GET** /api/v1/agent-sessions/{service_session_id}/messages | Get Agent Session Messages |
| [**getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet**](AgentSessionsApi.md#getagentsessionresultapiv1agentsessionsservicesessionidresultget) | **GET** /api/v1/agent-sessions/{service_session_id}/result | Get Agent Session Result |
| [**listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet**](AgentSessionsApi.md#listagentsessionharnessesapiv1agentsessionsharnessesget) | **GET** /api/v1/agent-sessions/harnesses | List Agent Session Harnesses |
| [**listAgentSessionsApiV1AgentSessionsGet**](AgentSessionsApi.md#listagentsessionsapiv1agentsessionsget) | **GET** /api/v1/agent-sessions | List Agent Sessions |
| [**openaiChatCompletionsV1ChatCompletionsPost**](AgentSessionsApi.md#openaichatcompletionsv1chatcompletionspost) | **POST** /v1/chat/completions | Openai Chat Completions |
| [**openaiResponsesV1ResponsesPost**](AgentSessionsApi.md#openairesponsesv1responsespost) | **POST** /v1/responses | Openai Responses |
| [**postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost**](AgentSessionsApi.md#postagentsessionmessageapiv1agentsessionsservicesessionidmessagespost) | **POST** /api/v1/agent-sessions/{service_session_id}/messages | Post Agent Session Message |
| [**streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet**](AgentSessionsApi.md#streamagentsessioneventsapiv1agentsessionsservicesessionideventsstreamget) | **GET** /api/v1/agent-sessions/{service_session_id}/events/stream | Stream Agent Session Events |



## controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost

> AgentSessionLaunchResponse controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost(serviceSessionId, action, agentSessionControlRequest, authorization, xAmeshCSRF, xAmeshTenant)

Control Agent Session

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // string
    serviceSessionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // 'cancel' | 'pause' | 'retry' | 'resume'
    action: action_example,
    // AgentSessionControlRequest
    agentSessionControlRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ControlAgentSessionApiV1AgentSessionsServiceSessionIdActionPostRequest;

  try {
    const data = await api.controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost(body);
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
| **serviceSessionId** | `string` |  | [Defaults to `undefined`] |
| **action** | `cancel`, `pause`, `retry`, `resume` |  | [Defaults to `undefined`] [Enum: cancel, pause, retry, resume] |
| **agentSessionControlRequest** | AgentSessionControlRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionLaunchResponse**

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


## createAgentSessionApiV1AgentSessionsPost

> AgentSessionLaunchResponse createAgentSessionApiV1AgentSessionsPost(agentSessionCreateRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant)

Create Agent Session

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { CreateAgentSessionApiV1AgentSessionsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // AgentSessionCreateRequest
    agentSessionCreateRequest: ...,
    // string (optional)
    prefer: prefer_example,
    // string (optional)
    idempotencyKey: idempotencyKey_example,
    // string (optional)
    xCorrelationID: xCorrelationID_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreateAgentSessionApiV1AgentSessionsPostRequest;

  try {
    const data = await api.createAgentSessionApiV1AgentSessionsPost(body);
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
| **agentSessionCreateRequest** | AgentSessionCreateRequest |  | |
| **prefer** | `string` |  | [Optional] [Defaults to `undefined`] |
| **idempotencyKey** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xCorrelationID** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionLaunchResponse**

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


## getAgentSessionApiV1AgentSessionsServiceSessionIdGet

> AgentSessionServiceDetailResponse getAgentSessionApiV1AgentSessionsServiceSessionIdGet(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { GetAgentSessionApiV1AgentSessionsServiceSessionIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // string
    serviceSessionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number (optional)
    afterEventIndex: 56,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAgentSessionApiV1AgentSessionsServiceSessionIdGetRequest;

  try {
    const data = await api.getAgentSessionApiV1AgentSessionsServiceSessionIdGet(body);
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
| **serviceSessionId** | `string` |  | [Defaults to `undefined`] |
| **afterEventIndex** | `number` |  | [Optional] [Defaults to `0`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionServiceDetailResponse**

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


## getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet

> AgentSessionServiceDetailResponse getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Events

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // string
    serviceSessionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number (optional)
    afterEventIndex: 56,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGetRequest;

  try {
    const data = await api.getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet(body);
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
| **serviceSessionId** | `string` |  | [Defaults to `undefined`] |
| **afterEventIndex** | `number` |  | [Optional] [Defaults to `0`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionServiceDetailResponse**

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


## getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet

> AgentSessionServiceDetailResponse getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Messages

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // string
    serviceSessionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number (optional)
    afterEventIndex: 56,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGetRequest;

  try {
    const data = await api.getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet(body);
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
| **serviceSessionId** | `string` |  | [Defaults to `undefined`] |
| **afterEventIndex** | `number` |  | [Optional] [Defaults to `0`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionServiceDetailResponse**

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


## getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet

> AgentSessionResultResponse getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet(serviceSessionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Result

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // string
    serviceSessionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGetRequest;

  try {
    const data = await api.getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet(body);
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
| **serviceSessionId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionResultResponse**

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


## listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet

> { [key: string]: AgentSessionHarnessCatalogEntry; } listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet(authorization, xAmeshCSRF, xAmeshTenant)

List Agent Session Harnesses

Return registered harness provenance without exposing worker details.

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAgentSessionHarnessesApiV1AgentSessionsHarnessesGetRequest;

  try {
    const data = await api.listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet(body);
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

[**{ [key: string]: AgentSessionHarnessCatalogEntry; }**](AgentSessionHarnessCatalogEntry.md)

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


## listAgentSessionsApiV1AgentSessionsGet

> Array&lt;AgentSessionServiceItem&gt; listAgentSessionsApiV1AgentSessionsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Sessions

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { ListAgentSessionsApiV1AgentSessionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAgentSessionsApiV1AgentSessionsGetRequest;

  try {
    const data = await api.listAgentSessionsApiV1AgentSessionsGet(body);
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

**Array&lt;AgentSessionServiceItem&gt;**

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


## openaiChatCompletionsV1ChatCompletionsPost

> OpenAIChatCompletionResponse openaiChatCompletionsV1ChatCompletionsPost(openAIChatCompletionRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant)

Openai Chat Completions

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { OpenaiChatCompletionsV1ChatCompletionsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // OpenAIChatCompletionRequest
    openAIChatCompletionRequest: ...,
    // string (optional)
    idempotencyKey: idempotencyKey_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies OpenaiChatCompletionsV1ChatCompletionsPostRequest;

  try {
    const data = await api.openaiChatCompletionsV1ChatCompletionsPost(body);
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
| **openAIChatCompletionRequest** | OpenAIChatCompletionRequest |  | |
| **idempotencyKey** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**OpenAIChatCompletionResponse**

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


## openaiResponsesV1ResponsesPost

> OpenAIResponse openaiResponsesV1ResponsesPost(openAIResponseRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant)

Openai Responses

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { OpenaiResponsesV1ResponsesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // OpenAIResponseRequest
    openAIResponseRequest: ...,
    // string (optional)
    idempotencyKey: idempotencyKey_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies OpenaiResponsesV1ResponsesPostRequest;

  try {
    const data = await api.openaiResponsesV1ResponsesPost(body);
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
| **openAIResponseRequest** | OpenAIResponseRequest |  | |
| **idempotencyKey** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**OpenAIResponse**

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


## postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost

> postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost(serviceSessionId, authorization, xAmeshCSRF, xAmeshTenant)

Post Agent Session Message

Reject follow-up turns until the durable turn mapping is implemented.

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // string
    serviceSessionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PostAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPostRequest;

  try {
    const data = await api.postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost(body);
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
| **serviceSessionId** | `string` |  | [Defaults to `undefined`] |
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
| **409** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet

> streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet(serviceSessionId, afterEventIndex, authorization, xAmeshCSRF, xAmeshTenant)

Stream Agent Session Events

Stream durable redacted events with a bounded reconnectable poll window.

### Example

```ts
import {
  Configuration,
  AgentSessionsApi,
} from '@amesh/client';
import type { StreamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionsApi();

  const body = {
    // string
    serviceSessionId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number (optional)
    afterEventIndex: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies StreamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGetRequest;

  try {
    const data = await api.streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet(body);
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
| **serviceSessionId** | `string` |  | [Defaults to `undefined`] |
| **afterEventIndex** | `number` |  | [Optional] [Defaults to `0`] |
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
