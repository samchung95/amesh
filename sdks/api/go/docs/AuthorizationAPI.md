# \AuthorizationAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**AddGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut**](AuthorizationAPI.md#AddGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut) | **Put** /api/v1/admin/groups/{group_id}/members/{member_id} | Add Group Member
[**CreatePrincipalApiV1AdminPrincipalsPost**](AuthorizationAPI.md#CreatePrincipalApiV1AdminPrincipalsPost) | **Post** /api/v1/admin/principals | Create Principal
[**CreateRoleBindingApiV1AdminBindingsPost**](AuthorizationAPI.md#CreateRoleBindingApiV1AdminBindingsPost) | **Post** /api/v1/admin/bindings | Create Role Binding
[**DeleteRoleBindingApiV1AdminBindingsBindingIdDelete**](AuthorizationAPI.md#DeleteRoleBindingApiV1AdminBindingsBindingIdDelete) | **Delete** /api/v1/admin/bindings/{binding_id} | Delete Role Binding
[**ExplainAuthorizationApiV1AuthorizationExplainPost**](AuthorizationAPI.md#ExplainAuthorizationApiV1AuthorizationExplainPost) | **Post** /api/v1/authorization/explain | Explain Authorization
[**ListPrincipalsApiV1AdminPrincipalsGet**](AuthorizationAPI.md#ListPrincipalsApiV1AdminPrincipalsGet) | **Get** /api/v1/admin/principals | List Principals
[**ListRoleBindingsApiV1AdminBindingsGet**](AuthorizationAPI.md#ListRoleBindingsApiV1AdminBindingsGet) | **Get** /api/v1/admin/bindings | List Role Bindings
[**ListRolesApiV1AdminRolesGet**](AuthorizationAPI.md#ListRolesApiV1AdminRolesGet) | **Get** /api/v1/admin/roles | List Roles
[**RemoveGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete**](AuthorizationAPI.md#RemoveGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete) | **Delete** /api/v1/admin/groups/{group_id}/members/{member_id} | Remove Group Member
[**SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut**](AuthorizationAPI.md#SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut) | **Put** /api/v1/admin/tenants/{tenant_id}/namespaces/{namespace}/authorization-boundary | Set Namespace Authorization Boundary
[**UpsertRoleApiV1AdminRolesRoleNamePut**](AuthorizationAPI.md#UpsertRoleApiV1AdminRolesRoleNamePut) | **Put** /api/v1/admin/roles/{role_name} | Upsert Role



## AddGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut

> AddGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut(ctx, groupId, memberId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Add Group Member

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	groupId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	memberId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.AuthorizationAPI.AddGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut(context.Background(), groupId, memberId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.AddGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**groupId** | **string** |  |
**memberId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiAddGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreatePrincipalApiV1AdminPrincipalsPost

> PrincipalDefinition CreatePrincipalApiV1AdminPrincipalsPost(ctx).PrincipalDefinition(principalDefinition).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Create Principal

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	principalDefinition := *openapiclient.NewPrincipalDefinition("DisplayName_example", "Handle_example", openapiclient.PrincipalType("USER")) // PrincipalDefinition |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationAPI.CreatePrincipalApiV1AdminPrincipalsPost(context.Background()).PrincipalDefinition(principalDefinition).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.CreatePrincipalApiV1AdminPrincipalsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreatePrincipalApiV1AdminPrincipalsPost`: PrincipalDefinition
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationAPI.CreatePrincipalApiV1AdminPrincipalsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreatePrincipalApiV1AdminPrincipalsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **principalDefinition** | **PrincipalDefinition** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**PrincipalDefinition**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateRoleBindingApiV1AdminBindingsPost

> RoleBinding CreateRoleBindingApiV1AdminBindingsPost(ctx).RoleBinding(roleBinding).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Create Role Binding

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	roleBinding := *openapiclient.NewRoleBinding("PrincipalId_example", openapiclient.PrincipalType("USER"), "RoleName_example", openapiclient.AuthorizationScopeType("INSTANCE")) // RoleBinding |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationAPI.CreateRoleBindingApiV1AdminBindingsPost(context.Background()).RoleBinding(roleBinding).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.CreateRoleBindingApiV1AdminBindingsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateRoleBindingApiV1AdminBindingsPost`: RoleBinding
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationAPI.CreateRoleBindingApiV1AdminBindingsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateRoleBindingApiV1AdminBindingsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **roleBinding** | **RoleBinding** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**RoleBinding**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteRoleBindingApiV1AdminBindingsBindingIdDelete

> DeleteRoleBindingApiV1AdminBindingsBindingIdDelete(ctx, bindingId).XAmeshTenant(xAmeshTenant).XAmeshNamespace(xAmeshNamespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Delete Role Binding

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	bindingId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	xAmeshNamespace := "xAmeshNamespace_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.AuthorizationAPI.DeleteRoleBindingApiV1AdminBindingsBindingIdDelete(context.Background(), bindingId).XAmeshTenant(xAmeshTenant).XAmeshNamespace(xAmeshNamespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.DeleteRoleBindingApiV1AdminBindingsBindingIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**bindingId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteRoleBindingApiV1AdminBindingsBindingIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **xAmeshTenant** | **string** |  |
 **xAmeshNamespace** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExplainAuthorizationApiV1AuthorizationExplainPost

> AuthorizationDecision ExplainAuthorizationApiV1AuthorizationExplainPost(ctx).AuthorizationExplanationRequest(authorizationExplanationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Explain Authorization

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	authorizationExplanationRequest := *openapiclient.NewAuthorizationExplanationRequest(openapiclient.PermissionAction("view"), "PrincipalId_example", openapiclient.PrincipalType("USER"), "ResourceType_example") // AuthorizationExplanationRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationAPI.ExplainAuthorizationApiV1AuthorizationExplainPost(context.Background()).AuthorizationExplanationRequest(authorizationExplanationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.ExplainAuthorizationApiV1AuthorizationExplainPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExplainAuthorizationApiV1AuthorizationExplainPost`: AuthorizationDecision
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationAPI.ExplainAuthorizationApiV1AuthorizationExplainPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiExplainAuthorizationApiV1AuthorizationExplainPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorizationExplanationRequest** | **AuthorizationExplanationRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**AuthorizationDecision**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListPrincipalsApiV1AdminPrincipalsGet

> []PrincipalDefinition ListPrincipalsApiV1AdminPrincipalsGet(ctx).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

List Principals

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	cursor := "cursor_example" // string | Opaque cursor from the prior page (optional)
	limit := int32(56) // int32 |  (optional)
	filter := []string{"Inner_example"} // []string | Repeatable top-level equality filter in field=value form (optional)
	sort := "sort_example" // string | Comma-separated top-level fields; prefix descending fields with - (optional)
	fields := "fields_example" // string | Comma-separated top-level response fields (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationAPI.ListPrincipalsApiV1AdminPrincipalsGet(context.Background()).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.ListPrincipalsApiV1AdminPrincipalsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListPrincipalsApiV1AdminPrincipalsGet`: []PrincipalDefinition
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationAPI.ListPrincipalsApiV1AdminPrincipalsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListPrincipalsApiV1AdminPrincipalsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **string** | Opaque cursor from the prior page |
 **limit** | **int32** |  |
 **filter** | **[]string** | Repeatable top-level equality filter in field&#x3D;value form |
 **sort** | **string** | Comma-separated top-level fields; prefix descending fields with - |
 **fields** | **string** | Comma-separated top-level response fields |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**[]PrincipalDefinition**](PrincipalDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListRoleBindingsApiV1AdminBindingsGet

> []RoleBinding ListRoleBindingsApiV1AdminBindingsGet(ctx).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

List Role Bindings

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	cursor := "cursor_example" // string | Opaque cursor from the prior page (optional)
	limit := int32(56) // int32 |  (optional)
	filter := []*string{"Inner_example"} // []*string | Repeatable top-level equality filter in field=value form (optional)
	sort := "sort_example" // string | Comma-separated top-level fields; prefix descending fields with - (optional)
	fields := "fields_example" // string | Comma-separated top-level response fields (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationAPI.ListRoleBindingsApiV1AdminBindingsGet(context.Background()).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.ListRoleBindingsApiV1AdminBindingsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListRoleBindingsApiV1AdminBindingsGet`: []RoleBinding
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationAPI.ListRoleBindingsApiV1AdminBindingsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListRoleBindingsApiV1AdminBindingsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **string** | Opaque cursor from the prior page |
 **limit** | **int32** |  |
 **filter** | **[]string** | Repeatable top-level equality filter in field&#x3D;value form |
 **sort** | **string** | Comma-separated top-level fields; prefix descending fields with - |
 **fields** | **string** | Comma-separated top-level response fields |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**[]RoleBinding**](RoleBinding.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListRolesApiV1AdminRolesGet

> []RoleDefinition ListRolesApiV1AdminRolesGet(ctx).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

List Roles

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	cursor := "cursor_example" // string | Opaque cursor from the prior page (optional)
	limit := int32(56) // int32 |  (optional)
	filter := []string{"Inner_example"} // []string | Repeatable top-level equality filter in field=value form (optional)
	sort := "sort_example" // string | Comma-separated top-level fields; prefix descending fields with - (optional)
	fields := "fields_example" // string | Comma-separated top-level response fields (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationAPI.ListRolesApiV1AdminRolesGet(context.Background()).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.ListRolesApiV1AdminRolesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListRolesApiV1AdminRolesGet`: []RoleDefinition
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationAPI.ListRolesApiV1AdminRolesGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListRolesApiV1AdminRolesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **string** | Opaque cursor from the prior page |
 **limit** | **int32** |  |
 **filter** | **[]string** | Repeatable top-level equality filter in field&#x3D;value form |
 **sort** | **string** | Comma-separated top-level fields; prefix descending fields with - |
 **fields** | **string** | Comma-separated top-level response fields |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**[]RoleDefinition**](RoleDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RemoveGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete

> RemoveGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete(ctx, groupId, memberId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Remove Group Member

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	groupId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	memberId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.AuthorizationAPI.RemoveGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete(context.Background(), groupId, memberId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.RemoveGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**groupId** | **string** |  |
**memberId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRemoveGroupMemberApiV1AdminGroupsGroupIdMembersMemberIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut

> NamespaceAuthorizationBoundary SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut(ctx, tenantId, namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Set Namespace Authorization Boundary

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	tenantId := "tenantId_example" // string |
	namespace := "namespace_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationAPI.SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut(context.Background(), tenantId, namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut`: NamespaceAuthorizationBoundary
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationAPI.SetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**tenantId** | **string** |  |
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiSetNamespaceAuthorizationBoundaryApiV1AdminTenantsTenantIdNamespacesNamespaceAuthorizationBoundaryPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**NamespaceAuthorizationBoundary**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpsertRoleApiV1AdminRolesRoleNamePut

> RoleDefinition UpsertRoleApiV1AdminRolesRoleNamePut(ctx, roleName).RoleDefinition(roleDefinition).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Upsert Role

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	roleName := "roleName_example" // string |
	roleDefinition := *openapiclient.NewRoleDefinition("DisplayName_example", "Name_example") // RoleDefinition |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthorizationAPI.UpsertRoleApiV1AdminRolesRoleNamePut(context.Background(), roleName).RoleDefinition(roleDefinition).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthorizationAPI.UpsertRoleApiV1AdminRolesRoleNamePut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpsertRoleApiV1AdminRolesRoleNamePut`: RoleDefinition
	fmt.Fprintf(os.Stdout, "Response from `AuthorizationAPI.UpsertRoleApiV1AdminRolesRoleNamePut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**roleName** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUpsertRoleApiV1AdminRolesRoleNamePutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **roleDefinition** | **RoleDefinition** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**RoleDefinition**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
