# FlowsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**applyFlowApiV1FlowsPut**](FlowsApi.md#applyFlowApiV1FlowsPut) | **PUT** /api/v1/flows | Apply Flow |
| [**applyFlowApiV1FlowsPutWithHttpInfo**](FlowsApi.md#applyFlowApiV1FlowsPutWithHttpInfo) | **PUT** /api/v1/flows | Apply Flow |
| [**deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete**](FlowsApi.md#deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision} | Delete Flow Revision |
| [**deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDeleteWithHttpInfo**](FlowsApi.md#deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDeleteWithHttpInfo) | **DELETE** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision} | Delete Flow Revision |
| [**diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost**](FlowsApi.md#diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/diff-draft | Diff Flow Draft |
| [**diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPostWithHttpInfo**](FlowsApi.md#diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPostWithHttpInfo) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/diff-draft | Diff Flow Draft |
| [**diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet**](FlowsApi.md#diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions/diff | Diff Flow Revisions |
| [**diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGetWithHttpInfo**](FlowsApi.md#diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGetWithHttpInfo) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions/diff | Diff Flow Revisions |
| [**exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet**](FlowsApi.md#exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet) | **GET** /api/v1/flows/{namespace}/{flow_id}/document | Export Flow Document |
| [**exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGetWithHttpInfo**](FlowsApi.md#exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGetWithHttpInfo) | **GET** /api/v1/flows/{namespace}/{flow_id}/document | Export Flow Document |
| [**formatFlowApiV1FlowsFormatPost**](FlowsApi.md#formatFlowApiV1FlowsFormatPost) | **POST** /api/v1/flows/format | Format Flow |
| [**formatFlowApiV1FlowsFormatPostWithHttpInfo**](FlowsApi.md#formatFlowApiV1FlowsFormatPostWithHttpInfo) | **POST** /api/v1/flows/format | Format Flow |
| [**getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet**](FlowsApi.md#getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet) | **GET** /api/v1/flows/{namespace}/{flow_id}/data-contract | Get Flow Data Contract |
| [**getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGetWithHttpInfo**](FlowsApi.md#getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGetWithHttpInfo) | **GET** /api/v1/flows/{namespace}/{flow_id}/data-contract | Get Flow Data Contract |
| [**getFlowEditorSchemaApiV1FlowsEditorSchemaGet**](FlowsApi.md#getFlowEditorSchemaApiV1FlowsEditorSchemaGet) | **GET** /api/v1/flows/editor/schema | Get Flow Editor Schema |
| [**getFlowEditorSchemaApiV1FlowsEditorSchemaGetWithHttpInfo**](FlowsApi.md#getFlowEditorSchemaApiV1FlowsEditorSchemaGetWithHttpInfo) | **GET** /api/v1/flows/editor/schema | Get Flow Editor Schema |
| [**getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet**](FlowsApi.md#getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet) | **GET** /api/v1/flows/{namespace}/{flow_id}/graph | Get Flow Graph |
| [**getFlowGraphApiV1FlowsNamespaceFlowIdGraphGetWithHttpInfo**](FlowsApi.md#getFlowGraphApiV1FlowsNamespaceFlowIdGraphGetWithHttpInfo) | **GET** /api/v1/flows/{namespace}/{flow_id}/graph | Get Flow Graph |
| [**getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet**](FlowsApi.md#getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet) | **GET** /api/v1/flows/{namespace}/{flow_id}/metadata | Get Flow Metadata |
| [**getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGetWithHttpInfo**](FlowsApi.md#getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGetWithHttpInfo) | **GET** /api/v1/flows/{namespace}/{flow_id}/metadata | Get Flow Metadata |
| [**listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet**](FlowsApi.md#listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions | List Flow Revisions |
| [**listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGetWithHttpInfo**](FlowsApi.md#listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGetWithHttpInfo) | **GET** /api/v1/flows/{namespace}/{flow_id}/revisions | List Flow Revisions |
| [**listFlowsApiV1FlowsGet**](FlowsApi.md#listFlowsApiV1FlowsGet) | **GET** /api/v1/flows | List Flows |
| [**listFlowsApiV1FlowsGetWithHttpInfo**](FlowsApi.md#listFlowsApiV1FlowsGetWithHttpInfo) | **GET** /api/v1/flows | List Flows |
| [**previewFlowExpressionApiV1FlowsExpressionsPreviewPost**](FlowsApi.md#previewFlowExpressionApiV1FlowsExpressionsPreviewPost) | **POST** /api/v1/flows/expressions/preview | Preview Flow Expression |
| [**previewFlowExpressionApiV1FlowsExpressionsPreviewPostWithHttpInfo**](FlowsApi.md#previewFlowExpressionApiV1FlowsExpressionsPreviewPostWithHttpInfo) | **POST** /api/v1/flows/expressions/preview | Preview Flow Expression |
| [**promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut**](FlowsApi.md#promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut) | **PUT** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/lifecycle | Promote Flow Revision |
| [**promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePutWithHttpInfo**](FlowsApi.md#promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePutWithHttpInfo) | **PUT** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/lifecycle | Promote Flow Revision |
| [**restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost**](FlowsApi.md#restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/restore | Restore Flow Revision |
| [**restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePostWithHttpInfo**](FlowsApi.md#restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePostWithHttpInfo) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/restore | Restore Flow Revision |
| [**validateFlowApiV1FlowsValidatePost**](FlowsApi.md#validateFlowApiV1FlowsValidatePost) | **POST** /api/v1/flows/validate | Validate Flow |
| [**validateFlowApiV1FlowsValidatePostWithHttpInfo**](FlowsApi.md#validateFlowApiV1FlowsValidatePostWithHttpInfo) | **POST** /api/v1/flows/validate | Validate Flow |



## applyFlowApiV1FlowsPut

> PersistedFlow applyFlowApiV1FlowsPut(ifMatch, xAMESHSource, xAMESHCommit, xAMESHEnvironment, xAMESHDeployment, authorization, xAmeshCSRF, xAmeshTenant)

Apply Flow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String ifMatch = "ifMatch_example"; // String |
        String xAMESHSource = "xAMESHSource_example"; // String |
        String xAMESHCommit = "xAMESHCommit_example"; // String |
        String xAMESHEnvironment = "xAMESHEnvironment_example"; // String |
        String xAMESHDeployment = "xAMESHDeployment_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PersistedFlow result = apiInstance.applyFlowApiV1FlowsPut(ifMatch, xAMESHSource, xAMESHCommit, xAMESHEnvironment, xAMESHDeployment, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#applyFlowApiV1FlowsPut");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ifMatch** | **String**|  | [optional] |
| **xAMESHSource** | **String**|  | [optional] |
| **xAMESHCommit** | **String**|  | [optional] |
| **xAMESHEnvironment** | **String**|  | [optional] |
| **xAMESHDeployment** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PersistedFlow**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## applyFlowApiV1FlowsPutWithHttpInfo

> ApiResponse<PersistedFlow> applyFlowApiV1FlowsPutWithHttpInfo(ifMatch, xAMESHSource, xAMESHCommit, xAMESHEnvironment, xAMESHDeployment, authorization, xAmeshCSRF, xAmeshTenant)

Apply Flow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String ifMatch = "ifMatch_example"; // String |
        String xAMESHSource = "xAMESHSource_example"; // String |
        String xAMESHCommit = "xAMESHCommit_example"; // String |
        String xAMESHEnvironment = "xAMESHEnvironment_example"; // String |
        String xAMESHDeployment = "xAMESHDeployment_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PersistedFlow> response = apiInstance.applyFlowApiV1FlowsPutWithHttpInfo(ifMatch, xAMESHSource, xAMESHCommit, xAMESHEnvironment, xAMESHDeployment, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#applyFlowApiV1FlowsPut");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **ifMatch** | **String**|  | [optional] |
| **xAMESHSource** | **String**|  | [optional] |
| **xAMESHCommit** | **String**|  | [optional] |
| **xAMESHEnvironment** | **String**|  | [optional] |
| **xAMESHDeployment** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PersistedFlow**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete

> void deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Delete Flow Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            apiInstance.deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDeleteWithHttpInfo

> ApiResponse<Void> deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDeleteWithHttpInfo(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Delete Flow Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDeleteWithHttpInfo(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#deleteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionDelete");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type


ApiResponse<Void>

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost

> FlowRevisionDiff diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Diff Flow Draft

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowRevisionDiff result = apiInstance.diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowRevisionDiff**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPostWithHttpInfo

> ApiResponse<FlowRevisionDiff> diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPostWithHttpInfo(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Diff Flow Draft

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowRevisionDiff> response = apiInstance.diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPostWithHttpInfo(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#diffFlowDraftApiV1FlowsNamespaceFlowIdRevisionsRevisionDiffDraftPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowRevisionDiff**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet

> FlowRevisionDiff diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet(namespace, flowId, from, to, authorization, xAmeshCSRF, xAmeshTenant)

Diff Flow Revisions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer from = 56; // Integer |
        Integer to = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowRevisionDiff result = apiInstance.diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet(namespace, flowId, from, to, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **from** | **Integer**|  | |
| **to** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowRevisionDiff**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGetWithHttpInfo

> ApiResponse<FlowRevisionDiff> diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGetWithHttpInfo(namespace, flowId, from, to, authorization, xAmeshCSRF, xAmeshTenant)

Diff Flow Revisions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer from = 56; // Integer |
        Integer to = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowRevisionDiff> response = apiInstance.diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGetWithHttpInfo(namespace, flowId, from, to, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#diffFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsDiffGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **from** | **Integer**|  | |
| **to** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowRevisionDiff**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet

> FlowDocumentExport exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Export Flow Document

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowDocumentExport result = apiInstance.exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowDocumentExport**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGetWithHttpInfo

> ApiResponse<FlowDocumentExport> exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGetWithHttpInfo(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Export Flow Document

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowDocumentExport> response = apiInstance.exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGetWithHttpInfo(namespace, flowId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#exportFlowDocumentApiV1FlowsNamespaceFlowIdDocumentGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowDocumentExport**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## formatFlowApiV1FlowsFormatPost

> FlowFormatResponse formatFlowApiV1FlowsFormatPost()

Format Flow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        try {
            FlowFormatResponse result = apiInstance.formatFlowApiV1FlowsFormatPost();
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#formatFlowApiV1FlowsFormatPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

**FlowFormatResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

## formatFlowApiV1FlowsFormatPostWithHttpInfo

> ApiResponse<FlowFormatResponse> formatFlowApiV1FlowsFormatPostWithHttpInfo()

Format Flow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        try {
            ApiResponse<FlowFormatResponse> response = apiInstance.formatFlowApiV1FlowsFormatPostWithHttpInfo();
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#formatFlowApiV1FlowsFormatPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

ApiResponse<**FlowFormatResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |


## getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet

> FlowDataContract getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Data Contract

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowDataContract result = apiInstance.getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowDataContract**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGetWithHttpInfo

> ApiResponse<FlowDataContract> getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGetWithHttpInfo(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Data Contract

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowDataContract> response = apiInstance.getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGetWithHttpInfo(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#getFlowDataContractApiV1FlowsNamespaceFlowIdDataContractGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowDataContract**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getFlowEditorSchemaApiV1FlowsEditorSchemaGet

> FlowEditorSchemaResponse getFlowEditorSchemaApiV1FlowsEditorSchemaGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Editor Schema

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowEditorSchemaResponse result = apiInstance.getFlowEditorSchemaApiV1FlowsEditorSchemaGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#getFlowEditorSchemaApiV1FlowsEditorSchemaGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowEditorSchemaResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getFlowEditorSchemaApiV1FlowsEditorSchemaGetWithHttpInfo

> ApiResponse<FlowEditorSchemaResponse> getFlowEditorSchemaApiV1FlowsEditorSchemaGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Editor Schema

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowEditorSchemaResponse> response = apiInstance.getFlowEditorSchemaApiV1FlowsEditorSchemaGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#getFlowEditorSchemaApiV1FlowsEditorSchemaGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowEditorSchemaResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet

> FlowGraph getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Graph

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowGraph result = apiInstance.getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowGraph**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getFlowGraphApiV1FlowsNamespaceFlowIdGraphGetWithHttpInfo

> ApiResponse<FlowGraph> getFlowGraphApiV1FlowsNamespaceFlowIdGraphGetWithHttpInfo(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Graph

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowGraph> response = apiInstance.getFlowGraphApiV1FlowsNamespaceFlowIdGraphGetWithHttpInfo(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#getFlowGraphApiV1FlowsNamespaceFlowIdGraphGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowGraph**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet

> FlowMetadataResponse getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Metadata

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            FlowMetadataResponse result = apiInstance.getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**FlowMetadataResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGetWithHttpInfo

> ApiResponse<FlowMetadataResponse> getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGetWithHttpInfo(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

Get Flow Metadata

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<FlowMetadataResponse> response = apiInstance.getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGetWithHttpInfo(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#getFlowMetadataApiV1FlowsNamespaceFlowIdMetadataGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**FlowMetadataResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet

> List<FlowRevisionRecord> listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

List Flow Revisions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<FlowRevisionRecord> result = apiInstance.listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;FlowRevisionRecord&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGetWithHttpInfo

> ApiResponse<List<FlowRevisionRecord>> listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGetWithHttpInfo(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant)

List Flow Revisions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<FlowRevisionRecord>> response = apiInstance.listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGetWithHttpInfo(namespace, flowId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#listFlowRevisionsApiV1FlowsNamespaceFlowIdRevisionsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;FlowRevisionRecord&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listFlowsApiV1FlowsGet

> List<PersistedFlow> listFlowsApiV1FlowsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Flows

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<PersistedFlow> result = apiInstance.listFlowsApiV1FlowsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#listFlowsApiV1FlowsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cursor** | **String**| Opaque cursor from the prior page | [optional] |
| **limit** | **Integer**|  | [optional] |
| **filter** | **List&lt;String&gt;**| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;PersistedFlow&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listFlowsApiV1FlowsGetWithHttpInfo

> ApiResponse<List<PersistedFlow>> listFlowsApiV1FlowsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant)

List Flows

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<PersistedFlow>> response = apiInstance.listFlowsApiV1FlowsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#listFlowsApiV1FlowsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **cursor** | **String**| Opaque cursor from the prior page | [optional] |
| **limit** | **Integer**|  | [optional] |
| **filter** | **List&lt;String&gt;**| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;PersistedFlow&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## previewFlowExpressionApiV1FlowsExpressionsPreviewPost

> ExpressionPreviewResponse previewFlowExpressionApiV1FlowsExpressionsPreviewPost(expressionPreviewRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Flow Expression

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        ExpressionPreviewRequest expressionPreviewRequest = new ExpressionPreviewRequest(); // ExpressionPreviewRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ExpressionPreviewResponse result = apiInstance.previewFlowExpressionApiV1FlowsExpressionsPreviewPost(expressionPreviewRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#previewFlowExpressionApiV1FlowsExpressionsPreviewPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **expressionPreviewRequest** | **ExpressionPreviewRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**ExpressionPreviewResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## previewFlowExpressionApiV1FlowsExpressionsPreviewPostWithHttpInfo

> ApiResponse<ExpressionPreviewResponse> previewFlowExpressionApiV1FlowsExpressionsPreviewPostWithHttpInfo(expressionPreviewRequest, authorization, xAmeshCSRF, xAmeshTenant)

Preview Flow Expression

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        ExpressionPreviewRequest expressionPreviewRequest = new ExpressionPreviewRequest(); // ExpressionPreviewRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ExpressionPreviewResponse> response = apiInstance.previewFlowExpressionApiV1FlowsExpressionsPreviewPostWithHttpInfo(expressionPreviewRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#previewFlowExpressionApiV1FlowsExpressionsPreviewPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **expressionPreviewRequest** | **ExpressionPreviewRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**ExpressionPreviewResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut

> PersistedFlow promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut(namespace, flowId, revision, flowRevisionLifecycleRequest, authorization, xAmeshCSRF, xAmeshTenant)

Promote Flow Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        FlowRevisionLifecycleRequest flowRevisionLifecycleRequest = new FlowRevisionLifecycleRequest(); // FlowRevisionLifecycleRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PersistedFlow result = apiInstance.promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut(namespace, flowId, revision, flowRevisionLifecycleRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **flowRevisionLifecycleRequest** | **FlowRevisionLifecycleRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PersistedFlow**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePutWithHttpInfo

> ApiResponse<PersistedFlow> promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePutWithHttpInfo(namespace, flowId, revision, flowRevisionLifecycleRequest, authorization, xAmeshCSRF, xAmeshTenant)

Promote Flow Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        FlowRevisionLifecycleRequest flowRevisionLifecycleRequest = new FlowRevisionLifecycleRequest(); // FlowRevisionLifecycleRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PersistedFlow> response = apiInstance.promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePutWithHttpInfo(namespace, flowId, revision, flowRevisionLifecycleRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#promoteFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionLifecyclePut");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **flowRevisionLifecycleRequest** | **FlowRevisionLifecycleRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PersistedFlow**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost

> PersistedFlow restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost(namespace, flowId, revision, flowRevisionRestoreRequest, authorization, xAmeshCSRF, xAmeshTenant)

Restore Flow Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        FlowRevisionRestoreRequest flowRevisionRestoreRequest = new FlowRevisionRestoreRequest(); // FlowRevisionRestoreRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            PersistedFlow result = apiInstance.restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost(namespace, flowId, revision, flowRevisionRestoreRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **flowRevisionRestoreRequest** | **FlowRevisionRestoreRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**PersistedFlow**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePostWithHttpInfo

> ApiResponse<PersistedFlow> restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePostWithHttpInfo(namespace, flowId, revision, flowRevisionRestoreRequest, authorization, xAmeshCSRF, xAmeshTenant)

Restore Flow Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        FlowRevisionRestoreRequest flowRevisionRestoreRequest = new FlowRevisionRestoreRequest(); // FlowRevisionRestoreRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<PersistedFlow> response = apiInstance.restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePostWithHttpInfo(namespace, flowId, revision, flowRevisionRestoreRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#restoreFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionRestorePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **flowRevisionRestoreRequest** | **FlowRevisionRestoreRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**PersistedFlow**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## validateFlowApiV1FlowsValidatePost

> FlowValidationResult validateFlowApiV1FlowsValidatePost()

Validate Flow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        try {
            FlowValidationResult result = apiInstance.validateFlowApiV1FlowsValidatePost();
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#validateFlowApiV1FlowsValidatePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

**FlowValidationResult**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

## validateFlowApiV1FlowsValidatePostWithHttpInfo

> ApiResponse<FlowValidationResult> validateFlowApiV1FlowsValidatePostWithHttpInfo()

Validate Flow

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.FlowsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        FlowsApi apiInstance = new FlowsApi(defaultClient);
        try {
            ApiResponse<FlowValidationResult> response = apiInstance.validateFlowApiV1FlowsValidatePostWithHttpInfo();
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling FlowsApi#validateFlowApiV1FlowsValidatePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

ApiResponse<**FlowValidationResult**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
