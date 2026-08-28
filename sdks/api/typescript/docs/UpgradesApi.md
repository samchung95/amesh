# UpgradesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getUpgradePolicyApiV1UpgradesPolicyGet**](UpgradesApi.md#getupgradepolicyapiv1upgradespolicyget) | **GET** /api/v1/upgrades/policy | Get Upgrade Policy |
| [**migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost**](UpgradesApi.md#migrateupgradeconfigurationapiv1upgradesconfigurationmigratepost) | **POST** /api/v1/upgrades/configuration/migrate | Migrate Upgrade Configuration |
| [**previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet**](UpgradesApi.md#previewupgradeeventupcastapiv1upgradeseventsupcastget) | **GET** /api/v1/upgrades/events/upcast | Preview Upgrade Event Upcast |
| [**runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost**](UpgradesApi.md#runupgradeeventupcastapiv1upgradeseventsupcastpost) | **POST** /api/v1/upgrades/events/upcast | Run Upgrade Event Upcast |
| [**runUpgradePostflightApiV1UpgradesPostflightPost**](UpgradesApi.md#runupgradepostflightapiv1upgradespostflightpost) | **POST** /api/v1/upgrades/postflight | Run Upgrade Postflight |
| [**runUpgradePreflightApiV1UpgradesPreflightPost**](UpgradesApi.md#runupgradepreflightapiv1upgradespreflightpost) | **POST** /api/v1/upgrades/preflight | Run Upgrade Preflight |



## getUpgradePolicyApiV1UpgradesPolicyGet

> UpgradePolicy getUpgradePolicyApiV1UpgradesPolicyGet(authorization, xAmeshCSRF)

Get Upgrade Policy

### Example

```ts
import {
  Configuration,
  UpgradesApi,
} from '@amesh/client';
import type { GetUpgradePolicyApiV1UpgradesPolicyGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new UpgradesApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies GetUpgradePolicyApiV1UpgradesPolicyGetRequest;

  try {
    const data = await api.getUpgradePolicyApiV1UpgradesPolicyGet(body);
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

### Return type

**UpgradePolicy**

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


## migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost

> ConfigurationMigration migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost(configurationMigrationRequest, authorization, xAmeshCSRF)

Migrate Upgrade Configuration

### Example

```ts
import {
  Configuration,
  UpgradesApi,
} from '@amesh/client';
import type { MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new UpgradesApi();

  const body = {
    // ConfigurationMigrationRequest
    configurationMigrationRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies MigrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePostRequest;

  try {
    const data = await api.migrateUpgradeConfigurationApiV1UpgradesConfigurationMigratePost(body);
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
| **configurationMigrationRequest** | ConfigurationMigrationRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ConfigurationMigration**

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


## previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet

> PersistedEventMigration previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet(authorization, xAmeshCSRF)

Preview Upgrade Event Upcast

### Example

```ts
import {
  Configuration,
  UpgradesApi,
} from '@amesh/client';
import type { PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new UpgradesApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies PreviewUpgradeEventUpcastApiV1UpgradesEventsUpcastGetRequest;

  try {
    const data = await api.previewUpgradeEventUpcastApiV1UpgradesEventsUpcastGet(body);
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

### Return type

**PersistedEventMigration**

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


## runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost

> PersistedEventMigration runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost(persistedEventMigrationRequest, authorization, xAmeshCSRF)

Run Upgrade Event Upcast

### Example

```ts
import {
  Configuration,
  UpgradesApi,
} from '@amesh/client';
import type { RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new UpgradesApi();

  const body = {
    // PersistedEventMigrationRequest
    persistedEventMigrationRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RunUpgradeEventUpcastApiV1UpgradesEventsUpcastPostRequest;

  try {
    const data = await api.runUpgradeEventUpcastApiV1UpgradesEventsUpcastPost(body);
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
| **persistedEventMigrationRequest** | PersistedEventMigrationRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**PersistedEventMigration**

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


## runUpgradePostflightApiV1UpgradesPostflightPost

> UpgradeReport runUpgradePostflightApiV1UpgradesPostflightPost(upgradeReportRequest, authorization, xAmeshCSRF)

Run Upgrade Postflight

### Example

```ts
import {
  Configuration,
  UpgradesApi,
} from '@amesh/client';
import type { RunUpgradePostflightApiV1UpgradesPostflightPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new UpgradesApi();

  const body = {
    // UpgradeReportRequest
    upgradeReportRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RunUpgradePostflightApiV1UpgradesPostflightPostRequest;

  try {
    const data = await api.runUpgradePostflightApiV1UpgradesPostflightPost(body);
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
| **upgradeReportRequest** | UpgradeReportRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**UpgradeReport**

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


## runUpgradePreflightApiV1UpgradesPreflightPost

> UpgradeReport runUpgradePreflightApiV1UpgradesPreflightPost(upgradeReportRequest, authorization, xAmeshCSRF)

Run Upgrade Preflight

### Example

```ts
import {
  Configuration,
  UpgradesApi,
} from '@amesh/client';
import type { RunUpgradePreflightApiV1UpgradesPreflightPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new UpgradesApi();

  const body = {
    // UpgradeReportRequest
    upgradeReportRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RunUpgradePreflightApiV1UpgradesPreflightPostRequest;

  try {
    const data = await api.runUpgradePreflightApiV1UpgradesPreflightPost(body);
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
| **upgradeReportRequest** | UpgradeReportRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**UpgradeReport**

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
