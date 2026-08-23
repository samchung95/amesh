# \AdministrationAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ApplyAdministrationControlApiV1AdminControlsKeyPut**](AdministrationAPI.md#ApplyAdministrationControlApiV1AdminControlsKeyPut) | **Put** /api/v1/admin/controls/{key} | Apply Administration Control
[**ListAdministrationAuditApiV1AdminAuditGet**](AdministrationAPI.md#ListAdministrationAuditApiV1AdminAuditGet) | **Get** /api/v1/admin/audit | List Administration Audit
[**ListAdministrationControlsApiV1AdminControlsGet**](AdministrationAPI.md#ListAdministrationControlsApiV1AdminControlsGet) | **Get** /api/v1/admin/controls | List Administration Controls
[**PreviewAdministrationControlApiV1AdminControlsPreviewPost**](AdministrationAPI.md#PreviewAdministrationControlApiV1AdminControlsPreviewPost) | **Post** /api/v1/admin/controls/preview | Preview Administration Control



## ApplyAdministrationControlApiV1AdminControlsKeyPut

> AdministrationControl ApplyAdministrationControlApiV1AdminControlsKeyPut(ctx, key).AdministrationApplyRequest(administrationApplyRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Apply Administration Control

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
	key := openapiclient.AdministrationControlKey("RETENTION") // AdministrationControlKey |
	administrationApplyRequest := *openapiclient.NewAdministrationApplyRequest("Approval_example", "Confirmation_example", *openapiclient.NewAdministrationControlDraft(false, openapiclient.AdministrationControlKey("RETENTION"), "Reason_example")) // AdministrationApplyRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AdministrationAPI.ApplyAdministrationControlApiV1AdminControlsKeyPut(context.Background(), key).AdministrationApplyRequest(administrationApplyRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AdministrationAPI.ApplyAdministrationControlApiV1AdminControlsKeyPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ApplyAdministrationControlApiV1AdminControlsKeyPut`: AdministrationControl
	fmt.Fprintf(os.Stdout, "Response from `AdministrationAPI.ApplyAdministrationControlApiV1AdminControlsKeyPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**key** | [**AdministrationControlKey**](.md) |  |

### Other Parameters

Other parameters are passed through a pointer to a apiApplyAdministrationControlApiV1AdminControlsKeyPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **administrationApplyRequest** | [**AdministrationApplyRequest**](AdministrationApplyRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AdministrationControl**](AdministrationControl.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAdministrationAuditApiV1AdminAuditGet

> []AdministrationAuditEntry ListAdministrationAuditApiV1AdminAuditGet(ctx).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Administration Audit

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
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AdministrationAPI.ListAdministrationAuditApiV1AdminAuditGet(context.Background()).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AdministrationAPI.ListAdministrationAuditApiV1AdminAuditGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAdministrationAuditApiV1AdminAuditGet`: []AdministrationAuditEntry
	fmt.Fprintf(os.Stdout, "Response from `AdministrationAPI.ListAdministrationAuditApiV1AdminAuditGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAdministrationAuditApiV1AdminAuditGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]AdministrationAuditEntry**](AdministrationAuditEntry.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAdministrationControlsApiV1AdminControlsGet

> []AdministrationControl ListAdministrationControlsApiV1AdminControlsGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Administration Controls

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AdministrationAPI.ListAdministrationControlsApiV1AdminControlsGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AdministrationAPI.ListAdministrationControlsApiV1AdminControlsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAdministrationControlsApiV1AdminControlsGet`: []AdministrationControl
	fmt.Fprintf(os.Stdout, "Response from `AdministrationAPI.ListAdministrationControlsApiV1AdminControlsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAdministrationControlsApiV1AdminControlsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]AdministrationControl**](AdministrationControl.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PreviewAdministrationControlApiV1AdminControlsPreviewPost

> AdministrationImpactPreview PreviewAdministrationControlApiV1AdminControlsPreviewPost(ctx).AdministrationControlDraft(administrationControlDraft).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Preview Administration Control

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
	administrationControlDraft := *openapiclient.NewAdministrationControlDraft(false, openapiclient.AdministrationControlKey("RETENTION"), "Reason_example") // AdministrationControlDraft |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AdministrationAPI.PreviewAdministrationControlApiV1AdminControlsPreviewPost(context.Background()).AdministrationControlDraft(administrationControlDraft).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AdministrationAPI.PreviewAdministrationControlApiV1AdminControlsPreviewPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PreviewAdministrationControlApiV1AdminControlsPreviewPost`: AdministrationImpactPreview
	fmt.Fprintf(os.Stdout, "Response from `AdministrationAPI.PreviewAdministrationControlApiV1AdminControlsPreviewPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPreviewAdministrationControlApiV1AdminControlsPreviewPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **administrationControlDraft** | [**AdministrationControlDraft**](AdministrationControlDraft.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AdministrationImpactPreview**](AdministrationImpactPreview.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
