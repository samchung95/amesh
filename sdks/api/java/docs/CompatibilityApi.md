# CompatibilityApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost**](CompatibilityApi.md#createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost) | **POST** /api/v1/executions/{namespace}/{flow_id} | Create Kestra Execution |
| [**createKestraExecutionApiV1ExecutionsNamespaceFlowIdPostWithHttpInfo**](CompatibilityApi.md#createKestraExecutionApiV1ExecutionsNamespaceFlowIdPostWithHttpInfo) | **POST** /api/v1/executions/{namespace}/{flow_id} | Create Kestra Execution |
| [**getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet**](CompatibilityApi.md#getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet) | **GET** /api/v1/compatibility/kestra/manifest | Get Kestra Compatibility Manifest |
| [**getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGetWithHttpInfo**](CompatibilityApi.md#getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGetWithHttpInfo) | **GET** /api/v1/compatibility/kestra/manifest | Get Kestra Compatibility Manifest |
| [**validateKestraFlowApiV1MainFlowsValidatePost**](CompatibilityApi.md#validateKestraFlowApiV1MainFlowsValidatePost) | **POST** /api/v1/main/flows/validate | Validate Kestra Flow |
| [**validateKestraFlowApiV1MainFlowsValidatePostWithHttpInfo**](CompatibilityApi.md#validateKestraFlowApiV1MainFlowsValidatePostWithHttpInfo) | **POST** /api/v1/main/flows/validate | Validate Kestra Flow |



## createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost

> ExecutionDetail createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost(namespace, flowId, kestraExecutionRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant)

Create Kestra Execution

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CompatibilityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CompatibilityApi apiInstance = new CompatibilityApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        KestraExecutionRequest kestraExecutionRequest = new KestraExecutionRequest(); // KestraExecutionRequest |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xCorrelationID = "xCorrelationID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ExecutionDetail result = apiInstance.createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost(namespace, flowId, kestraExecutionRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CompatibilityApi#createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost");
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
| **kestraExecutionRequest** | **KestraExecutionRequest**|  | |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **xCorrelationID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**ExecutionDetail**


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

## createKestraExecutionApiV1ExecutionsNamespaceFlowIdPostWithHttpInfo

> ApiResponse<ExecutionDetail> createKestraExecutionApiV1ExecutionsNamespaceFlowIdPostWithHttpInfo(namespace, flowId, kestraExecutionRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant)

Create Kestra Execution

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CompatibilityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CompatibilityApi apiInstance = new CompatibilityApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        KestraExecutionRequest kestraExecutionRequest = new KestraExecutionRequest(); // KestraExecutionRequest |
        String prefer = "prefer_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xCorrelationID = "xCorrelationID_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ExecutionDetail> response = apiInstance.createKestraExecutionApiV1ExecutionsNamespaceFlowIdPostWithHttpInfo(namespace, flowId, kestraExecutionRequest, prefer, idempotencyKey, xCorrelationID, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling CompatibilityApi#createKestraExecutionApiV1ExecutionsNamespaceFlowIdPost");
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
| **kestraExecutionRequest** | **KestraExecutionRequest**|  | |
| **prefer** | **String**|  | [optional] |
| **idempotencyKey** | **String**|  | [optional] |
| **xCorrelationID** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**ExecutionDetail**>


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


## getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet

> Map<String, Object> getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet()

Get Kestra Compatibility Manifest

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CompatibilityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CompatibilityApi apiInstance = new CompatibilityApi(defaultClient);
        try {
            Map<String, Object> result = apiInstance.getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet();
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CompatibilityApi#getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

**Map&lt;String, Object&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

## getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGetWithHttpInfo

> ApiResponse<Map<String, Object>> getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGetWithHttpInfo()

Get Kestra Compatibility Manifest

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CompatibilityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CompatibilityApi apiInstance = new CompatibilityApi(defaultClient);
        try {
            ApiResponse<Map<String, Object>> response = apiInstance.getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGetWithHttpInfo();
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling CompatibilityApi#getKestraCompatibilityManifestApiV1CompatibilityKestraManifestGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

ApiResponse<**Map&lt;String, Object&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |


## validateKestraFlowApiV1MainFlowsValidatePost

> KestraFlowImport validateKestraFlowApiV1MainFlowsValidatePost()

Validate Kestra Flow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CompatibilityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CompatibilityApi apiInstance = new CompatibilityApi(defaultClient);
        try {
            KestraFlowImport result = apiInstance.validateKestraFlowApiV1MainFlowsValidatePost();
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling CompatibilityApi#validateKestraFlowApiV1MainFlowsValidatePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

**KestraFlowImport**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

## validateKestraFlowApiV1MainFlowsValidatePostWithHttpInfo

> ApiResponse<KestraFlowImport> validateKestraFlowApiV1MainFlowsValidatePostWithHttpInfo()

Validate Kestra Flow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.CompatibilityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        CompatibilityApi apiInstance = new CompatibilityApi(defaultClient);
        try {
            ApiResponse<KestraFlowImport> response = apiInstance.validateKestraFlowApiV1MainFlowsValidatePostWithHttpInfo();
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling CompatibilityApi#validateKestraFlowApiV1MainFlowsValidatePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

ApiResponse<**KestraFlowImport**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
