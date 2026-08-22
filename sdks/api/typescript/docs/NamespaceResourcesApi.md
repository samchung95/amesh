# NamespaceResourcesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**deleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete**](NamespaceResourcesApi.md#deletenamespacefileapiv1namespacesnamespacefilespathdelete) | **DELETE** /api/v1/namespaces/{namespace}/files/{path} | Delete Namespace File |
| [**deleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete**](NamespaceResourcesApi.md#deletenamespacekeyvalueapiv1namespacesnamespacekeyvalueskeydelete) | **DELETE** /api/v1/namespaces/{namespace}/key-values/{key} | Delete Namespace Key Value |
| [**deleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete**](NamespaceResourcesApi.md#deletenamespacesecretbindingapiv1namespacesnamespacesecretbindingskeydelete) | **DELETE** /api/v1/namespaces/{namespace}/secret-bindings/{key} | Delete Namespace Secret Binding |
| [**downloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet**](NamespaceResourcesApi.md#downloadnamespacefileapiv1namespacesnamespacefilespathget) | **GET** /api/v1/namespaces/{namespace}/files/{path} | Download Namespace File |
| [**exportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet**](NamespaceResourcesApi.md#exportnamespaceresourcebundleapiv1namespacesnamespaceresourcebundleget) | **GET** /api/v1/namespaces/{namespace}/resource-bundle | Export Namespace Resource Bundle |
| [**getNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet**](NamespaceResourcesApi.md#getnamespacekeyvalueapiv1namespacesnamespacekeyvalueskeyget) | **GET** /api/v1/namespaces/{namespace}/key-values/{key} | Get Namespace Key Value |
| [**importNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost**](NamespaceResourcesApi.md#importnamespaceresourcebundleapiv1namespacesnamespaceresourcebundlepost) | **POST** /api/v1/namespaces/{namespace}/resource-bundle | Import Namespace Resource Bundle |
| [**listNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet**](NamespaceResourcesApi.md#listnamespacefileversionsapiv1namespacesnamespacefilespathversionsget) | **GET** /api/v1/namespaces/{namespace}/files/{path}/versions | List Namespace File Versions |
| [**listNamespaceFilesApiV1NamespacesNamespaceFilesGet**](NamespaceResourcesApi.md#listnamespacefilesapiv1namespacesnamespacefilesget) | **GET** /api/v1/namespaces/{namespace}/files | List Namespace Files |
| [**listNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet**](NamespaceResourcesApi.md#listnamespacekeyvaluechangesapiv1namespacesnamespacekeyvalueschangesget) | **GET** /api/v1/namespaces/{namespace}/key-values/changes | List Namespace Key Value Changes |
| [**listNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet**](NamespaceResourcesApi.md#listnamespacekeyvaluesapiv1namespacesnamespacekeyvaluesget) | **GET** /api/v1/namespaces/{namespace}/key-values | List Namespace Key Values |
| [**listNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet**](NamespaceResourcesApi.md#listnamespacesecretbindingsapiv1namespacesnamespacesecretbindingsget) | **GET** /api/v1/namespaces/{namespace}/secret-bindings | List Namespace Secret Bindings |
| [**moveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost**](NamespaceResourcesApi.md#movenamespacefileapiv1namespacesnamespacefilespathmovepost) | **POST** /api/v1/namespaces/{namespace}/files/{path}/move | Move Namespace File |
| [**putNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut**](NamespaceResourcesApi.md#putnamespacekeyvalueapiv1namespacesnamespacekeyvalueskeyput) | **PUT** /api/v1/namespaces/{namespace}/key-values/{key} | Put Namespace Key Value |
| [**putNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut**](NamespaceResourcesApi.md#putnamespacesecretbindingapiv1namespacesnamespacesecretbindingskeyput) | **PUT** /api/v1/namespaces/{namespace}/secret-bindings/{key} | Put Namespace Secret Binding |
| [**uploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut**](NamespaceResourcesApi.md#uploadnamespacefileapiv1namespacesnamespacefilespathput) | **PUT** /api/v1/namespaces/{namespace}/files/{path} | Upload Namespace File |



## deleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete

> { [key: string]: number; } deleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete(namespace, path, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Delete Namespace File

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    path: path_example,
    // number (optional)
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDeleteRequest;

  try {
    const data = await api.deleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete(body);
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
| **path** | `string` |  | [Defaults to `undefined`] |
| **expectedVersion** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**{ [key: string]: number; }**

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


## deleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete

> { [key: string]: boolean | null; } deleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete(namespace, key, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Delete Namespace Key Value

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // number (optional)
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDeleteRequest;

  try {
    const data = await api.deleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete(body);
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
| **key** | `string` |  | [Defaults to `undefined`] |
| **expectedVersion** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**{ [key: string]: boolean | null; }**

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


## deleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete

> { [key: string]: boolean | null; } deleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete(namespace, key, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Delete Namespace Secret Binding

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // number (optional)
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDeleteRequest;

  try {
    const data = await api.deleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete(body);
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
| **key** | `string` |  | [Defaults to `undefined`] |
| **expectedVersion** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**{ [key: string]: boolean | null; }**

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


## downloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet

> downloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet(namespace, path, version, authorization, xAmeshCSRF, xAmeshTenant)

Download Namespace File

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { DownloadNamespaceFileApiV1NamespacesNamespaceFilesPathGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    path: path_example,
    // number (optional)
    version: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies DownloadNamespaceFileApiV1NamespacesNamespaceFilesPathGetRequest;

  try {
    const data = await api.downloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet(body);
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
| **path** | `string` |  | [Defaults to `undefined`] |
| **version** | `number` |  | [Optional] [Defaults to `undefined`] |
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


## exportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet

> NamespaceResourceBundle exportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Export Namespace Resource Bundle

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGetRequest;

  try {
    const data = await api.exportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet(body);
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

[**NamespaceResourceBundle**](NamespaceResourceBundle.md)

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


## getNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet

> KeyValueEntry getNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet(namespace, key, authorization, xAmeshCSRF, xAmeshTenant)

Get Namespace Key Value

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGetRequest;

  try {
    const data = await api.getNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet(body);
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
| **key** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**KeyValueEntry**](KeyValueEntry.md)

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


## importNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost

> NamespaceResourceImportResult importNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost(namespace, namespaceResourceBundle, authorization, xAmeshCSRF, xAmeshTenant)

Import Namespace Resource Bundle

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // NamespaceResourceBundle
    namespaceResourceBundle: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePostRequest;

  try {
    const data = await api.importNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost(body);
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
| **namespaceResourceBundle** | [NamespaceResourceBundle](NamespaceResourceBundle.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**NamespaceResourceImportResult**](NamespaceResourceImportResult.md)

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


## listNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet

> Array&lt;NamespaceFileVersion&gt; listNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet(namespace, path, authorization, xAmeshCSRF, xAmeshTenant)

List Namespace File Versions

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    path: path_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGetRequest;

  try {
    const data = await api.listNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet(body);
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
| **path** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;NamespaceFileVersion&gt;**](NamespaceFileVersion.md)

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


## listNamespaceFilesApiV1NamespacesNamespaceFilesGet

> Array&lt;NamespaceFile&gt; listNamespaceFilesApiV1NamespacesNamespaceFilesGet(namespace, inherited, authorization, xAmeshCSRF, xAmeshTenant)

List Namespace Files

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { ListNamespaceFilesApiV1NamespacesNamespaceFilesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // boolean (optional)
    inherited: true,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListNamespaceFilesApiV1NamespacesNamespaceFilesGetRequest;

  try {
    const data = await api.listNamespaceFilesApiV1NamespacesNamespaceFilesGet(body);
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
| **inherited** | `boolean` |  | [Optional] [Defaults to `true`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;NamespaceFile&gt;**](NamespaceFile.md)

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


## listNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet

> Array&lt;KeyValueChange&gt; listNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet(namespace, after, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Namespace Key Value Changes

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // number (optional)
    after: 56,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGetRequest;

  try {
    const data = await api.listNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet(body);
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
| **after** | `number` |  | [Optional] [Defaults to `0`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;KeyValueChange&gt;**](KeyValueChange.md)

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


## listNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet

> Array&lt;KeyValueEntry&gt; listNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

List Namespace Key Values

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGetRequest;

  try {
    const data = await api.listNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet(body);
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

[**Array&lt;KeyValueEntry&gt;**](KeyValueEntry.md)

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


## listNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet

> Array&lt;SecretBinding&gt; listNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet(namespace, inherited, authorization, xAmeshCSRF, xAmeshTenant)

List Namespace Secret Bindings

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // boolean (optional)
    inherited: true,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGetRequest;

  try {
    const data = await api.listNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet(body);
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
| **inherited** | `boolean` |  | [Optional] [Defaults to `true`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;SecretBinding&gt;**](SecretBinding.md)

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


## moveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost

> NamespaceFile moveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost(namespace, path, namespaceFileMoveRequest, authorization, xAmeshCSRF, xAmeshTenant)

Move Namespace File

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    path: path_example,
    // NamespaceFileMoveRequest
    namespaceFileMoveRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePostRequest;

  try {
    const data = await api.moveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost(body);
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
| **path** | `string` |  | [Defaults to `undefined`] |
| **namespaceFileMoveRequest** | [NamespaceFileMoveRequest](NamespaceFileMoveRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**NamespaceFile**](NamespaceFile.md)

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


## putNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut

> KeyValueEntry putNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut(namespace, key, keyValueWrite, authorization, xAmeshCSRF, xAmeshTenant)

Put Namespace Key Value

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // KeyValueWrite
    keyValueWrite: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPutRequest;

  try {
    const data = await api.putNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut(body);
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
| **key** | `string` |  | [Defaults to `undefined`] |
| **keyValueWrite** | [KeyValueWrite](KeyValueWrite.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**KeyValueEntry**](KeyValueEntry.md)

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


## putNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut

> SecretBinding putNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut(namespace, key, secretBindingWrite, authorization, xAmeshCSRF, xAmeshTenant)

Put Namespace Secret Binding

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    key: key_example,
    // SecretBindingWrite
    secretBindingWrite: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPutRequest;

  try {
    const data = await api.putNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut(body);
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
| **key** | `string` |  | [Defaults to `undefined`] |
| **secretBindingWrite** | [SecretBindingWrite](SecretBindingWrite.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**SecretBinding**](SecretBinding.md)

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


## uploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut

> NamespaceFile uploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut(namespace, path, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Upload Namespace File

### Example

```ts
import {
  Configuration,
  NamespaceResourcesApi,
} from '@amesh/client';
import type { UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespaceResourcesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string
    path: path_example,
    // number (optional)
    expectedVersion: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPutRequest;

  try {
    const data = await api.uploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut(body);
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
| **path** | `string` |  | [Defaults to `undefined`] |
| **expectedVersion** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**NamespaceFile**](NamespaceFile.md)

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
