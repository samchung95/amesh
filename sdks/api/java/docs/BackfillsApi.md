# BackfillsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**cancelBackfillApiV1BackfillsBackfillIdCancelPost**](BackfillsApi.md#cancelBackfillApiV1BackfillsBackfillIdCancelPost) | **POST** /api/v1/backfills/{backfill_id}/cancel | Cancel Backfill |
| [**cancelBackfillApiV1BackfillsBackfillIdCancelPostWithHttpInfo**](BackfillsApi.md#cancelBackfillApiV1BackfillsBackfillIdCancelPostWithHttpInfo) | **POST** /api/v1/backfills/{backfill_id}/cancel | Cancel Backfill |
| [**createBackfillApiV1BackfillsPost**](BackfillsApi.md#createBackfillApiV1BackfillsPost) | **POST** /api/v1/backfills | Create Backfill |
| [**createBackfillApiV1BackfillsPostWithHttpInfo**](BackfillsApi.md#createBackfillApiV1BackfillsPostWithHttpInfo) | **POST** /api/v1/backfills | Create Backfill |
| [**getBackfillApiV1BackfillsBackfillIdGet**](BackfillsApi.md#getBackfillApiV1BackfillsBackfillIdGet) | **GET** /api/v1/backfills/{backfill_id} | Get Backfill |
| [**getBackfillApiV1BackfillsBackfillIdGetWithHttpInfo**](BackfillsApi.md#getBackfillApiV1BackfillsBackfillIdGetWithHttpInfo) | **GET** /api/v1/backfills/{backfill_id} | Get Backfill |
| [**listBackfillsApiV1BackfillsGet**](BackfillsApi.md#listBackfillsApiV1BackfillsGet) | **GET** /api/v1/backfills | List Backfills |
| [**listBackfillsApiV1BackfillsGetWithHttpInfo**](BackfillsApi.md#listBackfillsApiV1BackfillsGetWithHttpInfo) | **GET** /api/v1/backfills | List Backfills |
| [**pauseBackfillApiV1BackfillsBackfillIdPausePost**](BackfillsApi.md#pauseBackfillApiV1BackfillsBackfillIdPausePost) | **POST** /api/v1/backfills/{backfill_id}/pause | Pause Backfill |
| [**pauseBackfillApiV1BackfillsBackfillIdPausePostWithHttpInfo**](BackfillsApi.md#pauseBackfillApiV1BackfillsBackfillIdPausePostWithHttpInfo) | **POST** /api/v1/backfills/{backfill_id}/pause | Pause Backfill |
| [**previewBackfillApiV1BackfillsPreviewPost**](BackfillsApi.md#previewBackfillApiV1BackfillsPreviewPost) | **POST** /api/v1/backfills/preview | Preview Backfill |
| [**previewBackfillApiV1BackfillsPreviewPostWithHttpInfo**](BackfillsApi.md#previewBackfillApiV1BackfillsPreviewPostWithHttpInfo) | **POST** /api/v1/backfills/preview | Preview Backfill |
| [**resumeBackfillApiV1BackfillsBackfillIdResumePost**](BackfillsApi.md#resumeBackfillApiV1BackfillsBackfillIdResumePost) | **POST** /api/v1/backfills/{backfill_id}/resume | Resume Backfill |
| [**resumeBackfillApiV1BackfillsBackfillIdResumePostWithHttpInfo**](BackfillsApi.md#resumeBackfillApiV1BackfillsBackfillIdResumePostWithHttpInfo) | **POST** /api/v1/backfills/{backfill_id}/resume | Resume Backfill |



## cancelBackfillApiV1BackfillsBackfillIdCancelPost

> BackfillRecord cancelBackfillApiV1BackfillsBackfillIdCancelPost(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Cancel Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        UUID backfillId = UUID.randomUUID(); // UUID |
        BackfillActionRequest backfillActionRequest = new BackfillActionRequest(); // BackfillActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            BackfillRecord result = apiInstance.cancelBackfillApiV1BackfillsBackfillIdCancelPost(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#cancelBackfillApiV1BackfillsBackfillIdCancelPost");
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
| **backfillId** | **UUID**|  | |
| **backfillActionRequest** | [**BackfillActionRequest**](BackfillActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**BackfillRecord**](BackfillRecord.md)


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

## cancelBackfillApiV1BackfillsBackfillIdCancelPostWithHttpInfo

> ApiResponse<BackfillRecord> cancelBackfillApiV1BackfillsBackfillIdCancelPostWithHttpInfo(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Cancel Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        UUID backfillId = UUID.randomUUID(); // UUID |
        BackfillActionRequest backfillActionRequest = new BackfillActionRequest(); // BackfillActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<BackfillRecord> response = apiInstance.cancelBackfillApiV1BackfillsBackfillIdCancelPostWithHttpInfo(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#cancelBackfillApiV1BackfillsBackfillIdCancelPost");
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
| **backfillId** | **UUID**|  | |
| **backfillActionRequest** | [**BackfillActionRequest**](BackfillActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**BackfillRecord**](BackfillRecord.md)>


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


## createBackfillApiV1BackfillsPost

> BackfillRecord createBackfillApiV1BackfillsPost(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant)

Create Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        BackfillSpec backfillSpec = new BackfillSpec(); // BackfillSpec |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            BackfillRecord result = apiInstance.createBackfillApiV1BackfillsPost(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#createBackfillApiV1BackfillsPost");
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
| **backfillSpec** | [**BackfillSpec**](BackfillSpec.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**BackfillRecord**](BackfillRecord.md)


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

## createBackfillApiV1BackfillsPostWithHttpInfo

> ApiResponse<BackfillRecord> createBackfillApiV1BackfillsPostWithHttpInfo(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant)

Create Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        BackfillSpec backfillSpec = new BackfillSpec(); // BackfillSpec |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<BackfillRecord> response = apiInstance.createBackfillApiV1BackfillsPostWithHttpInfo(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#createBackfillApiV1BackfillsPost");
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
| **backfillSpec** | [**BackfillSpec**](BackfillSpec.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**BackfillRecord**](BackfillRecord.md)>


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


## getBackfillApiV1BackfillsBackfillIdGet

> BackfillRecord getBackfillApiV1BackfillsBackfillIdGet(backfillId, authorization, xAmeshCSRF, xAmeshTenant)

Get Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        UUID backfillId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            BackfillRecord result = apiInstance.getBackfillApiV1BackfillsBackfillIdGet(backfillId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#getBackfillApiV1BackfillsBackfillIdGet");
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
| **backfillId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**BackfillRecord**](BackfillRecord.md)


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

## getBackfillApiV1BackfillsBackfillIdGetWithHttpInfo

> ApiResponse<BackfillRecord> getBackfillApiV1BackfillsBackfillIdGetWithHttpInfo(backfillId, authorization, xAmeshCSRF, xAmeshTenant)

Get Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        UUID backfillId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<BackfillRecord> response = apiInstance.getBackfillApiV1BackfillsBackfillIdGetWithHttpInfo(backfillId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#getBackfillApiV1BackfillsBackfillIdGet");
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
| **backfillId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**BackfillRecord**](BackfillRecord.md)>


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


## listBackfillsApiV1BackfillsGet

> List<BackfillRecord> listBackfillsApiV1BackfillsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Backfills

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 100; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<BackfillRecord> result = apiInstance.listBackfillsApiV1BackfillsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#listBackfillsApiV1BackfillsGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;BackfillRecord&gt;**](BackfillRecord.md)


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

## listBackfillsApiV1BackfillsGetWithHttpInfo

> ApiResponse<List<BackfillRecord>> listBackfillsApiV1BackfillsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Backfills

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 100; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<BackfillRecord>> response = apiInstance.listBackfillsApiV1BackfillsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#listBackfillsApiV1BackfillsGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;BackfillRecord&gt;**](BackfillRecord.md)>


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


## pauseBackfillApiV1BackfillsBackfillIdPausePost

> BackfillRecord pauseBackfillApiV1BackfillsBackfillIdPausePost(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Pause Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        UUID backfillId = UUID.randomUUID(); // UUID |
        BackfillActionRequest backfillActionRequest = new BackfillActionRequest(); // BackfillActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            BackfillRecord result = apiInstance.pauseBackfillApiV1BackfillsBackfillIdPausePost(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#pauseBackfillApiV1BackfillsBackfillIdPausePost");
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
| **backfillId** | **UUID**|  | |
| **backfillActionRequest** | [**BackfillActionRequest**](BackfillActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**BackfillRecord**](BackfillRecord.md)


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

## pauseBackfillApiV1BackfillsBackfillIdPausePostWithHttpInfo

> ApiResponse<BackfillRecord> pauseBackfillApiV1BackfillsBackfillIdPausePostWithHttpInfo(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Pause Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        UUID backfillId = UUID.randomUUID(); // UUID |
        BackfillActionRequest backfillActionRequest = new BackfillActionRequest(); // BackfillActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<BackfillRecord> response = apiInstance.pauseBackfillApiV1BackfillsBackfillIdPausePostWithHttpInfo(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#pauseBackfillApiV1BackfillsBackfillIdPausePost");
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
| **backfillId** | **UUID**|  | |
| **backfillActionRequest** | [**BackfillActionRequest**](BackfillActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**BackfillRecord**](BackfillRecord.md)>


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


## previewBackfillApiV1BackfillsPreviewPost

> BackfillPreview previewBackfillApiV1BackfillsPreviewPost(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant)

Preview Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        BackfillSpec backfillSpec = new BackfillSpec(); // BackfillSpec |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            BackfillPreview result = apiInstance.previewBackfillApiV1BackfillsPreviewPost(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#previewBackfillApiV1BackfillsPreviewPost");
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
| **backfillSpec** | [**BackfillSpec**](BackfillSpec.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**BackfillPreview**](BackfillPreview.md)


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

## previewBackfillApiV1BackfillsPreviewPostWithHttpInfo

> ApiResponse<BackfillPreview> previewBackfillApiV1BackfillsPreviewPostWithHttpInfo(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant)

Preview Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        BackfillSpec backfillSpec = new BackfillSpec(); // BackfillSpec |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<BackfillPreview> response = apiInstance.previewBackfillApiV1BackfillsPreviewPostWithHttpInfo(backfillSpec, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#previewBackfillApiV1BackfillsPreviewPost");
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
| **backfillSpec** | [**BackfillSpec**](BackfillSpec.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**BackfillPreview**](BackfillPreview.md)>


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


## resumeBackfillApiV1BackfillsBackfillIdResumePost

> BackfillRecord resumeBackfillApiV1BackfillsBackfillIdResumePost(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resume Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        UUID backfillId = UUID.randomUUID(); // UUID |
        BackfillActionRequest backfillActionRequest = new BackfillActionRequest(); // BackfillActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            BackfillRecord result = apiInstance.resumeBackfillApiV1BackfillsBackfillIdResumePost(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#resumeBackfillApiV1BackfillsBackfillIdResumePost");
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
| **backfillId** | **UUID**|  | |
| **backfillActionRequest** | [**BackfillActionRequest**](BackfillActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**BackfillRecord**](BackfillRecord.md)


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

## resumeBackfillApiV1BackfillsBackfillIdResumePostWithHttpInfo

> ApiResponse<BackfillRecord> resumeBackfillApiV1BackfillsBackfillIdResumePostWithHttpInfo(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Resume Backfill

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.BackfillsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        BackfillsApi apiInstance = new BackfillsApi(defaultClient);
        UUID backfillId = UUID.randomUUID(); // UUID |
        BackfillActionRequest backfillActionRequest = new BackfillActionRequest(); // BackfillActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<BackfillRecord> response = apiInstance.resumeBackfillApiV1BackfillsBackfillIdResumePostWithHttpInfo(backfillId, backfillActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling BackfillsApi#resumeBackfillApiV1BackfillsBackfillIdResumePost");
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
| **backfillId** | **UUID**|  | |
| **backfillActionRequest** | [**BackfillActionRequest**](BackfillActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**BackfillRecord**](BackfillRecord.md)>


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
