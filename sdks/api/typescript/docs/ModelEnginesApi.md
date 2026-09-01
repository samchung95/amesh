# ModelEnginesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost**](ModelEnginesApi.md#accountloginstartapiv1namespacesnamespacemodelenginesadapterenginerefloginpost) | **POST** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/login | Account Login Start |
| [**accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost**](ModelEnginesApi.md#accountlogoutapiv1namespacesnamespacemodelenginesadapterenginereflogoutpost) | **POST** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/logout | Account Logout |
| [**accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet**](ModelEnginesApi.md#accountstatusapiv1namespacesnamespacemodelenginesadapterenginerefstatusget) | **GET** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/status | Account Status |
| [**catalogApiV1NamespacesNamespaceModelEnginesCatalogGet**](ModelEnginesApi.md#catalogapiv1namespacesnamespacemodelenginescatalogget) | **GET** /api/v1/namespaces/{namespace}/model-engines/catalog | Catalog |



## accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost

> ModelEngineLoginStartResponse accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost(namespace, adapter, engineRef, modelEngineLoginRequest, xAmeshTenant, authorization, xAmeshCSRF)

Account Login Start

### Example

```ts
import {
  Configuration,
  ModelEnginesApi,
} from '@amesh/client';
import type { AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ModelEnginesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    adapter: adapter_example,
    // string
    engineRef: engineRef_example,
    // ModelEngineLoginRequest
    modelEngineLoginRequest: ...,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPostRequest;

  try {
    const data = await api.accountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost(body);
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
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **adapter** | `string` |  | [Defaults to `undefined`] |
| **engineRef** | `string` |  | [Defaults to `undefined`] |
| **modelEngineLoginRequest** | ModelEngineLoginRequest |  | |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ModelEngineLoginStartResponse**

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


## accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost

> ModelEngineLogoutResponse accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF)

Account Logout

### Example

```ts
import {
  Configuration,
  ModelEnginesApi,
} from '@amesh/client';
import type { AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ModelEnginesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    adapter: adapter_example,
    // string
    engineRef: engineRef_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPostRequest;

  try {
    const data = await api.accountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost(body);
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
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **adapter** | `string` |  | [Defaults to `undefined`] |
| **engineRef** | `string` |  | [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ModelEngineLogoutResponse**

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


## accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet

> ModelEngineAccountStatusResponse accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet(namespace, adapter, engineRef, xAmeshTenant, authorization, xAmeshCSRF)

Account Status

### Example

```ts
import {
  Configuration,
  ModelEnginesApi,
} from '@amesh/client';
import type { AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ModelEnginesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    adapter: adapter_example,
    // string
    engineRef: engineRef_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGetRequest;

  try {
    const data = await api.accountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet(body);
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
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **adapter** | `string` |  | [Defaults to `undefined`] |
| **engineRef** | `string` |  | [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ModelEngineAccountStatusResponse**

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


## catalogApiV1NamespacesNamespaceModelEnginesCatalogGet

> ModelEngineCatalog catalogApiV1NamespacesNamespaceModelEnginesCatalogGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Catalog

### Example

```ts
import {
  Configuration,
  ModelEnginesApi,
} from '@amesh/client';
import type { CatalogApiV1NamespacesNamespaceModelEnginesCatalogGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ModelEnginesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies CatalogApiV1NamespacesNamespaceModelEnginesCatalogGetRequest;

  try {
    const data = await api.catalogApiV1NamespacesNamespaceModelEnginesCatalogGet(body);
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
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**ModelEngineCatalog**

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
