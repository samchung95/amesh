# AssetsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**declareAssetLineageApiV1AssetsLineagePost**](AssetsApi.md#declareAssetLineageApiV1AssetsLineagePost) | **POST** /api/v1/assets/lineage | Declare Asset Lineage |
| [**declareAssetLineageApiV1AssetsLineagePostWithHttpInfo**](AssetsApi.md#declareAssetLineageApiV1AssetsLineagePostWithHttpInfo) | **POST** /api/v1/assets/lineage | Declare Asset Lineage |
| [**exportAssetCatalogApiV1AssetsExportOpenlineageGet**](AssetsApi.md#exportAssetCatalogApiV1AssetsExportOpenlineageGet) | **GET** /api/v1/assets/export/openlineage | Export Asset Catalog |
| [**exportAssetCatalogApiV1AssetsExportOpenlineageGetWithHttpInfo**](AssetsApi.md#exportAssetCatalogApiV1AssetsExportOpenlineageGetWithHttpInfo) | **GET** /api/v1/assets/export/openlineage | Export Asset Catalog |
| [**getAssetCatalogEntryApiV1AssetsAssetIdGet**](AssetsApi.md#getAssetCatalogEntryApiV1AssetsAssetIdGet) | **GET** /api/v1/assets/{asset_id} | Get Asset Catalog Entry |
| [**getAssetCatalogEntryApiV1AssetsAssetIdGetWithHttpInfo**](AssetsApi.md#getAssetCatalogEntryApiV1AssetsAssetIdGetWithHttpInfo) | **GET** /api/v1/assets/{asset_id} | Get Asset Catalog Entry |
| [**listAssetsApiV1AssetsGet**](AssetsApi.md#listAssetsApiV1AssetsGet) | **GET** /api/v1/assets | List Assets |
| [**listAssetsApiV1AssetsGetWithHttpInfo**](AssetsApi.md#listAssetsApiV1AssetsGetWithHttpInfo) | **GET** /api/v1/assets | List Assets |
| [**recordAssetObservationApiV1AssetsObservationsPost**](AssetsApi.md#recordAssetObservationApiV1AssetsObservationsPost) | **POST** /api/v1/assets/observations | Record Asset Observation |
| [**recordAssetObservationApiV1AssetsObservationsPostWithHttpInfo**](AssetsApi.md#recordAssetObservationApiV1AssetsObservationsPostWithHttpInfo) | **POST** /api/v1/assets/observations | Record Asset Observation |
| [**registerAssetApiV1AssetsPost**](AssetsApi.md#registerAssetApiV1AssetsPost) | **POST** /api/v1/assets | Register Asset |
| [**registerAssetApiV1AssetsPostWithHttpInfo**](AssetsApi.md#registerAssetApiV1AssetsPostWithHttpInfo) | **POST** /api/v1/assets | Register Asset |



## declareAssetLineageApiV1AssetsLineagePost

> AssetLineageEdge declareAssetLineageApiV1AssetsLineagePost(assetLineageDeclaration, authorization, xAmeshCSRF, xAmeshTenant)

Declare Asset Lineage

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        AssetLineageDeclaration assetLineageDeclaration = new AssetLineageDeclaration(); // AssetLineageDeclaration |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AssetLineageEdge result = apiInstance.declareAssetLineageApiV1AssetsLineagePost(assetLineageDeclaration, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#declareAssetLineageApiV1AssetsLineagePost");
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
| **assetLineageDeclaration** | **AssetLineageDeclaration**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AssetLineageEdge**


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

## declareAssetLineageApiV1AssetsLineagePostWithHttpInfo

> ApiResponse<AssetLineageEdge> declareAssetLineageApiV1AssetsLineagePostWithHttpInfo(assetLineageDeclaration, authorization, xAmeshCSRF, xAmeshTenant)

Declare Asset Lineage

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        AssetLineageDeclaration assetLineageDeclaration = new AssetLineageDeclaration(); // AssetLineageDeclaration |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AssetLineageEdge> response = apiInstance.declareAssetLineageApiV1AssetsLineagePostWithHttpInfo(assetLineageDeclaration, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#declareAssetLineageApiV1AssetsLineagePost");
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
| **assetLineageDeclaration** | **AssetLineageDeclaration**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AssetLineageEdge**>


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


## exportAssetCatalogApiV1AssetsExportOpenlineageGet

> AssetCatalogExport exportAssetCatalogApiV1AssetsExportOpenlineageGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Export Asset Catalog

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AssetCatalogExport result = apiInstance.exportAssetCatalogApiV1AssetsExportOpenlineageGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#exportAssetCatalogApiV1AssetsExportOpenlineageGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AssetCatalogExport**


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

## exportAssetCatalogApiV1AssetsExportOpenlineageGetWithHttpInfo

> ApiResponse<AssetCatalogExport> exportAssetCatalogApiV1AssetsExportOpenlineageGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Export Asset Catalog

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AssetCatalogExport> response = apiInstance.exportAssetCatalogApiV1AssetsExportOpenlineageGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#exportAssetCatalogApiV1AssetsExportOpenlineageGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AssetCatalogExport**>


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


## getAssetCatalogEntryApiV1AssetsAssetIdGet

> AssetCatalogEntry getAssetCatalogEntryApiV1AssetsAssetIdGet(assetId, authorization, xAmeshCSRF, xAmeshTenant)

Get Asset Catalog Entry

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        UUID assetId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AssetCatalogEntry result = apiInstance.getAssetCatalogEntryApiV1AssetsAssetIdGet(assetId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#getAssetCatalogEntryApiV1AssetsAssetIdGet");
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
| **assetId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AssetCatalogEntry**


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

## getAssetCatalogEntryApiV1AssetsAssetIdGetWithHttpInfo

> ApiResponse<AssetCatalogEntry> getAssetCatalogEntryApiV1AssetsAssetIdGetWithHttpInfo(assetId, authorization, xAmeshCSRF, xAmeshTenant)

Get Asset Catalog Entry

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        UUID assetId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AssetCatalogEntry> response = apiInstance.getAssetCatalogEntryApiV1AssetsAssetIdGetWithHttpInfo(assetId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#getAssetCatalogEntryApiV1AssetsAssetIdGet");
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
| **assetId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AssetCatalogEntry**>


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


## listAssetsApiV1AssetsGet

> List<PersistedAsset> listAssetsApiV1AssetsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Assets

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<PersistedAsset> result = apiInstance.listAssetsApiV1AssetsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#listAssetsApiV1AssetsGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;PersistedAsset&gt;**


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

## listAssetsApiV1AssetsGetWithHttpInfo

> ApiResponse<List<PersistedAsset>> listAssetsApiV1AssetsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Assets

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<PersistedAsset>> response = apiInstance.listAssetsApiV1AssetsGetWithHttpInfo(namespace, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#listAssetsApiV1AssetsGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;PersistedAsset&gt;**>


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


## recordAssetObservationApiV1AssetsObservationsPost

> AssetObservation recordAssetObservationApiV1AssetsObservationsPost(assetObservationCreate, authorization, xAmeshCSRF, xAmeshTenant)

Record Asset Observation

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        AssetObservationCreate assetObservationCreate = new AssetObservationCreate(); // AssetObservationCreate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AssetObservation result = apiInstance.recordAssetObservationApiV1AssetsObservationsPost(assetObservationCreate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#recordAssetObservationApiV1AssetsObservationsPost");
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
| **assetObservationCreate** | **AssetObservationCreate**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AssetObservation**


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

## recordAssetObservationApiV1AssetsObservationsPostWithHttpInfo

> ApiResponse<AssetObservation> recordAssetObservationApiV1AssetsObservationsPostWithHttpInfo(assetObservationCreate, authorization, xAmeshCSRF, xAmeshTenant)

Record Asset Observation

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        AssetObservationCreate assetObservationCreate = new AssetObservationCreate(); // AssetObservationCreate |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AssetObservation> response = apiInstance.recordAssetObservationApiV1AssetsObservationsPostWithHttpInfo(assetObservationCreate, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#recordAssetObservationApiV1AssetsObservationsPost");
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
| **assetObservationCreate** | **AssetObservationCreate**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AssetObservation**>


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


## registerAssetApiV1AssetsPost

> PersistedAsset registerAssetApiV1AssetsPost(assetMetadata, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Register Asset

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        AssetMetadata assetMetadata = new AssetMetadata(); // AssetMetadata |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PersistedAsset result = apiInstance.registerAssetApiV1AssetsPost(assetMetadata, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#registerAssetApiV1AssetsPost");
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
| **assetMetadata** | **AssetMetadata**|  | |
| **expectedVersion** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PersistedAsset**


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

## registerAssetApiV1AssetsPostWithHttpInfo

> ApiResponse<PersistedAsset> registerAssetApiV1AssetsPostWithHttpInfo(assetMetadata, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Register Asset

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AssetsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AssetsApi apiInstance = new AssetsApi(defaultClient);
        AssetMetadata assetMetadata = new AssetMetadata(); // AssetMetadata |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PersistedAsset> response = apiInstance.registerAssetApiV1AssetsPostWithHttpInfo(assetMetadata, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AssetsApi#registerAssetApiV1AssetsPost");
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
| **assetMetadata** | **AssetMetadata**|  | |
| **expectedVersion** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PersistedAsset**>


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
