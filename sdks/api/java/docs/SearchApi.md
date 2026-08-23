# SearchApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**controlSearchProjectionApiV1SearchControlPost**](SearchApi.md#controlSearchProjectionApiV1SearchControlPost) | **POST** /api/v1/search/control | Control Search Projection |
| [**controlSearchProjectionApiV1SearchControlPostWithHttpInfo**](SearchApi.md#controlSearchProjectionApiV1SearchControlPostWithHttpInfo) | **POST** /api/v1/search/control | Control Search Projection |
| [**getSearchStatusApiV1SearchStatusGet**](SearchApi.md#getSearchStatusApiV1SearchStatusGet) | **GET** /api/v1/search/status | Get Search Status |
| [**getSearchStatusApiV1SearchStatusGetWithHttpInfo**](SearchApi.md#getSearchStatusApiV1SearchStatusGetWithHttpInfo) | **GET** /api/v1/search/status | Get Search Status |
| [**rebuildSearchProjectionApiV1SearchRebuildPost**](SearchApi.md#rebuildSearchProjectionApiV1SearchRebuildPost) | **POST** /api/v1/search/rebuild | Rebuild Search Projection |
| [**rebuildSearchProjectionApiV1SearchRebuildPostWithHttpInfo**](SearchApi.md#rebuildSearchProjectionApiV1SearchRebuildPostWithHttpInfo) | **POST** /api/v1/search/rebuild | Rebuild Search Projection |
| [**searchResourcesApiV1SearchPost**](SearchApi.md#searchResourcesApiV1SearchPost) | **POST** /api/v1/search | Search Resources |
| [**searchResourcesApiV1SearchPostWithHttpInfo**](SearchApi.md#searchResourcesApiV1SearchPostWithHttpInfo) | **POST** /api/v1/search | Search Resources |
| [**verifySearchProjectionApiV1SearchVerifyGet**](SearchApi.md#verifySearchProjectionApiV1SearchVerifyGet) | **GET** /api/v1/search/verify | Verify Search Projection |
| [**verifySearchProjectionApiV1SearchVerifyGetWithHttpInfo**](SearchApi.md#verifySearchProjectionApiV1SearchVerifyGetWithHttpInfo) | **GET** /api/v1/search/verify | Verify Search Projection |



## controlSearchProjectionApiV1SearchControlPost

> SearchProjectionStatus controlSearchProjectionApiV1SearchControlPost(searchProjectionControlRequest, authorization, xAmeshCSRF, xAmeshTenant)

Control Search Projection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        SearchProjectionControlRequest searchProjectionControlRequest = new SearchProjectionControlRequest(); // SearchProjectionControlRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SearchProjectionStatus result = apiInstance.controlSearchProjectionApiV1SearchControlPost(searchProjectionControlRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#controlSearchProjectionApiV1SearchControlPost");
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
| **searchProjectionControlRequest** | [**SearchProjectionControlRequest**](SearchProjectionControlRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**SearchProjectionStatus**](SearchProjectionStatus.md)


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

## controlSearchProjectionApiV1SearchControlPostWithHttpInfo

> ApiResponse<SearchProjectionStatus> controlSearchProjectionApiV1SearchControlPostWithHttpInfo(searchProjectionControlRequest, authorization, xAmeshCSRF, xAmeshTenant)

Control Search Projection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        SearchProjectionControlRequest searchProjectionControlRequest = new SearchProjectionControlRequest(); // SearchProjectionControlRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SearchProjectionStatus> response = apiInstance.controlSearchProjectionApiV1SearchControlPostWithHttpInfo(searchProjectionControlRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#controlSearchProjectionApiV1SearchControlPost");
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
| **searchProjectionControlRequest** | [**SearchProjectionControlRequest**](SearchProjectionControlRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**SearchProjectionStatus**](SearchProjectionStatus.md)>


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


## getSearchStatusApiV1SearchStatusGet

> SearchProjectionStatus getSearchStatusApiV1SearchStatusGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Search Status

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SearchProjectionStatus result = apiInstance.getSearchStatusApiV1SearchStatusGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#getSearchStatusApiV1SearchStatusGet");
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

[**SearchProjectionStatus**](SearchProjectionStatus.md)


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

## getSearchStatusApiV1SearchStatusGetWithHttpInfo

> ApiResponse<SearchProjectionStatus> getSearchStatusApiV1SearchStatusGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Get Search Status

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SearchProjectionStatus> response = apiInstance.getSearchStatusApiV1SearchStatusGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#getSearchStatusApiV1SearchStatusGet");
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

ApiResponse<[**SearchProjectionStatus**](SearchProjectionStatus.md)>


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


## rebuildSearchProjectionApiV1SearchRebuildPost

> SearchProjectionStatus rebuildSearchProjectionApiV1SearchRebuildPost(searchRebuildRequest, authorization, xAmeshCSRF, xAmeshTenant)

Rebuild Search Projection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        SearchRebuildRequest searchRebuildRequest = new SearchRebuildRequest(); // SearchRebuildRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SearchProjectionStatus result = apiInstance.rebuildSearchProjectionApiV1SearchRebuildPost(searchRebuildRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#rebuildSearchProjectionApiV1SearchRebuildPost");
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
| **searchRebuildRequest** | [**SearchRebuildRequest**](SearchRebuildRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**SearchProjectionStatus**](SearchProjectionStatus.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## rebuildSearchProjectionApiV1SearchRebuildPostWithHttpInfo

> ApiResponse<SearchProjectionStatus> rebuildSearchProjectionApiV1SearchRebuildPostWithHttpInfo(searchRebuildRequest, authorization, xAmeshCSRF, xAmeshTenant)

Rebuild Search Projection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        SearchRebuildRequest searchRebuildRequest = new SearchRebuildRequest(); // SearchRebuildRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SearchProjectionStatus> response = apiInstance.rebuildSearchProjectionApiV1SearchRebuildPostWithHttpInfo(searchRebuildRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#rebuildSearchProjectionApiV1SearchRebuildPost");
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
| **searchRebuildRequest** | [**SearchRebuildRequest**](SearchRebuildRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**SearchProjectionStatus**](SearchProjectionStatus.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **202** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## searchResourcesApiV1SearchPost

> SearchResponse searchResourcesApiV1SearchPost(searchRequest, authorization, xAmeshCSRF, xAmeshTenant)

Search Resources

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        SearchRequest searchRequest = new SearchRequest(); // SearchRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SearchResponse result = apiInstance.searchResourcesApiV1SearchPost(searchRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#searchResourcesApiV1SearchPost");
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
| **searchRequest** | [**SearchRequest**](SearchRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**SearchResponse**](SearchResponse.md)


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

## searchResourcesApiV1SearchPostWithHttpInfo

> ApiResponse<SearchResponse> searchResourcesApiV1SearchPostWithHttpInfo(searchRequest, authorization, xAmeshCSRF, xAmeshTenant)

Search Resources

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        SearchRequest searchRequest = new SearchRequest(); // SearchRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SearchResponse> response = apiInstance.searchResourcesApiV1SearchPostWithHttpInfo(searchRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#searchResourcesApiV1SearchPost");
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
| **searchRequest** | [**SearchRequest**](SearchRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**SearchResponse**](SearchResponse.md)>


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


## verifySearchProjectionApiV1SearchVerifyGet

> SearchProjectionVerification verifySearchProjectionApiV1SearchVerifyGet(authorization, xAmeshCSRF, xAmeshTenant)

Verify Search Projection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SearchProjectionVerification result = apiInstance.verifySearchProjectionApiV1SearchVerifyGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#verifySearchProjectionApiV1SearchVerifyGet");
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

[**SearchProjectionVerification**](SearchProjectionVerification.md)


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

## verifySearchProjectionApiV1SearchVerifyGetWithHttpInfo

> ApiResponse<SearchProjectionVerification> verifySearchProjectionApiV1SearchVerifyGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Verify Search Projection

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SearchApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SearchApi apiInstance = new SearchApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SearchProjectionVerification> response = apiInstance.verifySearchProjectionApiV1SearchVerifyGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling SearchApi#verifySearchProjectionApiV1SearchVerifyGet");
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

ApiResponse<[**SearchProjectionVerification**](SearchProjectionVerification.md)>


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
