# PluginsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createPluginPolicyRuleApiV1PluginPolicyRulesPost**](PluginsApi.md#createpluginpolicyruleapiv1pluginpolicyrulespost) | **POST** /api/v1/plugin-policy/rules | Create Plugin Policy Rule |
| [**deletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete**](PluginsApi.md#deletepluginpolicyruleapiv1pluginpolicyrulesruleiddelete) | **DELETE** /api/v1/plugin-policy/rules/{rule_id} | Delete Plugin Policy Rule |
| [**downloadPluginRegistryBundleApiV1PluginRegistryBlobsDigestGet**](PluginsApi.md#downloadpluginregistrybundleapiv1pluginregistryblobsdigestget) | **GET** /api/v1/plugin-registry/blobs/{digest} | Download Plugin Registry Bundle |
| [**evaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost**](PluginsApi.md#evaluateflowpluginpolicyapiv1pluginpolicyevaluatepost) | **POST** /api/v1/plugin-policy/evaluate | Evaluate Flow Plugin Policy |
| [**exportPluginRegistryApiV1PluginRegistryOfflineExportGet**](PluginsApi.md#exportpluginregistryapiv1pluginregistryofflineexportget) | **GET** /api/v1/plugin-registry/offline-export | Export Plugin Registry |
| [**getEffectivePluginPolicyApiV1PluginPolicyEffectiveGet**](PluginsApi.md#geteffectivepluginpolicyapiv1pluginpolicyeffectiveget) | **GET** /api/v1/plugin-policy/effective | Get Effective Plugin Policy |
| [**getPluginRegistryIndexApiV1PluginRegistryIndexGet**](PluginsApi.md#getpluginregistryindexapiv1pluginregistryindexget) | **GET** /api/v1/plugin-registry/index | Get Plugin Registry Index |
| [**getPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionGet**](PluginsApi.md#getpluginregistrypackageapiv1pluginregistrypackagesnameversionget) | **GET** /api/v1/plugin-registry/packages/{name}/{version} | Get Plugin Registry Package |
| [**importPluginRegistryApiV1PluginRegistryOfflineImportPost**](PluginsApi.md#importpluginregistryapiv1pluginregistryofflineimportpost) | **POST** /api/v1/plugin-registry/offline-import | Import Plugin Registry |
| [**installPluginBundleApiV1PluginsInstallPost**](PluginsApi.md#installpluginbundleapiv1pluginsinstallpost) | **POST** /api/v1/plugins/install | Install Plugin Bundle |
| [**isolatedPluginRuntimeStatusApiV1PluginsIsolatedRuntimeGet**](PluginsApi.md#isolatedpluginruntimestatusapiv1pluginsisolatedruntimeget) | **GET** /api/v1/plugins/isolated-runtime | Isolated Plugin Runtime Status |
| [**listPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet**](PluginsApi.md#listpluginpolicydecisionsapiv1pluginpolicydecisionsget) | **GET** /api/v1/plugin-policy/decisions | List Plugin Policy Decisions |
| [**listPluginsApiV1PluginsGet**](PluginsApi.md#listpluginsapiv1pluginsget) | **GET** /api/v1/plugins | List Plugins |
| [**previewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost**](PluginsApi.md#previewpluginquarantineapiv1pluginpolicyquarantinespreviewpost) | **POST** /api/v1/plugin-policy/quarantines/preview | Preview Plugin Quarantine |
| [**publishPluginRegistryPackageApiV1PluginRegistryPackagesPost**](PluginsApi.md#publishpluginregistrypackageapiv1pluginregistrypackagespost) | **POST** /api/v1/plugin-registry/packages | Publish Plugin Registry Package |
| [**quarantinePluginVersionApiV1PluginPolicyQuarantinesPost**](PluginsApi.md#quarantinepluginversionapiv1pluginpolicyquarantinespost) | **POST** /api/v1/plugin-policy/quarantines | Quarantine Plugin Version |
| [**refreshPluginsApiV1PluginsRefreshPost**](PluginsApi.md#refreshpluginsapiv1pluginsrefreshpost) | **POST** /api/v1/plugins/refresh | Refresh Plugins |
| [**releasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost**](PluginsApi.md#releasepluginquarantineapiv1pluginpolicyquarantinesquarantineidreleasepost) | **POST** /api/v1/plugin-policy/quarantines/{quarantine_id}/release | Release Plugin Quarantine |
| [**trustedPluginRuntimeStatusApiV1PluginsTrustedRuntimeGet**](PluginsApi.md#trustedpluginruntimestatusapiv1pluginstrustedruntimeget) | **GET** /api/v1/plugins/trusted-runtime | Trusted Plugin Runtime Status |
| [**updatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut**](PluginsApi.md#updatepluginpolicyruleapiv1pluginpolicyrulesruleidput) | **PUT** /api/v1/plugin-policy/rules/{rule_id} | Update Plugin Policy Rule |
| [**yankPluginRegistryPackageApiV1PluginRegistryPackagesNameVersionYankPost**](PluginsApi.md#yankpluginregistrypackageapiv1pluginregistrypackagesnameversionyankpost) | **POST** /api/v1/plugin-registry/packages/{name}/{version}/yank | Yank Plugin Registry Package |



## createPluginPolicyRuleApiV1PluginPolicyRulesPost

> PluginPolicyRule createPluginPolicyRuleApiV1PluginPolicyRulesPost(pluginPolicyRuleCreate, authorization, xAmeshCSRF, xAmeshTenant)

Create Plugin Policy Rule

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { CreatePluginPolicyRuleApiV1PluginPolicyRulesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // PluginPolicyRuleCreate
    pluginPolicyRuleCreate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CreatePluginPolicyRuleApiV1PluginPolicyRulesPostRequest;

  try {
    const data = await api.createPluginPolicyRuleApiV1PluginPolicyRulesPost(body);
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
| **pluginPolicyRuleCreate** | [PluginPolicyRuleCreate](PluginPolicyRuleCreate.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginPolicyRule**](PluginPolicyRule.md)

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


## deletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete

> deletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete(ruleId, authorization, xAmeshCSRF, xAmeshTenant)

Delete Plugin Policy Rule

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { DeletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string
    ruleId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDeleteRequest;

  try {
    const data = await api.deletePluginPolicyRuleApiV1PluginPolicyRulesRuleIdDelete(body);
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
| **ruleId** | `string` |  | [Defaults to `undefined`] |
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
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


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


## evaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost

> PluginPolicyDecision evaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost(stage, authorization, xAmeshCSRF, xAmeshTenant)

Evaluate Flow Plugin Policy

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // PluginPolicyStage (optional)
    stage: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies EvaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePostRequest;

  try {
    const data = await api.evaluateFlowPluginPolicyApiV1PluginPolicyEvaluatePost(body);
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
| **stage** | `PluginPolicyStage` |  | [Optional] [Defaults to `undefined`] [Enum: AUTHORING, VALIDATION, EXECUTION, ADMINISTRATION] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginPolicyDecision**](PluginPolicyDecision.md)

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


## getEffectivePluginPolicyApiV1PluginPolicyEffectiveGet

> EffectivePluginPolicy getEffectivePluginPolicyApiV1PluginPolicyEffectiveGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Effective Plugin Policy

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetEffectivePluginPolicyApiV1PluginPolicyEffectiveGetRequest;

  try {
    const data = await api.getEffectivePluginPolicyApiV1PluginPolicyEffectiveGet(body);
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

[**EffectivePluginPolicy**](EffectivePluginPolicy.md)

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


## listPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet

> Array&lt;PluginPolicyDecision&gt; listPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Plugin Policy Decisions

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListPluginPolicyDecisionsApiV1PluginPolicyDecisionsGetRequest;

  try {
    const data = await api.listPluginPolicyDecisionsApiV1PluginPolicyDecisionsGet(body);
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
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;PluginPolicyDecision&gt;**](PluginPolicyDecision.md)

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


## previewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost

> PluginPolicyImpactPreview previewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost(pluginQuarantineCreate, authorization, xAmeshCSRF, xAmeshTenant)

Preview Plugin Quarantine

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // PluginQuarantineCreate
    pluginQuarantineCreate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PreviewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPostRequest;

  try {
    const data = await api.previewPluginQuarantineApiV1PluginPolicyQuarantinesPreviewPost(body);
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
| **pluginQuarantineCreate** | [PluginQuarantineCreate](PluginQuarantineCreate.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginPolicyImpactPreview**](PluginPolicyImpactPreview.md)

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


## quarantinePluginVersionApiV1PluginPolicyQuarantinesPost

> PluginQuarantine quarantinePluginVersionApiV1PluginPolicyQuarantinesPost(pluginQuarantineCreate, authorization, xAmeshCSRF, xAmeshTenant)

Quarantine Plugin Version

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { QuarantinePluginVersionApiV1PluginPolicyQuarantinesPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // PluginQuarantineCreate
    pluginQuarantineCreate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies QuarantinePluginVersionApiV1PluginPolicyQuarantinesPostRequest;

  try {
    const data = await api.quarantinePluginVersionApiV1PluginPolicyQuarantinesPost(body);
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
| **pluginQuarantineCreate** | [PluginQuarantineCreate](PluginQuarantineCreate.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginQuarantine**](PluginQuarantine.md)

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


## releasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost

> PluginQuarantine releasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost(quarantineId, reason, authorization, xAmeshCSRF, xAmeshTenant)

Release Plugin Quarantine

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string
    quarantineId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string
    reason: reason_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ReleasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePostRequest;

  try {
    const data = await api.releasePluginQuarantineApiV1PluginPolicyQuarantinesQuarantineIdReleasePost(body);
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
| **quarantineId** | `string` |  | [Defaults to `undefined`] |
| **reason** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginQuarantine**](PluginQuarantine.md)

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


## updatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut

> PluginPolicyRule updatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut(ruleId, pluginPolicyRuleCreate, authorization, xAmeshCSRF, xAmeshTenant)

Update Plugin Policy Rule

### Example

```ts
import {
  Configuration,
  PluginsApi,
} from '@amesh/client';
import type { UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new PluginsApi();

  const body = {
    // string
    ruleId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // PluginPolicyRuleCreate
    pluginPolicyRuleCreate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies UpdatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPutRequest;

  try {
    const data = await api.updatePluginPolicyRuleApiV1PluginPolicyRulesRuleIdPut(body);
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
| **ruleId** | `string` |  | [Defaults to `undefined`] |
| **pluginPolicyRuleCreate** | [PluginPolicyRuleCreate](PluginPolicyRuleCreate.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PluginPolicyRule**](PluginPolicyRule.md)

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
