# ExecutionsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost**](ExecutionsApi.md#applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost) | **POST** /api/v1/executions/{execution_id}/interventions | Apply Execution Control |
| [**applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPostWithHttpInfo**](ExecutionsApi.md#applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPostWithHttpInfo) | **POST** /api/v1/executions/{execution_id}/interventions | Apply Execution Control |
| [**createExecutionApiV1ExecutionsPost**](ExecutionsApi.md#createExecutionApiV1ExecutionsPost) | **POST** /api/v1/executions | Create Execution |
| [**createExecutionApiV1ExecutionsPostWithHttpInfo**](ExecutionsApi.md#createExecutionApiV1ExecutionsPostWithHttpInfo) | **POST** /api/v1/executions | Create Execution |
| [**createExecutionsBulkApiV1ExecutionsBulkPost**](ExecutionsApi.md#createExecutionsBulkApiV1ExecutionsBulkPost) | **POST** /api/v1/executions/bulk | Create Executions Bulk |
| [**createExecutionsBulkApiV1ExecutionsBulkPostWithHttpInfo**](ExecutionsApi.md#createExecutionsBulkApiV1ExecutionsBulkPostWithHttpInfo) | **POST** /api/v1/executions/bulk | Create Executions Bulk |
| [**downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet**](ExecutionsApi.md#downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet) | **GET** /api/v1/executions/{execution_id}/files/{artifact_id} | Download Execution File |
| [**downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGetWithHttpInfo**](ExecutionsApi.md#downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/files/{artifact_id} | Download Execution File |
| [**getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet**](ExecutionsApi.md#getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet) | **GET** /api/v1/executions/{execution_id}/admission | Get Execution Admission |
| [**getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGetWithHttpInfo**](ExecutionsApi.md#getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/admission | Get Execution Admission |
| [**getExecutionApiV1ExecutionsExecutionIdGet**](ExecutionsApi.md#getExecutionApiV1ExecutionsExecutionIdGet) | **GET** /api/v1/executions/{execution_id} | Get Execution |
| [**getExecutionApiV1ExecutionsExecutionIdGetWithHttpInfo**](ExecutionsApi.md#getExecutionApiV1ExecutionsExecutionIdGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id} | Get Execution |
| [**getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet**](ExecutionsApi.md#getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet) | **GET** /api/v1/executions/{execution_id}/evidence | Get Execution Evidence |
| [**getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGetWithHttpInfo**](ExecutionsApi.md#getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/evidence | Get Execution Evidence |
| [**getExecutionGraphApiV1ExecutionsExecutionIdGraphGet**](ExecutionsApi.md#getExecutionGraphApiV1ExecutionsExecutionIdGraphGet) | **GET** /api/v1/executions/{execution_id}/graph | Get Execution Graph |
| [**getExecutionGraphApiV1ExecutionsExecutionIdGraphGetWithHttpInfo**](ExecutionsApi.md#getExecutionGraphApiV1ExecutionsExecutionIdGraphGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/graph | Get Execution Graph |
| [**getExecutionLogsApiV1ExecutionsExecutionIdLogsGet**](ExecutionsApi.md#getExecutionLogsApiV1ExecutionsExecutionIdLogsGet) | **GET** /api/v1/executions/{execution_id}/logs | Get Execution Logs |
| [**getExecutionLogsApiV1ExecutionsExecutionIdLogsGetWithHttpInfo**](ExecutionsApi.md#getExecutionLogsApiV1ExecutionsExecutionIdLogsGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/logs | Get Execution Logs |
| [**getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet**](ExecutionsApi.md#getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet) | **GET** /api/v1/executions/{execution_id}/parent-subflow | Get Execution Parent Subflow |
| [**getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGetWithHttpInfo**](ExecutionsApi.md#getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/parent-subflow | Get Execution Parent Subflow |
| [**getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet**](ExecutionsApi.md#getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet) | **GET** /api/v1/task-runs/{task_run_id}/admission | Get Task Admission |
| [**getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGetWithHttpInfo**](ExecutionsApi.md#getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGetWithHttpInfo) | **GET** /api/v1/task-runs/{task_run_id}/admission | Get Task Admission |
| [**listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet**](ExecutionsApi.md#listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet) | **GET** /api/v1/executions/{execution_id}/interventions | List Execution Control History |
| [**listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGetWithHttpInfo**](ExecutionsApi.md#listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/interventions | List Execution Control History |
| [**listExecutionFilesApiV1ExecutionsExecutionIdFilesGet**](ExecutionsApi.md#listExecutionFilesApiV1ExecutionsExecutionIdFilesGet) | **GET** /api/v1/executions/{execution_id}/files | List Execution Files |
| [**listExecutionFilesApiV1ExecutionsExecutionIdFilesGetWithHttpInfo**](ExecutionsApi.md#listExecutionFilesApiV1ExecutionsExecutionIdFilesGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/files | List Execution Files |
| [**listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet**](ExecutionsApi.md#listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet) | **GET** /api/v1/executions/{execution_id}/subflows | List Execution Subflows |
| [**listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGetWithHttpInfo**](ExecutionsApi.md#listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/subflows | List Execution Subflows |
| [**listExecutionsApiV1ExecutionsGet**](ExecutionsApi.md#listExecutionsApiV1ExecutionsGet) | **GET** /api/v1/executions | List Executions |
| [**listExecutionsApiV1ExecutionsGetWithHttpInfo**](ExecutionsApi.md#listExecutionsApiV1ExecutionsGetWithHttpInfo) | **GET** /api/v1/executions | List Executions |
| [**previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost**](ExecutionsApi.md#previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost) | **POST** /api/v1/executions/{execution_id}/interventions/preview | Preview Execution Control |
| [**previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPostWithHttpInfo**](ExecutionsApi.md#previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPostWithHttpInfo) | **POST** /api/v1/executions/{execution_id}/interventions/preview | Preview Execution Control |
| [**reduceExecutionEventsApiV1ExecutionsReducePost**](ExecutionsApi.md#reduceExecutionEventsApiV1ExecutionsReducePost) | **POST** /api/v1/executions/reduce | Reduce Execution Events |
| [**reduceExecutionEventsApiV1ExecutionsReducePostWithHttpInfo**](ExecutionsApi.md#reduceExecutionEventsApiV1ExecutionsReducePostWithHttpInfo) | **POST** /api/v1/executions/reduce | Reduce Execution Events |
| [**resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost**](ExecutionsApi.md#resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost) | **POST** /api/v1/executions/{execution_id}/task-runs/{task_run_id}/resume | Resume Task Run |
| [**resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePostWithHttpInfo**](ExecutionsApi.md#resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePostWithHttpInfo) | **POST** /api/v1/executions/{execution_id}/task-runs/{task_run_id}/resume | Resume Task Run |
| [**streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet**](ExecutionsApi.md#streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet) | **GET** /api/v1/executions/{execution_id}/evidence/stream | Stream Execution Evidence |
| [**streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGetWithHttpInfo**](ExecutionsApi.md#streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/evidence/stream | Stream Execution Evidence |
| [**streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet**](ExecutionsApi.md#streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet) | **GET** /api/v1/executions/{execution_id}/logs/stream | Stream Execution Logs |
| [**streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGetWithHttpInfo**](ExecutionsApi.md#streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGetWithHttpInfo) | **GET** /api/v1/executions/{execution_id}/logs/stream | Stream Execution Logs |



## applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost

> ExecutionDetail applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost(executionId, executionInterventionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Apply Execution Control

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        ExecutionInterventionRequest executionInterventionRequest = new ExecutionInterventionRequest(); // ExecutionInterventionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ExecutionDetail result = apiInstance.applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost(executionId, executionInterventionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost");
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
| **executionId** | **UUID**|  | |
| **executionInterventionRequest** | [**ExecutionInterventionRequest**](ExecutionInterventionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ExecutionDetail**](ExecutionDetail.md)


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

## applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPostWithHttpInfo

> ApiResponse<ExecutionDetail> applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPostWithHttpInfo(executionId, executionInterventionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Apply Execution Control

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        ExecutionInterventionRequest executionInterventionRequest = new ExecutionInterventionRequest(); // ExecutionInterventionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ExecutionDetail> response = apiInstance.applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPostWithHttpInfo(executionId, executionInterventionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#applyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost");
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
| **executionId** | **UUID**|  | |
| **executionInterventionRequest** | [**ExecutionInterventionRequest**](ExecutionInterventionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ExecutionDetail**](ExecutionDetail.md)>


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


## createExecutionApiV1ExecutionsPost

> ExecutionDetail createExecutionApiV1ExecutionsPost(createExecutionRequest, prefer, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant)

Create Execution

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        CreateExecutionRequest createExecutionRequest = new CreateExecutionRequest(); // CreateExecutionRequest |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ExecutionDetail result = apiInstance.createExecutionApiV1ExecutionsPost(createExecutionRequest, prefer, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#createExecutionApiV1ExecutionsPost");
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
| **createExecutionRequest** | [**CreateExecutionRequest**](CreateExecutionRequest.md)|  | |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ExecutionDetail**](ExecutionDetail.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **202** | Execution persisted and accepted for asynchronous processing |  -  |
| **422** | Validation Error |  -  |

## createExecutionApiV1ExecutionsPostWithHttpInfo

> ApiResponse<ExecutionDetail> createExecutionApiV1ExecutionsPostWithHttpInfo(createExecutionRequest, prefer, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant)

Create Execution

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        CreateExecutionRequest createExecutionRequest = new CreateExecutionRequest(); // CreateExecutionRequest |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ExecutionDetail> response = apiInstance.createExecutionApiV1ExecutionsPostWithHttpInfo(createExecutionRequest, prefer, idempotencyKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#createExecutionApiV1ExecutionsPost");
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
| **createExecutionRequest** | [**CreateExecutionRequest**](CreateExecutionRequest.md)|  | |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ExecutionDetail**](ExecutionDetail.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **202** | Execution persisted and accepted for asynchronous processing |  -  |
| **422** | Validation Error |  -  |


## createExecutionsBulkApiV1ExecutionsBulkPost

> List<BulkExecutionItemResult> createExecutionsBulkApiV1ExecutionsBulkPost(bulkExecutionRequest, prefer, authorization, xAmeshCSRF, xAmeshTenant)

Create Executions Bulk

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        BulkExecutionRequest bulkExecutionRequest = new BulkExecutionRequest(); // BulkExecutionRequest |
        String prefer = "prefer_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<BulkExecutionItemResult> result = apiInstance.createExecutionsBulkApiV1ExecutionsBulkPost(bulkExecutionRequest, prefer, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#createExecutionsBulkApiV1ExecutionsBulkPost");
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
| **bulkExecutionRequest** | [**BulkExecutionRequest**](BulkExecutionRequest.md)|  | |
| **prefer** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;BulkExecutionItemResult&gt;**](BulkExecutionItemResult.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **207** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createExecutionsBulkApiV1ExecutionsBulkPostWithHttpInfo

> ApiResponse<List<BulkExecutionItemResult>> createExecutionsBulkApiV1ExecutionsBulkPostWithHttpInfo(bulkExecutionRequest, prefer, authorization, xAmeshCSRF, xAmeshTenant)

Create Executions Bulk

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        BulkExecutionRequest bulkExecutionRequest = new BulkExecutionRequest(); // BulkExecutionRequest |
        String prefer = "prefer_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<BulkExecutionItemResult>> response = apiInstance.createExecutionsBulkApiV1ExecutionsBulkPostWithHttpInfo(bulkExecutionRequest, prefer, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#createExecutionsBulkApiV1ExecutionsBulkPost");
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
| **bulkExecutionRequest** | [**BulkExecutionRequest**](BulkExecutionRequest.md)|  | |
| **prefer** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;BulkExecutionItemResult&gt;**](BulkExecutionItemResult.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **207** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet

> void downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet(executionId, artifactId, authorization, xAmeshCSRF, xAmeshTenant)

Download Execution File

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        UUID artifactId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet(executionId, artifactId, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet");
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
| **executionId** | **UUID**|  | |
| **artifactId** | **UUID**|  | |
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

## downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGetWithHttpInfo

> ApiResponse<Void> downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGetWithHttpInfo(executionId, artifactId, authorization, xAmeshCSRF, xAmeshTenant)

Download Execution File

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        UUID artifactId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGetWithHttpInfo(executionId, artifactId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#downloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet");
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
| **executionId** | **UUID**|  | |
| **artifactId** | **UUID**|  | |
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


## getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet

> AdmissionDecision getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Admission

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AdmissionDecision result = apiInstance.getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**AdmissionDecision**](AdmissionDecision.md)


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

## getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGetWithHttpInfo

> ApiResponse<AdmissionDecision> getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Admission

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AdmissionDecision> response = apiInstance.getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**AdmissionDecision**](AdmissionDecision.md)>


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


## getExecutionApiV1ExecutionsExecutionIdGet

> ExecutionDetail getExecutionApiV1ExecutionsExecutionIdGet(executionId, taskOffset, taskLimit, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        Integer taskOffset = 0; // Integer |
        Integer taskLimit = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ExecutionDetail result = apiInstance.getExecutionApiV1ExecutionsExecutionIdGet(executionId, taskOffset, taskLimit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionApiV1ExecutionsExecutionIdGet");
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
| **executionId** | **UUID**|  | |
| **taskOffset** | **Integer**|  | [optional] [default to 0] |
| **taskLimit** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ExecutionDetail**](ExecutionDetail.md)


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

## getExecutionApiV1ExecutionsExecutionIdGetWithHttpInfo

> ApiResponse<ExecutionDetail> getExecutionApiV1ExecutionsExecutionIdGetWithHttpInfo(executionId, taskOffset, taskLimit, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        Integer taskOffset = 0; // Integer |
        Integer taskLimit = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ExecutionDetail> response = apiInstance.getExecutionApiV1ExecutionsExecutionIdGetWithHttpInfo(executionId, taskOffset, taskLimit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionApiV1ExecutionsExecutionIdGet");
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
| **executionId** | **UUID**|  | |
| **taskOffset** | **Integer**|  | [optional] [default to 0] |
| **taskLimit** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ExecutionDetail**](ExecutionDetail.md)>


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


## getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet

> ExecutionEvidencePage getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet(executionId, cursor, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String cursor = "cursor_example"; // String | Opaque reconnect cursor
        Integer limit = 500; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ExecutionEvidencePage result = apiInstance.getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet(executionId, cursor, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet");
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
| **executionId** | **UUID**|  | |
| **cursor** | **String**| Opaque reconnect cursor | [optional] |
| **limit** | **Integer**|  | [optional] [default to 500] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ExecutionEvidencePage**](ExecutionEvidencePage.md)


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

## getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGetWithHttpInfo

> ApiResponse<ExecutionEvidencePage> getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGetWithHttpInfo(executionId, cursor, limit, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String cursor = "cursor_example"; // String | Opaque reconnect cursor
        Integer limit = 500; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ExecutionEvidencePage> response = apiInstance.getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGetWithHttpInfo(executionId, cursor, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet");
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
| **executionId** | **UUID**|  | |
| **cursor** | **String**| Opaque reconnect cursor | [optional] |
| **limit** | **Integer**|  | [optional] [default to 500] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ExecutionEvidencePage**](ExecutionEvidencePage.md)>


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


## getExecutionGraphApiV1ExecutionsExecutionIdGraphGet

> FlowGraph getExecutionGraphApiV1ExecutionsExecutionIdGraphGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Graph

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowGraph result = apiInstance.getExecutionGraphApiV1ExecutionsExecutionIdGraphGet(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionGraphApiV1ExecutionsExecutionIdGraphGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**FlowGraph**](FlowGraph.md)


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

## getExecutionGraphApiV1ExecutionsExecutionIdGraphGetWithHttpInfo

> ApiResponse<FlowGraph> getExecutionGraphApiV1ExecutionsExecutionIdGraphGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Graph

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowGraph> response = apiInstance.getExecutionGraphApiV1ExecutionsExecutionIdGraphGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionGraphApiV1ExecutionsExecutionIdGraphGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**FlowGraph**](FlowGraph.md)>


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


## getExecutionLogsApiV1ExecutionsExecutionIdLogsGet

> List<TaskLog> getExecutionLogsApiV1ExecutionsExecutionIdLogsGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Logs

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<TaskLog> result = apiInstance.getExecutionLogsApiV1ExecutionsExecutionIdLogsGet(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionLogsApiV1ExecutionsExecutionIdLogsGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;TaskLog&gt;**](TaskLog.md)


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

## getExecutionLogsApiV1ExecutionsExecutionIdLogsGetWithHttpInfo

> ApiResponse<List<TaskLog>> getExecutionLogsApiV1ExecutionsExecutionIdLogsGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Logs

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<TaskLog>> response = apiInstance.getExecutionLogsApiV1ExecutionsExecutionIdLogsGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionLogsApiV1ExecutionsExecutionIdLogsGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;TaskLog&gt;**](TaskLog.md)>


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


## getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet

> PersistedSubflow getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Parent Subflow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PersistedSubflow result = apiInstance.getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**PersistedSubflow**](PersistedSubflow.md)


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

## getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGetWithHttpInfo

> ApiResponse<PersistedSubflow> getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Get Execution Parent Subflow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PersistedSubflow> response = apiInstance.getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**PersistedSubflow**](PersistedSubflow.md)>


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


## getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet

> AdmissionDecision getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet(taskRunId, authorization, xAmeshCSRF, xAmeshTenant)

Get Task Admission

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID taskRunId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AdmissionDecision result = apiInstance.getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet(taskRunId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet");
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
| **taskRunId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**AdmissionDecision**](AdmissionDecision.md)


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

## getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGetWithHttpInfo

> ApiResponse<AdmissionDecision> getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGetWithHttpInfo(taskRunId, authorization, xAmeshCSRF, xAmeshTenant)

Get Task Admission

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID taskRunId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AdmissionDecision> response = apiInstance.getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGetWithHttpInfo(taskRunId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#getTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet");
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
| **taskRunId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**AdmissionDecision**](AdmissionDecision.md)>


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


## listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet

> List<ExecutionInterventionRecord> listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

List Execution Control History

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<ExecutionInterventionRecord> result = apiInstance.listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;ExecutionInterventionRecord&gt;**](ExecutionInterventionRecord.md)


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

## listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGetWithHttpInfo

> ApiResponse<List<ExecutionInterventionRecord>> listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant)

List Execution Control History

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<ExecutionInterventionRecord>> response = apiInstance.listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#listExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;ExecutionInterventionRecord&gt;**](ExecutionInterventionRecord.md)>


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


## listExecutionFilesApiV1ExecutionsExecutionIdFilesGet

> List<ExecutionArtifact> listExecutionFilesApiV1ExecutionsExecutionIdFilesGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

List Execution Files

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<ExecutionArtifact> result = apiInstance.listExecutionFilesApiV1ExecutionsExecutionIdFilesGet(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#listExecutionFilesApiV1ExecutionsExecutionIdFilesGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;ExecutionArtifact&gt;**](ExecutionArtifact.md)


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

## listExecutionFilesApiV1ExecutionsExecutionIdFilesGetWithHttpInfo

> ApiResponse<List<ExecutionArtifact>> listExecutionFilesApiV1ExecutionsExecutionIdFilesGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant)

List Execution Files

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<ExecutionArtifact>> response = apiInstance.listExecutionFilesApiV1ExecutionsExecutionIdFilesGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#listExecutionFilesApiV1ExecutionsExecutionIdFilesGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;ExecutionArtifact&gt;**](ExecutionArtifact.md)>


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


## listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet

> List<PersistedSubflow> listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

List Execution Subflows

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<PersistedSubflow> result = apiInstance.listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;PersistedSubflow&gt;**](PersistedSubflow.md)


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

## listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGetWithHttpInfo

> ApiResponse<List<PersistedSubflow>> listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant)

List Execution Subflows

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<PersistedSubflow>> response = apiInstance.listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#listExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;PersistedSubflow&gt;**](PersistedSubflow.md)>


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


## listExecutionsApiV1ExecutionsGet

> List<PersistedExecution> listExecutionsApiV1ExecutionsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Executions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 100; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<PersistedExecution> result = apiInstance.listExecutionsApiV1ExecutionsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#listExecutionsApiV1ExecutionsGet");
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
| **cursor** | **String**| Opaque cursor from the prior page | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;PersistedExecution&gt;**](PersistedExecution.md)


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

## listExecutionsApiV1ExecutionsGetWithHttpInfo

> ApiResponse<List<PersistedExecution>> listExecutionsApiV1ExecutionsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Executions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 100; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<PersistedExecution>> response = apiInstance.listExecutionsApiV1ExecutionsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#listExecutionsApiV1ExecutionsGet");
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
| **cursor** | **String**| Opaque cursor from the prior page | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;PersistedExecution&gt;**](PersistedExecution.md)>


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


## previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost

> ExecutionInterventionPreview previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost(executionId, executionInterventionPreviewRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Execution Control

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        ExecutionInterventionPreviewRequest executionInterventionPreviewRequest = new ExecutionInterventionPreviewRequest(); // ExecutionInterventionPreviewRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ExecutionInterventionPreview result = apiInstance.previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost(executionId, executionInterventionPreviewRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost");
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
| **executionId** | **UUID**|  | |
| **executionInterventionPreviewRequest** | [**ExecutionInterventionPreviewRequest**](ExecutionInterventionPreviewRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ExecutionInterventionPreview**](ExecutionInterventionPreview.md)


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

## previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPostWithHttpInfo

> ApiResponse<ExecutionInterventionPreview> previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPostWithHttpInfo(executionId, executionInterventionPreviewRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Execution Control

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        ExecutionInterventionPreviewRequest executionInterventionPreviewRequest = new ExecutionInterventionPreviewRequest(); // ExecutionInterventionPreviewRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ExecutionInterventionPreview> response = apiInstance.previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPostWithHttpInfo(executionId, executionInterventionPreviewRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#previewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost");
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
| **executionId** | **UUID**|  | |
| **executionInterventionPreviewRequest** | [**ExecutionInterventionPreviewRequest**](ExecutionInterventionPreviewRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ExecutionInterventionPreview**](ExecutionInterventionPreview.md)>


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


## reduceExecutionEventsApiV1ExecutionsReducePost

> ReduceExecutionResponse reduceExecutionEventsApiV1ExecutionsReducePost(reduceExecutionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Reduce Execution Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        ReduceExecutionRequest reduceExecutionRequest = new ReduceExecutionRequest(); // ReduceExecutionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ReduceExecutionResponse result = apiInstance.reduceExecutionEventsApiV1ExecutionsReducePost(reduceExecutionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#reduceExecutionEventsApiV1ExecutionsReducePost");
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
| **reduceExecutionRequest** | [**ReduceExecutionRequest**](ReduceExecutionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ReduceExecutionResponse**](ReduceExecutionResponse.md)


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

## reduceExecutionEventsApiV1ExecutionsReducePostWithHttpInfo

> ApiResponse<ReduceExecutionResponse> reduceExecutionEventsApiV1ExecutionsReducePostWithHttpInfo(reduceExecutionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Reduce Execution Events

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        ReduceExecutionRequest reduceExecutionRequest = new ReduceExecutionRequest(); // ReduceExecutionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ReduceExecutionResponse> response = apiInstance.reduceExecutionEventsApiV1ExecutionsReducePostWithHttpInfo(reduceExecutionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#reduceExecutionEventsApiV1ExecutionsReducePost");
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
| **reduceExecutionRequest** | [**ReduceExecutionRequest**](ReduceExecutionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ReduceExecutionResponse**](ReduceExecutionResponse.md)>


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


## resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost

> PersistedTaskRun resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost(executionId, taskRunId, resumeTaskRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resume Task Run

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        UUID taskRunId = UUID.randomUUID(); // UUID |
        ResumeTaskRequest resumeTaskRequest = new ResumeTaskRequest(); // ResumeTaskRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PersistedTaskRun result = apiInstance.resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost(executionId, taskRunId, resumeTaskRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost");
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
| **executionId** | **UUID**|  | |
| **taskRunId** | **UUID**|  | |
| **resumeTaskRequest** | [**ResumeTaskRequest**](ResumeTaskRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**PersistedTaskRun**](PersistedTaskRun.md)


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

## resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePostWithHttpInfo

> ApiResponse<PersistedTaskRun> resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePostWithHttpInfo(executionId, taskRunId, resumeTaskRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resume Task Run

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        UUID taskRunId = UUID.randomUUID(); // UUID |
        ResumeTaskRequest resumeTaskRequest = new ResumeTaskRequest(); // ResumeTaskRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PersistedTaskRun> response = apiInstance.resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePostWithHttpInfo(executionId, taskRunId, resumeTaskRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#resumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost");
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
| **executionId** | **UUID**|  | |
| **taskRunId** | **UUID**|  | |
| **resumeTaskRequest** | [**ResumeTaskRequest**](ResumeTaskRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**PersistedTaskRun**](PersistedTaskRun.md)>


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


## streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet

> void streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet(executionId, cursor, authorization, xAmeshCSRF, xAmeshTenant)

Stream Execution Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String cursor = "cursor_example"; // String | Opaque reconnect cursor
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet(executionId, cursor, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet");
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
| **executionId** | **UUID**|  | |
| **cursor** | **String**| Opaque reconnect cursor | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/x-ndjson, application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Evidence events streamed as newline-delimited JSON |  -  |
| **422** | Validation Error |  -  |

## streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGetWithHttpInfo

> ApiResponse<Void> streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGetWithHttpInfo(executionId, cursor, authorization, xAmeshCSRF, xAmeshTenant)

Stream Execution Evidence

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String cursor = "cursor_example"; // String | Opaque reconnect cursor
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGetWithHttpInfo(executionId, cursor, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#streamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet");
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
| **executionId** | **UUID**|  | |
| **cursor** | **String**| Opaque reconnect cursor | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


ApiResponse<Void>

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/x-ndjson, application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Evidence events streamed as newline-delimited JSON |  -  |
| **422** | Validation Error |  -  |


## streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet

> void streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Stream Execution Logs

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet(executionId, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/x-ndjson, application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Task logs streamed as newline-delimited JSON |  -  |
| **422** | Validation Error |  -  |

## streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGetWithHttpInfo

> ApiResponse<Void> streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant)

Stream Execution Logs

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExecutionsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExecutionsApi apiInstance = new ExecutionsApi(defaultClient);
        UUID executionId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGetWithHttpInfo(executionId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExecutionsApi#streamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet");
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
| **executionId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


ApiResponse<Void>

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/x-ndjson, application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Task logs streamed as newline-delimited JSON |  -  |
| **422** | Validation Error |  -  |
