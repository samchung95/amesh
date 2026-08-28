# QualityApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet**](QualityApi.md#getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet) | **GET** /api/v1/namespaces/{namespace}/differentials/{idempotency_key} | Get Differential |
| [**getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGetWithHttpInfo**](QualityApi.md#getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/differentials/{idempotency_key} | Get Differential |
| [**runDifferentialApiV1NamespacesNamespaceDifferentialsPost**](QualityApi.md#runDifferentialApiV1NamespacesNamespaceDifferentialsPost) | **POST** /api/v1/namespaces/{namespace}/differentials | Run Differential |
| [**runDifferentialApiV1NamespacesNamespaceDifferentialsPostWithHttpInfo**](QualityApi.md#runDifferentialApiV1NamespacesNamespaceDifferentialsPostWithHttpInfo) | **POST** /api/v1/namespaces/{namespace}/differentials | Run Differential |



## getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet

> ComparisonReport getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet(namespace, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF)

Get Differential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.QualityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        QualityApi apiInstance = new QualityApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ComparisonReport result = apiInstance.getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet(namespace, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling QualityApi#getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet");
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
| **idempotencyKey** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**ComparisonReport**


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

## getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGetWithHttpInfo

> ApiResponse<ComparisonReport> getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGetWithHttpInfo(namespace, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF)

Get Differential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.QualityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        QualityApi apiInstance = new QualityApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ComparisonReport> response = apiInstance.getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGetWithHttpInfo(namespace, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling QualityApi#getDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet");
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
| **idempotencyKey** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**ComparisonReport**>


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


## runDifferentialApiV1NamespacesNamespaceDifferentialsPost

> ComparisonReport runDifferentialApiV1NamespacesNamespaceDifferentialsPost(namespace, differentialSpec, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF)

Run Differential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.QualityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        QualityApi apiInstance = new QualityApi(defaultClient);
        String namespace = "namespace_example"; // String |
        DifferentialSpec differentialSpec = new DifferentialSpec(); // DifferentialSpec |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ComparisonReport result = apiInstance.runDifferentialApiV1NamespacesNamespaceDifferentialsPost(namespace, differentialSpec, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling QualityApi#runDifferentialApiV1NamespacesNamespaceDifferentialsPost");
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
| **differentialSpec** | **DifferentialSpec**|  | |
| **idempotencyKey** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**ComparisonReport**


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

## runDifferentialApiV1NamespacesNamespaceDifferentialsPostWithHttpInfo

> ApiResponse<ComparisonReport> runDifferentialApiV1NamespacesNamespaceDifferentialsPostWithHttpInfo(namespace, differentialSpec, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF)

Run Differential

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.QualityApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        QualityApi apiInstance = new QualityApi(defaultClient);
        String namespace = "namespace_example"; // String |
        DifferentialSpec differentialSpec = new DifferentialSpec(); // DifferentialSpec |
        String idempotencyKey = "idempotencyKey_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ComparisonReport> response = apiInstance.runDifferentialApiV1NamespacesNamespaceDifferentialsPostWithHttpInfo(namespace, differentialSpec, idempotencyKey, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling QualityApi#runDifferentialApiV1NamespacesNamespaceDifferentialsPost");
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
| **differentialSpec** | **DifferentialSpec**|  | |
| **idempotencyKey** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**ComparisonReport**>


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
