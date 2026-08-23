# AdministrationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyAdministrationControlApiV1AdminControlsKeyPut**](AdministrationApi.md#applyadministrationcontrolapiv1admincontrolskeyput) | **PUT** /api/v1/admin/controls/{key} | Apply Administration Control |
| [**listAdministrationAuditApiV1AdminAuditGet**](AdministrationApi.md#listadministrationauditapiv1adminauditget) | **GET** /api/v1/admin/audit | List Administration Audit |
| [**listAdministrationControlsApiV1AdminControlsGet**](AdministrationApi.md#listadministrationcontrolsapiv1admincontrolsget) | **GET** /api/v1/admin/controls | List Administration Controls |
| [**previewAdministrationControlApiV1AdminControlsPreviewPost**](AdministrationApi.md#previewadministrationcontrolapiv1admincontrolspreviewpost) | **POST** /api/v1/admin/controls/preview | Preview Administration Control |



## applyAdministrationControlApiV1AdminControlsKeyPut

> AdministrationControl applyAdministrationControlApiV1AdminControlsKeyPut(key, administrationApplyRequest, authorization, xAmeshCSRF, xAmeshTenant)

Apply Administration Control

### Example

```ts
import {
  Configuration,
  AdministrationApi,
} from '@amesh/client';
import type { ApplyAdministrationControlApiV1AdminControlsKeyPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AdministrationApi();

  const body = {
    // AdministrationControlKey
    key: ...,
    // AdministrationApplyRequest
    administrationApplyRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ApplyAdministrationControlApiV1AdminControlsKeyPutRequest;

  try {
    const data = await api.applyAdministrationControlApiV1AdminControlsKeyPut(body);
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
| **key** | `AdministrationControlKey` |  | [Defaults to `undefined`] [Enum: RETENTION, ANNOUNCEMENT, MAINTENANCE, KILL_SWITCH] |
| **administrationApplyRequest** | [AdministrationApplyRequest](AdministrationApplyRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AdministrationControl**](AdministrationControl.md)

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


## listAdministrationAuditApiV1AdminAuditGet

> Array&lt;AdministrationAuditEntry&gt; listAdministrationAuditApiV1AdminAuditGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Administration Audit

### Example

```ts
import {
  Configuration,
  AdministrationApi,
} from '@amesh/client';
import type { ListAdministrationAuditApiV1AdminAuditGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AdministrationApi();

  const body = {
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAdministrationAuditApiV1AdminAuditGetRequest;

  try {
    const data = await api.listAdministrationAuditApiV1AdminAuditGet(body);
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

[**Array&lt;AdministrationAuditEntry&gt;**](AdministrationAuditEntry.md)

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


## listAdministrationControlsApiV1AdminControlsGet

> Array&lt;AdministrationControl&gt; listAdministrationControlsApiV1AdminControlsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Administration Controls

### Example

```ts
import {
  Configuration,
  AdministrationApi,
} from '@amesh/client';
import type { ListAdministrationControlsApiV1AdminControlsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AdministrationApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAdministrationControlsApiV1AdminControlsGetRequest;

  try {
    const data = await api.listAdministrationControlsApiV1AdminControlsGet(body);
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

[**Array&lt;AdministrationControl&gt;**](AdministrationControl.md)

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


## previewAdministrationControlApiV1AdminControlsPreviewPost

> AdministrationImpactPreview previewAdministrationControlApiV1AdminControlsPreviewPost(administrationControlDraft, authorization, xAmeshCSRF, xAmeshTenant)

Preview Administration Control

### Example

```ts
import {
  Configuration,
  AdministrationApi,
} from '@amesh/client';
import type { PreviewAdministrationControlApiV1AdminControlsPreviewPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AdministrationApi();

  const body = {
    // AdministrationControlDraft
    administrationControlDraft: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PreviewAdministrationControlApiV1AdminControlsPreviewPostRequest;

  try {
    const data = await api.previewAdministrationControlApiV1AdminControlsPreviewPost(body);
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
| **administrationControlDraft** | [AdministrationControlDraft](AdministrationControlDraft.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AdministrationImpactPreview**](AdministrationImpactPreview.md)

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
