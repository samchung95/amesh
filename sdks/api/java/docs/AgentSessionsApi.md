# AgentSessionsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost**](AgentSessionsApi.md#controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost) | **POST** /api/v1/agent-sessions/{service_session_id}/{action} | Control Agent Session |
| [**controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPostWithHttpInfo**](AgentSessionsApi.md#controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPostWithHttpInfo) | **POST** /api/v1/agent-sessions/{service_session_id}/{action} | Control Agent Session |
| [**createAgentSessionApiV1AgentSessionsPost**](AgentSessionsApi.md#createAgentSessionApiV1AgentSessionsPost) | **POST** /api/v1/agent-sessions | Create Agent Session |
| [**createAgentSessionApiV1AgentSessionsPostWithHttpInfo**](AgentSessionsApi.md#createAgentSessionApiV1AgentSessionsPostWithHttpInfo) | **POST** /api/v1/agent-sessions | Create Agent Session |
| [**getAgentSessionApiV1AgentSessionsServiceSessionIdGet**](AgentSessionsApi.md#getAgentSessionApiV1AgentSessionsServiceSessionIdGet) | **GET** /api/v1/agent-sessions/{service_session_id} | Get Agent Session |
| [**getAgentSessionApiV1AgentSessionsServiceSessionIdGetWithHttpInfo**](AgentSessionsApi.md#getAgentSessionApiV1AgentSessionsServiceSessionIdGetWithHttpInfo) | **GET** /api/v1/agent-sessions/{service_session_id} | Get Agent Session |
| [**getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet**](AgentSessionsApi.md#getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet) | **GET** /api/v1/agent-sessions/{service_session_id}/events | Get Agent Session Events |
| [**getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGetWithHttpInfo**](AgentSessionsApi.md#getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGetWithHttpInfo) | **GET** /api/v1/agent-sessions/{service_session_id}/events | Get Agent Session Events |
| [**getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet**](AgentSessionsApi.md#getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet) | **GET** /api/v1/agent-sessions/{service_session_id}/messages | Get Agent Session Messages |
| [**getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGetWithHttpInfo**](AgentSessionsApi.md#getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGetWithHttpInfo) | **GET** /api/v1/agent-sessions/{service_session_id}/messages | Get Agent Session Messages |
| [**getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet**](AgentSessionsApi.md#getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet) | **GET** /api/v1/agent-sessions/{service_session_id}/progress | Get Agent Session Progress |
| [**getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGetWithHttpInfo**](AgentSessionsApi.md#getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGetWithHttpInfo) | **GET** /api/v1/agent-sessions/{service_session_id}/progress | Get Agent Session Progress |
| [**getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet**](AgentSessionsApi.md#getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet) | **GET** /api/v1/agent-sessions/{service_session_id}/result | Get Agent Session Result |
| [**getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGetWithHttpInfo**](AgentSessionsApi.md#getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGetWithHttpInfo) | **GET** /api/v1/agent-sessions/{service_session_id}/result | Get Agent Session Result |
| [**listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet**](AgentSessionsApi.md#listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet) | **GET** /api/v1/agent-sessions/harnesses | List Agent Session Harnesses |
| [**listAgentSessionHarnessesApiV1AgentSessionsHarnessesGetWithHttpInfo**](AgentSessionsApi.md#listAgentSessionHarnessesApiV1AgentSessionsHarnessesGetWithHttpInfo) | **GET** /api/v1/agent-sessions/harnesses | List Agent Session Harnesses |
| [**listAgentSessionsApiV1AgentSessionsGet**](AgentSessionsApi.md#listAgentSessionsApiV1AgentSessionsGet) | **GET** /api/v1/agent-sessions | List Agent Sessions |
| [**listAgentSessionsApiV1AgentSessionsGetWithHttpInfo**](AgentSessionsApi.md#listAgentSessionsApiV1AgentSessionsGetWithHttpInfo) | **GET** /api/v1/agent-sessions | List Agent Sessions |
| [**openaiChatCompletionsV1ChatCompletionsPost**](AgentSessionsApi.md#openaiChatCompletionsV1ChatCompletionsPost) | **POST** /v1/chat/completions | Openai Chat Completions |
| [**openaiChatCompletionsV1ChatCompletionsPostWithHttpInfo**](AgentSessionsApi.md#openaiChatCompletionsV1ChatCompletionsPostWithHttpInfo) | **POST** /v1/chat/completions | Openai Chat Completions |
| [**openaiResponsesV1ResponsesPost**](AgentSessionsApi.md#openaiResponsesV1ResponsesPost) | **POST** /v1/responses | Openai Responses |
| [**openaiResponsesV1ResponsesPostWithHttpInfo**](AgentSessionsApi.md#openaiResponsesV1ResponsesPostWithHttpInfo) | **POST** /v1/responses | Openai Responses |
| [**postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost**](AgentSessionsApi.md#postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost) | **POST** /api/v1/agent-sessions/{service_session_id}/messages | Post Agent Session Message |
| [**postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPostWithHttpInfo**](AgentSessionsApi.md#postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPostWithHttpInfo) | **POST** /api/v1/agent-sessions/{service_session_id}/messages | Post Agent Session Message |
| [**streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet**](AgentSessionsApi.md#streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet) | **GET** /api/v1/agent-sessions/{service_session_id}/events/stream | Stream Agent Session Events |
| [**streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGetWithHttpInfo**](AgentSessionsApi.md#streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGetWithHttpInfo) | **GET** /api/v1/agent-sessions/{service_session_id}/events/stream | Stream Agent Session Events |
| [**streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet**](AgentSessionsApi.md#streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet) | **GET** /api/v1/agent-sessions/{service_session_id}/progress/stream | Stream Agent Session Progress |
| [**streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGetWithHttpInfo**](AgentSessionsApi.md#streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGetWithHttpInfo) | **GET** /api/v1/agent-sessions/{service_session_id}/progress/stream | Stream Agent Session Progress |



## controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost

> AgentSessionLaunchResponse controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost(serviceSessionId, action, agentSessionControlRequest, authorization, xAmeshCSRF, xAmeshTenant)

Control Agent Session

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        String action = "cancel"; // String |
        AgentSessionControlRequest agentSessionControlRequest = new AgentSessionControlRequest(); // AgentSessionControlRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionLaunchResponse result = apiInstance.controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost(serviceSessionId, action, agentSessionControlRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **action** | **String**|  | [enum: cancel, pause, retry, resume] |
| **agentSessionControlRequest** | **AgentSessionControlRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionLaunchResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPostWithHttpInfo

> ApiResponse<AgentSessionLaunchResponse> controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPostWithHttpInfo(serviceSessionId, action, agentSessionControlRequest, authorization, xAmeshCSRF, xAmeshTenant)

Control Agent Session

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        String action = "cancel"; // String |
        AgentSessionControlRequest agentSessionControlRequest = new AgentSessionControlRequest(); // AgentSessionControlRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionLaunchResponse> response = apiInstance.controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPostWithHttpInfo(serviceSessionId, action, agentSessionControlRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#controlAgentSessionApiV1AgentSessionsServiceSessionIdActionPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **action** | **String**|  | [enum: cancel, pause, retry, resume] |
| **agentSessionControlRequest** | **AgentSessionControlRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionLaunchResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## createAgentSessionApiV1AgentSessionsPost

> AgentSessionLaunchResponse createAgentSessionApiV1AgentSessionsPost(agentSessionCreateRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant)

Create Agent Session

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        AgentSessionCreateRequest agentSessionCreateRequest = new AgentSessionCreateRequest(); // AgentSessionCreateRequest |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xCorrelationID = "xCorrelationID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionLaunchResponse result = apiInstance.createAgentSessionApiV1AgentSessionsPost(agentSessionCreateRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#createAgentSessionApiV1AgentSessionsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **agentSessionCreateRequest** | **AgentSessionCreateRequest**|  | |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **xCorrelationID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionLaunchResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createAgentSessionApiV1AgentSessionsPostWithHttpInfo

> ApiResponse<AgentSessionLaunchResponse> createAgentSessionApiV1AgentSessionsPostWithHttpInfo(agentSessionCreateRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant)

Create Agent Session

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        AgentSessionCreateRequest agentSessionCreateRequest = new AgentSessionCreateRequest(); // AgentSessionCreateRequest |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xCorrelationID = "xCorrelationID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionLaunchResponse> response = apiInstance.createAgentSessionApiV1AgentSessionsPostWithHttpInfo(agentSessionCreateRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#createAgentSessionApiV1AgentSessionsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **agentSessionCreateRequest** | **AgentSessionCreateRequest**|  | |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **xCorrelationID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionLaunchResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getAgentSessionApiV1AgentSessionsServiceSessionIdGet

> AgentSessionServiceDetailResponse getAgentSessionApiV1AgentSessionsServiceSessionIdGet(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        Integer afterEventIndex = 0; // Integer |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionServiceDetailResponse result = apiInstance.getAgentSessionApiV1AgentSessionsServiceSessionIdGet(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionApiV1AgentSessionsServiceSessionIdGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **afterEventIndex** | **Integer**|  | [optional] [default to 0] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionServiceDetailResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getAgentSessionApiV1AgentSessionsServiceSessionIdGetWithHttpInfo

> ApiResponse<AgentSessionServiceDetailResponse> getAgentSessionApiV1AgentSessionsServiceSessionIdGetWithHttpInfo(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        Integer afterEventIndex = 0; // Integer |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionServiceDetailResponse> response = apiInstance.getAgentSessionApiV1AgentSessionsServiceSessionIdGetWithHttpInfo(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionApiV1AgentSessionsServiceSessionIdGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **afterEventIndex** | **Integer**|  | [optional] [default to 0] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionServiceDetailResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet

> AgentSessionServiceDetailResponse getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        Integer afterEventIndex = 0; // Integer |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionServiceDetailResponse result = apiInstance.getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **afterEventIndex** | **Integer**|  | [optional] [default to 0] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionServiceDetailResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGetWithHttpInfo

> ApiResponse<AgentSessionServiceDetailResponse> getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGetWithHttpInfo(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        Integer afterEventIndex = 0; // Integer |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionServiceDetailResponse> response = apiInstance.getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGetWithHttpInfo(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **afterEventIndex** | **Integer**|  | [optional] [default to 0] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionServiceDetailResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet

> AgentSessionServiceDetailResponse getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Messages

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        Integer afterEventIndex = 0; // Integer |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionServiceDetailResponse result = apiInstance.getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **afterEventIndex** | **Integer**|  | [optional] [default to 0] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionServiceDetailResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGetWithHttpInfo

> ApiResponse<AgentSessionServiceDetailResponse> getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGetWithHttpInfo(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Messages

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        Integer afterEventIndex = 0; // Integer |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionServiceDetailResponse> response = apiInstance.getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGetWithHttpInfo(serviceSessionId, afterEventIndex, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionMessagesApiV1AgentSessionsServiceSessionIdMessagesGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **afterEventIndex** | **Integer**|  | [optional] [default to 0] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionServiceDetailResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet

> AgentProgressPage getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet(serviceSessionId, after, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Progress

Return one authorized page from the canonical cross-attempt timeline.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        String after = "after_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentProgressPage result = apiInstance.getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet(serviceSessionId, after, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **after** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentProgressPage**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGetWithHttpInfo

> ApiResponse<AgentProgressPage> getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGetWithHttpInfo(serviceSessionId, after, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Progress

Return one authorized page from the canonical cross-attempt timeline.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        String after = "after_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentProgressPage> response = apiInstance.getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGetWithHttpInfo(serviceSessionId, after, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **after** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentProgressPage**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet

> AgentSessionResultResponse getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet(serviceSessionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Result

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionResultResponse result = apiInstance.getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet(serviceSessionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionResultResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGetWithHttpInfo

> ApiResponse<AgentSessionResultResponse> getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGetWithHttpInfo(serviceSessionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Result

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionResultResponse> response = apiInstance.getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGetWithHttpInfo(serviceSessionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#getAgentSessionResultApiV1AgentSessionsServiceSessionIdResultGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionResultResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet

> Map<String, AgentSessionHarnessCatalogEntry> listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet(authorization, xAmeshCSRF, xAmeshTenant)

List Agent Session Harnesses

Return registered harness provenance without exposing worker details.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            Map<String, AgentSessionHarnessCatalogEntry> result = apiInstance.listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**Map&lt;String, AgentSessionHarnessCatalogEntry&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listAgentSessionHarnessesApiV1AgentSessionsHarnessesGetWithHttpInfo

> ApiResponse<Map<String, AgentSessionHarnessCatalogEntry>> listAgentSessionHarnessesApiV1AgentSessionsHarnessesGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Agent Session Harnesses

Return registered harness provenance without exposing worker details.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Map<String, AgentSessionHarnessCatalogEntry>> response = apiInstance.listAgentSessionHarnessesApiV1AgentSessionsHarnessesGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#listAgentSessionHarnessesApiV1AgentSessionsHarnessesGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**Map&lt;String, AgentSessionHarnessCatalogEntry&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listAgentSessionsApiV1AgentSessionsGet

> List<AgentSessionServiceItem> listAgentSessionsApiV1AgentSessionsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Sessions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<AgentSessionServiceItem> result = apiInstance.listAgentSessionsApiV1AgentSessionsGet(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#listAgentSessionsApiV1AgentSessionsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;AgentSessionServiceItem&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listAgentSessionsApiV1AgentSessionsGetWithHttpInfo

> ApiResponse<List<AgentSessionServiceItem>> listAgentSessionsApiV1AgentSessionsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Sessions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<AgentSessionServiceItem>> response = apiInstance.listAgentSessionsApiV1AgentSessionsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#listAgentSessionsApiV1AgentSessionsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;AgentSessionServiceItem&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## openaiChatCompletionsV1ChatCompletionsPost

> OpenAIChatCompletionResponse openaiChatCompletionsV1ChatCompletionsPost(openAIChatCompletionRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant)

Openai Chat Completions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        OpenAIChatCompletionRequest openAIChatCompletionRequest = new OpenAIChatCompletionRequest(); // OpenAIChatCompletionRequest |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            OpenAIChatCompletionResponse result = apiInstance.openaiChatCompletionsV1ChatCompletionsPost(openAIChatCompletionRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#openaiChatCompletionsV1ChatCompletionsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **openAIChatCompletionRequest** | **OpenAIChatCompletionRequest**|  | |
| **idempotencyKey** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**OpenAIChatCompletionResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## openaiChatCompletionsV1ChatCompletionsPostWithHttpInfo

> ApiResponse<OpenAIChatCompletionResponse> openaiChatCompletionsV1ChatCompletionsPostWithHttpInfo(openAIChatCompletionRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant)

Openai Chat Completions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        OpenAIChatCompletionRequest openAIChatCompletionRequest = new OpenAIChatCompletionRequest(); // OpenAIChatCompletionRequest |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<OpenAIChatCompletionResponse> response = apiInstance.openaiChatCompletionsV1ChatCompletionsPostWithHttpInfo(openAIChatCompletionRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#openaiChatCompletionsV1ChatCompletionsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **openAIChatCompletionRequest** | **OpenAIChatCompletionRequest**|  | |
| **idempotencyKey** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**OpenAIChatCompletionResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## openaiResponsesV1ResponsesPost

> OpenAIResponse openaiResponsesV1ResponsesPost(openAIResponseRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant)

Openai Responses

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        OpenAIResponseRequest openAIResponseRequest = new OpenAIResponseRequest(); // OpenAIResponseRequest |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            OpenAIResponse result = apiInstance.openaiResponsesV1ResponsesPost(openAIResponseRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#openaiResponsesV1ResponsesPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **openAIResponseRequest** | **OpenAIResponseRequest**|  | |
| **idempotencyKey** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**OpenAIResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## openaiResponsesV1ResponsesPostWithHttpInfo

> ApiResponse<OpenAIResponse> openaiResponsesV1ResponsesPostWithHttpInfo(openAIResponseRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant)

Openai Responses

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        OpenAIResponseRequest openAIResponseRequest = new OpenAIResponseRequest(); // OpenAIResponseRequest |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<OpenAIResponse> response = apiInstance.openaiResponsesV1ResponsesPostWithHttpInfo(openAIResponseRequest, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#openaiResponsesV1ResponsesPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **openAIResponseRequest** | **OpenAIResponseRequest**|  | |
| **idempotencyKey** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**OpenAIResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost

> AgentSessionLaunchResponse postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost(serviceSessionId, agentSessionMessageRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant)

Post Agent Session Message

Append one idempotent input through a new canonical execution turn.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        AgentSessionMessageRequest agentSessionMessageRequest = new AgentSessionMessageRequest(); // AgentSessionMessageRequest |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xCorrelationID = "xCorrelationID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionLaunchResponse result = apiInstance.postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost(serviceSessionId, agentSessionMessageRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **agentSessionMessageRequest** | **AgentSessionMessageRequest**|  | |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **xCorrelationID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionLaunchResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPostWithHttpInfo

> ApiResponse<AgentSessionLaunchResponse> postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPostWithHttpInfo(serviceSessionId, agentSessionMessageRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant)

Post Agent Session Message

Append one idempotent input through a new canonical execution turn.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        AgentSessionMessageRequest agentSessionMessageRequest = new AgentSessionMessageRequest(); // AgentSessionMessageRequest |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xCorrelationID = "xCorrelationID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionLaunchResponse> response = apiInstance.postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPostWithHttpInfo(serviceSessionId, agentSessionMessageRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#postAgentSessionMessageApiV1AgentSessionsServiceSessionIdMessagesPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **agentSessionMessageRequest** | **AgentSessionMessageRequest**|  | |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **xCorrelationID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionLaunchResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet

> void streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet(serviceSessionId, afterEventIndex, authorization, xAmeshCSRF, xAmeshTenant)

Stream Agent Session Events

Stream durable redacted events with a bounded reconnectable poll window.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        Integer afterEventIndex = 0; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet(serviceSessionId, afterEventIndex, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **afterEventIndex** | **Integer**|  | [optional] [default to 0] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGetWithHttpInfo

> ApiResponse<Void> streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGetWithHttpInfo(serviceSessionId, afterEventIndex, authorization, xAmeshCSRF, xAmeshTenant)

Stream Agent Session Events

Stream durable redacted events with a bounded reconnectable poll window.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        Integer afterEventIndex = 0; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGetWithHttpInfo(serviceSessionId, afterEventIndex, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#streamAgentSessionEventsApiV1AgentSessionsServiceSessionIdEventsStreamGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **afterEventIndex** | **Integer**|  | [optional] [default to 0] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


ApiResponse<Void>

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet

> void streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet(serviceSessionId, after, lastEventID, authorization, xAmeshCSRF, xAmeshTenant)

Stream Agent Session Progress

Poll the durable journal without coupling observer speed to execution.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        String after = "after_example"; // String |
        String lastEventID = "lastEventID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet(serviceSessionId, after, lastEventID, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **after** | **String**|  | [optional] |
| **lastEventID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGetWithHttpInfo

> ApiResponse<Void> streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGetWithHttpInfo(serviceSessionId, after, lastEventID, authorization, xAmeshCSRF, xAmeshTenant)

Stream Agent Session Progress

Poll the durable journal without coupling observer speed to execution.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionsApi apiInstance = new AgentSessionsApi(defaultClient);
        UUID serviceSessionId = UUID.randomUUID(); // UUID |
        String after = "after_example"; // String |
        String lastEventID = "lastEventID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGetWithHttpInfo(serviceSessionId, after, lastEventID, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionsApi#streamAgentSessionProgressApiV1AgentSessionsServiceSessionIdProgressStreamGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **serviceSessionId** | **UUID**|  | |
| **after** | **String**|  | [optional] |
| **lastEventID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


ApiResponse<Void>

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |
