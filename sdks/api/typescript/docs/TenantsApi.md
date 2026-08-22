# TenantsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createTenantApiV1AdminTenantsPost**](TenantsApi.md#createtenantapiv1admintenantspost) | **POST** /api/v1/admin/tenants | Create Tenant |
| [**deleteTenantApiV1AdminTenantsTenantSlugDelete**](TenantsApi.md#deletetenantapiv1admintenantstenantslugdelete) | **DELETE** /api/v1/admin/tenants/{tenant_slug} | Delete Tenant |
| [**exportTenantApiV1AdminTenantsTenantSlugExportsPost**](TenantsApi.md#exporttenantapiv1admintenantstenantslugexportspost) | **POST** /api/v1/admin/tenants/{tenant_slug}/exports | Export Tenant |
| [**getTenantApiV1AdminTenantsTenantSlugGet**](TenantsApi.md#gettenantapiv1admintenantstenantslugget) | **GET** /api/v1/admin/tenants/{tenant_slug} | Get Tenant |
| [**listTenantsApiV1AdminTenantsGet**](TenantsApi.md#listtenantsapiv1admintenantsget) | **GET** /api/v1/admin/tenants | List Tenants |
| [**restoreTenantApiV1AdminTenantsTenantSlugRestorePost**](TenantsApi.md#restoretenantapiv1admintenantstenantslugrestorepost) | **POST** /api/v1/admin/tenants/{tenant_slug}/restore | Restore Tenant |
| [**suspendTenantApiV1AdminTenantsTenantSlugSuspendPost**](TenantsApi.md#suspendtenantapiv1admintenantstenantslugsuspendpost) | **POST** /api/v1/admin/tenants/{tenant_slug}/suspend | Suspend Tenant |
| [**updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut**](TenantsApi.md#updatetenantpolicyapiv1admintenantstenantslugpolicyput) | **PUT** /api/v1/admin/tenants/{tenant_slug}/policy | Update Tenant Policy |



## createTenantApiV1AdminTenantsPost

> TenantDefinition createTenantApiV1AdminTenantsPost(createTenantRequest, authorization, xAmeshCSRF)

Create Tenant

### Example

```ts
import {
  Configuration,
  TenantsApi,
} from '@amesh/client';
import type { CreateTenantApiV1AdminTenantsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TenantsApi();

  const body = {
    // CreateTenantRequest
    createTenantRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies CreateTenantApiV1AdminTenantsPostRequest;

  try {
    const data = await api.createTenantApiV1AdminTenantsPost(body);
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
| **createTenantRequest** | [CreateTenantRequest](CreateTenantRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TenantDefinition**](TenantDefinition.md)

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


## deleteTenantApiV1AdminTenantsTenantSlugDelete

> TenantDefinition deleteTenantApiV1AdminTenantsTenantSlugDelete(tenantSlug, authorization, xAmeshCSRF)

Delete Tenant

### Example

```ts
import {
  Configuration,
  TenantsApi,
} from '@amesh/client';
import type { DeleteTenantApiV1AdminTenantsTenantSlugDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TenantsApi();

  const body = {
    // string
    tenantSlug: tenantSlug_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies DeleteTenantApiV1AdminTenantsTenantSlugDeleteRequest;

  try {
    const data = await api.deleteTenantApiV1AdminTenantsTenantSlugDelete(body);
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
| **tenantSlug** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TenantDefinition**](TenantDefinition.md)

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


## exportTenantApiV1AdminTenantsTenantSlugExportsPost

> TenantExport exportTenantApiV1AdminTenantsTenantSlugExportsPost(tenantSlug, authorization, xAmeshCSRF)

Export Tenant

### Example

```ts
import {
  Configuration,
  TenantsApi,
} from '@amesh/client';
import type { ExportTenantApiV1AdminTenantsTenantSlugExportsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TenantsApi();

  const body = {
    // string
    tenantSlug: tenantSlug_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies ExportTenantApiV1AdminTenantsTenantSlugExportsPostRequest;

  try {
    const data = await api.exportTenantApiV1AdminTenantsTenantSlugExportsPost(body);
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
| **tenantSlug** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TenantExport**](TenantExport.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getTenantApiV1AdminTenantsTenantSlugGet

> TenantDefinition getTenantApiV1AdminTenantsTenantSlugGet(tenantSlug, authorization, xAmeshCSRF)

Get Tenant

### Example

```ts
import {
  Configuration,
  TenantsApi,
} from '@amesh/client';
import type { GetTenantApiV1AdminTenantsTenantSlugGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TenantsApi();

  const body = {
    // string
    tenantSlug: tenantSlug_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies GetTenantApiV1AdminTenantsTenantSlugGetRequest;

  try {
    const data = await api.getTenantApiV1AdminTenantsTenantSlugGet(body);
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
| **tenantSlug** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TenantDefinition**](TenantDefinition.md)

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


## listTenantsApiV1AdminTenantsGet

> Array&lt;TenantDefinition&gt; listTenantsApiV1AdminTenantsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Tenants

### Example

```ts
import {
  Configuration,
  TenantsApi,
} from '@amesh/client';
import type { ListTenantsApiV1AdminTenantsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TenantsApi();

  const body = {
    // string | Opaque cursor from the prior page (optional)
    cursor: cursor_example,
    // number (optional)
    limit: 56,
    // Array<string> | Repeatable top-level equality filter in field=value form (optional)
    filter: ...,
    // string | Comma-separated top-level fields; prefix descending fields with - (optional)
    sort: sort_example,
    // string | Comma-separated top-level response fields (optional)
    fields: fields_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies ListTenantsApiV1AdminTenantsGetRequest;

  try {
    const data = await api.listTenantsApiV1AdminTenantsGet(body);
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
| **cursor** | `string` | Opaque cursor from the prior page | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `undefined`] |
| **filter** | `Array<string>` | Repeatable top-level equality filter in field&#x3D;value form | [Optional] |
| **sort** | `string` | Comma-separated top-level fields; prefix descending fields with - | [Optional] [Defaults to `undefined`] |
| **fields** | `string` | Comma-separated top-level response fields | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**Array&lt;TenantDefinition&gt;**](TenantDefinition.md)

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


## restoreTenantApiV1AdminTenantsTenantSlugRestorePost

> TenantDefinition restoreTenantApiV1AdminTenantsTenantSlugRestorePost(tenantSlug, authorization, xAmeshCSRF)

Restore Tenant

### Example

```ts
import {
  Configuration,
  TenantsApi,
} from '@amesh/client';
import type { RestoreTenantApiV1AdminTenantsTenantSlugRestorePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TenantsApi();

  const body = {
    // string
    tenantSlug: tenantSlug_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RestoreTenantApiV1AdminTenantsTenantSlugRestorePostRequest;

  try {
    const data = await api.restoreTenantApiV1AdminTenantsTenantSlugRestorePost(body);
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
| **tenantSlug** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TenantDefinition**](TenantDefinition.md)

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


## suspendTenantApiV1AdminTenantsTenantSlugSuspendPost

> TenantDefinition suspendTenantApiV1AdminTenantsTenantSlugSuspendPost(tenantSlug, authorization, xAmeshCSRF)

Suspend Tenant

### Example

```ts
import {
  Configuration,
  TenantsApi,
} from '@amesh/client';
import type { SuspendTenantApiV1AdminTenantsTenantSlugSuspendPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TenantsApi();

  const body = {
    // string
    tenantSlug: tenantSlug_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies SuspendTenantApiV1AdminTenantsTenantSlugSuspendPostRequest;

  try {
    const data = await api.suspendTenantApiV1AdminTenantsTenantSlugSuspendPost(body);
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
| **tenantSlug** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TenantDefinition**](TenantDefinition.md)

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


## updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut

> TenantDefinition updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut(tenantSlug, tenantPolicy, authorization, xAmeshCSRF)

Update Tenant Policy

### Example

```ts
import {
  Configuration,
  TenantsApi,
} from '@amesh/client';
import type { UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new TenantsApi();

  const body = {
    // string
    tenantSlug: tenantSlug_example,
    // TenantPolicy
    tenantPolicy: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPutRequest;

  try {
    const data = await api.updateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut(body);
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
| **tenantSlug** | `string` |  | [Defaults to `undefined`] |
| **tenantPolicy** | [TenantPolicy](TenantPolicy.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**TenantDefinition**](TenantDefinition.md)

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
