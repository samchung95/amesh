# NamespacesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet**](NamespacesApi.md#getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet) | **GET** /api/v1/namespaces/{namespace}/workflow-metadata | Get Namespace Workflow Metadata |
| [**getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGetWithHttpInfo**](NamespacesApi.md#getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/workflow-metadata | Get Namespace Workflow Metadata |
| [**upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut**](NamespacesApi.md#upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut) | **PUT** /api/v1/namespaces/{namespace}/workflow-metadata | Upsert Namespace Workflow Metadata |
| [**upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPutWithHttpInfo**](NamespacesApi.md#upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPutWithHttpInfo) | **PUT** /api/v1/namespaces/{namespace}/workflow-metadata | Upsert Namespace Workflow Metadata |



## getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet

> NamespaceWorkflowMetadataView getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Namespace Workflow Metadata

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.NamespacesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        NamespacesApi apiInstance = new NamespacesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            NamespaceWorkflowMetadataView result = apiInstance.getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling NamespacesApi#getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**NamespaceWorkflowMetadataView**](NamespaceWorkflowMetadataView.md)


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

## getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGetWithHttpInfo

> ApiResponse<NamespaceWorkflowMetadataView> getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Namespace Workflow Metadata

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.NamespacesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        NamespacesApi apiInstance = new NamespacesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<NamespaceWorkflowMetadataView> response = apiInstance.getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling NamespacesApi#getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**NamespaceWorkflowMetadataView**](NamespaceWorkflowMetadataView.md)>


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


## upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut

> NamespaceWorkflowMetadata upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut(namespace, namespaceWorkflowMetadataUpdate, authorization, xAmeshCSRF, xAmeshTenant)

Upsert Namespace Workflow Metadata

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.NamespacesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        NamespacesApi apiInstance = new NamespacesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        NamespaceWorkflowMetadataUpdate namespaceWorkflowMetadataUpdate = new NamespaceWorkflowMetadataUpdate(); // NamespaceWorkflowMetadataUpdate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            NamespaceWorkflowMetadata result = apiInstance.upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut(namespace, namespaceWorkflowMetadataUpdate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling NamespacesApi#upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut");
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
| **namespaceWorkflowMetadataUpdate** | [**NamespaceWorkflowMetadataUpdate**](NamespaceWorkflowMetadataUpdate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**NamespaceWorkflowMetadata**](NamespaceWorkflowMetadata.md)


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

## upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPutWithHttpInfo

> ApiResponse<NamespaceWorkflowMetadata> upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPutWithHttpInfo(namespace, namespaceWorkflowMetadataUpdate, authorization, xAmeshCSRF, xAmeshTenant)

Upsert Namespace Workflow Metadata

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.NamespacesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        NamespacesApi apiInstance = new NamespacesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        NamespaceWorkflowMetadataUpdate namespaceWorkflowMetadataUpdate = new NamespaceWorkflowMetadataUpdate(); // NamespaceWorkflowMetadataUpdate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<NamespaceWorkflowMetadata> response = apiInstance.upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPutWithHttpInfo(namespace, namespaceWorkflowMetadataUpdate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling NamespacesApi#upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut");
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
| **namespaceWorkflowMetadataUpdate** | [**NamespaceWorkflowMetadataUpdate**](NamespaceWorkflowMetadataUpdate.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**NamespaceWorkflowMetadata**](NamespaceWorkflowMetadata.md)>


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
