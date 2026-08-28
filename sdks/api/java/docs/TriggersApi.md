# TriggersApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**listTriggerOccurrencesApiV1TriggerOccurrencesGet**](TriggersApi.md#listTriggerOccurrencesApiV1TriggerOccurrencesGet) | **GET** /api/v1/trigger-occurrences | List Trigger Occurrences |
| [**listTriggerOccurrencesApiV1TriggerOccurrencesGetWithHttpInfo**](TriggersApi.md#listTriggerOccurrencesApiV1TriggerOccurrencesGetWithHttpInfo) | **GET** /api/v1/trigger-occurrences | List Trigger Occurrences |
| [**listTriggerRuntimeStatesApiV1TriggersGet**](TriggersApi.md#listTriggerRuntimeStatesApiV1TriggersGet) | **GET** /api/v1/triggers | List Trigger Runtime States |
| [**listTriggerRuntimeStatesApiV1TriggersGetWithHttpInfo**](TriggersApi.md#listTriggerRuntimeStatesApiV1TriggersGetWithHttpInfo) | **GET** /api/v1/triggers | List Trigger Runtime States |
| [**pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost**](TriggersApi.md#pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/pause | Pause Trigger Runtime |
| [**pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePostWithHttpInfo**](TriggersApi.md#pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePostWithHttpInfo) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/pause | Pause Trigger Runtime |
| [**previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet**](TriggersApi.md#previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet) | **GET** /api/v1/flows/{namespace}/{flow_id}/schedules/{trigger_id}/preview | Preview Schedule |
| [**previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGetWithHttpInfo**](TriggersApi.md#previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGetWithHttpInfo) | **GET** /api/v1/flows/{namespace}/{flow_id}/schedules/{trigger_id}/preview | Preview Schedule |
| [**replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost**](TriggersApi.md#replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost) | **POST** /api/v1/trigger-occurrences/{occurrence_id}/replay | Replay Trigger Occurrence |
| [**replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPostWithHttpInfo**](TriggersApi.md#replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPostWithHttpInfo) | **POST** /api/v1/trigger-occurrences/{occurrence_id}/replay | Replay Trigger Occurrence |
| [**resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost**](TriggersApi.md#resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/resume | Resume Trigger Runtime |
| [**resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePostWithHttpInfo**](TriggersApi.md#resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePostWithHttpInfo) | **POST** /api/v1/triggers/{namespace}/{flow_id}/{trigger_id}/resume | Resume Trigger Runtime |
| [**triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost**](TriggersApi.md#triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost) | **POST** /api/v1/webhooks/{namespace}/{flow_id}/{trigger_id} | Trigger Webhook |
| [**triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPostWithHttpInfo**](TriggersApi.md#triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPostWithHttpInfo) | **POST** /api/v1/webhooks/{namespace}/{flow_id}/{trigger_id} | Trigger Webhook |



## listTriggerOccurrencesApiV1TriggerOccurrencesGet

> List<TriggerOccurrence> listTriggerOccurrencesApiV1TriggerOccurrencesGet(namespace, flowId, triggerId, state, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Trigger Occurrences

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        TriggerOccurrenceState state = TriggerOccurrenceState.fromValue("ACCEPTED"); // TriggerOccurrenceState |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<TriggerOccurrence> result = apiInstance.listTriggerOccurrencesApiV1TriggerOccurrencesGet(namespace, flowId, triggerId, state, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#listTriggerOccurrencesApiV1TriggerOccurrencesGet");
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
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **triggerId** | **String**|  | [optional] |
| **state** | **TriggerOccurrenceState**|  | [optional] [enum: ACCEPTED, DEFERRED, PROCESSING, RETRY_WAIT, SUCCEEDED, DEAD_LETTERED] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;TriggerOccurrence&gt;**


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

## listTriggerOccurrencesApiV1TriggerOccurrencesGetWithHttpInfo

> ApiResponse<List<TriggerOccurrence>> listTriggerOccurrencesApiV1TriggerOccurrencesGetWithHttpInfo(namespace, flowId, triggerId, state, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Trigger Occurrences

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        TriggerOccurrenceState state = TriggerOccurrenceState.fromValue("ACCEPTED"); // TriggerOccurrenceState |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<TriggerOccurrence>> response = apiInstance.listTriggerOccurrencesApiV1TriggerOccurrencesGetWithHttpInfo(namespace, flowId, triggerId, state, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#listTriggerOccurrencesApiV1TriggerOccurrencesGet");
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
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **triggerId** | **String**|  | [optional] |
| **state** | **TriggerOccurrenceState**|  | [optional] [enum: ACCEPTED, DEFERRED, PROCESSING, RETRY_WAIT, SUCCEEDED, DEAD_LETTERED] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;TriggerOccurrence&gt;**>


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


## listTriggerRuntimeStatesApiV1TriggersGet

> List<TriggerRuntimeState> listTriggerRuntimeStatesApiV1TriggersGet(namespace, flowId, triggerId, active, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Trigger Runtime States

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        Boolean active = true; // Boolean |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<TriggerRuntimeState> result = apiInstance.listTriggerRuntimeStatesApiV1TriggersGet(namespace, flowId, triggerId, active, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#listTriggerRuntimeStatesApiV1TriggersGet");
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
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **triggerId** | **String**|  | [optional] |
| **active** | **Boolean**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;TriggerRuntimeState&gt;**


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

## listTriggerRuntimeStatesApiV1TriggersGetWithHttpInfo

> ApiResponse<List<TriggerRuntimeState>> listTriggerRuntimeStatesApiV1TriggersGetWithHttpInfo(namespace, flowId, triggerId, active, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Trigger Runtime States

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        Boolean active = true; // Boolean |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<TriggerRuntimeState>> response = apiInstance.listTriggerRuntimeStatesApiV1TriggersGetWithHttpInfo(namespace, flowId, triggerId, active, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#listTriggerRuntimeStatesApiV1TriggersGet");
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
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **triggerId** | **String**|  | [optional] |
| **active** | **Boolean**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;TriggerRuntimeState&gt;**>


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


## pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost

> TriggerRuntimeState pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Pause Trigger Runtime

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        TriggerActionRequest triggerActionRequest = new TriggerActionRequest(); // TriggerActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            TriggerRuntimeState result = apiInstance.pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost");
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
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **triggerId** | **String**|  | |
| **triggerActionRequest** | **TriggerActionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**TriggerRuntimeState**


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

## pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePostWithHttpInfo

> ApiResponse<TriggerRuntimeState> pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePostWithHttpInfo(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Pause Trigger Runtime

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        TriggerActionRequest triggerActionRequest = new TriggerActionRequest(); // TriggerActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<TriggerRuntimeState> response = apiInstance.pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePostWithHttpInfo(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#pauseTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdPausePost");
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
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **triggerId** | **String**|  | |
| **triggerActionRequest** | **TriggerActionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**TriggerRuntimeState**>


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


## previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet

> SchedulePreview previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet(namespace, flowId, triggerId, after, count, authorization, xAmeshCSRF, xAmeshTenant)

Preview Schedule

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        OffsetDateTime after = OffsetDateTime.now(); // OffsetDateTime |
        Integer count = 5; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SchedulePreview result = apiInstance.previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet(namespace, flowId, triggerId, after, count, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet");
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
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **triggerId** | **String**|  | |
| **after** | **OffsetDateTime**|  | [optional] |
| **count** | **Integer**|  | [optional] [default to 5] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**SchedulePreview**


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

## previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGetWithHttpInfo

> ApiResponse<SchedulePreview> previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGetWithHttpInfo(namespace, flowId, triggerId, after, count, authorization, xAmeshCSRF, xAmeshTenant)

Preview Schedule

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        OffsetDateTime after = OffsetDateTime.now(); // OffsetDateTime |
        Integer count = 5; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SchedulePreview> response = apiInstance.previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGetWithHttpInfo(namespace, flowId, triggerId, after, count, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#previewScheduleApiV1FlowsNamespaceFlowIdSchedulesTriggerIdPreviewGet");
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
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **triggerId** | **String**|  | |
| **after** | **OffsetDateTime**|  | [optional] |
| **count** | **Integer**|  | [optional] [default to 5] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**SchedulePreview**>


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


## replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost

> TriggerOccurrence replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost(occurrenceId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Replay Trigger Occurrence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        UUID occurrenceId = UUID.randomUUID(); // UUID |
        TriggerActionRequest triggerActionRequest = new TriggerActionRequest(); // TriggerActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            TriggerOccurrence result = apiInstance.replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost(occurrenceId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost");
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
| **occurrenceId** | **UUID**|  | |
| **triggerActionRequest** | **TriggerActionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**TriggerOccurrence**


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

## replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPostWithHttpInfo

> ApiResponse<TriggerOccurrence> replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPostWithHttpInfo(occurrenceId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Replay Trigger Occurrence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        UUID occurrenceId = UUID.randomUUID(); // UUID |
        TriggerActionRequest triggerActionRequest = new TriggerActionRequest(); // TriggerActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<TriggerOccurrence> response = apiInstance.replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPostWithHttpInfo(occurrenceId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#replayTriggerOccurrenceApiV1TriggerOccurrencesOccurrenceIdReplayPost");
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
| **occurrenceId** | **UUID**|  | |
| **triggerActionRequest** | **TriggerActionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**TriggerOccurrence**>


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


## resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost

> TriggerRuntimeState resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resume Trigger Runtime

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        TriggerActionRequest triggerActionRequest = new TriggerActionRequest(); // TriggerActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            TriggerRuntimeState result = apiInstance.resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost");
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
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **triggerId** | **String**|  | |
| **triggerActionRequest** | **TriggerActionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**TriggerRuntimeState**


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

## resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePostWithHttpInfo

> ApiResponse<TriggerRuntimeState> resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePostWithHttpInfo(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resume Trigger Runtime

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        TriggerActionRequest triggerActionRequest = new TriggerActionRequest(); // TriggerActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<TriggerRuntimeState> response = apiInstance.resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePostWithHttpInfo(namespace, flowId, triggerId, triggerActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#resumeTriggerRuntimeApiV1TriggersNamespaceFlowIdTriggerIdResumePost");
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
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **triggerId** | **String**|  | |
| **triggerActionRequest** | **TriggerActionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**TriggerRuntimeState**>


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


## triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost

> ExecutionDetail triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost(namespace, flowId, triggerId, runner, prefer, idempotencyKey, xEventId, authorization, xAmeshCSRF, xAmeshTenant)

Trigger Webhook

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        RunnerMode runner = RunnerMode.fromValue("local"); // RunnerMode |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xEventId = "xEventId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ExecutionDetail result = apiInstance.triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost(namespace, flowId, triggerId, runner, prefer, idempotencyKey, xEventId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost");
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
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **triggerId** | **String**|  | |
| **runner** | **RunnerMode**|  | [optional] [default to local] [enum: local, docker, kubernetes] |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **xEventId** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**ExecutionDetail**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **202** | Webhook execution persisted and accepted for asynchronous processing |  -  |
| **422** | Validation Error |  -  |

## triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPostWithHttpInfo

> ApiResponse<ExecutionDetail> triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPostWithHttpInfo(namespace, flowId, triggerId, runner, prefer, idempotencyKey, xEventId, authorization, xAmeshCSRF, xAmeshTenant)

Trigger Webhook

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TriggersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TriggersApi apiInstance = new TriggersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String triggerId = "triggerId_example"; // String |
        RunnerMode runner = RunnerMode.fromValue("local"); // RunnerMode |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xEventId = "xEventId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ExecutionDetail> response = apiInstance.triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPostWithHttpInfo(namespace, flowId, triggerId, runner, prefer, idempotencyKey, xEventId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TriggersApi#triggerWebhookApiV1WebhooksNamespaceFlowIdTriggerIdPost");
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
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **triggerId** | **String**|  | |
| **runner** | **RunnerMode**|  | [optional] [default to local] [enum: local, docker, kubernetes] |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **xEventId** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**ExecutionDetail**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **202** | Webhook execution persisted and accepted for asynchronous processing |  -  |
| **422** | Validation Error |  -  |
