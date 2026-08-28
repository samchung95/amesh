# ExternalOrchestrationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getExternalOrchestrationProfileApiV1OrchestrationProfileGet**](ExternalOrchestrationApi.md#getExternalOrchestrationProfileApiV1OrchestrationProfileGet) | **GET** /api/v1/orchestration/profile | Get External Orchestration Profile |
| [**getExternalOrchestrationProfileApiV1OrchestrationProfileGetWithHttpInfo**](ExternalOrchestrationApi.md#getExternalOrchestrationProfileApiV1OrchestrationProfileGetWithHttpInfo) | **GET** /api/v1/orchestration/profile | Get External Orchestration Profile |



## getExternalOrchestrationProfileApiV1OrchestrationProfileGet

> ExternalOrchestrationProfile getExternalOrchestrationProfileApiV1OrchestrationProfileGet()

Get External Orchestration Profile

Publish the client-neutral contract without exposing tenant data.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExternalOrchestrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExternalOrchestrationApi apiInstance = new ExternalOrchestrationApi(defaultClient);
        try {
            ExternalOrchestrationProfile result = apiInstance.getExternalOrchestrationProfileApiV1OrchestrationProfileGet();
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ExternalOrchestrationApi#getExternalOrchestrationProfileApiV1OrchestrationProfileGet");
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

**ExternalOrchestrationProfile**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

## getExternalOrchestrationProfileApiV1OrchestrationProfileGetWithHttpInfo

> ApiResponse<ExternalOrchestrationProfile> getExternalOrchestrationProfileApiV1OrchestrationProfileGetWithHttpInfo()

Get External Orchestration Profile

Publish the client-neutral contract without exposing tenant data.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ExternalOrchestrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ExternalOrchestrationApi apiInstance = new ExternalOrchestrationApi(defaultClient);
        try {
            ApiResponse<ExternalOrchestrationProfile> response = apiInstance.getExternalOrchestrationProfileApiV1OrchestrationProfileGetWithHttpInfo();
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ExternalOrchestrationApi#getExternalOrchestrationProfileApiV1OrchestrationProfileGet");
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

ApiResponse<**ExternalOrchestrationProfile**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
