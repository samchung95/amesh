# AgentSessionAdministrationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost**](AgentSessionAdministrationApi.md#bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost) | **POST** /api/v1/admin/agent-sessions/actions | Bulk Control Agent Sessions |
| [**bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPostWithHttpInfo**](AgentSessionAdministrationApi.md#bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPostWithHttpInfo) | **POST** /api/v1/admin/agent-sessions/actions | Bulk Control Agent Sessions |
| [**getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet**](AgentSessionAdministrationApi.md#getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet) | **GET** /api/v1/admin/agent-sessions/aggregate | Get Agent Session Instance Aggregate |
| [**getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGetWithHttpInfo**](AgentSessionAdministrationApi.md#getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGetWithHttpInfo) | **GET** /api/v1/admin/agent-sessions/aggregate | Get Agent Session Instance Aggregate |
| [**getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet**](AgentSessionAdministrationApi.md#getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet) | **GET** /api/v1/admin/agent-session-policies/{policy_id} | Get Agent Session Policy Revision |
| [**getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGetWithHttpInfo**](AgentSessionAdministrationApi.md#getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGetWithHttpInfo) | **GET** /api/v1/admin/agent-session-policies/{policy_id} | Get Agent Session Policy Revision |
| [**getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet**](AgentSessionAdministrationApi.md#getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet) | **GET** /api/v1/admin/agent-session-policies/effective | Get Effective Agent Session Policies |
| [**getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGetWithHttpInfo**](AgentSessionAdministrationApi.md#getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGetWithHttpInfo) | **GET** /api/v1/admin/agent-session-policies/effective | Get Effective Agent Session Policies |
| [**listAgentSessionFleetApiV1AdminAgentSessionsGet**](AgentSessionAdministrationApi.md#listAgentSessionFleetApiV1AdminAgentSessionsGet) | **GET** /api/v1/admin/agent-sessions | List Agent Session Fleet |
| [**listAgentSessionFleetApiV1AdminAgentSessionsGetWithHttpInfo**](AgentSessionAdministrationApi.md#listAgentSessionFleetApiV1AdminAgentSessionsGetWithHttpInfo) | **GET** /api/v1/admin/agent-sessions | List Agent Session Fleet |
| [**listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet**](AgentSessionAdministrationApi.md#listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet) | **GET** /api/v1/admin/agent-session-policies | List Agent Session Policies |
| [**listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGetWithHttpInfo**](AgentSessionAdministrationApi.md#listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGetWithHttpInfo) | **GET** /api/v1/admin/agent-session-policies | List Agent Session Policies |
| [**putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut**](AgentSessionAdministrationApi.md#putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut) | **PUT** /api/v1/admin/agent-session-policies | Put Agent Session Policy |
| [**putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPutWithHttpInfo**](AgentSessionAdministrationApi.md#putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPutWithHttpInfo) | **PUT** /api/v1/admin/agent-session-policies | Put Agent Session Policy |



## bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost

> AgentSessionBulkActionResponse bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost(agentSessionBulkActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Bulk Control Agent Sessions

Apply bounded, independently fenced lifecycle controls to agent sessions.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        AgentSessionBulkActionRequest agentSessionBulkActionRequest = new AgentSessionBulkActionRequest(); // AgentSessionBulkActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionBulkActionResponse result = apiInstance.bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost(agentSessionBulkActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost");
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
| **agentSessionBulkActionRequest** | **AgentSessionBulkActionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionBulkActionResponse**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **207** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPostWithHttpInfo

> ApiResponse<AgentSessionBulkActionResponse> bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPostWithHttpInfo(agentSessionBulkActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Bulk Control Agent Sessions

Apply bounded, independently fenced lifecycle controls to agent sessions.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        AgentSessionBulkActionRequest agentSessionBulkActionRequest = new AgentSessionBulkActionRequest(); // AgentSessionBulkActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionBulkActionResponse> response = apiInstance.bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPostWithHttpInfo(agentSessionBulkActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost");
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
| **agentSessionBulkActionRequest** | **AgentSessionBulkActionRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionBulkActionResponse**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **207** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet

> AgentSessionInstanceAggregate getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet(authorization, xAmeshCSRF)

Get Agent Session Instance Aggregate

Return instance-wide metadata-only totals without exposing tenant session rows.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            AgentSessionInstanceAggregate result = apiInstance.getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet(authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet");
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

### Return type

**AgentSessionInstanceAggregate**


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

## getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGetWithHttpInfo

> ApiResponse<AgentSessionInstanceAggregate> getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGetWithHttpInfo(authorization, xAmeshCSRF)

Get Agent Session Instance Aggregate

Return instance-wide metadata-only totals without exposing tenant session rows.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<AgentSessionInstanceAggregate> response = apiInstance.getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGetWithHttpInfo(authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet");
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

### Return type

ApiResponse<**AgentSessionInstanceAggregate**>


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


## getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet

> AgentSessionPolicyRevision getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet(policyId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Policy Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        UUID policyId = UUID.randomUUID(); // UUID |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionPolicyRevision result = apiInstance.getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet(policyId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet");
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
| **policyId** | **UUID**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionPolicyRevision**


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

## getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGetWithHttpInfo

> ApiResponse<AgentSessionPolicyRevision> getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGetWithHttpInfo(policyId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Policy Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        UUID policyId = UUID.randomUUID(); // UUID |
        Integer revision = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionPolicyRevision> response = apiInstance.getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGetWithHttpInfo(policyId, revision, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet");
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
| **policyId** | **UUID**|  | |
| **revision** | **Integer**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionPolicyRevision**>


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


## getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet

> List<AgentSessionPolicyRevision> getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet(namespace, applicationId, authorization, xAmeshCSRF, xAmeshTenant)

Get Effective Agent Session Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String applicationId = "applicationId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<AgentSessionPolicyRevision> result = apiInstance.getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet(namespace, applicationId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet");
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
| **applicationId** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;AgentSessionPolicyRevision&gt;**


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

## getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGetWithHttpInfo

> ApiResponse<List<AgentSessionPolicyRevision>> getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGetWithHttpInfo(namespace, applicationId, authorization, xAmeshCSRF, xAmeshTenant)

Get Effective Agent Session Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String applicationId = "applicationId_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<AgentSessionPolicyRevision>> response = apiInstance.getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGetWithHttpInfo(namespace, applicationId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet");
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
| **applicationId** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;AgentSessionPolicyRevision&gt;**>


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


## listAgentSessionFleetApiV1AdminAgentSessionsGet

> AgentSessionFleetPage listAgentSessionFleetApiV1AdminAgentSessionsGet(limit, cursor, state, namespace, agentRef, ownerId, harness, createdFrom, createdTo, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Session Fleet

Return a bounded, tenant-isolated administrative session fleet projection.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        Integer limit = 100; // Integer |
        String cursor = "cursor_example"; // String |
        String state = "state_example"; // String |
        String namespace = "namespace_example"; // String |
        String agentRef = "agentRef_example"; // String |
        String ownerId = "ownerId_example"; // String |
        String harness = "harness_example"; // String |
        OffsetDateTime createdFrom = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime createdTo = OffsetDateTime.now(); // OffsetDateTime |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionFleetPage result = apiInstance.listAgentSessionFleetApiV1AdminAgentSessionsGet(limit, cursor, state, namespace, agentRef, ownerId, harness, createdFrom, createdTo, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#listAgentSessionFleetApiV1AdminAgentSessionsGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **cursor** | **String**|  | [optional] |
| **state** | **String**|  | [optional] |
| **namespace** | **String**|  | [optional] |
| **agentRef** | **String**|  | [optional] |
| **ownerId** | **String**|  | [optional] |
| **harness** | **String**|  | [optional] |
| **createdFrom** | **OffsetDateTime**|  | [optional] |
| **createdTo** | **OffsetDateTime**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionFleetPage**


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

## listAgentSessionFleetApiV1AdminAgentSessionsGetWithHttpInfo

> ApiResponse<AgentSessionFleetPage> listAgentSessionFleetApiV1AdminAgentSessionsGetWithHttpInfo(limit, cursor, state, namespace, agentRef, ownerId, harness, createdFrom, createdTo, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Session Fleet

Return a bounded, tenant-isolated administrative session fleet projection.

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        Integer limit = 100; // Integer |
        String cursor = "cursor_example"; // String |
        String state = "state_example"; // String |
        String namespace = "namespace_example"; // String |
        String agentRef = "agentRef_example"; // String |
        String ownerId = "ownerId_example"; // String |
        String harness = "harness_example"; // String |
        OffsetDateTime createdFrom = OffsetDateTime.now(); // OffsetDateTime |
        OffsetDateTime createdTo = OffsetDateTime.now(); // OffsetDateTime |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionFleetPage> response = apiInstance.listAgentSessionFleetApiV1AdminAgentSessionsGetWithHttpInfo(limit, cursor, state, namespace, agentRef, ownerId, harness, createdFrom, createdTo, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#listAgentSessionFleetApiV1AdminAgentSessionsGet");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **cursor** | **String**|  | [optional] |
| **state** | **String**|  | [optional] |
| **namespace** | **String**|  | [optional] |
| **agentRef** | **String**|  | [optional] |
| **ownerId** | **String**|  | [optional] |
| **harness** | **String**|  | [optional] |
| **createdFrom** | **OffsetDateTime**|  | [optional] |
| **createdTo** | **OffsetDateTime**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionFleetPage**>


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


## listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet

> List<AgentSessionPolicyRevision> listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet(namespace, applicationId, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Session Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String applicationId = "applicationId_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<AgentSessionPolicyRevision> result = apiInstance.listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet(namespace, applicationId, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet");
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
| **namespace** | **String**|  | [optional] |
| **applicationId** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**List&lt;AgentSessionPolicyRevision&gt;**


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

## listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGetWithHttpInfo

> ApiResponse<List<AgentSessionPolicyRevision>> listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGetWithHttpInfo(namespace, applicationId, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Session Policies

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String applicationId = "applicationId_example"; // String |
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<AgentSessionPolicyRevision>> response = apiInstance.listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGetWithHttpInfo(namespace, applicationId, limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet");
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
| **namespace** | **String**|  | [optional] |
| **applicationId** | **String**|  | [optional] |
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**List&lt;AgentSessionPolicyRevision&gt;**>


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


## putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut

> AgentSessionPolicyRevision putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut(agentSessionPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Put Agent Session Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        AgentSessionPolicyUpsertRequest agentSessionPolicyUpsertRequest = new AgentSessionPolicyUpsertRequest(); // AgentSessionPolicyUpsertRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AgentSessionPolicyRevision result = apiInstance.putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut(agentSessionPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut");
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
| **agentSessionPolicyUpsertRequest** | **AgentSessionPolicyUpsertRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**AgentSessionPolicyRevision**


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

## putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPutWithHttpInfo

> ApiResponse<AgentSessionPolicyRevision> putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPutWithHttpInfo(agentSessionPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Put Agent Session Policy

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AgentSessionAdministrationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AgentSessionAdministrationApi apiInstance = new AgentSessionAdministrationApi(defaultClient);
        AgentSessionPolicyUpsertRequest agentSessionPolicyUpsertRequest = new AgentSessionPolicyUpsertRequest(); // AgentSessionPolicyUpsertRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AgentSessionPolicyRevision> response = apiInstance.putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPutWithHttpInfo(agentSessionPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AgentSessionAdministrationApi#putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut");
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
| **agentSessionPolicyUpsertRequest** | **AgentSessionPolicyUpsertRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**AgentSessionPolicyRevision**>


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
