# AssetsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**declareAssetLineageApiV1AssetsLineagePost**](AssetsApi.md#declareassetlineageapiv1assetslineagepost) | **POST** /api/v1/assets/lineage | Declare Asset Lineage |
| [**exportAssetCatalogApiV1AssetsExportOpenlineageGet**](AssetsApi.md#exportassetcatalogapiv1assetsexportopenlineageget) | **GET** /api/v1/assets/export/openlineage | Export Asset Catalog |
| [**getAssetCatalogEntryApiV1AssetsAssetIdGet**](AssetsApi.md#getassetcatalogentryapiv1assetsassetidget) | **GET** /api/v1/assets/{asset_id} | Get Asset Catalog Entry |
| [**listAssetsApiV1AssetsGet**](AssetsApi.md#listassetsapiv1assetsget) | **GET** /api/v1/assets | List Assets |
| [**recordAssetObservationApiV1AssetsObservationsPost**](AssetsApi.md#recordassetobservationapiv1assetsobservationspost) | **POST** /api/v1/assets/observations | Record Asset Observation |
| [**registerAssetApiV1AssetsPost**](AssetsApi.md#registerassetapiv1assetspost) | **POST** /api/v1/assets | Register Asset |



## declareAssetLineageApiV1AssetsLineagePost

> AssetLineageEdge declareAssetLineageApiV1AssetsLineagePost(assetLineageDeclaration, authorization, xAmeshCSRF, xAmeshTenant)

Declare Asset Lineage

### Example

```ts
import {
  Configuration,
  AssetsApi,
} from '@amesh/client';
import type { DeclareAssetLineageApiV1AssetsLineagePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AssetsApi();

  const body = {
    // AssetLineageDeclaration
    assetLineageDeclaration: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeclareAssetLineageApiV1AssetsLineagePostRequest;

  try {
    const data = await api.declareAssetLineageApiV1AssetsLineagePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **assetLineageDeclaration** | AssetLineageDeclaration |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AssetLineageEdge**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## exportAssetCatalogApiV1AssetsExportOpenlineageGet

> AssetCatalogExport exportAssetCatalogApiV1AssetsExportOpenlineageGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Export Asset Catalog

### Example

```ts
import {
  Configuration,
  AssetsApi,
} from '@amesh/client';
import type { ExportAssetCatalogApiV1AssetsExportOpenlineageGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AssetsApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExportAssetCatalogApiV1AssetsExportOpenlineageGetRequest;

  try {
    const data = await api.exportAssetCatalogApiV1AssetsExportOpenlineageGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AssetCatalogExport**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getAssetCatalogEntryApiV1AssetsAssetIdGet

> AssetCatalogEntry getAssetCatalogEntryApiV1AssetsAssetIdGet(assetId, authorization, xAmeshCSRF, xAmeshTenant)

Get Asset Catalog Entry

### Example

```ts
import {
  Configuration,
  AssetsApi,
} from '@amesh/client';
import type { GetAssetCatalogEntryApiV1AssetsAssetIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AssetsApi();

  const body = {
    // string
    assetId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAssetCatalogEntryApiV1AssetsAssetIdGetRequest;

  try {
    const data = await api.getAssetCatalogEntryApiV1AssetsAssetIdGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **assetId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AssetCatalogEntry**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listAssetsApiV1AssetsGet

> Array&lt;PersistedAsset&gt; listAssetsApiV1AssetsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Assets

### Example

```ts
import {
  Configuration,
  AssetsApi,
} from '@amesh/client';
import type { ListAssetsApiV1AssetsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AssetsApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAssetsApiV1AssetsGetRequest;

  try {
    const data = await api.listAssetsApiV1AssetsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;PersistedAsset&gt;**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## recordAssetObservationApiV1AssetsObservationsPost

> AssetObservation recordAssetObservationApiV1AssetsObservationsPost(assetObservationCreate, authorization, xAmeshCSRF, xAmeshTenant)

Record Asset Observation

### Example

```ts
import {
  Configuration,
  AssetsApi,
} from '@amesh/client';
import type { RecordAssetObservationApiV1AssetsObservationsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AssetsApi();

  const body = {
    // AssetObservationCreate
    assetObservationCreate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies RecordAssetObservationApiV1AssetsObservationsPostRequest;

  try {
    const data = await api.recordAssetObservationApiV1AssetsObservationsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **assetObservationCreate** | AssetObservationCreate |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AssetObservation**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## registerAssetApiV1AssetsPost

> PersistedAsset registerAssetApiV1AssetsPost(assetMetadata, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Register Asset

### Example

```ts
import {
  Configuration,
  AssetsApi,
} from '@amesh/client';
import type { RegisterAssetApiV1AssetsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AssetsApi();

  const body = {
    // AssetMetadata
    assetMetadata: ...,
    // number (optional)
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies RegisterAssetApiV1AssetsPostRequest;

  try {
    const data = await api.registerAssetApiV1AssetsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **assetMetadata** | AssetMetadata |  | |
| **expectedVersion** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**PersistedAsset**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
