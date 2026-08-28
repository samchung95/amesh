# NamespacesApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet**](NamespacesApi.md#getnamespaceworkflowmetadataapiv1namespacesnamespaceworkflowmetadataget) | **GET** /api/v1/namespaces/{namespace}/workflow-metadata | Get Namespace Workflow Metadata |
| [**upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut**](NamespacesApi.md#upsertnamespaceworkflowmetadataapiv1namespacesnamespaceworkflowmetadataput) | **PUT** /api/v1/namespaces/{namespace}/workflow-metadata | Upsert Namespace Workflow Metadata |



## getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet

> NamespaceWorkflowMetadataView getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet(namespace, authorization, xAmeshCSRF, xAmeshTenant)

Get Namespace Workflow Metadata

### Example

```ts
import {
  Configuration,
  NamespacesApi,
} from '@amesh/client';
import type { GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespacesApi();

  const body = {
    // string
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGetRequest;

  try {
    const data = await api.getNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataGet(body);
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

**NamespaceWorkflowMetadataView**

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


## upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut

> NamespaceWorkflowMetadata upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut(namespace, namespaceWorkflowMetadataUpdate, authorization, xAmeshCSRF, xAmeshTenant)

Upsert Namespace Workflow Metadata

### Example

```ts
import {
  Configuration,
  NamespacesApi,
} from '@amesh/client';
import type { UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new NamespacesApi();

  const body = {
    // string
    namespace: namespace_example,
    // NamespaceWorkflowMetadataUpdate
    namespaceWorkflowMetadataUpdate: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies UpsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPutRequest;

  try {
    const data = await api.upsertNamespaceWorkflowMetadataApiV1NamespacesNamespaceWorkflowMetadataPut(body);
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
| **namespaceWorkflowMetadataUpdate** | NamespaceWorkflowMetadataUpdate |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**NamespaceWorkflowMetadata**

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
