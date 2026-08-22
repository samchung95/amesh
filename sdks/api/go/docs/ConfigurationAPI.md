# \ConfigurationAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet**](ConfigurationAPI.md#EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet) | **Get** /api/v1/feature-flags/{key}/evaluate | Evaluate Feature Flag
[**GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet**](ConfigurationAPI.md#GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet) | **Get** /api/v1/configuration/diagnostics | Get Configuration Diagnostics
[**GetEffectiveConfigurationApiV1ConfigurationGet**](ConfigurationAPI.md#GetEffectiveConfigurationApiV1ConfigurationGet) | **Get** /api/v1/configuration | Get Effective Configuration
[**ListFeatureFlagsApiV1FeatureFlagsGet**](ConfigurationAPI.md#ListFeatureFlagsApiV1FeatureFlagsGet) | **Get** /api/v1/feature-flags | List Feature Flags
[**PutFeatureFlagApiV1FeatureFlagsKeyPut**](ConfigurationAPI.md#PutFeatureFlagApiV1FeatureFlagsKeyPut) | **Put** /api/v1/feature-flags/{key} | Put Feature Flag
[**ReloadConfigurationApiV1ConfigurationReloadPost**](ConfigurationAPI.md#ReloadConfigurationApiV1ConfigurationReloadPost) | **Post** /api/v1/configuration/reload | Reload Configuration



## EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet

> FeatureFlagDecision EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet(ctx, key).Namespace(namespace).Default_(default_).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Evaluate Feature Flag

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
	key := "key_example" // string |
	namespace := "namespace_example" // string |  (optional)
	default_ := true // bool |  (optional) (default to false)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ConfigurationAPI.EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet(context.Background(), key).Namespace(namespace).Default_(default_).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ConfigurationAPI.EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet`: FeatureFlagDecision
	fmt.Fprintf(os.Stdout, "Response from `ConfigurationAPI.EvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiEvaluateFeatureFlagApiV1FeatureFlagsKeyEvaluateGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **namespace** | **string** |  |
 **default_** | **bool** |  | [default to false]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FeatureFlagDecision**](FeatureFlagDecision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet

> ConfigurationDiagnosticBundle GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet(ctx).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Configuration Diagnostics

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
	namespace := "namespace_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ConfigurationAPI.GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet(context.Background()).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ConfigurationAPI.GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet`: ConfigurationDiagnosticBundle
	fmt.Fprintf(os.Stdout, "Response from `ConfigurationAPI.GetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetConfigurationDiagnosticsApiV1ConfigurationDiagnosticsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ConfigurationDiagnosticBundle**](ConfigurationDiagnosticBundle.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetEffectiveConfigurationApiV1ConfigurationGet

> ConfigurationSnapshot GetEffectiveConfigurationApiV1ConfigurationGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Get Effective Configuration

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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ConfigurationAPI.GetEffectiveConfigurationApiV1ConfigurationGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ConfigurationAPI.GetEffectiveConfigurationApiV1ConfigurationGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetEffectiveConfigurationApiV1ConfigurationGet`: ConfigurationSnapshot
	fmt.Fprintf(os.Stdout, "Response from `ConfigurationAPI.GetEffectiveConfigurationApiV1ConfigurationGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetEffectiveConfigurationApiV1ConfigurationGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**ConfigurationSnapshot**](ConfigurationSnapshot.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListFeatureFlagsApiV1FeatureFlagsGet

> []FeatureFlag ListFeatureFlagsApiV1FeatureFlagsGet(ctx).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Feature Flags

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
	namespace := "namespace_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ConfigurationAPI.ListFeatureFlagsApiV1FeatureFlagsGet(context.Background()).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ConfigurationAPI.ListFeatureFlagsApiV1FeatureFlagsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListFeatureFlagsApiV1FeatureFlagsGet`: []FeatureFlag
	fmt.Fprintf(os.Stdout, "Response from `ConfigurationAPI.ListFeatureFlagsApiV1FeatureFlagsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListFeatureFlagsApiV1FeatureFlagsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]FeatureFlag**](FeatureFlag.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PutFeatureFlagApiV1FeatureFlagsKeyPut

> FeatureFlag PutFeatureFlagApiV1FeatureFlagsKeyPut(ctx, key).FeatureFlagUpsertRequest(featureFlagUpsertRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Put Feature Flag

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
	key := "key_example" // string |
	featureFlagUpsertRequest := *openapiclient.NewFeatureFlagUpsertRequest(false, openapiclient.FeatureFlagScope("INSTANCE")) // FeatureFlagUpsertRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ConfigurationAPI.PutFeatureFlagApiV1FeatureFlagsKeyPut(context.Background(), key).FeatureFlagUpsertRequest(featureFlagUpsertRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ConfigurationAPI.PutFeatureFlagApiV1FeatureFlagsKeyPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PutFeatureFlagApiV1FeatureFlagsKeyPut`: FeatureFlag
	fmt.Fprintf(os.Stdout, "Response from `ConfigurationAPI.PutFeatureFlagApiV1FeatureFlagsKeyPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPutFeatureFlagApiV1FeatureFlagsKeyPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **featureFlagUpsertRequest** | [**FeatureFlagUpsertRequest**](FeatureFlagUpsertRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FeatureFlag**](FeatureFlag.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ReloadConfigurationApiV1ConfigurationReloadPost

> ConfigurationSnapshot ReloadConfigurationApiV1ConfigurationReloadPost(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Reload Configuration

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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ConfigurationAPI.ReloadConfigurationApiV1ConfigurationReloadPost(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ConfigurationAPI.ReloadConfigurationApiV1ConfigurationReloadPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReloadConfigurationApiV1ConfigurationReloadPost`: ConfigurationSnapshot
	fmt.Fprintf(os.Stdout, "Response from `ConfigurationAPI.ReloadConfigurationApiV1ConfigurationReloadPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiReloadConfigurationApiV1ConfigurationReloadPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**ConfigurationSnapshot**](ConfigurationSnapshot.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
