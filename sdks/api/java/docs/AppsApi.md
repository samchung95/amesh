# AppsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getWorkflowAppApiV1AppsNamespaceAppIdGet**](AppsApi.md#getWorkflowAppApiV1AppsNamespaceAppIdGet) | **GET** /api/v1/apps/{namespace}/{app_id} | Get Workflow App |
| [**getWorkflowAppApiV1AppsNamespaceAppIdGetWithHttpInfo**](AppsApi.md#getWorkflowAppApiV1AppsNamespaceAppIdGetWithHttpInfo) | **GET** /api/v1/apps/{namespace}/{app_id} | Get Workflow App |
| [**launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost**](AppsApi.md#launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost) | **POST** /api/v1/apps/{namespace}/{app_id}/launch | Launch Workflow App |
| [**launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPostWithHttpInfo**](AppsApi.md#launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPostWithHttpInfo) | **POST** /api/v1/apps/{namespace}/{app_id}/launch | Launch Workflow App |
| [**listWorkflowAppsApiV1AppsGet**](AppsApi.md#listWorkflowAppsApiV1AppsGet) | **GET** /api/v1/apps | List Workflow Apps |
| [**listWorkflowAppsApiV1AppsGetWithHttpInfo**](AppsApi.md#listWorkflowAppsApiV1AppsGetWithHttpInfo) | **GET** /api/v1/apps | List Workflow Apps |
| [**upsertWorkflowAppApiV1AppsNamespaceAppIdPut**](AppsApi.md#upsertWorkflowAppApiV1AppsNamespaceAppIdPut) | **PUT** /api/v1/apps/{namespace}/{app_id} | Upsert Workflow App |
| [**upsertWorkflowAppApiV1AppsNamespaceAppIdPutWithHttpInfo**](AppsApi.md#upsertWorkflowAppApiV1AppsNamespaceAppIdPutWithHttpInfo) | **PUT** /api/v1/apps/{namespace}/{app_id} | Upsert Workflow App |



## getWorkflowAppApiV1AppsNamespaceAppIdGet

> WorkflowApp getWorkflowAppApiV1AppsNamespaceAppIdGet(namespace, appId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Workflow App

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AppsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AppsApi apiInstance = new AppsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String appId = "appId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            WorkflowApp result = apiInstance.getWorkflowAppApiV1AppsNamespaceAppIdGet(namespace, appId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AppsApi#getWorkflowAppApiV1AppsNamespaceAppIdGet");
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
| **appId** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**WorkflowApp**](WorkflowApp.md)


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

## getWorkflowAppApiV1AppsNamespaceAppIdGetWithHttpInfo

> ApiResponse<WorkflowApp> getWorkflowAppApiV1AppsNamespaceAppIdGetWithHttpInfo(namespace, appId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Workflow App

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AppsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AppsApi apiInstance = new AppsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String appId = "appId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<WorkflowApp> response = apiInstance.getWorkflowAppApiV1AppsNamespaceAppIdGetWithHttpInfo(namespace, appId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AppsApi#getWorkflowAppApiV1AppsNamespaceAppIdGet");
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
| **appId** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**WorkflowApp**](WorkflowApp.md)>


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


## launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost

> ExecutionDetail launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost(namespace, appId, workflowAppLaunchRequest, authorization, xAmeshCSRF, xAmeshTenant)

Launch Workflow App

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AppsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AppsApi apiInstance = new AppsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String appId = "appId_example"; // String |
        WorkflowAppLaunchRequest workflowAppLaunchRequest = new WorkflowAppLaunchRequest(); // WorkflowAppLaunchRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ExecutionDetail result = apiInstance.launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost(namespace, appId, workflowAppLaunchRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AppsApi#launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost");
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
| **appId** | **String**|  | |
| **workflowAppLaunchRequest** | [**WorkflowAppLaunchRequest**](WorkflowAppLaunchRequest.md)|  | |
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

## launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPostWithHttpInfo

> ApiResponse<ExecutionDetail> launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPostWithHttpInfo(namespace, appId, workflowAppLaunchRequest, authorization, xAmeshCSRF, xAmeshTenant)

Launch Workflow App

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AppsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AppsApi apiInstance = new AppsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String appId = "appId_example"; // String |
        WorkflowAppLaunchRequest workflowAppLaunchRequest = new WorkflowAppLaunchRequest(); // WorkflowAppLaunchRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ExecutionDetail> response = apiInstance.launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPostWithHttpInfo(namespace, appId, workflowAppLaunchRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AppsApi#launchWorkflowAppApiV1AppsNamespaceAppIdLaunchPost");
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
| **appId** | **String**|  | |
| **workflowAppLaunchRequest** | [**WorkflowAppLaunchRequest**](WorkflowAppLaunchRequest.md)|  | |
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


## listWorkflowAppsApiV1AppsGet

> List<WorkflowApp> listWorkflowAppsApiV1AppsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Workflow Apps

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AppsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AppsApi apiInstance = new AppsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<WorkflowApp> result = apiInstance.listWorkflowAppsApiV1AppsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AppsApi#listWorkflowAppsApiV1AppsGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;WorkflowApp&gt;**](WorkflowApp.md)


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

## listWorkflowAppsApiV1AppsGetWithHttpInfo

> ApiResponse<List<WorkflowApp>> listWorkflowAppsApiV1AppsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Workflow Apps

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AppsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AppsApi apiInstance = new AppsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<WorkflowApp>> response = apiInstance.listWorkflowAppsApiV1AppsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AppsApi#listWorkflowAppsApiV1AppsGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;WorkflowApp&gt;**](WorkflowApp.md)>


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


## upsertWorkflowAppApiV1AppsNamespaceAppIdPut

> WorkflowApp upsertWorkflowAppApiV1AppsNamespaceAppIdPut(namespace, appId, workflowAppUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Upsert Workflow App

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AppsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AppsApi apiInstance = new AppsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String appId = "appId_example"; // String |
        WorkflowAppUpsertRequest workflowAppUpsertRequest = new WorkflowAppUpsertRequest(); // WorkflowAppUpsertRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            WorkflowApp result = apiInstance.upsertWorkflowAppApiV1AppsNamespaceAppIdPut(namespace, appId, workflowAppUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AppsApi#upsertWorkflowAppApiV1AppsNamespaceAppIdPut");
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
| **appId** | **String**|  | |
| **workflowAppUpsertRequest** | [**WorkflowAppUpsertRequest**](WorkflowAppUpsertRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**WorkflowApp**](WorkflowApp.md)


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

## upsertWorkflowAppApiV1AppsNamespaceAppIdPutWithHttpInfo

> ApiResponse<WorkflowApp> upsertWorkflowAppApiV1AppsNamespaceAppIdPutWithHttpInfo(namespace, appId, workflowAppUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Upsert Workflow App

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AppsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AppsApi apiInstance = new AppsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String appId = "appId_example"; // String |
        WorkflowAppUpsertRequest workflowAppUpsertRequest = new WorkflowAppUpsertRequest(); // WorkflowAppUpsertRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<WorkflowApp> response = apiInstance.upsertWorkflowAppApiV1AppsNamespaceAppIdPutWithHttpInfo(namespace, appId, workflowAppUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AppsApi#upsertWorkflowAppApiV1AppsNamespaceAppIdPut");
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
| **appId** | **String**|  | |
| **workflowAppUpsertRequest** | [**WorkflowAppUpsertRequest**](WorkflowAppUpsertRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**WorkflowApp**](WorkflowApp.md)>


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
