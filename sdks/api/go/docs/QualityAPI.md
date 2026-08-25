# \QualityAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet**](QualityAPI.md#GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet) | **Get** /api/v1/namespaces/{namespace}/differentials/{idempotency_key} | Get Differential
[**RunDifferentialApiV1NamespacesNamespaceDifferentialsPost**](QualityAPI.md#RunDifferentialApiV1NamespacesNamespaceDifferentialsPost) | **Post** /api/v1/namespaces/{namespace}/differentials | Run Differential



## GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet

> ComparisonReport GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet(ctx, namespace, idempotencyKey).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Get Differential

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
	namespace := "namespace_example" // string |
	idempotencyKey := "idempotencyKey_example" // string |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.QualityAPI.GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet(context.Background(), namespace, idempotencyKey).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `QualityAPI.GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet`: ComparisonReport
	fmt.Fprintf(os.Stdout, "Response from `QualityAPI.GetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**idempotencyKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetDifferentialApiV1NamespacesNamespaceDifferentialsIdempotencyKeyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**ComparisonReport**](ComparisonReport.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RunDifferentialApiV1NamespacesNamespaceDifferentialsPost

> ComparisonReport RunDifferentialApiV1NamespacesNamespaceDifferentialsPost(ctx, namespace).DifferentialSpec(differentialSpec).IdempotencyKey(idempotencyKey).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Run Differential

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
	namespace := "namespace_example" // string |
	differentialSpec := *openapiclient.NewDifferentialSpec("IdempotencyKey_example", *openapiclient.NewConfigurationPin("Digest_example", "Key_example", int32(123)), "Namespace_example", *openapiclient.NewConfigurationPin("Digest_example", "Key_example", int32(123)), "TenantId_example") // DifferentialSpec |
	idempotencyKey := "idempotencyKey_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.QualityAPI.RunDifferentialApiV1NamespacesNamespaceDifferentialsPost(context.Background(), namespace).DifferentialSpec(differentialSpec).IdempotencyKey(idempotencyKey).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `QualityAPI.RunDifferentialApiV1NamespacesNamespaceDifferentialsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RunDifferentialApiV1NamespacesNamespaceDifferentialsPost`: ComparisonReport
	fmt.Fprintf(os.Stdout, "Response from `QualityAPI.RunDifferentialApiV1NamespacesNamespaceDifferentialsPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRunDifferentialApiV1NamespacesNamespaceDifferentialsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **differentialSpec** | [**DifferentialSpec**](DifferentialSpec.md) |  |
 **idempotencyKey** | **string** |  |
 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**ComparisonReport**](ComparisonReport.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
