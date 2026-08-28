# WorkersApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**drainWorkerApiV1WorkersWorkerIdDrainPost**](WorkersApi.md#drainWorkerApiV1WorkersWorkerIdDrainPost) | **POST** /api/v1/workers/{worker_id}/drain | Drain Worker |
| [**drainWorkerApiV1WorkersWorkerIdDrainPostWithHttpInfo**](WorkersApi.md#drainWorkerApiV1WorkersWorkerIdDrainPostWithHttpInfo) | **POST** /api/v1/workers/{worker_id}/drain | Drain Worker |
| [**listRunnerCapabilitiesApiV1RunnersCapabilitiesGet**](WorkersApi.md#listRunnerCapabilitiesApiV1RunnersCapabilitiesGet) | **GET** /api/v1/runners/capabilities | List Runner Capabilities |
| [**listRunnerCapabilitiesApiV1RunnersCapabilitiesGetWithHttpInfo**](WorkersApi.md#listRunnerCapabilitiesApiV1RunnersCapabilitiesGetWithHttpInfo) | **GET** /api/v1/runners/capabilities | List Runner Capabilities |
| [**listWorkersApiV1WorkersGet**](WorkersApi.md#listWorkersApiV1WorkersGet) | **GET** /api/v1/workers | List Workers |
| [**listWorkersApiV1WorkersGetWithHttpInfo**](WorkersApi.md#listWorkersApiV1WorkersGetWithHttpInfo) | **GET** /api/v1/workers | List Workers |



## drainWorkerApiV1WorkersWorkerIdDrainPost

> WorkerInventory drainWorkerApiV1WorkersWorkerIdDrainPost(workerId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Drain Worker

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.WorkersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkersApi apiInstance = new WorkersApi(defaultClient);
        UUID workerId = UUID.randomUUID(); // UUID |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            WorkerInventory result = apiInstance.drainWorkerApiV1WorkersWorkerIdDrainPost(workerId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkersApi#drainWorkerApiV1WorkersWorkerIdDrainPost");
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
| **workerId** | **UUID**|  | |
| **expectedVersion** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**WorkerInventory**


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

## drainWorkerApiV1WorkersWorkerIdDrainPostWithHttpInfo

> ApiResponse<WorkerInventory> drainWorkerApiV1WorkersWorkerIdDrainPostWithHttpInfo(workerId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Drain Worker

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.WorkersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkersApi apiInstance = new WorkersApi(defaultClient);
        UUID workerId = UUID.randomUUID(); // UUID |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<WorkerInventory> response = apiInstance.drainWorkerApiV1WorkersWorkerIdDrainPostWithHttpInfo(workerId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkersApi#drainWorkerApiV1WorkersWorkerIdDrainPost");
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
| **workerId** | **UUID**|  | |
| **expectedVersion** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**WorkerInventory**>


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


## listRunnerCapabilitiesApiV1RunnersCapabilitiesGet

> List<RunnerCapabilities> listRunnerCapabilitiesApiV1RunnersCapabilitiesGet(authorization, xAmeshCSRF, xAmeshTenant)

List Runner Capabilities

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.WorkersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkersApi apiInstance = new WorkersApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<RunnerCapabilities> result = apiInstance.listRunnerCapabilitiesApiV1RunnersCapabilitiesGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkersApi#listRunnerCapabilitiesApiV1RunnersCapabilitiesGet");
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

**List&lt;RunnerCapabilities&gt;**


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

## listRunnerCapabilitiesApiV1RunnersCapabilitiesGetWithHttpInfo

> ApiResponse<List<RunnerCapabilities>> listRunnerCapabilitiesApiV1RunnersCapabilitiesGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Runner Capabilities

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.WorkersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkersApi apiInstance = new WorkersApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<RunnerCapabilities>> response = apiInstance.listRunnerCapabilitiesApiV1RunnersCapabilitiesGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkersApi#listRunnerCapabilitiesApiV1RunnersCapabilitiesGet");
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

ApiResponse<**List&lt;RunnerCapabilities&gt;**>


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


## listWorkersApiV1WorkersGet

> List<WorkerInventory> listWorkersApiV1WorkersGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Workers

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.WorkersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkersApi apiInstance = new WorkersApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<WorkerInventory> result = apiInstance.listWorkersApiV1WorkersGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkersApi#listWorkersApiV1WorkersGet");
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
| **limit** | **Integer**|  | [optional] |
| **filter** | **List&lt;String&gt;**| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;WorkerInventory&gt;**


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

## listWorkersApiV1WorkersGetWithHttpInfo

> ApiResponse<List<WorkerInventory>> listWorkersApiV1WorkersGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Workers

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.WorkersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        WorkersApi apiInstance = new WorkersApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<WorkerInventory>> response = apiInstance.listWorkersApiV1WorkersGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling WorkersApi#listWorkersApiV1WorkersGet");
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
| **limit** | **Integer**|  | [optional] |
| **filter** | **List&lt;String&gt;**| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;WorkerInventory&gt;**>


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
