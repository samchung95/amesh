# AdministrationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyAdministrationControlApiV1AdminControlsKeyPut**](AdministrationApi.md#applyAdministrationControlApiV1AdminControlsKeyPut) | **PUT** /api/v1/admin/controls/{key} | Apply Administration Control |
| [**applyAdministrationControlApiV1AdminControlsKeyPutWithHttpInfo**](AdministrationApi.md#applyAdministrationControlApiV1AdminControlsKeyPutWithHttpInfo) | **PUT** /api/v1/admin/controls/{key} | Apply Administration Control |
| [**listAdministrationAuditApiV1AdminAuditGet**](AdministrationApi.md#listAdministrationAuditApiV1AdminAuditGet) | **GET** /api/v1/admin/audit | List Administration Audit |
| [**listAdministrationAuditApiV1AdminAuditGetWithHttpInfo**](AdministrationApi.md#listAdministrationAuditApiV1AdminAuditGetWithHttpInfo) | **GET** /api/v1/admin/audit | List Administration Audit |
| [**listAdministrationControlsApiV1AdminControlsGet**](AdministrationApi.md#listAdministrationControlsApiV1AdminControlsGet) | **GET** /api/v1/admin/controls | List Administration Controls |
| [**listAdministrationControlsApiV1AdminControlsGetWithHttpInfo**](AdministrationApi.md#listAdministrationControlsApiV1AdminControlsGetWithHttpInfo) | **GET** /api/v1/admin/controls | List Administration Controls |
| [**previewAdministrationControlApiV1AdminControlsPreviewPost**](AdministrationApi.md#previewAdministrationControlApiV1AdminControlsPreviewPost) | **POST** /api/v1/admin/controls/preview | Preview Administration Control |
| [**previewAdministrationControlApiV1AdminControlsPreviewPostWithHttpInfo**](AdministrationApi.md#previewAdministrationControlApiV1AdminControlsPreviewPostWithHttpInfo) | **POST** /api/v1/admin/controls/preview | Preview Administration Control |



## applyAdministrationControlApiV1AdminControlsKeyPut

> AdministrationControl applyAdministrationControlApiV1AdminControlsKeyPut(key, administrationApplyRequest, authorization, xAmeshCSRF, xAmeshTenant)

Apply Administration Control

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AdministrationApi apiInstance = new AdministrationApi(defaultClient);
        AdministrationControlKey key = AdministrationControlKey.fromValue("RETENTION"); // AdministrationControlKey |
        AdministrationApplyRequest administrationApplyRequest = new AdministrationApplyRequest(); // AdministrationApplyRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AdministrationControl result = apiInstance.applyAdministrationControlApiV1AdminControlsKeyPut(key, administrationApplyRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AdministrationApi#applyAdministrationControlApiV1AdminControlsKeyPut");
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
| **key** | **AdministrationControlKey**|  | [enum: RETENTION, ANNOUNCEMENT, MAINTENANCE, KILL_SWITCH] |
| **administrationApplyRequest** | **AdministrationApplyRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AdministrationControl**


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

## applyAdministrationControlApiV1AdminControlsKeyPutWithHttpInfo

> ApiResponse<AdministrationControl> applyAdministrationControlApiV1AdminControlsKeyPutWithHttpInfo(key, administrationApplyRequest, authorization, xAmeshCSRF, xAmeshTenant)

Apply Administration Control

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AdministrationApi apiInstance = new AdministrationApi(defaultClient);
        AdministrationControlKey key = AdministrationControlKey.fromValue("RETENTION"); // AdministrationControlKey |
        AdministrationApplyRequest administrationApplyRequest = new AdministrationApplyRequest(); // AdministrationApplyRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AdministrationControl> response = apiInstance.applyAdministrationControlApiV1AdminControlsKeyPutWithHttpInfo(key, administrationApplyRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AdministrationApi#applyAdministrationControlApiV1AdminControlsKeyPut");
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
| **key** | **AdministrationControlKey**|  | [enum: RETENTION, ANNOUNCEMENT, MAINTENANCE, KILL_SWITCH] |
| **administrationApplyRequest** | **AdministrationApplyRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AdministrationControl**>


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


## listAdministrationAuditApiV1AdminAuditGet

> List<AdministrationAuditEntry> listAdministrationAuditApiV1AdminAuditGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Administration Audit

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AdministrationApi apiInstance = new AdministrationApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<AdministrationAuditEntry> result = apiInstance.listAdministrationAuditApiV1AdminAuditGet(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AdministrationApi#listAdministrationAuditApiV1AdminAuditGet");
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

**List&lt;AdministrationAuditEntry&gt;**


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

## listAdministrationAuditApiV1AdminAuditGetWithHttpInfo

> ApiResponse<List<AdministrationAuditEntry>> listAdministrationAuditApiV1AdminAuditGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Administration Audit

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AdministrationApi apiInstance = new AdministrationApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<AdministrationAuditEntry>> response = apiInstance.listAdministrationAuditApiV1AdminAuditGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AdministrationApi#listAdministrationAuditApiV1AdminAuditGet");
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

ApiResponse<**List&lt;AdministrationAuditEntry&gt;**>


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


## listAdministrationControlsApiV1AdminControlsGet

> List<AdministrationControl> listAdministrationControlsApiV1AdminControlsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Administration Controls

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AdministrationApi apiInstance = new AdministrationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<AdministrationControl> result = apiInstance.listAdministrationControlsApiV1AdminControlsGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AdministrationApi#listAdministrationControlsApiV1AdminControlsGet");
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

**List&lt;AdministrationControl&gt;**


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

## listAdministrationControlsApiV1AdminControlsGetWithHttpInfo

> ApiResponse<List<AdministrationControl>> listAdministrationControlsApiV1AdminControlsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Administration Controls

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AdministrationApi apiInstance = new AdministrationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<AdministrationControl>> response = apiInstance.listAdministrationControlsApiV1AdminControlsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AdministrationApi#listAdministrationControlsApiV1AdminControlsGet");
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

ApiResponse<**List&lt;AdministrationControl&gt;**>


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


## previewAdministrationControlApiV1AdminControlsPreviewPost

> AdministrationImpactPreview previewAdministrationControlApiV1AdminControlsPreviewPost(administrationControlDraft, authorization, xAmeshCSRF, xAmeshTenant)

Preview Administration Control

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AdministrationApi apiInstance = new AdministrationApi(defaultClient);
        AdministrationControlDraft administrationControlDraft = new AdministrationControlDraft(); // AdministrationControlDraft |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AdministrationImpactPreview result = apiInstance.previewAdministrationControlApiV1AdminControlsPreviewPost(administrationControlDraft, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AdministrationApi#previewAdministrationControlApiV1AdminControlsPreviewPost");
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
| **administrationControlDraft** | **AdministrationControlDraft**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AdministrationImpactPreview**


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

## previewAdministrationControlApiV1AdminControlsPreviewPostWithHttpInfo

> ApiResponse<AdministrationImpactPreview> previewAdministrationControlApiV1AdminControlsPreviewPostWithHttpInfo(administrationControlDraft, authorization, xAmeshCSRF, xAmeshTenant)

Preview Administration Control

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AdministrationApi apiInstance = new AdministrationApi(defaultClient);
        AdministrationControlDraft administrationControlDraft = new AdministrationControlDraft(); // AdministrationControlDraft |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AdministrationImpactPreview> response = apiInstance.previewAdministrationControlApiV1AdminControlsPreviewPostWithHttpInfo(administrationControlDraft, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AdministrationApi#previewAdministrationControlApiV1AdminControlsPreviewPost");
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
| **administrationControlDraft** | **AdministrationControlDraft**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AdministrationImpactPreview**>


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
