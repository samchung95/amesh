# AuthorizationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut**](AuthorizationApi.md#addgroupmemberapiv1admingroupsgroupidmembersmemberidput) | **PUT** /api/v1/admin/groups/{group_id}/members/{member_id} | Add Group Member |
| [**createPrincipalApiV1AdminPrincipalsPost**](AuthorizationApi.md#createprincipalapiv1adminprincipalspost) | **POST** /api/v1/admin/principals | Create Principal |
| [**createRoleBindingApiV1AdminBindingsPost**](AuthorizationApi.md#createrolebindingapiv1adminbindingspost) | **POST** /api/v1/admin/bindings | Create Role Binding |
| [**deleteRoleBindingApiV1AdminBindingsBindingIdDelete**](AuthorizationApi.md#deleterolebindingapiv1adminbindingsbindingiddelete) | **DELETE** /api/v1/admin/bindings/{binding_id} | Delete Role Binding |
| [**explainAuthorizationApiV1AuthorizationExplainPost**](AuthorizationApi.md#explainauthorizationapiv1authorizationexplainpost) | **POST** /api/v1/authorization/explain | Explain Authorization |
| [**listPrincipalsApiV1AdminPrincipalsGet**](AuthorizationApi.md#listprincipalsapiv1adminprincipalsget) | **GET** /api/v1/admin/principals | List Principals |
| [**listRoleBindingsApiV1AdminBindingsGet**](AuthorizationApi.md#listrolebindingsapiv1adminbindingsget) | **GET** /api/v1/admin/bindings | List Role Bindings |
| [**listRolesApiV1AdminRolesGet**](AuthorizationApi.md#listrolesapiv1adminrolesget) | **GET** /api/v1/admin/roles | List Roles |
| [**removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete**](AuthorizationApi.md#removegroupmemberapiv1admingroupsgroupidmembersmemberiddelete) | **DELETE** /api/v1/admin/groups/{group_id}/members/{member_id} | Remove Group Member |
| [**setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut**](AuthorizationApi.md#setnamespaceauthorizationboundaryapiv1admintenantstenantidnamespacesnamespaceauthorizationboundaryput) | **PUT** /api/v1/admin/tenants/{tenant_id}/namespaces/{namespace}/authorization-boundary | Set Namespace Authorization Boundary |
| [**upsertRoleApiV1AdminRolesRoleNamePut**](AuthorizationApi.md#upsertroleapiv1adminrolesrolenameput) | **PUT** /api/v1/admin/roles/{role_name} | Upsert Role |



## addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut

> addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut(groupId, memberId, authorization, xAmeshCSRF)

Add Group Member

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { AddGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

  const body = {
    // string
    groupId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string
    memberId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies AddGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPutRequest;

  try {
    const data = await api.addGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut(body);
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
| **groupId** | `string` |  | [Defaults to `undefined`] |
| **memberId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

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
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## createPrincipalApiV1AdminPrincipalsPost

> PrincipalDefinition createPrincipalApiV1AdminPrincipalsPost(principalDefinition, authorization, xAmeshCSRF)

Create Principal

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { CreatePrincipalApiV1AdminPrincipalsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

  const body = {
    // PrincipalDefinition
    principalDefinition: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies CreatePrincipalApiV1AdminPrincipalsPostRequest;

  try {
    const data = await api.createPrincipalApiV1AdminPrincipalsPost(body);
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
| **principalDefinition** | [PrincipalDefinition](PrincipalDefinition.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**PrincipalDefinition**](PrincipalDefinition.md)

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


## createRoleBindingApiV1AdminBindingsPost

> RoleBinding createRoleBindingApiV1AdminBindingsPost(roleBinding, authorization, xAmeshCSRF)

Create Role Binding

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { CreateRoleBindingApiV1AdminBindingsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

  const body = {
    // RoleBinding
    roleBinding: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies CreateRoleBindingApiV1AdminBindingsPostRequest;

  try {
    const data = await api.createRoleBindingApiV1AdminBindingsPost(body);
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
| **roleBinding** | [RoleBinding](RoleBinding.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**RoleBinding**](RoleBinding.md)

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


## deleteRoleBindingApiV1AdminBindingsBindingIdDelete

> deleteRoleBindingApiV1AdminBindingsBindingIdDelete(bindingId, xAmeshTenant, xAmeshNamespace, authorization, xAmeshCSRF)

Delete Role Binding

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { DeleteRoleBindingApiV1AdminBindingsBindingIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

  const body = {
    // string
    bindingId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
    // string (optional)
    xAmeshNamespace: xAmeshNamespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies DeleteRoleBindingApiV1AdminBindingsBindingIdDeleteRequest;

  try {
    const data = await api.deleteRoleBindingApiV1AdminBindingsBindingIdDelete(body);
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
| **bindingId** | `string` |  | [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshNamespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

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
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## explainAuthorizationApiV1AuthorizationExplainPost

> AuthorizationDecision explainAuthorizationApiV1AuthorizationExplainPost(authorizationExplanationRequest, authorization, xAmeshCSRF)

Explain Authorization

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { ExplainAuthorizationApiV1AuthorizationExplainPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

  const body = {
    // AuthorizationExplanationRequest
    authorizationExplanationRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies ExplainAuthorizationApiV1AuthorizationExplainPostRequest;

  try {
    const data = await api.explainAuthorizationApiV1AuthorizationExplainPost(body);
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
| **authorizationExplanationRequest** | [AuthorizationExplanationRequest](AuthorizationExplanationRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**AuthorizationDecision**](AuthorizationDecision.md)

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


## listPrincipalsApiV1AdminPrincipalsGet

> Array&lt;PrincipalDefinition&gt; listPrincipalsApiV1AdminPrincipalsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Principals

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { ListPrincipalsApiV1AdminPrincipalsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

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
  } satisfies ListPrincipalsApiV1AdminPrincipalsGetRequest;

  try {
    const data = await api.listPrincipalsApiV1AdminPrincipalsGet(body);
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

[**Array&lt;PrincipalDefinition&gt;**](PrincipalDefinition.md)

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


## listRoleBindingsApiV1AdminBindingsGet

> Array&lt;RoleBinding&gt; listRoleBindingsApiV1AdminBindingsGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Role Bindings

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { ListRoleBindingsApiV1AdminBindingsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

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
  } satisfies ListRoleBindingsApiV1AdminBindingsGetRequest;

  try {
    const data = await api.listRoleBindingsApiV1AdminBindingsGet(body);
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

[**Array&lt;RoleBinding&gt;**](RoleBinding.md)

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


## listRolesApiV1AdminRolesGet

> Array&lt;RoleDefinition&gt; listRolesApiV1AdminRolesGet(cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Roles

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { ListRolesApiV1AdminRolesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

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
  } satisfies ListRolesApiV1AdminRolesGetRequest;

  try {
    const data = await api.listRolesApiV1AdminRolesGet(body);
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

[**Array&lt;RoleDefinition&gt;**](RoleDefinition.md)

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


## removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete

> removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete(groupId, memberId, authorization, xAmeshCSRF)

Remove Group Member

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { RemoveGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

  const body = {
    // string
    groupId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string
    memberId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RemoveGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDeleteRequest;

  try {
    const data = await api.removeGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete(body);
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
| **groupId** | `string` |  | [Defaults to `undefined`] |
| **memberId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

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
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut

> NamespaceAuthorizationBoundary setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut(tenantId, namespace, authorization, xAmeshCSRF)

Set Namespace Authorization Boundary

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

  const body = {
    // string
    tenantId: tenantId_example,
    // string
    namespace: namespace_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPutRequest;

  try {
    const data = await api.setNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut(body);
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
| **tenantId** | `string` |  | [Defaults to `undefined`] |
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**NamespaceAuthorizationBoundary**](NamespaceAuthorizationBoundary.md)

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


## upsertRoleApiV1AdminRolesRoleNamePut

> RoleDefinition upsertRoleApiV1AdminRolesRoleNamePut(roleName, roleDefinition, authorization, xAmeshCSRF)

Upsert Role

### Example

```ts
import {
  Configuration,
  AuthorizationApi,
} from '@amesh/client';
import type { UpsertRoleApiV1AdminRolesRoleNamePutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthorizationApi();

  const body = {
    // string
    roleName: roleName_example,
    // RoleDefinition
    roleDefinition: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies UpsertRoleApiV1AdminRolesRoleNamePutRequest;

  try {
    const data = await api.upsertRoleApiV1AdminRolesRoleNamePut(body);
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
| **roleName** | `string` |  | [Defaults to `undefined`] |
| **roleDefinition** | [RoleDefinition](RoleDefinition.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**RoleDefinition**](RoleDefinition.md)

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
