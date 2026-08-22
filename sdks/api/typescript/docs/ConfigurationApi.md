# ConfigurationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet**](ConfigurationApi.md#evaluatefeatureflagapiv1featureflagskeyevaluateget) | **GET** /api/v1/feature-flags/{key}/evaluate | Evaluate Feature Flag |
| [**getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet**](ConfigurationApi.md#getconfigurationdiagnosticsapiv1configurationdiagnosticsget) | **GET** /api/v1/configuration/diagnostics | Get Configuration Diagnostics |
| [**getEffectiveConfigurationApiV1ConfigurationGet**](ConfigurationApi.md#geteffectiveconfigurationapiv1configurationget) | **GET** /api/v1/configuration | Get Effective Configuration |
| [**listFeatureFlagsApiV1FeatureFlagsGet**](ConfigurationApi.md#listfeatureflagsapiv1featureflagsget) | **GET** /api/v1/feature-flags | List Feature Flags |
| [**putFeatureFlagApiV1FeatureFlagsKeyPut**](ConfigurationApi.md#putfeatureflagapiv1featureflagskeyput) | **PUT** /api/v1/feature-flags/{key} | Put Feature Flag |
| [**reloadConfigurationApiV1ConfigurationReloadPost**](ConfigurationApi.md#reloadconfigurationapiv1configurationreloadpost) | **POST** /api/v1/configuration/reload | Reload Configuration |



## evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet

> FeatureFlagDecision evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet(key, namespace, _default, authorization, xAmeshCSRF, xAmeshTenant)

Evaluate Feature Flag

### Example

```ts
import {
  Configuration,
  ConfigurationApi,
} from '@amesh/client';
import type { EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ConfigurationApi();

  const body = {
    // string
    key: key_example,
    // string (optional)
    namespace: namespace_example,
    // boolean (optional)
    _default: true,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGetRequest;

  try {
    const data = await api.evaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet(body);
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
| **key** | `string` |  | [Defaults to `undefined`] |
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **_default** | `boolean` |  | [Optional] [Defaults to `false`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**FeatureFlagDecision**](FeatureFlagDecision.md)

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


## getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet

> ConfigurationDiagnosticBundle getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Configuration Diagnostics

### Example

```ts
import {
  Configuration,
  ConfigurationApi,
} from '@amesh/client';
import type { GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ConfigurationApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGetRequest;

  try {
    const data = await api.getConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet(body);
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

[**ConfigurationDiagnosticBundle**](ConfigurationDiagnosticBundle.md)

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


## getEffectiveConfigurationApiV1ConfigurationGet

> ConfigurationSnapshot getEffectiveConfigurationApiV1ConfigurationGet(authorization, xAmeshCSRF)

Get Effective Configuration

### Example

```ts
import {
  Configuration,
  ConfigurationApi,
} from '@amesh/client';
import type { GetEffectiveConfigurationApiV1ConfigurationGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ConfigurationApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies GetEffectiveConfigurationApiV1ConfigurationGetRequest;

  try {
    const data = await api.getEffectiveConfigurationApiV1ConfigurationGet(body);
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

[**ConfigurationSnapshot**](ConfigurationSnapshot.md)

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


## listFeatureFlagsApiV1FeatureFlagsGet

> Array&lt;FeatureFlag&gt; listFeatureFlagsApiV1FeatureFlagsGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Feature Flags

### Example

```ts
import {
  Configuration,
  ConfigurationApi,
} from '@amesh/client';
import type { ListFeatureFlagsApiV1FeatureFlagsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ConfigurationApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListFeatureFlagsApiV1FeatureFlagsGetRequest;

  try {
    const data = await api.listFeatureFlagsApiV1FeatureFlagsGet(body);
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

[**Array&lt;FeatureFlag&gt;**](FeatureFlag.md)

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


## putFeatureFlagApiV1FeatureFlagsKeyPut

> FeatureFlag putFeatureFlagApiV1FeatureFlagsKeyPut(key, featureFlagUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Put Feature Flag

### Example

```ts
import {
  Configuration,
  ConfigurationApi,
} from '@amesh/client';
import type { PutFeatureFlagApiV1FeatureFlagsKeyPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ConfigurationApi();

  const body = {
    // string
    key: key_example,
    // FeatureFlagUpsertRequest
    featureFlagUpsertRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PutFeatureFlagApiV1FeatureFlagsKeyPutRequest;

  try {
    const data = await api.putFeatureFlagApiV1FeatureFlagsKeyPut(body);
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
| **key** | `string` |  | [Defaults to `undefined`] |
| **featureFlagUpsertRequest** | [FeatureFlagUpsertRequest](FeatureFlagUpsertRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**FeatureFlag**](FeatureFlag.md)

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


## reloadConfigurationApiV1ConfigurationReloadPost

> ConfigurationSnapshot reloadConfigurationApiV1ConfigurationReloadPost(authorization, xAmeshCSRF)

Reload Configuration

### Example

```ts
import {
  Configuration,
  ConfigurationApi,
} from '@amesh/client';
import type { ReloadConfigurationApiV1ConfigurationReloadPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ConfigurationApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies ReloadConfigurationApiV1ConfigurationReloadPostRequest;

  try {
    const data = await api.reloadConfigurationApiV1ConfigurationReloadPost(body);
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

[**ConfigurationSnapshot**](ConfigurationSnapshot.md)

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
