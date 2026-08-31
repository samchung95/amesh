# \NamespaceResourcesAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete**](NamespaceResourcesAPI.md#DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete) | **Delete** /api/v1/namespaces/{namespace}/files/{path} | Delete Namespace File
[**DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete**](NamespaceResourcesAPI.md#DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete) | **Delete** /api/v1/namespaces/{namespace}/key-values/{key} | Delete Namespace Key Value
[**DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete**](NamespaceResourcesAPI.md#DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete) | **Delete** /api/v1/namespaces/{namespace}/secret-bindings/{key} | Delete Namespace Secret Binding
[**DownloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet**](NamespaceResourcesAPI.md#DownloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet) | **Get** /api/v1/namespaces/{namespace}/files/{path} | Download Namespace File
[**ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet**](NamespaceResourcesAPI.md#ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet) | **Get** /api/v1/namespaces/{namespace}/resource-bundle | Export Namespace Resource Bundle
[**GetNamespaceArtifactApiV1NamespacesNamespaceArtifactsPathGet**](NamespaceResourcesAPI.md#GetNamespaceArtifactApiV1NamespacesNamespaceArtifactsPathGet) | **Get** /api/v1/namespaces/{namespace}/artifacts/{path} | Get Namespace Artifact
[**GetNamespaceImageApiV1NamespacesNamespaceImagesPathGet**](NamespaceResourcesAPI.md#GetNamespaceImageApiV1NamespacesNamespaceImagesPathGet) | **Get** /api/v1/namespaces/{namespace}/images/{path} | Get Namespace Image
[**GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet**](NamespaceResourcesAPI.md#GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet) | **Get** /api/v1/namespaces/{namespace}/key-values/{key} | Get Namespace Key Value
[**ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost**](NamespaceResourcesAPI.md#ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost) | **Post** /api/v1/namespaces/{namespace}/resource-bundle | Import Namespace Resource Bundle
[**ListNamespaceArtifactsApiV1NamespacesNamespaceArtifactsGet**](NamespaceResourcesAPI.md#ListNamespaceArtifactsApiV1NamespacesNamespaceArtifactsGet) | **Get** /api/v1/namespaces/{namespace}/artifacts | List Namespace Artifacts
[**ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet**](NamespaceResourcesAPI.md#ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet) | **Get** /api/v1/namespaces/{namespace}/files/{path}/versions | List Namespace File Versions
[**ListNamespaceFilesApiV1NamespacesNamespaceFilesGet**](NamespaceResourcesAPI.md#ListNamespaceFilesApiV1NamespacesNamespaceFilesGet) | **Get** /api/v1/namespaces/{namespace}/files | List Namespace Files
[**ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet**](NamespaceResourcesAPI.md#ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet) | **Get** /api/v1/namespaces/{namespace}/key-values/changes | List Namespace Key Value Changes
[**ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet**](NamespaceResourcesAPI.md#ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet) | **Get** /api/v1/namespaces/{namespace}/key-values | List Namespace Key Values
[**ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet**](NamespaceResourcesAPI.md#ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet) | **Get** /api/v1/namespaces/{namespace}/secret-bindings | List Namespace Secret Bindings
[**MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost**](NamespaceResourcesAPI.md#MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost) | **Post** /api/v1/namespaces/{namespace}/files/{path}/move | Move Namespace File
[**PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut**](NamespaceResourcesAPI.md#PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut) | **Put** /api/v1/namespaces/{namespace}/key-values/{key} | Put Namespace Key Value
[**PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut**](NamespaceResourcesAPI.md#PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut) | **Put** /api/v1/namespaces/{namespace}/secret-bindings/{key} | Put Namespace Secret Binding
[**UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut**](NamespaceResourcesAPI.md#UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut) | **Put** /api/v1/namespaces/{namespace}/files/{path} | Upload Namespace File
[**UploadNamespaceImageApiV1NamespacesNamespaceImagesPathPut**](NamespaceResourcesAPI.md#UploadNamespaceImageApiV1NamespacesNamespaceImagesPathPut) | **Put** /api/v1/namespaces/{namespace}/images/{path} | Upload Namespace Image



## DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete

> map[string]int32 DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete(ctx, namespace, path).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Delete Namespace File

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
	path := "path_example" // string |
	expectedVersion := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete(context.Background(), namespace, path).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete`: map[string]int32
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.DeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**path** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteNamespaceFileApiV1NamespacesNamespaceFilesPathDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **expectedVersion** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**map[string]int32**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete

> map[string]*bool DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete(ctx, namespace, key).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Delete Namespace Key Value

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
	key := "key_example" // string |
	expectedVersion := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete(context.Background(), namespace, key).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete`: map[string]*bool
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.DeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **expectedVersion** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**map[string]*bool**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete

> map[string]*bool DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete(ctx, namespace, key).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Delete Namespace Secret Binding

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
	key := "key_example" // string |
	expectedVersion := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete(context.Background(), namespace, key).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete`: map[string]*bool
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.DeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **expectedVersion** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**map[string]*bool**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DownloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet

> DownloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet(ctx, namespace, path).Version(version).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Download Namespace File

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
	path := "path_example" // string |
	version := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.NamespaceResourcesAPI.DownloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet(context.Background(), namespace, path).Version(version).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.DownloadNamespaceFileApiV1NamespacesNamespaceFilesPathGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**path** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDownloadNamespaceFileApiV1NamespacesNamespaceFilesPathGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **version** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

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


## ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet

> NamespaceResourceBundle ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet(ctx, namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Export Namespace Resource Bundle

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
	resp, r, err := apiClient.NamespaceResourcesAPI.ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet(context.Background(), namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet`: NamespaceResourceBundle
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.ExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiExportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundleGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**NamespaceResourceBundle**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetNamespaceArtifactApiV1NamespacesNamespaceArtifactsPathGet

> ArtifactRef GetNamespaceArtifactApiV1NamespacesNamespaceArtifactsPathGet(ctx, namespace, path).Version(version).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Namespace Artifact

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
	path := "path_example" // string |
	version := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.GetNamespaceArtifactApiV1NamespacesNamespaceArtifactsPathGet(context.Background(), namespace, path).Version(version).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.GetNamespaceArtifactApiV1NamespacesNamespaceArtifactsPathGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetNamespaceArtifactApiV1NamespacesNamespaceArtifactsPathGet`: ArtifactRef
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.GetNamespaceArtifactApiV1NamespacesNamespaceArtifactsPathGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**path** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetNamespaceArtifactApiV1NamespacesNamespaceArtifactsPathGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **version** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ArtifactRef**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetNamespaceImageApiV1NamespacesNamespaceImagesPathGet

> ImageArtifactRef GetNamespaceImageApiV1NamespacesNamespaceImagesPathGet(ctx, namespace, path).Version(version).AltText(altText).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Namespace Image

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
	path := "path_example" // string |
	version := int32(56) // int32 |  (optional)
	altText := "altText_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.GetNamespaceImageApiV1NamespacesNamespaceImagesPathGet(context.Background(), namespace, path).Version(version).AltText(altText).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.GetNamespaceImageApiV1NamespacesNamespaceImagesPathGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetNamespaceImageApiV1NamespacesNamespaceImagesPathGet`: ImageArtifactRef
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.GetNamespaceImageApiV1NamespacesNamespaceImagesPathGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**path** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetNamespaceImageApiV1NamespacesNamespaceImagesPathGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **version** | **int32** |  |
 **altText** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ImageArtifactRef**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet

> KeyValueEntry GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet(ctx, namespace, key).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Namespace Key Value

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
	key := "key_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet(context.Background(), namespace, key).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet`: KeyValueEntry
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.GetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**KeyValueEntry**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost

> NamespaceResourceImportResult ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost(ctx, namespace).NamespaceResourceBundle(namespaceResourceBundle).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Import Namespace Resource Bundle

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
    "time"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	namespaceResourceBundle := *openapiclient.NewNamespaceResourceBundle("ChecksumSha256_example", time.Now(), "SourceNamespace_example") // NamespaceResourceBundle |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost(context.Background(), namespace).NamespaceResourceBundle(namespaceResourceBundle).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost`: NamespaceResourceImportResult
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.ImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiImportNamespaceResourceBundleApiV1NamespacesNamespaceResourceBundlePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **namespaceResourceBundle** | **NamespaceResourceBundle** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**NamespaceResourceImportResult**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListNamespaceArtifactsApiV1NamespacesNamespaceArtifactsGet

> []ArtifactRef ListNamespaceArtifactsApiV1NamespacesNamespaceArtifactsGet(ctx, namespace).Inherited(inherited).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Namespace Artifacts

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
	inherited := true // bool |  (optional) (default to true)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.ListNamespaceArtifactsApiV1NamespacesNamespaceArtifactsGet(context.Background(), namespace).Inherited(inherited).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.ListNamespaceArtifactsApiV1NamespacesNamespaceArtifactsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListNamespaceArtifactsApiV1NamespacesNamespaceArtifactsGet`: []ArtifactRef
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.ListNamespaceArtifactsApiV1NamespacesNamespaceArtifactsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListNamespaceArtifactsApiV1NamespacesNamespaceArtifactsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **inherited** | **bool** |  | [default to true]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]ArtifactRef**](ArtifactRef.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet

> []NamespaceFileVersion ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet(ctx, namespace, path).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Namespace File Versions

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
	path := "path_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet(context.Background(), namespace, path).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet`: []NamespaceFileVersion
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.ListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**path** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListNamespaceFileVersionsApiV1NamespacesNamespaceFilesPathVersionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]NamespaceFileVersion**](NamespaceFileVersion.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListNamespaceFilesApiV1NamespacesNamespaceFilesGet

> []NamespaceFile ListNamespaceFilesApiV1NamespacesNamespaceFilesGet(ctx, namespace).Inherited(inherited).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Namespace Files

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
	inherited := true // bool |  (optional) (default to true)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.ListNamespaceFilesApiV1NamespacesNamespaceFilesGet(context.Background(), namespace).Inherited(inherited).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.ListNamespaceFilesApiV1NamespacesNamespaceFilesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListNamespaceFilesApiV1NamespacesNamespaceFilesGet`: []NamespaceFile
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.ListNamespaceFilesApiV1NamespacesNamespaceFilesGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListNamespaceFilesApiV1NamespacesNamespaceFilesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **inherited** | **bool** |  | [default to true]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]NamespaceFile**](NamespaceFile.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet

> []KeyValueChange ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet(ctx, namespace).After(after).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Namespace Key Value Changes

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
	after := int32(56) // int32 |  (optional) (default to 0)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet(context.Background(), namespace).After(after).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet`: []KeyValueChange
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.ListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListNamespaceKeyValueChangesApiV1NamespacesNamespaceKeyValuesChangesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **after** | **int32** |  | [default to 0]
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]KeyValueChange**](KeyValueChange.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet

> []KeyValueEntry ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet(ctx, namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Namespace Key Values

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
	resp, r, err := apiClient.NamespaceResourcesAPI.ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet(context.Background(), namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet`: []KeyValueEntry
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.ListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListNamespaceKeyValuesApiV1NamespacesNamespaceKeyValuesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]KeyValueEntry**](KeyValueEntry.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet

> []SecretBinding ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet(ctx, namespace).Inherited(inherited).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Namespace Secret Bindings

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
	inherited := true // bool |  (optional) (default to true)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet(context.Background(), namespace).Inherited(inherited).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet`: []SecretBinding
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.ListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListNamespaceSecretBindingsApiV1NamespacesNamespaceSecretBindingsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **inherited** | **bool** |  | [default to true]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]SecretBinding**](SecretBinding.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost

> NamespaceFile MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost(ctx, namespace, path).NamespaceFileMoveRequest(namespaceFileMoveRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Move Namespace File

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
	path := "path_example" // string |
	namespaceFileMoveRequest := *openapiclient.NewNamespaceFileMoveRequest("DestinationPath_example") // NamespaceFileMoveRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost(context.Background(), namespace, path).NamespaceFileMoveRequest(namespaceFileMoveRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost`: NamespaceFile
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.MoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**path** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiMoveNamespaceFileApiV1NamespacesNamespaceFilesPathMovePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **namespaceFileMoveRequest** | **NamespaceFileMoveRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**NamespaceFile**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut

> KeyValueEntry PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut(ctx, namespace, key).KeyValueWrite(keyValueWrite).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Put Namespace Key Value

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
	key := "key_example" // string |
	keyValueWrite := *openapiclient.NewKeyValueWrite(openapiclient.KeyValueType("STRING"), interface{}(123)) // KeyValueWrite |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut(context.Background(), namespace, key).KeyValueWrite(keyValueWrite).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut`: KeyValueEntry
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.PutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPutNamespaceKeyValueApiV1NamespacesNamespaceKeyValuesKeyPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **keyValueWrite** | **KeyValueWrite** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**KeyValueEntry**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut

> SecretBinding PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut(ctx, namespace, key).SecretBindingWrite(secretBindingWrite).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Put Namespace Secret Binding

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
	key := "key_example" // string |
	secretBindingWrite := *openapiclient.NewSecretBindingWrite("ProviderReference_example") // SecretBindingWrite |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut(context.Background(), namespace, key).SecretBindingWrite(secretBindingWrite).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut`: SecretBinding
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.PutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**key** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPutNamespaceSecretBindingApiV1NamespacesNamespaceSecretBindingsKeyPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **secretBindingWrite** | **SecretBindingWrite** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**SecretBinding**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut

> NamespaceFile UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut(ctx, namespace, path).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Upload Namespace File

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
	path := "path_example" // string |
	expectedVersion := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut(context.Background(), namespace, path).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut`: NamespaceFile
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.UploadNamespaceFileApiV1NamespacesNamespaceFilesPathPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**path** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUploadNamespaceFileApiV1NamespacesNamespaceFilesPathPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **expectedVersion** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**NamespaceFile**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UploadNamespaceImageApiV1NamespacesNamespaceImagesPathPut

> ImageArtifactRef UploadNamespaceImageApiV1NamespacesNamespaceImagesPathPut(ctx, namespace, path).ExpectedVersion(expectedVersion).AltText(altText).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Upload Namespace Image

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
	path := "path_example" // string |
	expectedVersion := int32(56) // int32 |  (optional)
	altText := "altText_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.NamespaceResourcesAPI.UploadNamespaceImageApiV1NamespacesNamespaceImagesPathPut(context.Background(), namespace, path).ExpectedVersion(expectedVersion).AltText(altText).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `NamespaceResourcesAPI.UploadNamespaceImageApiV1NamespacesNamespaceImagesPathPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UploadNamespaceImageApiV1NamespacesNamespaceImagesPathPut`: ImageArtifactRef
	fmt.Fprintf(os.Stdout, "Response from `NamespaceResourcesAPI.UploadNamespaceImageApiV1NamespacesNamespaceImagesPathPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**path** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUploadNamespaceImageApiV1NamespacesNamespaceImagesPathPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **expectedVersion** | **int32** |  |
 **altText** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ImageArtifactRef**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
