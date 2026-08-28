# \BackfillsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CancelBackfillApiV1BackfillsBackfillIdCancelPost**](BackfillsAPI.md#CancelBackfillApiV1BackfillsBackfillIdCancelPost) | **Post** /api/v1/backfills/{backfill_id}/cancel | Cancel Backfill
[**CreateBackfillApiV1BackfillsPost**](BackfillsAPI.md#CreateBackfillApiV1BackfillsPost) | **Post** /api/v1/backfills | Create Backfill
[**GetBackfillApiV1BackfillsBackfillIdGet**](BackfillsAPI.md#GetBackfillApiV1BackfillsBackfillIdGet) | **Get** /api/v1/backfills/{backfill_id} | Get Backfill
[**ListBackfillsApiV1BackfillsGet**](BackfillsAPI.md#ListBackfillsApiV1BackfillsGet) | **Get** /api/v1/backfills | List Backfills
[**PauseBackfillApiV1BackfillsBackfillIdPausePost**](BackfillsAPI.md#PauseBackfillApiV1BackfillsBackfillIdPausePost) | **Post** /api/v1/backfills/{backfill_id}/pause | Pause Backfill
[**PreviewBackfillApiV1BackfillsPreviewPost**](BackfillsAPI.md#PreviewBackfillApiV1BackfillsPreviewPost) | **Post** /api/v1/backfills/preview | Preview Backfill
[**ResumeBackfillApiV1BackfillsBackfillIdResumePost**](BackfillsAPI.md#ResumeBackfillApiV1BackfillsBackfillIdResumePost) | **Post** /api/v1/backfills/{backfill_id}/resume | Resume Backfill



## CancelBackfillApiV1BackfillsBackfillIdCancelPost

> BackfillRecord CancelBackfillApiV1BackfillsBackfillIdCancelPost(ctx, backfillId).BackfillActionRequest(backfillActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Cancel Backfill

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
	backfillId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	backfillActionRequest := *openapiclient.NewBackfillActionRequest("Reason_example") // BackfillActionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BackfillsAPI.CancelBackfillApiV1BackfillsBackfillIdCancelPost(context.Background(), backfillId).BackfillActionRequest(backfillActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BackfillsAPI.CancelBackfillApiV1BackfillsBackfillIdCancelPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CancelBackfillApiV1BackfillsBackfillIdCancelPost`: BackfillRecord
	fmt.Fprintf(os.Stdout, "Response from `BackfillsAPI.CancelBackfillApiV1BackfillsBackfillIdCancelPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**backfillId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiCancelBackfillApiV1BackfillsBackfillIdCancelPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **backfillActionRequest** | **BackfillActionRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**BackfillRecord**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateBackfillApiV1BackfillsPost

> BackfillRecord CreateBackfillApiV1BackfillsPost(ctx).BackfillSpec(backfillSpec).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Backfill

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
	backfillSpec := *openapiclient.NewBackfillSpec("FlowId_example", int32(123), "Namespace_example", *openapiclient.NewBackfillSelection()) // BackfillSpec |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BackfillsAPI.CreateBackfillApiV1BackfillsPost(context.Background()).BackfillSpec(backfillSpec).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BackfillsAPI.CreateBackfillApiV1BackfillsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateBackfillApiV1BackfillsPost`: BackfillRecord
	fmt.Fprintf(os.Stdout, "Response from `BackfillsAPI.CreateBackfillApiV1BackfillsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateBackfillApiV1BackfillsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfillSpec** | **BackfillSpec** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**BackfillRecord**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetBackfillApiV1BackfillsBackfillIdGet

> BackfillRecord GetBackfillApiV1BackfillsBackfillIdGet(ctx, backfillId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Backfill

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
	backfillId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BackfillsAPI.GetBackfillApiV1BackfillsBackfillIdGet(context.Background(), backfillId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BackfillsAPI.GetBackfillApiV1BackfillsBackfillIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetBackfillApiV1BackfillsBackfillIdGet`: BackfillRecord
	fmt.Fprintf(os.Stdout, "Response from `BackfillsAPI.GetBackfillApiV1BackfillsBackfillIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**backfillId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetBackfillApiV1BackfillsBackfillIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**BackfillRecord**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListBackfillsApiV1BackfillsGet

> []BackfillRecord ListBackfillsApiV1BackfillsGet(ctx).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Backfills

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
	limit := int32(56) // int32 |  (optional) (default to 100)
	filter := []string{"Inner_example"} // []string | Repeatable top-level equality filter in field=value form (optional)
	sort := "sort_example" // string | Comma-separated top-level fields; prefix descending fields with - (optional)
	fields := "fields_example" // string | Comma-separated top-level response fields (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BackfillsAPI.ListBackfillsApiV1BackfillsGet(context.Background()).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BackfillsAPI.ListBackfillsApiV1BackfillsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListBackfillsApiV1BackfillsGet`: []BackfillRecord
	fmt.Fprintf(os.Stdout, "Response from `BackfillsAPI.ListBackfillsApiV1BackfillsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListBackfillsApiV1BackfillsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **string** | Opaque cursor from the prior page |
 **limit** | **int32** |  | [default to 100]
 **filter** | **[]string** | Repeatable top-level equality filter in field&#x3D;value form |
 **sort** | **string** | Comma-separated top-level fields; prefix descending fields with - |
 **fields** | **string** | Comma-separated top-level response fields |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]BackfillRecord**](BackfillRecord.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PauseBackfillApiV1BackfillsBackfillIdPausePost

> BackfillRecord PauseBackfillApiV1BackfillsBackfillIdPausePost(ctx, backfillId).BackfillActionRequest(backfillActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Pause Backfill

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
	backfillId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	backfillActionRequest := *openapiclient.NewBackfillActionRequest("Reason_example") // BackfillActionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BackfillsAPI.PauseBackfillApiV1BackfillsBackfillIdPausePost(context.Background(), backfillId).BackfillActionRequest(backfillActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BackfillsAPI.PauseBackfillApiV1BackfillsBackfillIdPausePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PauseBackfillApiV1BackfillsBackfillIdPausePost`: BackfillRecord
	fmt.Fprintf(os.Stdout, "Response from `BackfillsAPI.PauseBackfillApiV1BackfillsBackfillIdPausePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**backfillId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPauseBackfillApiV1BackfillsBackfillIdPausePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **backfillActionRequest** | **BackfillActionRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**BackfillRecord**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PreviewBackfillApiV1BackfillsPreviewPost

> BackfillPreview PreviewBackfillApiV1BackfillsPreviewPost(ctx).BackfillSpec(backfillSpec).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Preview Backfill

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
	backfillSpec := *openapiclient.NewBackfillSpec("FlowId_example", int32(123), "Namespace_example", *openapiclient.NewBackfillSelection()) // BackfillSpec |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BackfillsAPI.PreviewBackfillApiV1BackfillsPreviewPost(context.Background()).BackfillSpec(backfillSpec).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BackfillsAPI.PreviewBackfillApiV1BackfillsPreviewPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PreviewBackfillApiV1BackfillsPreviewPost`: BackfillPreview
	fmt.Fprintf(os.Stdout, "Response from `BackfillsAPI.PreviewBackfillApiV1BackfillsPreviewPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPreviewBackfillApiV1BackfillsPreviewPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **backfillSpec** | **BackfillSpec** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**BackfillPreview**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ResumeBackfillApiV1BackfillsBackfillIdResumePost

> BackfillRecord ResumeBackfillApiV1BackfillsBackfillIdResumePost(ctx, backfillId).BackfillActionRequest(backfillActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Resume Backfill

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
	backfillId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	backfillActionRequest := *openapiclient.NewBackfillActionRequest("Reason_example") // BackfillActionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BackfillsAPI.ResumeBackfillApiV1BackfillsBackfillIdResumePost(context.Background(), backfillId).BackfillActionRequest(backfillActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BackfillsAPI.ResumeBackfillApiV1BackfillsBackfillIdResumePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ResumeBackfillApiV1BackfillsBackfillIdResumePost`: BackfillRecord
	fmt.Fprintf(os.Stdout, "Response from `BackfillsAPI.ResumeBackfillApiV1BackfillsBackfillIdResumePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**backfillId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiResumeBackfillApiV1BackfillsBackfillIdResumePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **backfillActionRequest** | **BackfillActionRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**BackfillRecord**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
