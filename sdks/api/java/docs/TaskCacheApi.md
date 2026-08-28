# TaskCacheApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**listTaskCacheEntriesApiV1TaskCacheGet**](TaskCacheApi.md#listTaskCacheEntriesApiV1TaskCacheGet) | **GET** /api/v1/task-cache | List Task Cache Entries |
| [**listTaskCacheEntriesApiV1TaskCacheGetWithHttpInfo**](TaskCacheApi.md#listTaskCacheEntriesApiV1TaskCacheGetWithHttpInfo) | **GET** /api/v1/task-cache | List Task Cache Entries |
| [**purgeTaskCacheEntriesApiV1TaskCachePurgePost**](TaskCacheApi.md#purgeTaskCacheEntriesApiV1TaskCachePurgePost) | **POST** /api/v1/task-cache/purge | Purge Task Cache Entries |
| [**purgeTaskCacheEntriesApiV1TaskCachePurgePostWithHttpInfo**](TaskCacheApi.md#purgeTaskCacheEntriesApiV1TaskCachePurgePostWithHttpInfo) | **POST** /api/v1/task-cache/purge | Purge Task Cache Entries |



## listTaskCacheEntriesApiV1TaskCacheGet

> List<TaskCacheEntry> listTaskCacheEntriesApiV1TaskCacheGet(keyPrefix, namespace, flowId, taskId, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Task Cache Entries

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TaskCacheApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TaskCacheApi apiInstance = new TaskCacheApi(defaultClient);
        String keyPrefix = "keyPrefix_example"; // String |
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String taskId = "taskId_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<TaskCacheEntry> result = apiInstance.listTaskCacheEntriesApiV1TaskCacheGet(keyPrefix, namespace, flowId, taskId, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TaskCacheApi#listTaskCacheEntriesApiV1TaskCacheGet");
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
| **keyPrefix** | **String**|  | [optional] |
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **taskId** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;TaskCacheEntry&gt;**


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

## listTaskCacheEntriesApiV1TaskCacheGetWithHttpInfo

> ApiResponse<List<TaskCacheEntry>> listTaskCacheEntriesApiV1TaskCacheGetWithHttpInfo(keyPrefix, namespace, flowId, taskId, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Task Cache Entries

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TaskCacheApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TaskCacheApi apiInstance = new TaskCacheApi(defaultClient);
        String keyPrefix = "keyPrefix_example"; // String |
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String taskId = "taskId_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<TaskCacheEntry>> response = apiInstance.listTaskCacheEntriesApiV1TaskCacheGetWithHttpInfo(keyPrefix, namespace, flowId, taskId, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TaskCacheApi#listTaskCacheEntriesApiV1TaskCacheGet");
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
| **keyPrefix** | **String**|  | [optional] |
| **namespace** | **String**|  | [optional] |
| **flowId** | **String**|  | [optional] |
| **taskId** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;TaskCacheEntry&gt;**>


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


## purgeTaskCacheEntriesApiV1TaskCachePurgePost

> TaskCachePurgeResult purgeTaskCacheEntriesApiV1TaskCachePurgePost(taskCachePurgeRequest, authorization, xAmeshCSRF, xAmeshTenant)

Purge Task Cache Entries

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TaskCacheApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TaskCacheApi apiInstance = new TaskCacheApi(defaultClient);
        TaskCachePurgeRequest taskCachePurgeRequest = new TaskCachePurgeRequest(); // TaskCachePurgeRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            TaskCachePurgeResult result = apiInstance.purgeTaskCacheEntriesApiV1TaskCachePurgePost(taskCachePurgeRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TaskCacheApi#purgeTaskCacheEntriesApiV1TaskCachePurgePost");
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
| **taskCachePurgeRequest** | **TaskCachePurgeRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**TaskCachePurgeResult**


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

## purgeTaskCacheEntriesApiV1TaskCachePurgePostWithHttpInfo

> ApiResponse<TaskCachePurgeResult> purgeTaskCacheEntriesApiV1TaskCachePurgePostWithHttpInfo(taskCachePurgeRequest, authorization, xAmeshCSRF, xAmeshTenant)

Purge Task Cache Entries

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TaskCacheApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TaskCacheApi apiInstance = new TaskCacheApi(defaultClient);
        TaskCachePurgeRequest taskCachePurgeRequest = new TaskCachePurgeRequest(); // TaskCachePurgeRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<TaskCachePurgeResult> response = apiInstance.purgeTaskCacheEntriesApiV1TaskCachePurgePostWithHttpInfo(taskCachePurgeRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TaskCacheApi#purgeTaskCacheEntriesApiV1TaskCachePurgePost");
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
| **taskCachePurgeRequest** | **TaskCachePurgeRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**TaskCachePurgeResult**>


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
