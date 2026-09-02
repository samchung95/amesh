# ModelEnginesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost**](ModelEnginesApi.md#accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost) | **POST** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/login | Account Login Start |
| [**accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPostWithHttpInfo**](ModelEnginesApi.md#accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPostWithHttpInfo) | **POST** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/login | Account Login Start |
| [**accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost**](ModelEnginesApi.md#accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost) | **POST** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/logout | Account Logout |
| [**accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPostWithHttpInfo**](ModelEnginesApi.md#accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPostWithHttpInfo) | **POST** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/logout | Account Logout |
| [**accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet**](ModelEnginesApi.md#accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet) | **GET** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/status | Account Status |
| [**accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGetWithHttpInfo**](ModelEnginesApi.md#accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/status | Account Status |
| [**catalogApiV1NamespacesNamespaceModelEnginesCatalogGet**](ModelEnginesApi.md#catalogApiV1NamespacesNamespaceModelEnginesCatalogGet) | **GET** /api/v1/namespaces/{namespace}/model-engines/catalog | Catalog |
| [**catalogApiV1NamespacesNamespaceModelEnginesCatalogGetWithHttpInfo**](ModelEnginesApi.md#catalogApiV1NamespacesNamespaceModelEnginesCatalogGetWithHttpInfo) | **GET** /api/v1/namespaces/{namespace}/model-engines/catalog | Catalog |



## accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost

> ModelEngineLoginStartResponse accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost(namespace, adapter, engineRef, modelEngineLoginRequest, xAmeshTenant, authorization, xAmeshCSRF)

Account Login Start

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ModelEnginesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ModelEnginesApi apiInstance = new ModelEnginesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String adapter = "adapter_example"; // String |
        String engineRef = "engineRef_example"; // String |
        ModelEngineLoginRequest modelEngineLoginRequest = new ModelEngineLoginRequest(); // ModelEngineLoginRequest |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ModelEngineLoginStartResponse result = apiInstance.accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost(namespace, adapter, engineRef, modelEngineLoginRequest, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ModelEnginesApi#accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost");
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
| **adapter** | **String**|  | |
| **engineRef** | **String**|  | |
| **modelEngineLoginRequest** | **ModelEngineLoginRequest**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**ModelEngineLoginStartResponse**


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

## accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPostWithHttpInfo

> ApiResponse<ModelEngineLoginStartResponse> accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPostWithHttpInfo(namespace, adapter, engineRef, modelEngineLoginRequest, xAmeshTenant, authorization, xAmeshCSRF)

Account Login Start

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ModelEnginesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ModelEnginesApi apiInstance = new ModelEnginesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String adapter = "adapter_example"; // String |
        String engineRef = "engineRef_example"; // String |
        ModelEngineLoginRequest modelEngineLoginRequest = new ModelEngineLoginRequest(); // ModelEngineLoginRequest |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ModelEngineLoginStartResponse> response = apiInstance.accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPostWithHttpInfo(namespace, adapter, engineRef, modelEngineLoginRequest, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ModelEnginesApi#accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost");
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
| **adapter** | **String**|  | |
| **engineRef** | **String**|  | |
| **modelEngineLoginRequest** | **ModelEngineLoginRequest**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**ModelEngineLoginStartResponse**>


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


## accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost

> ModelEngineLogoutResponse accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF)

Account Logout

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ModelEnginesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ModelEnginesApi apiInstance = new ModelEnginesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String adapter = "adapter_example"; // String |
        String engineRef = "engineRef_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ModelEngineLogoutResponse result = apiInstance.accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ModelEnginesApi#accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost");
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
| **adapter** | **String**|  | |
| **engineRef** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**ModelEngineLogoutResponse**


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

## accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPostWithHttpInfo

> ApiResponse<ModelEngineLogoutResponse> accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPostWithHttpInfo(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF)

Account Logout

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ModelEnginesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ModelEnginesApi apiInstance = new ModelEnginesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String adapter = "adapter_example"; // String |
        String engineRef = "engineRef_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ModelEngineLogoutResponse> response = apiInstance.accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPostWithHttpInfo(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ModelEnginesApi#accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost");
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
| **adapter** | **String**|  | |
| **engineRef** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**ModelEngineLogoutResponse**>


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


## accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet

> ModelEngineAccountStatusResponse accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF)

Account Status

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ModelEnginesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ModelEnginesApi apiInstance = new ModelEnginesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String adapter = "adapter_example"; // String |
        String engineRef = "engineRef_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ModelEngineAccountStatusResponse result = apiInstance.accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ModelEnginesApi#accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet");
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
| **adapter** | **String**|  | |
| **engineRef** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

**ModelEngineAccountStatusResponse**


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

## accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGetWithHttpInfo

> ApiResponse<ModelEngineAccountStatusResponse> accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGetWithHttpInfo(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF)

Account Status

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ModelEnginesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ModelEnginesApi apiInstance = new ModelEnginesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String adapter = "adapter_example"; // String |
        String engineRef = "engineRef_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ModelEngineAccountStatusResponse> response = apiInstance.accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGetWithHttpInfo(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ModelEnginesApi#accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet");
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
| **adapter** | **String**|  | |
| **engineRef** | **String**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<**ModelEngineAccountStatusResponse**>


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


## catalogApiV1NamespacesNamespaceModelEnginesCatalogGet

> ModelEngineCatalog catalogApiV1NamespacesNamespaceModelEnginesCatalogGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Catalog

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ModelEnginesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ModelEnginesApi apiInstance = new ModelEnginesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ModelEngineCatalog result = apiInstance.catalogApiV1NamespacesNamespaceModelEnginesCatalogGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ModelEnginesApi#catalogApiV1NamespacesNamespaceModelEnginesCatalogGet");
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

**ModelEngineCatalog**


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

## catalogApiV1NamespacesNamespaceModelEnginesCatalogGetWithHttpInfo

> ApiResponse<ModelEngineCatalog> catalogApiV1NamespacesNamespaceModelEnginesCatalogGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Catalog

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ModelEnginesApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ModelEnginesApi apiInstance = new ModelEnginesApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ModelEngineCatalog> response = apiInstance.catalogApiV1NamespacesNamespaceModelEnginesCatalogGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ModelEnginesApi#catalogApiV1NamespacesNamespaceModelEnginesCatalogGet");
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

ApiResponse<**ModelEngineCatalog**>


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
