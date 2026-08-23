# \SearchAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ControlSearchProjectionApiV1SearchControlPost**](SearchAPI.md#ControlSearchProjectionApiV1SearchControlPost) | **Post** /api/v1/search/control | Control Search Projection
[**GetSearchStatusApiV1SearchStatusGet**](SearchAPI.md#GetSearchStatusApiV1SearchStatusGet) | **Get** /api/v1/search/status | Get Search Status
[**RebuildSearchProjectionApiV1SearchRebuildPost**](SearchAPI.md#RebuildSearchProjectionApiV1SearchRebuildPost) | **Post** /api/v1/search/rebuild | Rebuild Search Projection
[**SearchResourcesApiV1SearchPost**](SearchAPI.md#SearchResourcesApiV1SearchPost) | **Post** /api/v1/search | Search Resources
[**VerifySearchProjectionApiV1SearchVerifyGet**](SearchAPI.md#VerifySearchProjectionApiV1SearchVerifyGet) | **Get** /api/v1/search/verify | Verify Search Projection



## ControlSearchProjectionApiV1SearchControlPost

> SearchProjectionStatus ControlSearchProjectionApiV1SearchControlPost(ctx).SearchProjectionControlRequest(searchProjectionControlRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Control Search Projection

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
	searchProjectionControlRequest := *openapiclient.NewSearchProjectionControlRequest(false, "Reason_example") // SearchProjectionControlRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.SearchAPI.ControlSearchProjectionApiV1SearchControlPost(context.Background()).SearchProjectionControlRequest(searchProjectionControlRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SearchAPI.ControlSearchProjectionApiV1SearchControlPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ControlSearchProjectionApiV1SearchControlPost`: SearchProjectionStatus
	fmt.Fprintf(os.Stdout, "Response from `SearchAPI.ControlSearchProjectionApiV1SearchControlPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiControlSearchProjectionApiV1SearchControlPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **searchProjectionControlRequest** | [**SearchProjectionControlRequest**](SearchProjectionControlRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**SearchProjectionStatus**](SearchProjectionStatus.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetSearchStatusApiV1SearchStatusGet

> SearchProjectionStatus GetSearchStatusApiV1SearchStatusGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Search Status

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
	resp, r, err := apiClient.SearchAPI.GetSearchStatusApiV1SearchStatusGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SearchAPI.GetSearchStatusApiV1SearchStatusGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetSearchStatusApiV1SearchStatusGet`: SearchProjectionStatus
	fmt.Fprintf(os.Stdout, "Response from `SearchAPI.GetSearchStatusApiV1SearchStatusGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetSearchStatusApiV1SearchStatusGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**SearchProjectionStatus**](SearchProjectionStatus.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RebuildSearchProjectionApiV1SearchRebuildPost

> SearchProjectionStatus RebuildSearchProjectionApiV1SearchRebuildPost(ctx).SearchRebuildRequest(searchRebuildRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Rebuild Search Projection

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
	searchRebuildRequest := *openapiclient.NewSearchRebuildRequest("Reason_example") // SearchRebuildRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.SearchAPI.RebuildSearchProjectionApiV1SearchRebuildPost(context.Background()).SearchRebuildRequest(searchRebuildRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SearchAPI.RebuildSearchProjectionApiV1SearchRebuildPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RebuildSearchProjectionApiV1SearchRebuildPost`: SearchProjectionStatus
	fmt.Fprintf(os.Stdout, "Response from `SearchAPI.RebuildSearchProjectionApiV1SearchRebuildPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRebuildSearchProjectionApiV1SearchRebuildPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **searchRebuildRequest** | [**SearchRebuildRequest**](SearchRebuildRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**SearchProjectionStatus**](SearchProjectionStatus.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SearchResourcesApiV1SearchPost

> SearchResponse SearchResourcesApiV1SearchPost(ctx).SearchRequest(searchRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Search Resources

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
	searchRequest := *openapiclient.NewSearchRequest() // SearchRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.SearchAPI.SearchResourcesApiV1SearchPost(context.Background()).SearchRequest(searchRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SearchAPI.SearchResourcesApiV1SearchPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SearchResourcesApiV1SearchPost`: SearchResponse
	fmt.Fprintf(os.Stdout, "Response from `SearchAPI.SearchResourcesApiV1SearchPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSearchResourcesApiV1SearchPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **searchRequest** | [**SearchRequest**](SearchRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**SearchResponse**](SearchResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## VerifySearchProjectionApiV1SearchVerifyGet

> SearchProjectionVerification VerifySearchProjectionApiV1SearchVerifyGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Verify Search Projection

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
	resp, r, err := apiClient.SearchAPI.VerifySearchProjectionApiV1SearchVerifyGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SearchAPI.VerifySearchProjectionApiV1SearchVerifyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `VerifySearchProjectionApiV1SearchVerifyGet`: SearchProjectionVerification
	fmt.Fprintf(os.Stdout, "Response from `SearchAPI.VerifySearchProjectionApiV1SearchVerifyGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiVerifySearchProjectionApiV1SearchVerifyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**SearchProjectionVerification**](SearchProjectionVerification.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
