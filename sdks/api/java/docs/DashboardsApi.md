# DashboardsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteDashboardApiV1DashboardsDashboardIdDelete**](DashboardsApi.md#deleteDashboardApiV1DashboardsDashboardIdDelete) | **DELETE** /api/v1/dashboards/{dashboard_id} | Delete Dashboard |
| [**deleteDashboardApiV1DashboardsDashboardIdDeleteWithHttpInfo**](DashboardsApi.md#deleteDashboardApiV1DashboardsDashboardIdDeleteWithHttpInfo) | **DELETE** /api/v1/dashboards/{dashboard_id} | Delete Dashboard |
| [**executeDashboardQueryApiV1DashboardQueriesPost**](DashboardsApi.md#executeDashboardQueryApiV1DashboardQueriesPost) | **POST** /api/v1/dashboard-queries | Execute Dashboard Query |
| [**executeDashboardQueryApiV1DashboardQueriesPostWithHttpInfo**](DashboardsApi.md#executeDashboardQueryApiV1DashboardQueriesPostWithHttpInfo) | **POST** /api/v1/dashboard-queries | Execute Dashboard Query |
| [**exportDashboardApiV1DashboardsDashboardIdExportGet**](DashboardsApi.md#exportDashboardApiV1DashboardsDashboardIdExportGet) | **GET** /api/v1/dashboards/{dashboard_id}/export | Export Dashboard |
| [**exportDashboardApiV1DashboardsDashboardIdExportGetWithHttpInfo**](DashboardsApi.md#exportDashboardApiV1DashboardsDashboardIdExportGetWithHttpInfo) | **GET** /api/v1/dashboards/{dashboard_id}/export | Export Dashboard |
| [**getDashboardApiV1DashboardsDashboardIdGet**](DashboardsApi.md#getDashboardApiV1DashboardsDashboardIdGet) | **GET** /api/v1/dashboards/{dashboard_id} | Get Dashboard |
| [**getDashboardApiV1DashboardsDashboardIdGetWithHttpInfo**](DashboardsApi.md#getDashboardApiV1DashboardsDashboardIdGetWithHttpInfo) | **GET** /api/v1/dashboards/{dashboard_id} | Get Dashboard |
| [**listDashboardsApiV1DashboardsGet**](DashboardsApi.md#listDashboardsApiV1DashboardsGet) | **GET** /api/v1/dashboards | List Dashboards |
| [**listDashboardsApiV1DashboardsGetWithHttpInfo**](DashboardsApi.md#listDashboardsApiV1DashboardsGetWithHttpInfo) | **GET** /api/v1/dashboards | List Dashboards |
| [**putDashboardApiV1DashboardsDashboardIdPut**](DashboardsApi.md#putDashboardApiV1DashboardsDashboardIdPut) | **PUT** /api/v1/dashboards/{dashboard_id} | Put Dashboard |
| [**putDashboardApiV1DashboardsDashboardIdPutWithHttpInfo**](DashboardsApi.md#putDashboardApiV1DashboardsDashboardIdPutWithHttpInfo) | **PUT** /api/v1/dashboards/{dashboard_id} | Put Dashboard |
| [**renderDashboardApiV1DashboardsDashboardIdRenderPost**](DashboardsApi.md#renderDashboardApiV1DashboardsDashboardIdRenderPost) | **POST** /api/v1/dashboards/{dashboard_id}/render | Render Dashboard |
| [**renderDashboardApiV1DashboardsDashboardIdRenderPostWithHttpInfo**](DashboardsApi.md#renderDashboardApiV1DashboardsDashboardIdRenderPostWithHttpInfo) | **POST** /api/v1/dashboards/{dashboard_id}/render | Render Dashboard |



## deleteDashboardApiV1DashboardsDashboardIdDelete

> void deleteDashboardApiV1DashboardsDashboardIdDelete(dashboardId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Delete Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.deleteDashboardApiV1DashboardsDashboardIdDelete(dashboardId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#deleteDashboardApiV1DashboardsDashboardIdDelete");
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
| **dashboardId** | **String**|  | |
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

## deleteDashboardApiV1DashboardsDashboardIdDeleteWithHttpInfo

> ApiResponse<Void> deleteDashboardApiV1DashboardsDashboardIdDeleteWithHttpInfo(dashboardId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Delete Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.deleteDashboardApiV1DashboardsDashboardIdDeleteWithHttpInfo(dashboardId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#deleteDashboardApiV1DashboardsDashboardIdDelete");
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
| **dashboardId** | **String**|  | |
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


## executeDashboardQueryApiV1DashboardQueriesPost

> DashboardQueryResult executeDashboardQueryApiV1DashboardQueriesPost(dashboardQuery, authorization, xAmeshCSRF, xAmeshTenant)

Execute Dashboard Query

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        DashboardQuery dashboardQuery = new DashboardQuery(); // DashboardQuery |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            DashboardQueryResult result = apiInstance.executeDashboardQueryApiV1DashboardQueriesPost(dashboardQuery, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#executeDashboardQueryApiV1DashboardQueriesPost");
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
| **dashboardQuery** | [**DashboardQuery**](DashboardQuery.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**DashboardQueryResult**](DashboardQueryResult.md)


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

## executeDashboardQueryApiV1DashboardQueriesPostWithHttpInfo

> ApiResponse<DashboardQueryResult> executeDashboardQueryApiV1DashboardQueriesPostWithHttpInfo(dashboardQuery, authorization, xAmeshCSRF, xAmeshTenant)

Execute Dashboard Query

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        DashboardQuery dashboardQuery = new DashboardQuery(); // DashboardQuery |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<DashboardQueryResult> response = apiInstance.executeDashboardQueryApiV1DashboardQueriesPostWithHttpInfo(dashboardQuery, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#executeDashboardQueryApiV1DashboardQueriesPost");
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
| **dashboardQuery** | [**DashboardQuery**](DashboardQuery.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**DashboardQueryResult**](DashboardQueryResult.md)>


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


## exportDashboardApiV1DashboardsDashboardIdExportGet

> Object exportDashboardApiV1DashboardsDashboardIdExportGet(dashboardId, format, authorization, xAmeshCSRF, xAmeshTenant)

Export Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        String format = "yaml"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            Object result = apiInstance.exportDashboardApiV1DashboardsDashboardIdExportGet(dashboardId, format, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#exportDashboardApiV1DashboardsDashboardIdExportGet");
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
| **dashboardId** | **String**|  | |
| **format** | **String**|  | [optional] [default to yaml] [enum: yaml, json] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**Object**


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

## exportDashboardApiV1DashboardsDashboardIdExportGetWithHttpInfo

> ApiResponse<Object> exportDashboardApiV1DashboardsDashboardIdExportGetWithHttpInfo(dashboardId, format, authorization, xAmeshCSRF, xAmeshTenant)

Export Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        String format = "yaml"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Object> response = apiInstance.exportDashboardApiV1DashboardsDashboardIdExportGetWithHttpInfo(dashboardId, format, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#exportDashboardApiV1DashboardsDashboardIdExportGet");
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
| **dashboardId** | **String**|  | |
| **format** | **String**|  | [optional] [default to yaml] [enum: yaml, json] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**Object**>


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


## getDashboardApiV1DashboardsDashboardIdGet

> DashboardDefinition getDashboardApiV1DashboardsDashboardIdGet(dashboardId, authorization, xAmeshCSRF, xAmeshTenant)

Get Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            DashboardDefinition result = apiInstance.getDashboardApiV1DashboardsDashboardIdGet(dashboardId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#getDashboardApiV1DashboardsDashboardIdGet");
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
| **dashboardId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**DashboardDefinition**](DashboardDefinition.md)


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

## getDashboardApiV1DashboardsDashboardIdGetWithHttpInfo

> ApiResponse<DashboardDefinition> getDashboardApiV1DashboardsDashboardIdGetWithHttpInfo(dashboardId, authorization, xAmeshCSRF, xAmeshTenant)

Get Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<DashboardDefinition> response = apiInstance.getDashboardApiV1DashboardsDashboardIdGetWithHttpInfo(dashboardId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#getDashboardApiV1DashboardsDashboardIdGet");
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
| **dashboardId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**DashboardDefinition**](DashboardDefinition.md)>


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


## listDashboardsApiV1DashboardsGet

> List<DashboardDefinition> listDashboardsApiV1DashboardsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Dashboards

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<DashboardDefinition> result = apiInstance.listDashboardsApiV1DashboardsGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#listDashboardsApiV1DashboardsGet");
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

[**List&lt;DashboardDefinition&gt;**](DashboardDefinition.md)


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

## listDashboardsApiV1DashboardsGetWithHttpInfo

> ApiResponse<List<DashboardDefinition>> listDashboardsApiV1DashboardsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Dashboards

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<DashboardDefinition>> response = apiInstance.listDashboardsApiV1DashboardsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#listDashboardsApiV1DashboardsGet");
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

ApiResponse<[**List&lt;DashboardDefinition&gt;**](DashboardDefinition.md)>


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


## putDashboardApiV1DashboardsDashboardIdPut

> DashboardDefinition putDashboardApiV1DashboardsDashboardIdPut(dashboardId, dashboardSpec, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Put Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        DashboardSpec dashboardSpec = new DashboardSpec(); // DashboardSpec |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            DashboardDefinition result = apiInstance.putDashboardApiV1DashboardsDashboardIdPut(dashboardId, dashboardSpec, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#putDashboardApiV1DashboardsDashboardIdPut");
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
| **dashboardId** | **String**|  | |
| **dashboardSpec** | [**DashboardSpec**](DashboardSpec.md)|  | |
| **expectedVersion** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**DashboardDefinition**](DashboardDefinition.md)


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

## putDashboardApiV1DashboardsDashboardIdPutWithHttpInfo

> ApiResponse<DashboardDefinition> putDashboardApiV1DashboardsDashboardIdPutWithHttpInfo(dashboardId, dashboardSpec, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Put Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        DashboardSpec dashboardSpec = new DashboardSpec(); // DashboardSpec |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<DashboardDefinition> response = apiInstance.putDashboardApiV1DashboardsDashboardIdPutWithHttpInfo(dashboardId, dashboardSpec, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#putDashboardApiV1DashboardsDashboardIdPut");
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
| **dashboardId** | **String**|  | |
| **dashboardSpec** | [**DashboardSpec**](DashboardSpec.md)|  | |
| **expectedVersion** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**DashboardDefinition**](DashboardDefinition.md)>


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


## renderDashboardApiV1DashboardsDashboardIdRenderPost

> DashboardRender renderDashboardApiV1DashboardsDashboardIdRenderPost(dashboardId, dashboardFilters, authorization, xAmeshCSRF, xAmeshTenant)

Render Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        DashboardFilters dashboardFilters = new DashboardFilters(); // DashboardFilters |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            DashboardRender result = apiInstance.renderDashboardApiV1DashboardsDashboardIdRenderPost(dashboardId, dashboardFilters, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#renderDashboardApiV1DashboardsDashboardIdRenderPost");
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
| **dashboardId** | **String**|  | |
| **dashboardFilters** | [**DashboardFilters**](DashboardFilters.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**DashboardRender**](DashboardRender.md)


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

## renderDashboardApiV1DashboardsDashboardIdRenderPostWithHttpInfo

> ApiResponse<DashboardRender> renderDashboardApiV1DashboardsDashboardIdRenderPostWithHttpInfo(dashboardId, dashboardFilters, authorization, xAmeshCSRF, xAmeshTenant)

Render Dashboard

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.DashboardsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        DashboardsApi apiInstance = new DashboardsApi(defaultClient);
        String dashboardId = "dashboardId_example"; // String |
        DashboardFilters dashboardFilters = new DashboardFilters(); // DashboardFilters |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<DashboardRender> response = apiInstance.renderDashboardApiV1DashboardsDashboardIdRenderPostWithHttpInfo(dashboardId, dashboardFilters, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling DashboardsApi#renderDashboardApiV1DashboardsDashboardIdRenderPost");
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
| **dashboardId** | **String**|  | |
| **dashboardFilters** | [**DashboardFilters**](DashboardFilters.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**DashboardRender**](DashboardRender.md)>


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
