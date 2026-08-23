# HumanTasksApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost**](HumanTasksApi.md#actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost) | **POST** /api/v1/human-tasks/{human_task_id}/actions | Act On Human Task |
| [**actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPostWithHttpInfo**](HumanTasksApi.md#actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPostWithHttpInfo) | **POST** /api/v1/human-tasks/{human_task_id}/actions | Act On Human Task |
| [**listHumanTaskNotificationsApiV1HumanTaskNotificationsGet**](HumanTasksApi.md#listHumanTaskNotificationsApiV1HumanTaskNotificationsGet) | **GET** /api/v1/human-task-notifications | List Human Task Notifications |
| [**listHumanTaskNotificationsApiV1HumanTaskNotificationsGetWithHttpInfo**](HumanTasksApi.md#listHumanTaskNotificationsApiV1HumanTaskNotificationsGetWithHttpInfo) | **GET** /api/v1/human-task-notifications | List Human Task Notifications |
| [**listHumanTasksApiV1HumanTasksGet**](HumanTasksApi.md#listHumanTasksApiV1HumanTasksGet) | **GET** /api/v1/human-tasks | List Human Tasks |
| [**listHumanTasksApiV1HumanTasksGetWithHttpInfo**](HumanTasksApi.md#listHumanTasksApiV1HumanTasksGetWithHttpInfo) | **GET** /api/v1/human-tasks | List Human Tasks |



## actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost

> HumanTask actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost(humanTaskId, humanTaskActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Act On Human Task

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.HumanTasksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        HumanTasksApi apiInstance = new HumanTasksApi(defaultClient);
        UUID humanTaskId = UUID.randomUUID(); // UUID |
        HumanTaskActionRequest humanTaskActionRequest = new HumanTaskActionRequest(); // HumanTaskActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            HumanTask result = apiInstance.actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost(humanTaskId, humanTaskActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling HumanTasksApi#actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost");
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
| **humanTaskId** | **UUID**|  | |
| **humanTaskActionRequest** | [**HumanTaskActionRequest**](HumanTaskActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**HumanTask**](HumanTask.md)


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

## actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPostWithHttpInfo

> ApiResponse<HumanTask> actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPostWithHttpInfo(humanTaskId, humanTaskActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Act On Human Task

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.HumanTasksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        HumanTasksApi apiInstance = new HumanTasksApi(defaultClient);
        UUID humanTaskId = UUID.randomUUID(); // UUID |
        HumanTaskActionRequest humanTaskActionRequest = new HumanTaskActionRequest(); // HumanTaskActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<HumanTask> response = apiInstance.actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPostWithHttpInfo(humanTaskId, humanTaskActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling HumanTasksApi#actOnHumanTaskApiV1HumanTasksHumanTaskIdActionsPost");
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
| **humanTaskId** | **UUID**|  | |
| **humanTaskActionRequest** | [**HumanTaskActionRequest**](HumanTaskActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**HumanTask**](HumanTask.md)>


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


## listHumanTaskNotificationsApiV1HumanTaskNotificationsGet

> List<HumanTaskNotification> listHumanTaskNotificationsApiV1HumanTaskNotificationsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Human Task Notifications

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.HumanTasksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        HumanTasksApi apiInstance = new HumanTasksApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<HumanTaskNotification> result = apiInstance.listHumanTaskNotificationsApiV1HumanTaskNotificationsGet(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling HumanTasksApi#listHumanTaskNotificationsApiV1HumanTaskNotificationsGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;HumanTaskNotification&gt;**](HumanTaskNotification.md)


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

## listHumanTaskNotificationsApiV1HumanTaskNotificationsGetWithHttpInfo

> ApiResponse<List<HumanTaskNotification>> listHumanTaskNotificationsApiV1HumanTaskNotificationsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Human Task Notifications

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.HumanTasksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        HumanTasksApi apiInstance = new HumanTasksApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<HumanTaskNotification>> response = apiInstance.listHumanTaskNotificationsApiV1HumanTaskNotificationsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling HumanTasksApi#listHumanTaskNotificationsApiV1HumanTaskNotificationsGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;HumanTaskNotification&gt;**](HumanTaskNotification.md)>


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


## listHumanTasksApiV1HumanTasksGet

> List<HumanTask> listHumanTasksApiV1HumanTasksGet(namespace, includeClosed, authorization, xAmeshCSRF, xAmeshTenant)

List Human Tasks

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.HumanTasksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        HumanTasksApi apiInstance = new HumanTasksApi(defaultClient);
        String namespace = "namespace_example"; // String |
        Boolean includeClosed = false; // Boolean |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<HumanTask> result = apiInstance.listHumanTasksApiV1HumanTasksGet(namespace, includeClosed, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling HumanTasksApi#listHumanTasksApiV1HumanTasksGet");
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
| **includeClosed** | **Boolean**|  | [optional] [default to false] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;HumanTask&gt;**](HumanTask.md)


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

## listHumanTasksApiV1HumanTasksGetWithHttpInfo

> ApiResponse<List<HumanTask>> listHumanTasksApiV1HumanTasksGetWithHttpInfo(namespace, includeClosed, authorization, xAmeshCSRF, xAmeshTenant)

List Human Tasks

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.HumanTasksApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        HumanTasksApi apiInstance = new HumanTasksApi(defaultClient);
        String namespace = "namespace_example"; // String |
        Boolean includeClosed = false; // Boolean |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<HumanTask>> response = apiInstance.listHumanTasksApiV1HumanTasksGetWithHttpInfo(namespace, includeClosed, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling HumanTasksApi#listHumanTasksApiV1HumanTasksGet");
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
| **includeClosed** | **Boolean**|  | [optional] [default to false] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;HumanTask&gt;**](HumanTask.md)>


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
