# PluginsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet**](PluginsApi.md#downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet) | **GET** /api/v1/plugin-registry/blobs/{digest} | Download Plugin Registry Bundle |
| [**downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGetWithHttpInfo**](PluginsApi.md#downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGetWithHttpInfo) | **GET** /api/v1/plugin-registry/blobs/{digest} | Download Plugin Registry Bundle |
| [**exportPluginRegistryApiV1PluginRegistryOfflineExportGet**](PluginsApi.md#exportPluginRegistryApiV1PluginRegistryOfflineExportGet) | **GET** /api/v1/plugin-registry/offline-export | Export Plugin Registry |
| [**exportPluginRegistryApiV1PluginRegistryOfflineExportGetWithHttpInfo**](PluginsApi.md#exportPluginRegistryApiV1PluginRegistryOfflineExportGetWithHttpInfo) | **GET** /api/v1/plugin-registry/offline-export | Export Plugin Registry |
| [**getPluginRegistryIndexApiV1PluginRegistryIndexGet**](PluginsApi.md#getPluginRegistryIndexApiV1PluginRegistryIndexGet) | **GET** /api/v1/plugin-registry/index | Get Plugin Registry Index |
| [**getPluginRegistryIndexApiV1PluginRegistryIndexGetWithHttpInfo**](PluginsApi.md#getPluginRegistryIndexApiV1PluginRegistryIndexGetWithHttpInfo) | **GET** /api/v1/plugin-registry/index | Get Plugin Registry Index |
| [**getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet**](PluginsApi.md#getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet) | **GET** /api/v1/plugin-registry/packages/{name}/{version} | Get Plugin Registry Package |
| [**getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGetWithHttpInfo**](PluginsApi.md#getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGetWithHttpInfo) | **GET** /api/v1/plugin-registry/packages/{name}/{version} | Get Plugin Registry Package |
| [**importPluginRegistryApiV1PluginRegistryOfflineImportPost**](PluginsApi.md#importPluginRegistryApiV1PluginRegistryOfflineImportPost) | **POST** /api/v1/plugin-registry/offline-import | Import Plugin Registry |
| [**importPluginRegistryApiV1PluginRegistryOfflineImportPostWithHttpInfo**](PluginsApi.md#importPluginRegistryApiV1PluginRegistryOfflineImportPostWithHttpInfo) | **POST** /api/v1/plugin-registry/offline-import | Import Plugin Registry |
| [**installPluginBundleApiV1PluginsInstallPost**](PluginsApi.md#installPluginBundleApiV1PluginsInstallPost) | **POST** /api/v1/plugins/install | Install Plugin Bundle |
| [**installPluginBundleApiV1PluginsInstallPostWithHttpInfo**](PluginsApi.md#installPluginBundleApiV1PluginsInstallPostWithHttpInfo) | **POST** /api/v1/plugins/install | Install Plugin Bundle |
| [**isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet**](PluginsApi.md#isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet) | **GET** /api/v1/plugins/isolated-runtime | Isolated Plugin Runtime Status |
| [**isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGetWithHttpInfo**](PluginsApi.md#isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGetWithHttpInfo) | **GET** /api/v1/plugins/isolated-runtime | Isolated Plugin Runtime Status |
| [**listPluginsApiV1PluginsGet**](PluginsApi.md#listPluginsApiV1PluginsGet) | **GET** /api/v1/plugins | List Plugins |
| [**listPluginsApiV1PluginsGetWithHttpInfo**](PluginsApi.md#listPluginsApiV1PluginsGetWithHttpInfo) | **GET** /api/v1/plugins | List Plugins |
| [**publishPluginRegistryPackageApiV1PluginRegistryPackagesPost**](PluginsApi.md#publishPluginRegistryPackageApiV1PluginRegistryPackagesPost) | **POST** /api/v1/plugin-registry/packages | Publish Plugin Registry Package |
| [**publishPluginRegistryPackageApiV1PluginRegistryPackagesPostWithHttpInfo**](PluginsApi.md#publishPluginRegistryPackageApiV1PluginRegistryPackagesPostWithHttpInfo) | **POST** /api/v1/plugin-registry/packages | Publish Plugin Registry Package |
| [**refreshPluginsApiV1PluginsRefreshPost**](PluginsApi.md#refreshPluginsApiV1PluginsRefreshPost) | **POST** /api/v1/plugins/refresh | Refresh Plugins |
| [**refreshPluginsApiV1PluginsRefreshPostWithHttpInfo**](PluginsApi.md#refreshPluginsApiV1PluginsRefreshPostWithHttpInfo) | **POST** /api/v1/plugins/refresh | Refresh Plugins |
| [**trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet**](PluginsApi.md#trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet) | **GET** /api/v1/plugins/trusted-runtime | Trusted Plugin Runtime Status |
| [**trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGetWithHttpInfo**](PluginsApi.md#trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGetWithHttpInfo) | **GET** /api/v1/plugins/trusted-runtime | Trusted Plugin Runtime Status |
| [**yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost**](PluginsApi.md#yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost) | **POST** /api/v1/plugin-registry/packages/{name}/{version}/yank | Yank Plugin Registry Package |
| [**yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPostWithHttpInfo**](PluginsApi.md#yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPostWithHttpInfo) | **POST** /api/v1/plugin-registry/packages/{name}/{version}/yank | Yank Plugin Registry Package |



## downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet

> void downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet(digest, authorization, xAmeshCSRF, xAmeshTenant)

Download Plugin Registry Bundle

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String digest = "digest_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet(digest, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet");
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
| **digest** | **String**|  | |
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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGetWithHttpInfo

> ApiResponse<Void> downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGetWithHttpInfo(digest, authorization, xAmeshCSRF, xAmeshTenant)

Download Plugin Registry Bundle

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String digest = "digest_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGetWithHttpInfo(digest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet");
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
| **digest** | **String**|  | |
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
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## exportPluginRegistryApiV1PluginRegistryOfflineExportGet

> void exportPluginRegistryApiV1PluginRegistryOfflineExportGet(authorization, xAmeshCSRF, xAmeshTenant)

Export Plugin Registry

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.exportPluginRegistryApiV1PluginRegistryOfflineExportGet(authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#exportPluginRegistryApiV1PluginRegistryOfflineExportGet");
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


null (empty response body)

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

## exportPluginRegistryApiV1PluginRegistryOfflineExportGetWithHttpInfo

> ApiResponse<Void> exportPluginRegistryApiV1PluginRegistryOfflineExportGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Export Plugin Registry

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.exportPluginRegistryApiV1PluginRegistryOfflineExportGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#exportPluginRegistryApiV1PluginRegistryOfflineExportGet");
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


ApiResponse<Void>

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


## getPluginRegistryIndexApiV1PluginRegistryIndexGet

> PluginRegistryIndex getPluginRegistryIndexApiV1PluginRegistryIndexGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Plugin Registry Index

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PluginRegistryIndex result = apiInstance.getPluginRegistryIndexApiV1PluginRegistryIndexGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#getPluginRegistryIndexApiV1PluginRegistryIndexGet");
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

[**PluginRegistryIndex**](PluginRegistryIndex.md)


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

## getPluginRegistryIndexApiV1PluginRegistryIndexGetWithHttpInfo

> ApiResponse<PluginRegistryIndex> getPluginRegistryIndexApiV1PluginRegistryIndexGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Get Plugin Registry Index

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PluginRegistryIndex> response = apiInstance.getPluginRegistryIndexApiV1PluginRegistryIndexGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#getPluginRegistryIndexApiV1PluginRegistryIndexGet");
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

ApiResponse<[**PluginRegistryIndex**](PluginRegistryIndex.md)>


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


## getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet

> PluginRegistryPackage getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet(name, version, authorization, xAmeshCSRF, xAmeshTenant)

Get Plugin Registry Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String name = "name_example"; // String |
        String version = "version_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PluginRegistryPackage result = apiInstance.getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet(name, version, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet");
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
| **name** | **String**|  | |
| **version** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)


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

## getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGetWithHttpInfo

> ApiResponse<PluginRegistryPackage> getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGetWithHttpInfo(name, version, authorization, xAmeshCSRF, xAmeshTenant)

Get Plugin Registry Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String name = "name_example"; // String |
        String version = "version_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PluginRegistryPackage> response = apiInstance.getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGetWithHttpInfo(name, version, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet");
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
| **name** | **String**|  | |
| **version** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**PluginRegistryPackage**](PluginRegistryPackage.md)>


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


## importPluginRegistryApiV1PluginRegistryOfflineImportPost

> PluginRegistryIndex importPluginRegistryApiV1PluginRegistryOfflineImportPost(authorization, xAmeshCSRF, xAmeshTenant)

Import Plugin Registry

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PluginRegistryIndex result = apiInstance.importPluginRegistryApiV1PluginRegistryOfflineImportPost(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#importPluginRegistryApiV1PluginRegistryOfflineImportPost");
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

[**PluginRegistryIndex**](PluginRegistryIndex.md)


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

## importPluginRegistryApiV1PluginRegistryOfflineImportPostWithHttpInfo

> ApiResponse<PluginRegistryIndex> importPluginRegistryApiV1PluginRegistryOfflineImportPostWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Import Plugin Registry

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PluginRegistryIndex> response = apiInstance.importPluginRegistryApiV1PluginRegistryOfflineImportPostWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#importPluginRegistryApiV1PluginRegistryOfflineImportPost");
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

ApiResponse<[**PluginRegistryIndex**](PluginRegistryIndex.md)>


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


## installPluginBundleApiV1PluginsInstallPost

> PluginCatalogSnapshot installPluginBundleApiV1PluginsInstallPost(contentDigest, authorization, xAmeshCSRF, xAmeshTenant)

Install Plugin Bundle

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String contentDigest = "contentDigest_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PluginCatalogSnapshot result = apiInstance.installPluginBundleApiV1PluginsInstallPost(contentDigest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#installPluginBundleApiV1PluginsInstallPost");
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
| **contentDigest** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)


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

## installPluginBundleApiV1PluginsInstallPostWithHttpInfo

> ApiResponse<PluginCatalogSnapshot> installPluginBundleApiV1PluginsInstallPostWithHttpInfo(contentDigest, authorization, xAmeshCSRF, xAmeshTenant)

Install Plugin Bundle

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String contentDigest = "contentDigest_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PluginCatalogSnapshot> response = apiInstance.installPluginBundleApiV1PluginsInstallPostWithHttpInfo(contentDigest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#installPluginBundleApiV1PluginsInstallPost");
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
| **contentDigest** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)>


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


## isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet

> IsolatedPluginRuntimeSnapshot isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet(authorization, xAmeshCSRF, xAmeshTenant)

Isolated Plugin Runtime Status

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            IsolatedPluginRuntimeSnapshot result = apiInstance.isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet");
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

[**IsolatedPluginRuntimeSnapshot**](IsolatedPluginRuntimeSnapshot.md)


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

## isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGetWithHttpInfo

> ApiResponse<IsolatedPluginRuntimeSnapshot> isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Isolated Plugin Runtime Status

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<IsolatedPluginRuntimeSnapshot> response = apiInstance.isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet");
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

ApiResponse<[**IsolatedPluginRuntimeSnapshot**](IsolatedPluginRuntimeSnapshot.md)>


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


## listPluginsApiV1PluginsGet

> PluginCatalogSnapshot listPluginsApiV1PluginsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Plugins

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PluginCatalogSnapshot result = apiInstance.listPluginsApiV1PluginsGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#listPluginsApiV1PluginsGet");
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

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)


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

## listPluginsApiV1PluginsGetWithHttpInfo

> ApiResponse<PluginCatalogSnapshot> listPluginsApiV1PluginsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Plugins

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PluginCatalogSnapshot> response = apiInstance.listPluginsApiV1PluginsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#listPluginsApiV1PluginsGet");
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

ApiResponse<[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)>


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


## publishPluginRegistryPackageApiV1PluginRegistryPackagesPost

> PluginRegistryPackage publishPluginRegistryPackageApiV1PluginRegistryPackagesPost(pluginRegistryPublishRequest, authorization, xAmeshCSRF, xAmeshTenant)

Publish Plugin Registry Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        PluginRegistryPublishRequest pluginRegistryPublishRequest = new PluginRegistryPublishRequest(); // PluginRegistryPublishRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PluginRegistryPackage result = apiInstance.publishPluginRegistryPackageApiV1PluginRegistryPackagesPost(pluginRegistryPublishRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#publishPluginRegistryPackageApiV1PluginRegistryPackagesPost");
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
| **pluginRegistryPublishRequest** | [**PluginRegistryPublishRequest**](PluginRegistryPublishRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)


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

## publishPluginRegistryPackageApiV1PluginRegistryPackagesPostWithHttpInfo

> ApiResponse<PluginRegistryPackage> publishPluginRegistryPackageApiV1PluginRegistryPackagesPostWithHttpInfo(pluginRegistryPublishRequest, authorization, xAmeshCSRF, xAmeshTenant)

Publish Plugin Registry Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        PluginRegistryPublishRequest pluginRegistryPublishRequest = new PluginRegistryPublishRequest(); // PluginRegistryPublishRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PluginRegistryPackage> response = apiInstance.publishPluginRegistryPackageApiV1PluginRegistryPackagesPostWithHttpInfo(pluginRegistryPublishRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#publishPluginRegistryPackageApiV1PluginRegistryPackagesPost");
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
| **pluginRegistryPublishRequest** | [**PluginRegistryPublishRequest**](PluginRegistryPublishRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**PluginRegistryPackage**](PluginRegistryPackage.md)>


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


## refreshPluginsApiV1PluginsRefreshPost

> PluginCatalogSnapshot refreshPluginsApiV1PluginsRefreshPost(authorization, xAmeshCSRF, xAmeshTenant)

Refresh Plugins

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PluginCatalogSnapshot result = apiInstance.refreshPluginsApiV1PluginsRefreshPost(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#refreshPluginsApiV1PluginsRefreshPost");
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

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)


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

## refreshPluginsApiV1PluginsRefreshPostWithHttpInfo

> ApiResponse<PluginCatalogSnapshot> refreshPluginsApiV1PluginsRefreshPostWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Refresh Plugins

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PluginCatalogSnapshot> response = apiInstance.refreshPluginsApiV1PluginsRefreshPostWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#refreshPluginsApiV1PluginsRefreshPost");
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

ApiResponse<[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)>


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


## trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet

> TrustedPluginRuntimeSnapshot trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet(authorization, xAmeshCSRF, xAmeshTenant)

Trusted Plugin Runtime Status

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            TrustedPluginRuntimeSnapshot result = apiInstance.trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet");
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

[**TrustedPluginRuntimeSnapshot**](TrustedPluginRuntimeSnapshot.md)


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

## trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGetWithHttpInfo

> ApiResponse<TrustedPluginRuntimeSnapshot> trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Trusted Plugin Runtime Status

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<TrustedPluginRuntimeSnapshot> response = apiInstance.trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet");
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

ApiResponse<[**TrustedPluginRuntimeSnapshot**](TrustedPluginRuntimeSnapshot.md)>


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


## yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost

> PluginRegistryPackage yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost(name, version, pluginRegistryYankRequest, authorization, xAmeshCSRF, xAmeshTenant)

Yank Plugin Registry Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String name = "name_example"; // String |
        String version = "version_example"; // String |
        PluginRegistryYankRequest pluginRegistryYankRequest = new PluginRegistryYankRequest(); // PluginRegistryYankRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PluginRegistryPackage result = apiInstance.yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost(name, version, pluginRegistryYankRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost");
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
| **name** | **String**|  | |
| **version** | **String**|  | |
| **pluginRegistryYankRequest** | [**PluginRegistryYankRequest**](PluginRegistryYankRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)


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

## yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPostWithHttpInfo

> ApiResponse<PluginRegistryPackage> yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPostWithHttpInfo(name, version, pluginRegistryYankRequest, authorization, xAmeshCSRF, xAmeshTenant)

Yank Plugin Registry Package

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.PluginsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        PluginsApi apiInstance = new PluginsApi(defaultClient);
        String name = "name_example"; // String |
        String version = "version_example"; // String |
        PluginRegistryYankRequest pluginRegistryYankRequest = new PluginRegistryYankRequest(); // PluginRegistryYankRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PluginRegistryPackage> response = apiInstance.yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPostWithHttpInfo(name, version, pluginRegistryYankRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling PluginsApi#yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost");
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
| **name** | **String**|  | |
| **version** | **String**|  | |
| **pluginRegistryYankRequest** | [**PluginRegistryYankRequest**](PluginRegistryYankRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**PluginRegistryPackage**](PluginRegistryPackage.md)>


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
