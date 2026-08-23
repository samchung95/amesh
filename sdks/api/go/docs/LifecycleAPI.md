# \LifecycleAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPost**](LifecycleAPI.md#CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPost) | **Post** /api/v1/lifecycle/legal-holds | Create Lifecycle Legal Hold
[**CreateLifecyclePolicyApiV1LifecyclePoliciesPost**](LifecycleAPI.md#CreateLifecyclePolicyApiV1LifecyclePoliciesPost) | **Post** /api/v1/lifecycle/policies | Create Lifecycle Policy
[**ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePost**](LifecycleAPI.md#ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePost) | **Post** /api/v1/lifecycle/jobs/{job_id}/execute | Execute Lifecycle Job
[**GetLifecycleJobApiV1LifecycleJobsJobIdGet**](LifecycleAPI.md#GetLifecycleJobApiV1LifecycleJobsJobIdGet) | **Get** /api/v1/lifecycle/jobs/{job_id} | Get Lifecycle Job
[**ListLifecycleJobsApiV1LifecycleJobsGet**](LifecycleAPI.md#ListLifecycleJobsApiV1LifecycleJobsGet) | **Get** /api/v1/lifecycle/jobs | List Lifecycle Jobs
[**ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet**](LifecycleAPI.md#ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet) | **Get** /api/v1/lifecycle/legal-holds | List Lifecycle Legal Holds
[**ListLifecyclePoliciesApiV1LifecyclePoliciesGet**](LifecycleAPI.md#ListLifecyclePoliciesApiV1LifecyclePoliciesGet) | **Get** /api/v1/lifecycle/policies | List Lifecycle Policies
[**PreviewLifecyclePurgeApiV1LifecyclePreviewsPost**](LifecycleAPI.md#PreviewLifecyclePurgeApiV1LifecyclePreviewsPost) | **Post** /api/v1/lifecycle/previews | Preview Lifecycle Purge
[**ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost**](LifecycleAPI.md#ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost) | **Post** /api/v1/lifecycle/legal-holds/{hold_id}/release | Release Lifecycle Legal Hold
[**ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePost**](LifecycleAPI.md#ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePost) | **Post** /api/v1/lifecycle/jobs/{job_id}/resume | Resume Lifecycle Job
[**UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut**](LifecycleAPI.md#UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut) | **Put** /api/v1/lifecycle/policies/{policy_id} | Update Lifecycle Policy



## CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPost

> LifecycleLegalHold CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPost(ctx).LifecycleLegalHoldDraft(lifecycleLegalHoldDraft).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Lifecycle Legal Hold

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
	lifecycleLegalHoldDraft := *openapiclient.NewLifecycleLegalHoldDraft("Name_example", "Reason_example") // LifecycleLegalHoldDraft |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LifecycleAPI.CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPost(context.Background()).LifecycleLegalHoldDraft(lifecycleLegalHoldDraft).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPost`: LifecycleLegalHold
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.CreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateLifecycleLegalHoldApiV1LifecycleLegalHoldsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lifecycleLegalHoldDraft** | [**LifecycleLegalHoldDraft**](LifecycleLegalHoldDraft.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**LifecycleLegalHold**](LifecycleLegalHold.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateLifecyclePolicyApiV1LifecyclePoliciesPost

> LifecyclePolicy CreateLifecyclePolicyApiV1LifecyclePoliciesPost(ctx).LifecyclePolicyDraft(lifecyclePolicyDraft).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Lifecycle Policy

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
	lifecyclePolicyDraft := *openapiclient.NewLifecyclePolicyDraft("Reason_example", openapiclient.LifecycleResourceType("EXECUTION"), int32(123), openapiclient.LifecycleScope("INSTANCE")) // LifecyclePolicyDraft |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LifecycleAPI.CreateLifecyclePolicyApiV1LifecyclePoliciesPost(context.Background()).LifecyclePolicyDraft(lifecyclePolicyDraft).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.CreateLifecyclePolicyApiV1LifecyclePoliciesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateLifecyclePolicyApiV1LifecyclePoliciesPost`: LifecyclePolicy
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.CreateLifecyclePolicyApiV1LifecyclePoliciesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateLifecyclePolicyApiV1LifecyclePoliciesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lifecyclePolicyDraft** | [**LifecyclePolicyDraft**](LifecyclePolicyDraft.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**LifecyclePolicy**](LifecyclePolicy.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePost

> LifecycleJob ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePost(ctx, jobId).LifecycleExecuteRequest(lifecycleExecuteRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Execute Lifecycle Job

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
	jobId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	lifecycleExecuteRequest := *openapiclient.NewLifecycleExecuteRequest("Confirmation_example") // LifecycleExecuteRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LifecycleAPI.ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePost(context.Background(), jobId).LifecycleExecuteRequest(lifecycleExecuteRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePost`: LifecycleJob
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.ExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**jobId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiExecuteLifecycleJobApiV1LifecycleJobsJobIdExecutePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **lifecycleExecuteRequest** | [**LifecycleExecuteRequest**](LifecycleExecuteRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**LifecycleJob**](LifecycleJob.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetLifecycleJobApiV1LifecycleJobsJobIdGet

> LifecycleJob GetLifecycleJobApiV1LifecycleJobsJobIdGet(ctx, jobId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Lifecycle Job

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
	jobId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LifecycleAPI.GetLifecycleJobApiV1LifecycleJobsJobIdGet(context.Background(), jobId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.GetLifecycleJobApiV1LifecycleJobsJobIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetLifecycleJobApiV1LifecycleJobsJobIdGet`: LifecycleJob
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.GetLifecycleJobApiV1LifecycleJobsJobIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**jobId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetLifecycleJobApiV1LifecycleJobsJobIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**LifecycleJob**](LifecycleJob.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListLifecycleJobsApiV1LifecycleJobsGet

> []LifecycleJob ListLifecycleJobsApiV1LifecycleJobsGet(ctx).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Lifecycle Jobs

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
	limit := int32(56) // int32 |  (optional) (default to 50)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LifecycleAPI.ListLifecycleJobsApiV1LifecycleJobsGet(context.Background()).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.ListLifecycleJobsApiV1LifecycleJobsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListLifecycleJobsApiV1LifecycleJobsGet`: []LifecycleJob
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.ListLifecycleJobsApiV1LifecycleJobsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListLifecycleJobsApiV1LifecycleJobsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 50]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]LifecycleJob**](LifecycleJob.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet

> []LifecycleLegalHold ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Lifecycle Legal Holds

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
	resp, r, err := apiClient.LifecycleAPI.ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet`: []LifecycleLegalHold
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.ListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListLifecycleLegalHoldsApiV1LifecycleLegalHoldsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]LifecycleLegalHold**](LifecycleLegalHold.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListLifecyclePoliciesApiV1LifecyclePoliciesGet

> []LifecyclePolicy ListLifecyclePoliciesApiV1LifecyclePoliciesGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Lifecycle Policies

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
	resp, r, err := apiClient.LifecycleAPI.ListLifecyclePoliciesApiV1LifecyclePoliciesGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.ListLifecyclePoliciesApiV1LifecyclePoliciesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListLifecyclePoliciesApiV1LifecyclePoliciesGet`: []LifecyclePolicy
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.ListLifecyclePoliciesApiV1LifecyclePoliciesGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListLifecyclePoliciesApiV1LifecyclePoliciesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]LifecyclePolicy**](LifecyclePolicy.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PreviewLifecyclePurgeApiV1LifecyclePreviewsPost

> LifecycleJob PreviewLifecyclePurgeApiV1LifecyclePreviewsPost(ctx).LifecyclePreviewRequest(lifecyclePreviewRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Preview Lifecycle Purge

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
	lifecyclePreviewRequest := *openapiclient.NewLifecyclePreviewRequest("PolicyId_example", "Reason_example") // LifecyclePreviewRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LifecycleAPI.PreviewLifecyclePurgeApiV1LifecyclePreviewsPost(context.Background()).LifecyclePreviewRequest(lifecyclePreviewRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.PreviewLifecyclePurgeApiV1LifecyclePreviewsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PreviewLifecyclePurgeApiV1LifecyclePreviewsPost`: LifecycleJob
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.PreviewLifecyclePurgeApiV1LifecyclePreviewsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPreviewLifecyclePurgeApiV1LifecyclePreviewsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lifecyclePreviewRequest** | [**LifecyclePreviewRequest**](LifecyclePreviewRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**LifecycleJob**](LifecycleJob.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost

> LifecycleLegalHold ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost(ctx, holdId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Release Lifecycle Legal Hold

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
	holdId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LifecycleAPI.ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost(context.Background(), holdId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost`: LifecycleLegalHold
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.ReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**holdId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiReleaseLifecycleLegalHoldApiV1LifecycleLegalHoldsHoldIdReleasePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**LifecycleLegalHold**](LifecycleLegalHold.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePost

> LifecycleJob ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePost(ctx, jobId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Resume Lifecycle Job

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
	jobId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LifecycleAPI.ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePost(context.Background(), jobId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePost`: LifecycleJob
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.ResumeLifecycleJobApiV1LifecycleJobsJobIdResumePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**jobId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiResumeLifecycleJobApiV1LifecycleJobsJobIdResumePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**LifecycleJob**](LifecycleJob.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut

> LifecyclePolicy UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut(ctx, policyId).LifecyclePolicyDraft(lifecyclePolicyDraft).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Update Lifecycle Policy

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
	policyId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	lifecyclePolicyDraft := *openapiclient.NewLifecyclePolicyDraft("Reason_example", openapiclient.LifecycleResourceType("EXECUTION"), int32(123), openapiclient.LifecycleScope("INSTANCE")) // LifecyclePolicyDraft |
	expectedVersion := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.LifecycleAPI.UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut(context.Background(), policyId).LifecyclePolicyDraft(lifecyclePolicyDraft).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `LifecycleAPI.UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut`: LifecyclePolicy
	fmt.Fprintf(os.Stdout, "Response from `LifecycleAPI.UpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**policyId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateLifecyclePolicyApiV1LifecyclePoliciesPolicyIdPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **lifecyclePolicyDraft** | [**LifecyclePolicyDraft**](LifecyclePolicyDraft.md) |  |
 **expectedVersion** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**LifecyclePolicy**](LifecyclePolicy.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
