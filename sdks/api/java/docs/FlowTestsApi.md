# FlowTestsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete**](FlowTestsApi.md#deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/tests/{test_id} | Delete Flow Test |
| [**deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDeleteWithHttpInfo**](FlowTestsApi.md#deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDeleteWithHttpInfo) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/tests/{test_id} | Delete Flow Test |
| [**getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet**](FlowTestsApi.md#getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet) | **GET** /api/v1/namespaces/{namespace}/flow-test-gate | Get Flow Test Gate |
| [**getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGetWithHttpInfo**](FlowTestsApi.md#getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/flow-test-gate | Get Flow Test Gate |
| [**listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet**](FlowTestsApi.md#listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests/runs | List Flow Test Runs |
| [**listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGetWithHttpInfo**](FlowTestsApi.md#listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGetWithHttpInfo) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests/runs | List Flow Test Runs |
| [**listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet**](FlowTestsApi.md#listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests | List Flow Tests |
| [**listFlowTestsApiV1FlowsNamespaceFlowIdTestsGetWithHttpInfo**](FlowTestsApi.md#listFlowTestsApiV1FlowsNamespaceFlowIdTestsGetWithHttpInfo) | **GET** /api/v1/flows/{namespace}/{flow_id}/tests | List Flow Tests |
| [**runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost**](FlowTestsApi.md#runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost) | **POST** /api/v1/flows/{namespace}/{flow_id}/tests/runs | Run Flow Tests |
| [**runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPostWithHttpInfo**](FlowTestsApi.md#runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPostWithHttpInfo) | **POST** /api/v1/flows/{namespace}/{flow_id}/tests/runs | Run Flow Tests |
| [**saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut**](FlowTestsApi.md#saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut) | **PUT** /api/v1/flows/{namespace}/{flow_id}/tests | Save Flow Test |
| [**saveFlowTestApiV1FlowsNamespaceFlowIdTestsPutWithHttpInfo**](FlowTestsApi.md#saveFlowTestApiV1FlowsNamespaceFlowIdTestsPutWithHttpInfo) | **PUT** /api/v1/flows/{namespace}/{flow_id}/tests | Save Flow Test |
| [**updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut**](FlowTestsApi.md#updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut) | **PUT** /api/v1/namespaces/{namespace}/flow-test-gate | Update Flow Test Gate |
| [**updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePutWithHttpInfo**](FlowTestsApi.md#updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePutWithHttpInfo) | **PUT** /api/v1/namespaces/{namespace}/flow-test-gate | Update Flow Test Gate |



## deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete

> void deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete(namespace, flowId, testId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Delete Flow Test

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String testId = "testId_example"; // String |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete(namespace, flowId, testId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete");
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
| **testId** | **String**|  | |
| **expectedVersion** | **Integer**|  | |
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
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDeleteWithHttpInfo

> ApiResponse<Void> deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDeleteWithHttpInfo(namespace, flowId, testId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Delete Flow Test

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String testId = "testId_example"; // String |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDeleteWithHttpInfo(namespace, flowId, testId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#deleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete");
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
| **testId** | **String**|  | |
| **expectedVersion** | **Integer**|  | |
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
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet

> FlowTestQualityGate getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Test Gate

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowTestQualityGate result = apiInstance.getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet");
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

**FlowTestQualityGate**


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

## getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGetWithHttpInfo

> ApiResponse<FlowTestQualityGate> getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Test Gate

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowTestQualityGate> response = apiInstance.getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#getFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet");
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

ApiResponse<**FlowTestQualityGate**>


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


## listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet

> List<FlowTestRunResult> listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet(namespace, flowId, revision, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Flow Test Runs

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        Integer limit = 50; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<FlowTestRunResult> result = apiInstance.listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet(namespace, flowId, revision, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet");
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
| **revision** | **Integer**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 50] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;FlowTestRunResult&gt;**


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

## listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGetWithHttpInfo

> ApiResponse<List<FlowTestRunResult>> listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGetWithHttpInfo(namespace, flowId, revision, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Flow Test Runs

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        Integer limit = 50; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<FlowTestRunResult>> response = apiInstance.listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGetWithHttpInfo(namespace, flowId, revision, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#listFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet");
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
| **revision** | **Integer**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 50] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;FlowTestRunResult&gt;**>


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


## listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet

> List<FlowTestDefinition> listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

List Flow Tests

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<FlowTestDefinition> result = apiInstance.listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet");
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
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;FlowTestDefinition&gt;**


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

## listFlowTestsApiV1FlowsNamespaceFlowIdTestsGetWithHttpInfo

> ApiResponse<List<FlowTestDefinition>> listFlowTestsApiV1FlowsNamespaceFlowIdTestsGetWithHttpInfo(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

List Flow Tests

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<FlowTestDefinition>> response = apiInstance.listFlowTestsApiV1FlowsNamespaceFlowIdTestsGetWithHttpInfo(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#listFlowTestsApiV1FlowsNamespaceFlowIdTestsGet");
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
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;FlowTestDefinition&gt;**>


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


## runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost

> FlowTestRunResult runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost(namespace, flowId, revision, flowTestRunRequest, authorization, xAmeshCSRF, xAmeshTenant)

Run Flow Tests

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        FlowTestRunRequest flowTestRunRequest = new FlowTestRunRequest(); // FlowTestRunRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowTestRunResult result = apiInstance.runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost(namespace, flowId, revision, flowTestRunRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost");
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
| **revision** | **Integer**|  | |
| **flowTestRunRequest** | **FlowTestRunRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowTestRunResult**


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

## runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPostWithHttpInfo

> ApiResponse<FlowTestRunResult> runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPostWithHttpInfo(namespace, flowId, revision, flowTestRunRequest, authorization, xAmeshCSRF, xAmeshTenant)

Run Flow Tests

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        FlowTestRunRequest flowTestRunRequest = new FlowTestRunRequest(); // FlowTestRunRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowTestRunResult> response = apiInstance.runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPostWithHttpInfo(namespace, flowId, revision, flowTestRunRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#runFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost");
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
| **revision** | **Integer**|  | |
| **flowTestRunRequest** | **FlowTestRunRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowTestRunResult**>


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


## saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut

> FlowTestDefinition saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut(namespace, flowId, flowTestDefinitionCreateRequest, authorization, xAmeshCSRF, xAmeshTenant)

Save Flow Test

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        FlowTestDefinitionCreateRequest flowTestDefinitionCreateRequest = new FlowTestDefinitionCreateRequest(); // FlowTestDefinitionCreateRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowTestDefinition result = apiInstance.saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut(namespace, flowId, flowTestDefinitionCreateRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut");
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
| **flowTestDefinitionCreateRequest** | **FlowTestDefinitionCreateRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowTestDefinition**


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

## saveFlowTestApiV1FlowsNamespaceFlowIdTestsPutWithHttpInfo

> ApiResponse<FlowTestDefinition> saveFlowTestApiV1FlowsNamespaceFlowIdTestsPutWithHttpInfo(namespace, flowId, flowTestDefinitionCreateRequest, authorization, xAmeshCSRF, xAmeshTenant)

Save Flow Test

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        FlowTestDefinitionCreateRequest flowTestDefinitionCreateRequest = new FlowTestDefinitionCreateRequest(); // FlowTestDefinitionCreateRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowTestDefinition> response = apiInstance.saveFlowTestApiV1FlowsNamespaceFlowIdTestsPutWithHttpInfo(namespace, flowId, flowTestDefinitionCreateRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#saveFlowTestApiV1FlowsNamespaceFlowIdTestsPut");
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
| **flowTestDefinitionCreateRequest** | **FlowTestDefinitionCreateRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowTestDefinition**>


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


## updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut

> FlowTestQualityGate updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut(namespace, flowTestQualityGateUpdate, authorization, xAmeshCSRF, xAmeshTenant)

Update Flow Test Gate

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        FlowTestQualityGateUpdate flowTestQualityGateUpdate = new FlowTestQualityGateUpdate(); // FlowTestQualityGateUpdate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowTestQualityGate result = apiInstance.updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut(namespace, flowTestQualityGateUpdate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut");
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
| **flowTestQualityGateUpdate** | **FlowTestQualityGateUpdate**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowTestQualityGate**


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

## updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePutWithHttpInfo

> ApiResponse<FlowTestQualityGate> updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePutWithHttpInfo(namespace, flowTestQualityGateUpdate, authorization, xAmeshCSRF, xAmeshTenant)

Update Flow Test Gate

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowTestsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowTestsApi apiInstance = new FlowTestsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        FlowTestQualityGateUpdate flowTestQualityGateUpdate = new FlowTestQualityGateUpdate(); // FlowTestQualityGateUpdate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowTestQualityGate> response = apiInstance.updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePutWithHttpInfo(namespace, flowTestQualityGateUpdate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowTestsApi#updateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut");
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
| **flowTestQualityGateUpdate** | **FlowTestQualityGateUpdate**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowTestQualityGate**>


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
