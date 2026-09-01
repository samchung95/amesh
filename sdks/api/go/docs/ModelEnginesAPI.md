# \ModelEnginesAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost**](ModelEnginesAPI.md#AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost) | **Post** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/login | Account Login Start
[**AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost**](ModelEnginesAPI.md#AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost) | **Post** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/logout | Account Logout
[**AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet**](ModelEnginesAPI.md#AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet) | **Get** /api/v1/namespaces/{namespace}/model-engines/{adapter}/{engine_ref}/status | Account Status
[**CatalogApiV1NamespacesNamespaceModelEnginesCatalogGet**](ModelEnginesAPI.md#CatalogApiV1NamespacesNamespaceModelEnginesCatalogGet) | **Get** /api/v1/namespaces/{namespace}/model-engines/catalog | Catalog



## AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost

> ModelEngineLoginStartResponse AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost(ctx, namespace, adapter, engineRef).ModelEngineLoginRequest(modelEngineLoginRequest).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Account Login Start

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
	adapter := "adapter_example" // string |
	engineRef := "engineRef_example" // string |
	modelEngineLoginRequest := *openapiclient.NewModelEngineLoginRequest() // ModelEngineLoginRequest |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ModelEnginesAPI.AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost(context.Background(), namespace, adapter, engineRef).ModelEngineLoginRequest(modelEngineLoginRequest).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ModelEnginesAPI.AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost`: ModelEngineLoginStartResponse
	fmt.Fprintf(os.Stdout, "Response from `ModelEnginesAPI.AccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**adapter** | **string** |  |
**engineRef** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiAccountLoginStartApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLoginPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **modelEngineLoginRequest** | **ModelEngineLoginRequest** |  |
 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**ModelEngineLoginStartResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost

> ModelEngineLogoutResponse AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost(ctx, namespace, adapter, engineRef).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Account Logout

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
	adapter := "adapter_example" // string |
	engineRef := "engineRef_example" // string |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ModelEnginesAPI.AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost(context.Background(), namespace, adapter, engineRef).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ModelEnginesAPI.AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost`: ModelEngineLogoutResponse
	fmt.Fprintf(os.Stdout, "Response from `ModelEnginesAPI.AccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**adapter** | **string** |  |
**engineRef** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiAccountLogoutApiV1NamespacesNamespaceModelEnginesAdapterEngineRefLogoutPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**ModelEngineLogoutResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet

> ModelEngineAccountStatusResponse AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet(ctx, namespace, adapter, engineRef).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Account Status

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
	adapter := "adapter_example" // string |
	engineRef := "engineRef_example" // string |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ModelEnginesAPI.AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet(context.Background(), namespace, adapter, engineRef).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ModelEnginesAPI.AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet`: ModelEngineAccountStatusResponse
	fmt.Fprintf(os.Stdout, "Response from `ModelEnginesAPI.AccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**adapter** | **string** |  |
**engineRef** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiAccountStatusApiV1NamespacesNamespaceModelEnginesAdapterEngineRefStatusGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**ModelEngineAccountStatusResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CatalogApiV1NamespacesNamespaceModelEnginesCatalogGet

> ModelEngineCatalog CatalogApiV1NamespacesNamespaceModelEnginesCatalogGet(ctx, namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Catalog

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ModelEnginesAPI.CatalogApiV1NamespacesNamespaceModelEnginesCatalogGet(context.Background(), namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ModelEnginesAPI.CatalogApiV1NamespacesNamespaceModelEnginesCatalogGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CatalogApiV1NamespacesNamespaceModelEnginesCatalogGet`: ModelEngineCatalog
	fmt.Fprintf(os.Stdout, "Response from `ModelEnginesAPI.CatalogApiV1NamespacesNamespaceModelEnginesCatalogGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiCatalogApiV1NamespacesNamespaceModelEnginesCatalogGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ModelEngineCatalog**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
