# PluginsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet**](PluginsApi.md#downloadpluginregistrybundleapiv1pluginregistryblobsdigestget) | **GET** /api/v1/plugin-registry/blobs/{digest} | Download Plugin Registry Bundle |
| [**exportPluginRegistryApiV1PluginRegistryOfflineExportGet**](PluginsApi.md#exportpluginregistryapiv1pluginregistryofflineexportget) | **GET** /api/v1/plugin-registry/offline-export | Export Plugin Registry |
| [**getPluginRegistryIndexApiV1PluginRegistryIndexGet**](PluginsApi.md#getpluginregistryindexapiv1pluginregistryindexget) | **GET** /api/v1/plugin-registry/index | Get Plugin Registry Index |
| [**getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet**](PluginsApi.md#getpluginregistrypackageapiv1pluginregistrypackagesnameversionget) | **GET** /api/v1/plugin-registry/packages/{name}/{version} | Get Plugin Registry Package |
| [**importPluginRegistryApiV1PluginRegistryOfflineImportPost**](PluginsApi.md#importpluginregistryapiv1pluginregistryofflineimportpost) | **POST** /api/v1/plugin-registry/offline-import | Import Plugin Registry |
| [**installPluginBundleApiV1PluginsInstallPost**](PluginsApi.md#installpluginbundleapiv1pluginsinstallpost) | **POST** /api/v1/plugins/install | Install Plugin Bundle |
| [**isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet**](PluginsApi.md#isolatedpluginruntimestatusapiv1pluginsisolatedruntimeget) | **GET** /api/v1/plugins/isolated-runtime | Isolated Plugin Runtime Status |
| [**listPluginsApiV1PluginsGet**](PluginsApi.md#listpluginsapiv1pluginsget) | **GET** /api/v1/plugins | List Plugins |
| [**publishPluginRegistryPackageApiV1PluginRegistryPackagesPost**](PluginsApi.md#publishpluginregistrypackageapiv1pluginregistrypackagespost) | **POST** /api/v1/plugin-registry/packages | Publish Plugin Registry Package |
| [**refreshPluginsApiV1PluginsRefreshPost**](PluginsApi.md#refreshpluginsapiv1pluginsrefreshpost) | **POST** /api/v1/plugins/refresh | Refresh Plugins |
| [**trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet**](PluginsApi.md#trustedpluginruntimestatusapiv1pluginstrustedruntimeget) | **GET** /api/v1/plugins/trusted-runtime | Trusted Plugin Runtime Status |
| [**yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost**](PluginsApi.md#yankpluginregistrypackageapiv1pluginregistrypackagesnameversionyankpost) | **POST** /api/v1/plugin-registry/packages/{name}/{version}/yank | Yank Plugin Registry Package |



## downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet

> downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet(digest, authorization, xAmeshCSRF, xAmeshTenant)

Download Plugin Registry Bundle

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { DownloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string
    digest: digest_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DownloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGetRequest;

  try {
    const data = await api.downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet(body);
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
| **digest** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

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


## exportPluginRegistryApiV1PluginRegistryOfflineExportGet

> exportPluginRegistryApiV1PluginRegistryOfflineExportGet(authorization, xAmeshCSRF, xAmeshTenant)

Export Plugin Registry

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { ExportPluginRegistryApiV1PluginRegistryOfflineExportGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExportPluginRegistryApiV1PluginRegistryOfflineExportGetRequest;

  try {
    const data = await api.exportPluginRegistryApiV1PluginRegistryOfflineExportGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

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


## getPluginRegistryIndexApiV1PluginRegistryIndexGet

> PluginRegistryIndex getPluginRegistryIndexApiV1PluginRegistryIndexGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Plugin Registry Index

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { GetPluginRegistryIndexApiV1PluginRegistryIndexGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetPluginRegistryIndexApiV1PluginRegistryIndexGetRequest;

  try {
    const data = await api.getPluginRegistryIndexApiV1PluginRegistryIndexGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginRegistryIndex**](PluginRegistryIndex.md)

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


## getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet

> PluginRegistryPackage getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet(name, version, authorization, xAmeshCSRF, xAmeshTenant)

Get Plugin Registry Package

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string
    name: name_example,
    // string
    version: version_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGetRequest;

  try {
    const data = await api.getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet(body);
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
| **name** | `string` |  | [Defaults to `undefined`] |
| **version** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)

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


## importPluginRegistryApiV1PluginRegistryOfflineImportPost

> PluginRegistryIndex importPluginRegistryApiV1PluginRegistryOfflineImportPost(authorization, xAmeshCSRF, xAmeshTenant)

Import Plugin Registry

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { ImportPluginRegistryApiV1PluginRegistryOfflineImportPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ImportPluginRegistryApiV1PluginRegistryOfflineImportPostRequest;

  try {
    const data = await api.importPluginRegistryApiV1PluginRegistryOfflineImportPost(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginRegistryIndex**](PluginRegistryIndex.md)

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


## installPluginBundleApiV1PluginsInstallPost

> PluginCatalogSnapshot installPluginBundleApiV1PluginsInstallPost(contentDigest, authorization, xAmeshCSRF, xAmeshTenant)

Install Plugin Bundle

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { InstallPluginBundleApiV1PluginsInstallPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string
    contentDigest: contentDigest_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies InstallPluginBundleApiV1PluginsInstallPostRequest;

  try {
    const data = await api.installPluginBundleApiV1PluginsInstallPost(body);
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
| **contentDigest** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)

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


## isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet

> IsolatedPluginRuntimeSnapshot isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet(authorization, xAmeshCSRF, xAmeshTenant)

Isolated Plugin Runtime Status

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies IsolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGetRequest;

  try {
    const data = await api.isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**IsolatedPluginRuntimeSnapshot**](IsolatedPluginRuntimeSnapshot.md)

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


## listPluginsApiV1PluginsGet

> PluginCatalogSnapshot listPluginsApiV1PluginsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Plugins

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { ListPluginsApiV1PluginsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListPluginsApiV1PluginsGetRequest;

  try {
    const data = await api.listPluginsApiV1PluginsGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)

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


## publishPluginRegistryPackageApiV1PluginRegistryPackagesPost

> PluginRegistryPackage publishPluginRegistryPackageApiV1PluginRegistryPackagesPost(pluginRegistryPublishRequest, authorization, xAmeshCSRF, xAmeshTenant)

Publish Plugin Registry Package

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { PublishPluginRegistryPackageApiV1PluginRegistryPackagesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // PluginRegistryPublishRequest
    pluginRegistryPublishRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PublishPluginRegistryPackageApiV1PluginRegistryPackagesPostRequest;

  try {
    const data = await api.publishPluginRegistryPackageApiV1PluginRegistryPackagesPost(body);
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
| **pluginRegistryPublishRequest** | [PluginRegistryPublishRequest](PluginRegistryPublishRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## refreshPluginsApiV1PluginsRefreshPost

> PluginCatalogSnapshot refreshPluginsApiV1PluginsRefreshPost(authorization, xAmeshCSRF, xAmeshTenant)

Refresh Plugins

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { RefreshPluginsApiV1PluginsRefreshPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies RefreshPluginsApiV1PluginsRefreshPostRequest;

  try {
    const data = await api.refreshPluginsApiV1PluginsRefreshPost(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginCatalogSnapshot**](PluginCatalogSnapshot.md)

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


## trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet

> TrustedPluginRuntimeSnapshot trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet(authorization, xAmeshCSRF, xAmeshTenant)

Trusted Plugin Runtime Status

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies TrustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGetRequest;

  try {
    const data = await api.trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TrustedPluginRuntimeSnapshot**](TrustedPluginRuntimeSnapshot.md)

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


## yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost

> PluginRegistryPackage yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost(name, version, pluginRegistryYankRequest, authorization, xAmeshCSRF, xAmeshTenant)

Yank Plugin Registry Package

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string
    name: name_example,
    // string
    version: version_example,
    // PluginRegistryYankRequest
    pluginRegistryYankRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies YankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPostRequest;

  try {
    const data = await api.yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost(body);
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
| **name** | `string` |  | [Defaults to `undefined`] |
| **version** | `string` |  | [Defaults to `undefined`] |
| **pluginRegistryYankRequest** | [PluginRegistryYankRequest](PluginRegistryYankRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginRegistryPackage**](PluginRegistryPackage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
