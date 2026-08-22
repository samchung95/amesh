# AuthorizationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut**](AuthorizationApi.md#addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut) | **PUT** /api/v1/admin/groups/{group_id}/members/{member_id} | Add Group Member |
| [**addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPutWithHttpInfo**](AuthorizationApi.md#addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPutWithHttpInfo) | **PUT** /api/v1/admin/groups/{group_id}/members/{member_id} | Add Group Member |
| [**createPrincipalApiV1AdminPrincipalsPost**](AuthorizationApi.md#createPrincipalApiV1AdminPrincipalsPost) | **POST** /api/v1/admin/principals | Create Principal |
| [**createPrincipalApiV1AdminPrincipalsPostWithHttpInfo**](AuthorizationApi.md#createPrincipalApiV1AdminPrincipalsPostWithHttpInfo) | **POST** /api/v1/admin/principals | Create Principal |
| [**createRoleBindingApiV1AdminBindingsPost**](AuthorizationApi.md#createRoleBindingApiV1AdminBindingsPost) | **POST** /api/v1/admin/bindings | Create Role Binding |
| [**createRoleBindingApiV1AdminBindingsPostWithHttpInfo**](AuthorizationApi.md#createRoleBindingApiV1AdminBindingsPostWithHttpInfo) | **POST** /api/v1/admin/bindings | Create Role Binding |
| [**deleteRoleBindingApiV1AdminBindingsBindingIdDelete**](AuthorizationApi.md#deleteRoleBindingApiV1AdminBindingsBindingIdDelete) | **DELETE** /api/v1/admin/bindings/{binding_id} | Delete Role Binding |
| [**deleteRoleBindingApiV1AdminBindingsBindingIdDeleteWithHttpInfo**](AuthorizationApi.md#deleteRoleBindingApiV1AdminBindingsBindingIdDeleteWithHttpInfo) | **DELETE** /api/v1/admin/bindings/{binding_id} | Delete Role Binding |
| [**explainAuthorizationApiV1AuthorizationExplainPost**](AuthorizationApi.md#explainAuthorizationApiV1AuthorizationExplainPost) | **POST** /api/v1/authorization/explain | Explain Authorization |
| [**explainAuthorizationApiV1AuthorizationExplainPostWithHttpInfo**](AuthorizationApi.md#explainAuthorizationApiV1AuthorizationExplainPostWithHttpInfo) | **POST** /api/v1/authorization/explain | Explain Authorization |
| [**listPrincipalsApiV1AdminPrincipalsGet**](AuthorizationApi.md#listPrincipalsApiV1AdminPrincipalsGet) | **GET** /api/v1/admin/principals | List Principals |
| [**listPrincipalsApiV1AdminPrincipalsGetWithHttpInfo**](AuthorizationApi.md#listPrincipalsApiV1AdminPrincipalsGetWithHttpInfo) | **GET** /api/v1/admin/principals | List Principals |
| [**listRoleBindingsApiV1AdminBindingsGet**](AuthorizationApi.md#listRoleBindingsApiV1AdminBindingsGet) | **GET** /api/v1/admin/bindings | List Role Bindings |
| [**listRoleBindingsApiV1AdminBindingsGetWithHttpInfo**](AuthorizationApi.md#listRoleBindingsApiV1AdminBindingsGetWithHttpInfo) | **GET** /api/v1/admin/bindings | List Role Bindings |
| [**listRolesApiV1AdminRolesGet**](AuthorizationApi.md#listRolesApiV1AdminRolesGet) | **GET** /api/v1/admin/roles | List Roles |
| [**listRolesApiV1AdminRolesGetWithHttpInfo**](AuthorizationApi.md#listRolesApiV1AdminRolesGetWithHttpInfo) | **GET** /api/v1/admin/roles | List Roles |
| [**removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete**](AuthorizationApi.md#removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete) | **DELETE** /api/v1/admin/groups/{group_id}/members/{member_id} | Remove Group Member |
| [**removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDeleteWithHttpInfo**](AuthorizationApi.md#removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDeleteWithHttpInfo) | **DELETE** /api/v1/admin/groups/{group_id}/members/{member_id} | Remove Group Member |
| [**setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut**](AuthorizationApi.md#setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut) | **PUT** /api/v1/admin/tenants/{tenant_id}/namespaces/{namespace}/authorization-boundary | Set Namespace Authorization Boundary |
| [**setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPutWithHttpInfo**](AuthorizationApi.md#setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPutWithHttpInfo) | **PUT** /api/v1/admin/tenants/{tenant_id}/namespaces/{namespace}/authorization-boundary | Set Namespace Authorization Boundary |
| [**upsertRoleApiV1AdminRolesRoleNamePut**](AuthorizationApi.md#upsertRoleApiV1AdminRolesRoleNamePut) | **PUT** /api/v1/admin/roles/{role_name} | Upsert Role |
| [**upsertRoleApiV1AdminRolesRoleNamePutWithHttpInfo**](AuthorizationApi.md#upsertRoleApiV1AdminRolesRoleNamePutWithHttpInfo) | **PUT** /api/v1/admin/roles/{role_name} | Upsert Role |



## addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut

> void addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut(groupId, memberId, authorization, xAmeshCSRF)

Add Group Member

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        UUID memberId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            apiInstance.addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut(groupId, memberId, authorization, xAmeshCSRF);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut");
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
| **groupId** | **UUID**|  | |
| **memberId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

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

## addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPutWithHttpInfo

> ApiResponse<Void> addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPutWithHttpInfo(groupId, memberId, authorization, xAmeshCSRF)

Add Group Member

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        UUID memberId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPutWithHttpInfo(groupId, memberId, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut");
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
| **groupId** | **UUID**|  | |
| **memberId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

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


## createPrincipalApiV1AdminPrincipalsPost

> PrincipalDefinition createPrincipalApiV1AdminPrincipalsPost(principalDefinition, authorization, xAmeshCSRF)

Create Principal

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        PrincipalDefinition principalDefinition = new PrincipalDefinition(); // PrincipalDefinition |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            PrincipalDefinition result = apiInstance.createPrincipalApiV1AdminPrincipalsPost(principalDefinition, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#createPrincipalApiV1AdminPrincipalsPost");
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
| **principalDefinition** | [**PrincipalDefinition**](PrincipalDefinition.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**PrincipalDefinition**](PrincipalDefinition.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createPrincipalApiV1AdminPrincipalsPostWithHttpInfo

> ApiResponse<PrincipalDefinition> createPrincipalApiV1AdminPrincipalsPostWithHttpInfo(principalDefinition, authorization, xAmeshCSRF)

Create Principal

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        PrincipalDefinition principalDefinition = new PrincipalDefinition(); // PrincipalDefinition |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<PrincipalDefinition> response = apiInstance.createPrincipalApiV1AdminPrincipalsPostWithHttpInfo(principalDefinition, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#createPrincipalApiV1AdminPrincipalsPost");
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
| **principalDefinition** | [**PrincipalDefinition**](PrincipalDefinition.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**PrincipalDefinition**](PrincipalDefinition.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## createRoleBindingApiV1AdminBindingsPost

> RoleBinding createRoleBindingApiV1AdminBindingsPost(roleBinding, authorization, xAmeshCSRF)

Create Role Binding

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        RoleBinding roleBinding = new RoleBinding(); // RoleBinding |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            RoleBinding result = apiInstance.createRoleBindingApiV1AdminBindingsPost(roleBinding, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#createRoleBindingApiV1AdminBindingsPost");
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
| **roleBinding** | [**RoleBinding**](RoleBinding.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**RoleBinding**](RoleBinding.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createRoleBindingApiV1AdminBindingsPostWithHttpInfo

> ApiResponse<RoleBinding> createRoleBindingApiV1AdminBindingsPostWithHttpInfo(roleBinding, authorization, xAmeshCSRF)

Create Role Binding

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        RoleBinding roleBinding = new RoleBinding(); // RoleBinding |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<RoleBinding> response = apiInstance.createRoleBindingApiV1AdminBindingsPostWithHttpInfo(roleBinding, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#createRoleBindingApiV1AdminBindingsPost");
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
| **roleBinding** | [**RoleBinding**](RoleBinding.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**RoleBinding**](RoleBinding.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## deleteRoleBindingApiV1AdminBindingsBindingIdDelete

> void deleteRoleBindingApiV1AdminBindingsBindingIdDelete(bindingId, xAmeshTenant, xAmeshNamespace, authorization, xAmeshCSRF)

Delete Role Binding

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        UUID bindingId = UUID.randomUUID(); // UUID |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String xAmeshNamespace = "xAmeshNamespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            apiInstance.deleteRoleBindingApiV1AdminBindingsBindingIdDelete(bindingId, xAmeshTenant, xAmeshNamespace, authorization, xAmeshCSRF);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#deleteRoleBindingApiV1AdminBindingsBindingIdDelete");
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
| **bindingId** | **UUID**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **xAmeshNamespace** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

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

## deleteRoleBindingApiV1AdminBindingsBindingIdDeleteWithHttpInfo

> ApiResponse<Void> deleteRoleBindingApiV1AdminBindingsBindingIdDeleteWithHttpInfo(bindingId, xAmeshTenant, xAmeshNamespace, authorization, xAmeshCSRF)

Delete Role Binding

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        UUID bindingId = UUID.randomUUID(); // UUID |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        String xAmeshNamespace = "xAmeshNamespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.deleteRoleBindingApiV1AdminBindingsBindingIdDeleteWithHttpInfo(bindingId, xAmeshTenant, xAmeshNamespace, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#deleteRoleBindingApiV1AdminBindingsBindingIdDelete");
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
| **bindingId** | **UUID**|  | |
| **xAmeshTenant** | **String**|  | [optional] |
| **xAmeshNamespace** | **String**|  | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

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


## explainAuthorizationApiV1AuthorizationExplainPost

> AuthorizationDecision explainAuthorizationApiV1AuthorizationExplainPost(authorizationExplanationRequest, authorization, xAmeshCSRF)

Explain Authorization

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        AuthorizationExplanationRequest authorizationExplanationRequest = new AuthorizationExplanationRequest(); // AuthorizationExplanationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            AuthorizationDecision result = apiInstance.explainAuthorizationApiV1AuthorizationExplainPost(authorizationExplanationRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#explainAuthorizationApiV1AuthorizationExplainPost");
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
| **authorizationExplanationRequest** | [**AuthorizationExplanationRequest**](AuthorizationExplanationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**AuthorizationDecision**](AuthorizationDecision.md)


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

## explainAuthorizationApiV1AuthorizationExplainPostWithHttpInfo

> ApiResponse<AuthorizationDecision> explainAuthorizationApiV1AuthorizationExplainPostWithHttpInfo(authorizationExplanationRequest, authorization, xAmeshCSRF)

Explain Authorization

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        AuthorizationExplanationRequest authorizationExplanationRequest = new AuthorizationExplanationRequest(); // AuthorizationExplanationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<AuthorizationDecision> response = apiInstance.explainAuthorizationApiV1AuthorizationExplainPostWithHttpInfo(authorizationExplanationRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#explainAuthorizationApiV1AuthorizationExplainPost");
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
| **authorizationExplanationRequest** | [**AuthorizationExplanationRequest**](AuthorizationExplanationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**AuthorizationDecision**](AuthorizationDecision.md)>


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


## listPrincipalsApiV1AdminPrincipalsGet

> List<PrincipalDefinition> listPrincipalsApiV1AdminPrincipalsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Principals

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            List<PrincipalDefinition> result = apiInstance.listPrincipalsApiV1AdminPrincipalsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#listPrincipalsApiV1AdminPrincipalsGet");
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
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**List&lt;PrincipalDefinition&gt;**](PrincipalDefinition.md)


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

## listPrincipalsApiV1AdminPrincipalsGetWithHttpInfo

> ApiResponse<List<PrincipalDefinition>> listPrincipalsApiV1AdminPrincipalsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Principals

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<List<PrincipalDefinition>> response = apiInstance.listPrincipalsApiV1AdminPrincipalsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#listPrincipalsApiV1AdminPrincipalsGet");
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
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;PrincipalDefinition&gt;**](PrincipalDefinition.md)>


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


## listRoleBindingsApiV1AdminBindingsGet

> List<RoleBinding> listRoleBindingsApiV1AdminBindingsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Role Bindings

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            List<RoleBinding> result = apiInstance.listRoleBindingsApiV1AdminBindingsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#listRoleBindingsApiV1AdminBindingsGet");
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
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**List&lt;RoleBinding&gt;**](RoleBinding.md)


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

## listRoleBindingsApiV1AdminBindingsGetWithHttpInfo

> ApiResponse<List<RoleBinding>> listRoleBindingsApiV1AdminBindingsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Role Bindings

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<List<RoleBinding>> response = apiInstance.listRoleBindingsApiV1AdminBindingsGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#listRoleBindingsApiV1AdminBindingsGet");
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
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;RoleBinding&gt;**](RoleBinding.md)>


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


## listRolesApiV1AdminRolesGet

> List<RoleDefinition> listRolesApiV1AdminRolesGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Roles

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            List<RoleDefinition> result = apiInstance.listRolesApiV1AdminRolesGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#listRolesApiV1AdminRolesGet");
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
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**List&lt;RoleDefinition&gt;**](RoleDefinition.md)


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

## listRolesApiV1AdminRolesGetWithHttpInfo

> ApiResponse<List<RoleDefinition>> listRolesApiV1AdminRolesGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Roles

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String cursor = "cursor_example"; // String | Opaque cursor from the prior page
        Integer limit = 56; // Integer |
        List<String> filter = Arrays.asList(); // List<String> | Repeatable top-level equality filter in field=value form
        String sort = "sort_example"; // String | Comma-separated top-level fields; prefix descending fields with -
        String fields = "fields_example"; // String | Comma-separated top-level response fields
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<List<RoleDefinition>> response = apiInstance.listRolesApiV1AdminRolesGetWithHttpInfo(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#listRolesApiV1AdminRolesGet");
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
| **filter** | [**List&lt;String&gt;**](String.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional] |
| **sort** | **String**| Comma-separated top-level fields; prefix descending fields with - | [optional] |
| **fields** | **String**| Comma-separated top-level response fields | [optional] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;RoleDefinition&gt;**](RoleDefinition.md)>


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


## removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete

> void removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete(groupId, memberId, authorization, xAmeshCSRF)

Remove Group Member

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        UUID memberId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            apiInstance.removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete(groupId, memberId, authorization, xAmeshCSRF);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete");
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
| **groupId** | **UUID**|  | |
| **memberId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

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

## removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDeleteWithHttpInfo

> ApiResponse<Void> removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDeleteWithHttpInfo(groupId, memberId, authorization, xAmeshCSRF)

Remove Group Member

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        UUID memberId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDeleteWithHttpInfo(groupId, memberId, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete");
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
| **groupId** | **UUID**|  | |
| **memberId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

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


## setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut

> NamespaceAuthorizationBoundary setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut(tenantId, namespace, authorization, xAmeshCSRF)

Set Namespace Authorization Boundary

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String tenantId = "tenantId_example"; // String |
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            NamespaceAuthorizationBoundary result = apiInstance.setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut(tenantId, namespace, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut");
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
| **tenantId** | **String**|  | |
| **namespace** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**NamespaceAuthorizationBoundary**](NamespaceAuthorizationBoundary.md)


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

## setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPutWithHttpInfo

> ApiResponse<NamespaceAuthorizationBoundary> setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPutWithHttpInfo(tenantId, namespace, authorization, xAmeshCSRF)

Set Namespace Authorization Boundary

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String tenantId = "tenantId_example"; // String |
        String namespace = "namespace_example"; // String |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<NamespaceAuthorizationBoundary> response = apiInstance.setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPutWithHttpInfo(tenantId, namespace, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut");
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
| **tenantId** | **String**|  | |
| **namespace** | **String**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**NamespaceAuthorizationBoundary**](NamespaceAuthorizationBoundary.md)>


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


## upsertRoleApiV1AdminRolesRoleNamePut

> RoleDefinition upsertRoleApiV1AdminRolesRoleNamePut(roleName, roleDefinition, authorization, xAmeshCSRF)

Upsert Role

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String roleName = "roleName_example"; // String |
        RoleDefinition roleDefinition = new RoleDefinition(); // RoleDefinition |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            RoleDefinition result = apiInstance.upsertRoleApiV1AdminRolesRoleNamePut(roleName, roleDefinition, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#upsertRoleApiV1AdminRolesRoleNamePut");
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
| **roleName** | **String**|  | |
| **roleDefinition** | [**RoleDefinition**](RoleDefinition.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**RoleDefinition**](RoleDefinition.md)


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

## upsertRoleApiV1AdminRolesRoleNamePutWithHttpInfo

> ApiResponse<RoleDefinition> upsertRoleApiV1AdminRolesRoleNamePutWithHttpInfo(roleName, roleDefinition, authorization, xAmeshCSRF)

Upsert Role

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthorizationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthorizationApi apiInstance = new AuthorizationApi(defaultClient);
        String roleName = "roleName_example"; // String |
        RoleDefinition roleDefinition = new RoleDefinition(); // RoleDefinition |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<RoleDefinition> response = apiInstance.upsertRoleApiV1AdminRolesRoleNamePutWithHttpInfo(roleName, roleDefinition, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthorizationApi#upsertRoleApiV1AdminRolesRoleNamePut");
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
| **roleName** | **String**|  | |
| **roleDefinition** | [**RoleDefinition**](RoleDefinition.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**RoleDefinition**](RoleDefinition.md)>


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
