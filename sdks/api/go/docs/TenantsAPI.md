# \TenantsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateTenantApiV1AdminTenantsPost**](TenantsAPI.md#CreateTenantApiV1AdminTenantsPost) | **Post** /api/v1/admin/tenants | Create Tenant
[**DeleteTenantApiV1AdminTenantsTenantSlugDelete**](TenantsAPI.md#DeleteTenantApiV1AdminTenantsTenantSlugDelete) | **Delete** /api/v1/admin/tenants/{tenant_slug} | Delete Tenant
[**ExportTenantApiV1AdminTenantsTenantSlugExportsPost**](TenantsAPI.md#ExportTenantApiV1AdminTenantsTenantSlugExportsPost) | **Post** /api/v1/admin/tenants/{tenant_slug}/exports | Export Tenant
[**GetTenantApiV1AdminTenantsTenantSlugGet**](TenantsAPI.md#GetTenantApiV1AdminTenantsTenantSlugGet) | **Get** /api/v1/admin/tenants/{tenant_slug} | Get Tenant
[**ListTenantsApiV1AdminTenantsGet**](TenantsAPI.md#ListTenantsApiV1AdminTenantsGet) | **Get** /api/v1/admin/tenants | List Tenants
[**RestoreTenantApiV1AdminTenantsTenantSlugRestorePost**](TenantsAPI.md#RestoreTenantApiV1AdminTenantsTenantSlugRestorePost) | **Post** /api/v1/admin/tenants/{tenant_slug}/restore | Restore Tenant
[**SuspendTenantApiV1AdminTenantsTenantSlugSuspendPost**](TenantsAPI.md#SuspendTenantApiV1AdminTenantsTenantSlugSuspendPost) | **Post** /api/v1/admin/tenants/{tenant_slug}/suspend | Suspend Tenant
[**UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut**](TenantsAPI.md#UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut) | **Put** /api/v1/admin/tenants/{tenant_slug}/policy | Update Tenant Policy



## CreateTenantApiV1AdminTenantsPost

> TenantDefinition CreateTenantApiV1AdminTenantsPost(ctx).CreateTenantRequest(createTenantRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Create Tenant

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
	createTenantRequest := *openapiclient.NewCreateTenantRequest("DisplayName_example", "Slug_example") // CreateTenantRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TenantsAPI.CreateTenantApiV1AdminTenantsPost(context.Background()).CreateTenantRequest(createTenantRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TenantsAPI.CreateTenantApiV1AdminTenantsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateTenantApiV1AdminTenantsPost`: TenantDefinition
	fmt.Fprintf(os.Stdout, "Response from `TenantsAPI.CreateTenantApiV1AdminTenantsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateTenantApiV1AdminTenantsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **createTenantRequest** | [**CreateTenantRequest**](CreateTenantRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**TenantDefinition**](TenantDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteTenantApiV1AdminTenantsTenantSlugDelete

> TenantDefinition DeleteTenantApiV1AdminTenantsTenantSlugDelete(ctx, tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Delete Tenant

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
	tenantSlug := "tenantSlug_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TenantsAPI.DeleteTenantApiV1AdminTenantsTenantSlugDelete(context.Background(), tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TenantsAPI.DeleteTenantApiV1AdminTenantsTenantSlugDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteTenantApiV1AdminTenantsTenantSlugDelete`: TenantDefinition
	fmt.Fprintf(os.Stdout, "Response from `TenantsAPI.DeleteTenantApiV1AdminTenantsTenantSlugDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**tenantSlug** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteTenantApiV1AdminTenantsTenantSlugDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**TenantDefinition**](TenantDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExportTenantApiV1AdminTenantsTenantSlugExportsPost

> TenantExport ExportTenantApiV1AdminTenantsTenantSlugExportsPost(ctx, tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Export Tenant

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
	tenantSlug := "tenantSlug_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TenantsAPI.ExportTenantApiV1AdminTenantsTenantSlugExportsPost(context.Background(), tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TenantsAPI.ExportTenantApiV1AdminTenantsTenantSlugExportsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExportTenantApiV1AdminTenantsTenantSlugExportsPost`: TenantExport
	fmt.Fprintf(os.Stdout, "Response from `TenantsAPI.ExportTenantApiV1AdminTenantsTenantSlugExportsPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**tenantSlug** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiExportTenantApiV1AdminTenantsTenantSlugExportsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**TenantExport**](TenantExport.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetTenantApiV1AdminTenantsTenantSlugGet

> TenantDefinition GetTenantApiV1AdminTenantsTenantSlugGet(ctx, tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Get Tenant

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
	tenantSlug := "tenantSlug_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TenantsAPI.GetTenantApiV1AdminTenantsTenantSlugGet(context.Background(), tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TenantsAPI.GetTenantApiV1AdminTenantsTenantSlugGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetTenantApiV1AdminTenantsTenantSlugGet`: TenantDefinition
	fmt.Fprintf(os.Stdout, "Response from `TenantsAPI.GetTenantApiV1AdminTenantsTenantSlugGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**tenantSlug** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetTenantApiV1AdminTenantsTenantSlugGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**TenantDefinition**](TenantDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListTenantsApiV1AdminTenantsGet

> []TenantDefinition ListTenantsApiV1AdminTenantsGet(ctx).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

List Tenants

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
	resp, r, err := apiClient.TenantsAPI.ListTenantsApiV1AdminTenantsGet(context.Background()).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TenantsAPI.ListTenantsApiV1AdminTenantsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListTenantsApiV1AdminTenantsGet`: []TenantDefinition
	fmt.Fprintf(os.Stdout, "Response from `TenantsAPI.ListTenantsApiV1AdminTenantsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListTenantsApiV1AdminTenantsGetRequest struct via the builder pattern


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

[**[]TenantDefinition**](TenantDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RestoreTenantApiV1AdminTenantsTenantSlugRestorePost

> TenantDefinition RestoreTenantApiV1AdminTenantsTenantSlugRestorePost(ctx, tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Restore Tenant

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
	tenantSlug := "tenantSlug_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TenantsAPI.RestoreTenantApiV1AdminTenantsTenantSlugRestorePost(context.Background(), tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TenantsAPI.RestoreTenantApiV1AdminTenantsTenantSlugRestorePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RestoreTenantApiV1AdminTenantsTenantSlugRestorePost`: TenantDefinition
	fmt.Fprintf(os.Stdout, "Response from `TenantsAPI.RestoreTenantApiV1AdminTenantsTenantSlugRestorePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**tenantSlug** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRestoreTenantApiV1AdminTenantsTenantSlugRestorePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**TenantDefinition**](TenantDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SuspendTenantApiV1AdminTenantsTenantSlugSuspendPost

> TenantDefinition SuspendTenantApiV1AdminTenantsTenantSlugSuspendPost(ctx, tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Suspend Tenant

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
	tenantSlug := "tenantSlug_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TenantsAPI.SuspendTenantApiV1AdminTenantsTenantSlugSuspendPost(context.Background(), tenantSlug).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TenantsAPI.SuspendTenantApiV1AdminTenantsTenantSlugSuspendPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SuspendTenantApiV1AdminTenantsTenantSlugSuspendPost`: TenantDefinition
	fmt.Fprintf(os.Stdout, "Response from `TenantsAPI.SuspendTenantApiV1AdminTenantsTenantSlugSuspendPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**tenantSlug** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiSuspendTenantApiV1AdminTenantsTenantSlugSuspendPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**TenantDefinition**](TenantDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut

> TenantDefinition UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut(ctx, tenantSlug).TenantPolicy(tenantPolicy).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Update Tenant Policy

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
	tenantSlug := "tenantSlug_example" // string |
	tenantPolicy := *openapiclient.NewTenantPolicy() // TenantPolicy |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.TenantsAPI.UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut(context.Background(), tenantSlug).TenantPolicy(tenantPolicy).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `TenantsAPI.UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut`: TenantDefinition
	fmt.Fprintf(os.Stdout, "Response from `TenantsAPI.UpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**tenantSlug** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateTenantPolicyApiV1AdminTenantsTenantSlugPolicyPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **tenantPolicy** | [**TenantPolicy**](TenantPolicy.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**TenantDefinition**](TenantDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
