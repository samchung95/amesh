# LifecycleApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost**](LifecycleApi.md#createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost) | **POST** /api/v1/lifecycle/legal-holds | Create Lifecycle Legal Hold |
| [**createLifecycleLegalHoldApiV1LifecycleLegalHoldsPostWithHttpInfo**](LifecycleApi.md#createLifecycleLegalHoldApiV1LifecycleLegalHoldsPostWithHttpInfo) | **POST** /api/v1/lifecycle/legal-holds | Create Lifecycle Legal Hold |
| [**createLifecyclePolicyApiV1LifecyclePoliciesPost**](LifecycleApi.md#createLifecyclePolicyApiV1LifecyclePoliciesPost) | **POST** /api/v1/lifecycle/policies | Create Lifecycle Policy |
| [**createLifecyclePolicyApiV1LifecyclePoliciesPostWithHttpInfo**](LifecycleApi.md#createLifecyclePolicyApiV1LifecyclePoliciesPostWithHttpInfo) | **POST** /api/v1/lifecycle/policies | Create Lifecycle Policy |
| [**executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost**](LifecycleApi.md#executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost) | **POST** /api/v1/lifecycle/jobs/{job_id}/execute | Execute Lifecycle Job |
| [**executeLifecycleJobApiV1LifecycleJobsJobIdExecutePostWithHttpInfo**](LifecycleApi.md#executeLifecycleJobApiV1LifecycleJobsJobIdExecutePostWithHttpInfo) | **POST** /api/v1/lifecycle/jobs/{job_id}/execute | Execute Lifecycle Job |
| [**getLifecycleJobApiV1LifecycleJobsJobIdGet**](LifecycleApi.md#getLifecycleJobApiV1LifecycleJobsJobIdGet) | **GET** /api/v1/lifecycle/jobs/{job_id} | Get Lifecycle Job |
| [**getLifecycleJobApiV1LifecycleJobsJobIdGetWithHttpInfo**](LifecycleApi.md#getLifecycleJobApiV1LifecycleJobsJobIdGetWithHttpInfo) | **GET** /api/v1/lifecycle/jobs/{job_id} | Get Lifecycle Job |
| [**listLifecycleJobsApiV1LifecycleJobsGet**](LifecycleApi.md#listLifecycleJobsApiV1LifecycleJobsGet) | **GET** /api/v1/lifecycle/jobs | List Lifecycle Jobs |
| [**listLifecycleJobsApiV1LifecycleJobsGetWithHttpInfo**](LifecycleApi.md#listLifecycleJobsApiV1LifecycleJobsGetWithHttpInfo) | **GET** /api/v1/lifecycle/jobs | List Lifecycle Jobs |
| [**listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet**](LifecycleApi.md#listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet) | **GET** /api/v1/lifecycle/legal-holds | List Lifecycle Legal Holds |
| [**listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGetWithHttpInfo**](LifecycleApi.md#listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGetWithHttpInfo) | **GET** /api/v1/lifecycle/legal-holds | List Lifecycle Legal Holds |
| [**listLifecyclePoliciesApiV1LifecyclePoliciesGet**](LifecycleApi.md#listLifecyclePoliciesApiV1LifecyclePoliciesGet) | **GET** /api/v1/lifecycle/policies | List Lifecycle Policies |
| [**listLifecyclePoliciesApiV1LifecyclePoliciesGetWithHttpInfo**](LifecycleApi.md#listLifecyclePoliciesApiV1LifecyclePoliciesGetWithHttpInfo) | **GET** /api/v1/lifecycle/policies | List Lifecycle Policies |
| [**previewLifecyclePurgeApiV1LifecyclePreviewsPost**](LifecycleApi.md#previewLifecyclePurgeApiV1LifecyclePreviewsPost) | **POST** /api/v1/lifecycle/previews | Preview Lifecycle Purge |
| [**previewLifecyclePurgeApiV1LifecyclePreviewsPostWithHttpInfo**](LifecycleApi.md#previewLifecyclePurgeApiV1LifecyclePreviewsPostWithHttpInfo) | **POST** /api/v1/lifecycle/previews | Preview Lifecycle Purge |
| [**releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost**](LifecycleApi.md#releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost) | **POST** /api/v1/lifecycle/legal-holds/{hold_id}/release | Release Lifecycle Legal Hold |
| [**releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePostWithHttpInfo**](LifecycleApi.md#releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePostWithHttpInfo) | **POST** /api/v1/lifecycle/legal-holds/{hold_id}/release | Release Lifecycle Legal Hold |
| [**resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost**](LifecycleApi.md#resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost) | **POST** /api/v1/lifecycle/jobs/{job_id}/resume | Resume Lifecycle Job |
| [**resumeLifecycleJobApiV1LifecycleJobsJobIdResumePostWithHttpInfo**](LifecycleApi.md#resumeLifecycleJobApiV1LifecycleJobsJobIdResumePostWithHttpInfo) | **POST** /api/v1/lifecycle/jobs/{job_id}/resume | Resume Lifecycle Job |
| [**updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut**](LifecycleApi.md#updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut) | **PUT** /api/v1/lifecycle/policies/{policy_id} | Update Lifecycle Policy |
| [**updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPutWithHttpInfo**](LifecycleApi.md#updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPutWithHttpInfo) | **PUT** /api/v1/lifecycle/policies/{policy_id} | Update Lifecycle Policy |



## createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost

> LifecycleLegalHold createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost(lifecycleLegalHoldDraft, authorization, xAmeshCSRF, xAmeshTenant)

Create Lifecycle Legal Hold

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        LifecycleLegalHoldDraft lifecycleLegalHoldDraft = new LifecycleLegalHoldDraft(); // LifecycleLegalHoldDraft |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            LifecycleLegalHold result = apiInstance.createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost(lifecycleLegalHoldDraft, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost");
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
| **lifecycleLegalHoldDraft** | [**LifecycleLegalHoldDraft**](LifecycleLegalHoldDraft.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**LifecycleLegalHold**](LifecycleLegalHold.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createLifecycleLegalHoldApiV1LifecycleLegalHoldsPostWithHttpInfo

> ApiResponse<LifecycleLegalHold> createLifecycleLegalHoldApiV1LifecycleLegalHoldsPostWithHttpInfo(lifecycleLegalHoldDraft, authorization, xAmeshCSRF, xAmeshTenant)

Create Lifecycle Legal Hold

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        LifecycleLegalHoldDraft lifecycleLegalHoldDraft = new LifecycleLegalHoldDraft(); // LifecycleLegalHoldDraft |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<LifecycleLegalHold> response = apiInstance.createLifecycleLegalHoldApiV1LifecycleLegalHoldsPostWithHttpInfo(lifecycleLegalHoldDraft, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#createLifecycleLegalHoldApiV1LifecycleLegalHoldsPost");
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
| **lifecycleLegalHoldDraft** | [**LifecycleLegalHoldDraft**](LifecycleLegalHoldDraft.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**LifecycleLegalHold**](LifecycleLegalHold.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## createLifecyclePolicyApiV1LifecyclePoliciesPost

> LifecyclePolicy createLifecyclePolicyApiV1LifecyclePoliciesPost(lifecyclePolicyDraft, authorization, xAmeshCSRF, xAmeshTenant)

Create Lifecycle Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        LifecyclePolicyDraft lifecyclePolicyDraft = new LifecyclePolicyDraft(); // LifecyclePolicyDraft |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            LifecyclePolicy result = apiInstance.createLifecyclePolicyApiV1LifecyclePoliciesPost(lifecyclePolicyDraft, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#createLifecyclePolicyApiV1LifecyclePoliciesPost");
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
| **lifecyclePolicyDraft** | [**LifecyclePolicyDraft**](LifecyclePolicyDraft.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**LifecyclePolicy**](LifecyclePolicy.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createLifecyclePolicyApiV1LifecyclePoliciesPostWithHttpInfo

> ApiResponse<LifecyclePolicy> createLifecyclePolicyApiV1LifecyclePoliciesPostWithHttpInfo(lifecyclePolicyDraft, authorization, xAmeshCSRF, xAmeshTenant)

Create Lifecycle Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        LifecyclePolicyDraft lifecyclePolicyDraft = new LifecyclePolicyDraft(); // LifecyclePolicyDraft |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<LifecyclePolicy> response = apiInstance.createLifecyclePolicyApiV1LifecyclePoliciesPostWithHttpInfo(lifecyclePolicyDraft, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#createLifecyclePolicyApiV1LifecyclePoliciesPost");
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
| **lifecyclePolicyDraft** | [**LifecyclePolicyDraft**](LifecyclePolicyDraft.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**LifecyclePolicy**](LifecyclePolicy.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost

> LifecycleJob executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost(jobId, lifecycleExecuteRequest, authorization, xAmeshCSRF, xAmeshTenant)

Execute Lifecycle Job

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID jobId = UUID.randomUUID(); // UUID |
        LifecycleExecuteRequest lifecycleExecuteRequest = new LifecycleExecuteRequest(); // LifecycleExecuteRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            LifecycleJob result = apiInstance.executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost(jobId, lifecycleExecuteRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost");
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
| **jobId** | **UUID**|  | |
| **lifecycleExecuteRequest** | [**LifecycleExecuteRequest**](LifecycleExecuteRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**LifecycleJob**](LifecycleJob.md)


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

## executeLifecycleJobApiV1LifecycleJobsJobIdExecutePostWithHttpInfo

> ApiResponse<LifecycleJob> executeLifecycleJobApiV1LifecycleJobsJobIdExecutePostWithHttpInfo(jobId, lifecycleExecuteRequest, authorization, xAmeshCSRF, xAmeshTenant)

Execute Lifecycle Job

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID jobId = UUID.randomUUID(); // UUID |
        LifecycleExecuteRequest lifecycleExecuteRequest = new LifecycleExecuteRequest(); // LifecycleExecuteRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<LifecycleJob> response = apiInstance.executeLifecycleJobApiV1LifecycleJobsJobIdExecutePostWithHttpInfo(jobId, lifecycleExecuteRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#executeLifecycleJobApiV1LifecycleJobsJobIdExecutePost");
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
| **jobId** | **UUID**|  | |
| **lifecycleExecuteRequest** | [**LifecycleExecuteRequest**](LifecycleExecuteRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**LifecycleJob**](LifecycleJob.md)>


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


## getLifecycleJobApiV1LifecycleJobsJobIdGet

> LifecycleJob getLifecycleJobApiV1LifecycleJobsJobIdGet(jobId, authorization, xAmeshCSRF, xAmeshTenant)

Get Lifecycle Job

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID jobId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            LifecycleJob result = apiInstance.getLifecycleJobApiV1LifecycleJobsJobIdGet(jobId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#getLifecycleJobApiV1LifecycleJobsJobIdGet");
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
| **jobId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**LifecycleJob**](LifecycleJob.md)


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

## getLifecycleJobApiV1LifecycleJobsJobIdGetWithHttpInfo

> ApiResponse<LifecycleJob> getLifecycleJobApiV1LifecycleJobsJobIdGetWithHttpInfo(jobId, authorization, xAmeshCSRF, xAmeshTenant)

Get Lifecycle Job

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID jobId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<LifecycleJob> response = apiInstance.getLifecycleJobApiV1LifecycleJobsJobIdGetWithHttpInfo(jobId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#getLifecycleJobApiV1LifecycleJobsJobIdGet");
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
| **jobId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**LifecycleJob**](LifecycleJob.md)>


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


## listLifecycleJobsApiV1LifecycleJobsGet

> List<LifecycleJob> listLifecycleJobsApiV1LifecycleJobsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Lifecycle Jobs

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        Integer limit = 50; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<LifecycleJob> result = apiInstance.listLifecycleJobsApiV1LifecycleJobsGet(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#listLifecycleJobsApiV1LifecycleJobsGet");
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
| **limit** | **Integer**|  | [optional] [default to 50] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;LifecycleJob&gt;**](LifecycleJob.md)


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

## listLifecycleJobsApiV1LifecycleJobsGetWithHttpInfo

> ApiResponse<List<LifecycleJob>> listLifecycleJobsApiV1LifecycleJobsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Lifecycle Jobs

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        Integer limit = 50; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<LifecycleJob>> response = apiInstance.listLifecycleJobsApiV1LifecycleJobsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#listLifecycleJobsApiV1LifecycleJobsGet");
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
| **limit** | **Integer**|  | [optional] [default to 50] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;LifecycleJob&gt;**](LifecycleJob.md)>


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


## listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet

> List<LifecycleLegalHold> listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Lifecycle Legal Holds

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<LifecycleLegalHold> result = apiInstance.listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet");
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

[**List&lt;LifecycleLegalHold&gt;**](LifecycleLegalHold.md)


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

## listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGetWithHttpInfo

> ApiResponse<List<LifecycleLegalHold>> listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Lifecycle Legal Holds

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<LifecycleLegalHold>> response = apiInstance.listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#listLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet");
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

ApiResponse<[**List&lt;LifecycleLegalHold&gt;**](LifecycleLegalHold.md)>


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


## listLifecyclePoliciesApiV1LifecyclePoliciesGet

> List<LifecyclePolicy> listLifecyclePoliciesApiV1LifecyclePoliciesGet(authorization, xAmeshCSRF, xAmeshTenant)

List Lifecycle Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<LifecyclePolicy> result = apiInstance.listLifecyclePoliciesApiV1LifecyclePoliciesGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#listLifecyclePoliciesApiV1LifecyclePoliciesGet");
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

[**List&lt;LifecyclePolicy&gt;**](LifecyclePolicy.md)


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

## listLifecyclePoliciesApiV1LifecyclePoliciesGetWithHttpInfo

> ApiResponse<List<LifecyclePolicy>> listLifecyclePoliciesApiV1LifecyclePoliciesGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Lifecycle Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<LifecyclePolicy>> response = apiInstance.listLifecyclePoliciesApiV1LifecyclePoliciesGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#listLifecyclePoliciesApiV1LifecyclePoliciesGet");
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

ApiResponse<[**List&lt;LifecyclePolicy&gt;**](LifecyclePolicy.md)>


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


## previewLifecyclePurgeApiV1LifecyclePreviewsPost

> LifecycleJob previewLifecyclePurgeApiV1LifecyclePreviewsPost(lifecyclePreviewRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Lifecycle Purge

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        LifecyclePreviewRequest lifecyclePreviewRequest = new LifecyclePreviewRequest(); // LifecyclePreviewRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            LifecycleJob result = apiInstance.previewLifecyclePurgeApiV1LifecyclePreviewsPost(lifecyclePreviewRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#previewLifecyclePurgeApiV1LifecyclePreviewsPost");
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
| **lifecyclePreviewRequest** | [**LifecyclePreviewRequest**](LifecyclePreviewRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**LifecycleJob**](LifecycleJob.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## previewLifecyclePurgeApiV1LifecyclePreviewsPostWithHttpInfo

> ApiResponse<LifecycleJob> previewLifecyclePurgeApiV1LifecyclePreviewsPostWithHttpInfo(lifecyclePreviewRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Lifecycle Purge

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        LifecyclePreviewRequest lifecyclePreviewRequest = new LifecyclePreviewRequest(); // LifecyclePreviewRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<LifecycleJob> response = apiInstance.previewLifecyclePurgeApiV1LifecyclePreviewsPostWithHttpInfo(lifecyclePreviewRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#previewLifecyclePurgeApiV1LifecyclePreviewsPost");
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
| **lifecyclePreviewRequest** | [**LifecyclePreviewRequest**](LifecyclePreviewRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**LifecycleJob**](LifecycleJob.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost

> LifecycleLegalHold releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost(holdId, authorization, xAmeshCSRF, xAmeshTenant)

Release Lifecycle Legal Hold

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID holdId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            LifecycleLegalHold result = apiInstance.releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost(holdId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost");
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
| **holdId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**LifecycleLegalHold**](LifecycleLegalHold.md)


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

## releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePostWithHttpInfo

> ApiResponse<LifecycleLegalHold> releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePostWithHttpInfo(holdId, authorization, xAmeshCSRF, xAmeshTenant)

Release Lifecycle Legal Hold

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID holdId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<LifecycleLegalHold> response = apiInstance.releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePostWithHttpInfo(holdId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#releaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost");
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
| **holdId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**LifecycleLegalHold**](LifecycleLegalHold.md)>


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


## resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost

> LifecycleJob resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost(jobId, authorization, xAmeshCSRF, xAmeshTenant)

Resume Lifecycle Job

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID jobId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            LifecycleJob result = apiInstance.resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost(jobId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost");
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
| **jobId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**LifecycleJob**](LifecycleJob.md)


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

## resumeLifecycleJobApiV1LifecycleJobsJobIdResumePostWithHttpInfo

> ApiResponse<LifecycleJob> resumeLifecycleJobApiV1LifecycleJobsJobIdResumePostWithHttpInfo(jobId, authorization, xAmeshCSRF, xAmeshTenant)

Resume Lifecycle Job

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID jobId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<LifecycleJob> response = apiInstance.resumeLifecycleJobApiV1LifecycleJobsJobIdResumePostWithHttpInfo(jobId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#resumeLifecycleJobApiV1LifecycleJobsJobIdResumePost");
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
| **jobId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**LifecycleJob**](LifecycleJob.md)>


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


## updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut

> LifecyclePolicy updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut(policyId, lifecyclePolicyDraft, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Update Lifecycle Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID policyId = UUID.randomUUID(); // UUID |
        LifecyclePolicyDraft lifecyclePolicyDraft = new LifecyclePolicyDraft(); // LifecyclePolicyDraft |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            LifecyclePolicy result = apiInstance.updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut(policyId, lifecyclePolicyDraft, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut");
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
| **policyId** | **UUID**|  | |
| **lifecyclePolicyDraft** | [**LifecyclePolicyDraft**](LifecyclePolicyDraft.md)|  | |
| **expectedVersion** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**LifecyclePolicy**](LifecyclePolicy.md)


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

## updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPutWithHttpInfo

> ApiResponse<LifecyclePolicy> updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPutWithHttpInfo(policyId, lifecyclePolicyDraft, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Update Lifecycle Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.LifecycleApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        LifecycleApi apiInstance = new LifecycleApi(defaultClient);
        UUID policyId = UUID.randomUUID(); // UUID |
        LifecyclePolicyDraft lifecyclePolicyDraft = new LifecyclePolicyDraft(); // LifecyclePolicyDraft |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<LifecyclePolicy> response = apiInstance.updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPutWithHttpInfo(policyId, lifecyclePolicyDraft, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling LifecycleApi#updateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut");
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
| **policyId** | **UUID**|  | |
| **lifecyclePolicyDraft** | [**LifecyclePolicyDraft**](LifecyclePolicyDraft.md)|  | |
| **expectedVersion** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**LifecyclePolicy**](LifecyclePolicy.md)>


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
