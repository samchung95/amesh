# TenantsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createTenantApiV1AdminTenantsPost**](TenantsApi.md#createTenantApiV1AdminTenantsPost) | **POST** /api/v1/admin/tenants | Create Tenant |
| [**createTenantApiV1AdminTenantsPostWithHttpInfo**](TenantsApi.md#createTenantApiV1AdminTenantsPostWithHttpInfo) | **POST** /api/v1/admin/tenants | Create Tenant |
| [**deleteTenantApiV1AdminTenantsTenantSlugDelete**](TenantsApi.md#deleteTenantApiV1AdminTenantsTenantSlugDelete) | **DELETE** /api/v1/admin/tenants/{tenant_slug} | Delete Tenant |
| [**deleteTenantApiV1AdminTenantsTenantSlugDeleteWithHttpInfo**](TenantsApi.md#deleteTenantApiV1AdminTenantsTenantSlugDeleteWithHttpInfo) | **DELETE** /api/v1/admin/tenants/{tenant_slug} | Delete Tenant |
| [**exportTenantApiV1AdminTenantsTenantSlugExportsPost**](TenantsApi.md#exportTenantApiV1AdminTenantsTenantSlugExportsPost) | **POST** /api/v1/admin/tenants/{tenant_slug}/exports | Export Tenant |
| [**exportTenantApiV1AdminTenantsTenantSlugExportsPostWithHttpInfo**](TenantsApi.md#exportTenantApiV1AdminTenantsTenantSlugExportsPostWithHttpInfo) | **POST** /api/v1/admin/tenants/{tenant_slug}/exports | Export Tenant |
| [**getTenantApiV1AdminTenantsTenantSlugGet**](TenantsApi.md#getTenantApiV1AdminTenantsTenantSlugGet) | **GET** /api/v1/admin/tenants/{tenant_slug} | Get Tenant |
| [**getTenantApiV1AdminTenantsTenantSlugGetWithHttpInfo**](TenantsApi.md#getTenantApiV1AdminTenantsTenantSlugGetWithHttpInfo) | **GET** /api/v1/admin/tenants/{tenant_slug} | Get Tenant |
| [**listTenantsApiV1AdminTenantsGet**](TenantsApi.md#listTenantsApiV1AdminTenantsGet) | **GET** /api/v1/admin/tenants | List Tenants |
| [**listTenantsApiV1AdminTenantsGetWithHttpInfo**](TenantsApi.md#listTenantsApiV1AdminTenantsGetWithHttpInfo) | **GET** /api/v1/admin/tenants | List Tenants |
| [**restoreTenantApiV1AdminTenantsTenantSlugRestorePost**](TenantsApi.md#restoreTenantApiV1AdminTenantsTenantSlugRestorePost) | **POST** /api/v1/admin/tenants/{tenant_slug}/restore | Restore Tenant |
| [**restoreTenantApiV1AdminTenantsTenantSlugRestorePostWithHttpInfo**](TenantsApi.md#restoreTenantApiV1AdminTenantsTenantSlugRestorePostWithHttpInfo) | **POST** /api/v1/admin/tenants/{tenant_slug}/restore | Restore Tenant |
| [**suspendTenantApiV1AdminTenantsTenantSlugSuspendPost**](TenantsApi.md#suspendTenantApiV1AdminTenantsTenantSlugSuspendPost) | **POST** /api/v1/admin/tenants/{tenant_slug}/suspend | Suspend Tenant |
| [**suspendTenantApiV1AdminTenantsTenantSlugSuspendPostWithHttpInfo**](TenantsApi.md#suspendTenantApiV1AdminTenantsTenantSlugSuspendPostWithHttpInfo) | **POST** /api/v1/admin/tenants/{tenant_slug}/suspend | Suspend Tenant |
| [**updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut**](TenantsApi.md#updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut) | **PUT** /api/v1/admin/tenants/{tenant_slug}/policy | Update Tenant Policy |
| [**updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPutWithHttpInfo**](TenantsApi.md#updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPutWithHttpInfo) | **PUT** /api/v1/admin/tenants/{tenant_slug}/policy | Update Tenant Policy |



## createTenantApiV1AdminTenantsPost

> TenantDefinition createTenantApiV1AdminTenantsPost(createTenantRequest, authorization, xAmeshCSRF)

Create Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        CreateTenantRequest createTenantRequest = new CreateTenantRequest(); // CreateTenantRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            TenantDefinition result = apiInstance.createTenantApiV1AdminTenantsPost(createTenantRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#createTenantApiV1AdminTenantsPost");
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
| **createTenantRequest** | [**CreateTenantRequest**](CreateTenantRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**TenantDefinition**](TenantDefinition.md)


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

## createTenantApiV1AdminTenantsPostWithHttpInfo

> ApiResponse<TenantDefinition> createTenantApiV1AdminTenantsPostWithHttpInfo(createTenantRequest, authorization, xAmeshCSRF)

Create Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        CreateTenantRequest createTenantRequest = new CreateTenantRequest(); // CreateTenantRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<TenantDefinition> response = apiInstance.createTenantApiV1AdminTenantsPostWithHttpInfo(createTenantRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#createTenantApiV1AdminTenantsPost");
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
| **createTenantRequest** | [**CreateTenantRequest**](CreateTenantRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**TenantDefinition**](TenantDefinition.md)>


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


## deleteTenantApiV1AdminTenantsTenantSlugDelete

> TenantDefinition deleteTenantApiV1AdminTenantsTenantSlugDelete(tenantSlug, authorization, xAmeshCSRF)

Delete Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            TenantDefinition result = apiInstance.deleteTenantApiV1AdminTenantsTenantSlugDelete(tenantSlug, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#deleteTenantApiV1AdminTenantsTenantSlugDelete");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**TenantDefinition**](TenantDefinition.md)


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

## deleteTenantApiV1AdminTenantsTenantSlugDeleteWithHttpInfo

> ApiResponse<TenantDefinition> deleteTenantApiV1AdminTenantsTenantSlugDeleteWithHttpInfo(tenantSlug, authorization, xAmeshCSRF)

Delete Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<TenantDefinition> response = apiInstance.deleteTenantApiV1AdminTenantsTenantSlugDeleteWithHttpInfo(tenantSlug, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#deleteTenantApiV1AdminTenantsTenantSlugDelete");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**TenantDefinition**](TenantDefinition.md)>


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


## exportTenantApiV1AdminTenantsTenantSlugExportsPost

> TenantExport exportTenantApiV1AdminTenantsTenantSlugExportsPost(tenantSlug, authorization, xAmeshCSRF)

Export Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            TenantExport result = apiInstance.exportTenantApiV1AdminTenantsTenantSlugExportsPost(tenantSlug, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#exportTenantApiV1AdminTenantsTenantSlugExportsPost");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**TenantExport**](TenantExport.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## exportTenantApiV1AdminTenantsTenantSlugExportsPostWithHttpInfo

> ApiResponse<TenantExport> exportTenantApiV1AdminTenantsTenantSlugExportsPostWithHttpInfo(tenantSlug, authorization, xAmeshCSRF)

Export Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<TenantExport> response = apiInstance.exportTenantApiV1AdminTenantsTenantSlugExportsPostWithHttpInfo(tenantSlug, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#exportTenantApiV1AdminTenantsTenantSlugExportsPost");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**TenantExport**](TenantExport.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getTenantApiV1AdminTenantsTenantSlugGet

> TenantDefinition getTenantApiV1AdminTenantsTenantSlugGet(tenantSlug, authorization, xAmeshCSRF)

Get Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            TenantDefinition result = apiInstance.getTenantApiV1AdminTenantsTenantSlugGet(tenantSlug, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#getTenantApiV1AdminTenantsTenantSlugGet");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**TenantDefinition**](TenantDefinition.md)


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

## getTenantApiV1AdminTenantsTenantSlugGetWithHttpInfo

> ApiResponse<TenantDefinition> getTenantApiV1AdminTenantsTenantSlugGetWithHttpInfo(tenantSlug, authorization, xAmeshCSRF)

Get Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<TenantDefinition> response = apiInstance.getTenantApiV1AdminTenantsTenantSlugGetWithHttpInfo(tenantSlug, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#getTenantApiV1AdminTenantsTenantSlugGet");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**TenantDefinition**](TenantDefinition.md)>


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


## listTenantsApiV1AdminTenantsGet

> List<TenantDefinition> listTenantsApiV1AdminTenantsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Tenants

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            List<TenantDefinition> result = apiInstance.listTenantsApiV1AdminTenantsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#listTenantsApiV1AdminTenantsGet");
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
| **limit** | **Integer**|  | [optional] |
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**List&lt;TenantDefinition&gt;**](TenantDefinition.md)


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

## listTenantsApiV1AdminTenantsGetWithHttpInfo

> ApiResponse<List<TenantDefinition>> listTenantsApiV1AdminTenantsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Tenants

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<List<TenantDefinition>> response = apiInstance.listTenantsApiV1AdminTenantsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#listTenantsApiV1AdminTenantsGet");
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
| **limit** | **Integer**|  | [optional] |
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;TenantDefinition&gt;**](TenantDefinition.md)>


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


## restoreTenantApiV1AdminTenantsTenantSlugRestorePost

> TenantDefinition restoreTenantApiV1AdminTenantsTenantSlugRestorePost(tenantSlug, authorization, xAmeshCSRF)

Restore Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            TenantDefinition result = apiInstance.restoreTenantApiV1AdminTenantsTenantSlugRestorePost(tenantSlug, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#restoreTenantApiV1AdminTenantsTenantSlugRestorePost");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**TenantDefinition**](TenantDefinition.md)


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

## restoreTenantApiV1AdminTenantsTenantSlugRestorePostWithHttpInfo

> ApiResponse<TenantDefinition> restoreTenantApiV1AdminTenantsTenantSlugRestorePostWithHttpInfo(tenantSlug, authorization, xAmeshCSRF)

Restore Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<TenantDefinition> response = apiInstance.restoreTenantApiV1AdminTenantsTenantSlugRestorePostWithHttpInfo(tenantSlug, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#restoreTenantApiV1AdminTenantsTenantSlugRestorePost");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**TenantDefinition**](TenantDefinition.md)>


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


## suspendTenantApiV1AdminTenantsTenantSlugSuspendPost

> TenantDefinition suspendTenantApiV1AdminTenantsTenantSlugSuspendPost(tenantSlug, authorization, xAmeshCSRF)

Suspend Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            TenantDefinition result = apiInstance.suspendTenantApiV1AdminTenantsTenantSlugSuspendPost(tenantSlug, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#suspendTenantApiV1AdminTenantsTenantSlugSuspendPost");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**TenantDefinition**](TenantDefinition.md)


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

## suspendTenantApiV1AdminTenantsTenantSlugSuspendPostWithHttpInfo

> ApiResponse<TenantDefinition> suspendTenantApiV1AdminTenantsTenantSlugSuspendPostWithHttpInfo(tenantSlug, authorization, xAmeshCSRF)

Suspend Tenant

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<TenantDefinition> response = apiInstance.suspendTenantApiV1AdminTenantsTenantSlugSuspendPostWithHttpInfo(tenantSlug, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#suspendTenantApiV1AdminTenantsTenantSlugSuspendPost");
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
| **tenantSlug** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**TenantDefinition**](TenantDefinition.md)>


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


## updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut

> TenantDefinition updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut(tenantSlug, tenantPolicy, authorization, xAmeshCSRF)

Update Tenant Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        TenantPolicy tenantPolicy = new TenantPolicy(); // TenantPolicy |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            TenantDefinition result = apiInstance.updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut(tenantSlug, tenantPolicy, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut");
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
| **tenantSlug** | **String**|  | |
| **tenantPolicy** | [**TenantPolicy**](TenantPolicy.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**TenantDefinition**](TenantDefinition.md)


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

## updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPutWithHttpInfo

> ApiResponse<TenantDefinition> updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPutWithHttpInfo(tenantSlug, tenantPolicy, authorization, xAmeshCSRF)

Update Tenant Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.TenantsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        TenantsApi apiInstance = new TenantsApi(defaultClient);
        String tenantSlug = "tenantSlug_example"; // String |
        TenantPolicy tenantPolicy = new TenantPolicy(); // TenantPolicy |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<TenantDefinition> response = apiInstance.updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPutWithHttpInfo(tenantSlug, tenantPolicy, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling TenantsApi#updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut");
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
| **tenantSlug** | **String**|  | |
| **tenantPolicy** | [**TenantPolicy**](TenantPolicy.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**TenantDefinition**](TenantDefinition.md)>


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
