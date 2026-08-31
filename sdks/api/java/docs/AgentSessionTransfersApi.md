# AgentSessionTransfersApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet**](AgentSessionTransfersApi.md#exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet) | **GET** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer |
| [**exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGetWithHttpInfo**](AgentSessionTransfersApi.md#exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGetWithHttpInfo) | **GET** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer |
| [**exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost**](AgentSessionTransfersApi.md#exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost) | **POST** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer |
| [**exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPostWithHttpInfo**](AgentSessionTransfersApi.md#exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPostWithHttpInfo) | **POST** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer |
| [**exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost**](AgentSessionTransfersApi.md#exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost) | **POST** /api/v1/admin/agent-session-transfers/sessions/{session_id}/export | Export Agent Session Transfer |
| [**exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPostWithHttpInfo**](AgentSessionTransfersApi.md#exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPostWithHttpInfo) | **POST** /api/v1/admin/agent-session-transfers/sessions/{session_id}/export | Export Agent Session Transfer |
| [**importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost**](AgentSessionTransfersApi.md#importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost) | **POST** /api/v1/admin/agent-session-transfers/profiles/import | Import Agent Profile Transfer |
| [**importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPostWithHttpInfo**](AgentSessionTransfersApi.md#importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPostWithHttpInfo) | **POST** /api/v1/admin/agent-session-transfers/profiles/import | Import Agent Profile Transfer |
| [**importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost**](AgentSessionTransfersApi.md#importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost) | **POST** /api/v1/admin/agent-session-transfers/sessions/import | Import Agent Session Transfer |
| [**importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPostWithHttpInfo**](AgentSessionTransfersApi.md#importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPostWithHttpInfo) | **POST** /api/v1/admin/agent-session-transfers/sessions/import | Import Agent Session Transfer |
| [**planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost**](AgentSessionTransfersApi.md#planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost) | **POST** /api/v1/admin/agent-session-transfers/profiles/plan | Plan Agent Profile Transfer |
| [**planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPostWithHttpInfo**](AgentSessionTransfersApi.md#planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPostWithHttpInfo) | **POST** /api/v1/admin/agent-session-transfers/profiles/plan | Plan Agent Profile Transfer |
| [**planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost**](AgentSessionTransfersApi.md#planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost) | **POST** /api/v1/admin/agent-session-transfers/sessions/plan | Plan Agent Session Transfer |
| [**planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPostWithHttpInfo**](AgentSessionTransfersApi.md#planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPostWithHttpInfo) | **POST** /api/v1/admin/agent-session-transfers/sessions/plan | Plan Agent Session Transfer |



## exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet

> ProfileBundleOutput exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant)

Export Agent Profile Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String agentKey = "agentKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ProfileBundleOutput result = apiInstance.exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet");
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
| **agentKey** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**ProfileBundleOutput**


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

## exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGetWithHttpInfo

> ApiResponse<ProfileBundleOutput> exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGetWithHttpInfo(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant)

Export Agent Profile Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String agentKey = "agentKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ProfileBundleOutput> response = apiInstance.exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGetWithHttpInfo(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet");
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
| **agentKey** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**ProfileBundleOutput**>


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


## exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost

> ProfileBundleOutput exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant)

Export Agent Profile Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String agentKey = "agentKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ProfileBundleOutput result = apiInstance.exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost");
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
| **agentKey** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**ProfileBundleOutput**


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

## exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPostWithHttpInfo

> ApiResponse<ProfileBundleOutput> exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPostWithHttpInfo(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant)

Export Agent Profile Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String agentKey = "agentKey_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ProfileBundleOutput> response = apiInstance.exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPostWithHttpInfo(namespace, agentKey, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#exportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost");
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
| **agentKey** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**ProfileBundleOutput**>


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


## exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost

> SessionTransferBundleOutput exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost(sessionId, agentSessionTransferSessionExportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Export Agent Session Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        UUID sessionId = UUID.randomUUID(); // UUID |
        AgentSessionTransferSessionExportRequest agentSessionTransferSessionExportRequest = new AgentSessionTransferSessionExportRequest(); // AgentSessionTransferSessionExportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SessionTransferBundleOutput result = apiInstance.exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost(sessionId, agentSessionTransferSessionExportRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost");
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
| **sessionId** | **UUID**|  | |
| **agentSessionTransferSessionExportRequest** | **AgentSessionTransferSessionExportRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**SessionTransferBundleOutput**


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

## exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPostWithHttpInfo

> ApiResponse<SessionTransferBundleOutput> exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPostWithHttpInfo(sessionId, agentSessionTransferSessionExportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Export Agent Session Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        UUID sessionId = UUID.randomUUID(); // UUID |
        AgentSessionTransferSessionExportRequest agentSessionTransferSessionExportRequest = new AgentSessionTransferSessionExportRequest(); // AgentSessionTransferSessionExportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SessionTransferBundleOutput> response = apiInstance.exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPostWithHttpInfo(sessionId, agentSessionTransferSessionExportRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#exportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost");
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
| **sessionId** | **UUID**|  | |
| **agentSessionTransferSessionExportRequest** | **AgentSessionTransferSessionExportRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**SessionTransferBundleOutput**>


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


## importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost

> ProfileImportResult importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost(agentSessionTransferProfileImportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Import Agent Profile Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        AgentSessionTransferProfileImportRequest agentSessionTransferProfileImportRequest = new AgentSessionTransferProfileImportRequest(); // AgentSessionTransferProfileImportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ProfileImportResult result = apiInstance.importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost(agentSessionTransferProfileImportRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost");
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
| **agentSessionTransferProfileImportRequest** | **AgentSessionTransferProfileImportRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**ProfileImportResult**


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

## importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPostWithHttpInfo

> ApiResponse<ProfileImportResult> importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPostWithHttpInfo(agentSessionTransferProfileImportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Import Agent Profile Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        AgentSessionTransferProfileImportRequest agentSessionTransferProfileImportRequest = new AgentSessionTransferProfileImportRequest(); // AgentSessionTransferProfileImportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ProfileImportResult> response = apiInstance.importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPostWithHttpInfo(agentSessionTransferProfileImportRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#importAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost");
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
| **agentSessionTransferProfileImportRequest** | **AgentSessionTransferProfileImportRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**ProfileImportResult**>


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


## importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost

> SessionTransferImportResult importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost(agentSessionTransferSessionImportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Import Agent Session Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        AgentSessionTransferSessionImportRequest agentSessionTransferSessionImportRequest = new AgentSessionTransferSessionImportRequest(); // AgentSessionTransferSessionImportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SessionTransferImportResult result = apiInstance.importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost(agentSessionTransferSessionImportRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost");
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
| **agentSessionTransferSessionImportRequest** | **AgentSessionTransferSessionImportRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**SessionTransferImportResult**


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

## importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPostWithHttpInfo

> ApiResponse<SessionTransferImportResult> importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPostWithHttpInfo(agentSessionTransferSessionImportRequest, authorization, xAmeshCSRF, xAmeshTenant)

Import Agent Session Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        AgentSessionTransferSessionImportRequest agentSessionTransferSessionImportRequest = new AgentSessionTransferSessionImportRequest(); // AgentSessionTransferSessionImportRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SessionTransferImportResult> response = apiInstance.importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPostWithHttpInfo(agentSessionTransferSessionImportRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#importAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost");
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
| **agentSessionTransferSessionImportRequest** | **AgentSessionTransferSessionImportRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**SessionTransferImportResult**>


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


## planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost

> ProfileCompatibilityReport planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost(agentSessionTransferProfilePlanRequest, authorization, xAmeshCSRF, xAmeshTenant)

Plan Agent Profile Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        AgentSessionTransferProfilePlanRequest agentSessionTransferProfilePlanRequest = new AgentSessionTransferProfilePlanRequest(); // AgentSessionTransferProfilePlanRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ProfileCompatibilityReport result = apiInstance.planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost(agentSessionTransferProfilePlanRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost");
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
| **agentSessionTransferProfilePlanRequest** | **AgentSessionTransferProfilePlanRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**ProfileCompatibilityReport**


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

## planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPostWithHttpInfo

> ApiResponse<ProfileCompatibilityReport> planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPostWithHttpInfo(agentSessionTransferProfilePlanRequest, authorization, xAmeshCSRF, xAmeshTenant)

Plan Agent Profile Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        AgentSessionTransferProfilePlanRequest agentSessionTransferProfilePlanRequest = new AgentSessionTransferProfilePlanRequest(); // AgentSessionTransferProfilePlanRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ProfileCompatibilityReport> response = apiInstance.planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPostWithHttpInfo(agentSessionTransferProfilePlanRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#planAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost");
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
| **agentSessionTransferProfilePlanRequest** | **AgentSessionTransferProfilePlanRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**ProfileCompatibilityReport**>


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


## planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost

> SessionTransferCompatibilityReport planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost(agentSessionTransferSessionPlanRequest, authorization, xAmeshCSRF, xAmeshTenant)

Plan Agent Session Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        AgentSessionTransferSessionPlanRequest agentSessionTransferSessionPlanRequest = new AgentSessionTransferSessionPlanRequest(); // AgentSessionTransferSessionPlanRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SessionTransferCompatibilityReport result = apiInstance.planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost(agentSessionTransferSessionPlanRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost");
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
| **agentSessionTransferSessionPlanRequest** | **AgentSessionTransferSessionPlanRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**SessionTransferCompatibilityReport**


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

## planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPostWithHttpInfo

> ApiResponse<SessionTransferCompatibilityReport> planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPostWithHttpInfo(agentSessionTransferSessionPlanRequest, authorization, xAmeshCSRF, xAmeshTenant)

Plan Agent Session Transfer

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionTransfersApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionTransfersApi apiInstance = new AgentSessionTransfersApi(defaultClient);
        AgentSessionTransferSessionPlanRequest agentSessionTransferSessionPlanRequest = new AgentSessionTransferSessionPlanRequest(); // AgentSessionTransferSessionPlanRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SessionTransferCompatibilityReport> response = apiInstance.planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPostWithHttpInfo(agentSessionTransferSessionPlanRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionTransfersApi#planAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost");
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
| **agentSessionTransferSessionPlanRequest** | **AgentSessionTransferSessionPlanRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**SessionTransferCompatibilityReport**>


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
