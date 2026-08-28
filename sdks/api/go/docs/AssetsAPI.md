# \AssetsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DeclareAssetLineageApiV1AssetsLineagePost**](AssetsAPI.md#DeclareAssetLineageApiV1AssetsLineagePost) | **Post** /api/v1/assets/lineage | Declare Asset Lineage
[**ExportAssetCatalogApiV1AssetsExportOpenlineageGet**](AssetsAPI.md#ExportAssetCatalogApiV1AssetsExportOpenlineageGet) | **Get** /api/v1/assets/export/openlineage | Export Asset Catalog
[**GetAssetCatalogEntryApiV1AssetsAssetIdGet**](AssetsAPI.md#GetAssetCatalogEntryApiV1AssetsAssetIdGet) | **Get** /api/v1/assets/{asset_id} | Get Asset Catalog Entry
[**ListAssetsApiV1AssetsGet**](AssetsAPI.md#ListAssetsApiV1AssetsGet) | **Get** /api/v1/assets | List Assets
[**RecordAssetObservationApiV1AssetsObservationsPost**](AssetsAPI.md#RecordAssetObservationApiV1AssetsObservationsPost) | **Post** /api/v1/assets/observations | Record Asset Observation
[**RegisterAssetApiV1AssetsPost**](AssetsAPI.md#RegisterAssetApiV1AssetsPost) | **Post** /api/v1/assets | Register Asset



## DeclareAssetLineageApiV1AssetsLineagePost

> AssetLineageEdge DeclareAssetLineageApiV1AssetsLineagePost(ctx).AssetLineageDeclaration(assetLineageDeclaration).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Declare Asset Lineage

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
	assetLineageDeclaration := *openapiclient.NewAssetLineageDeclaration("DownstreamAssetId_example", "UpstreamAssetId_example") // AssetLineageDeclaration |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AssetsAPI.DeclareAssetLineageApiV1AssetsLineagePost(context.Background()).AssetLineageDeclaration(assetLineageDeclaration).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AssetsAPI.DeclareAssetLineageApiV1AssetsLineagePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DeclareAssetLineageApiV1AssetsLineagePost`: AssetLineageEdge
	fmt.Fprintf(os.Stdout, "Response from `AssetsAPI.DeclareAssetLineageApiV1AssetsLineagePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiDeclareAssetLineageApiV1AssetsLineagePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **assetLineageDeclaration** | **AssetLineageDeclaration** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AssetLineageEdge**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExportAssetCatalogApiV1AssetsExportOpenlineageGet

> AssetCatalogExport ExportAssetCatalogApiV1AssetsExportOpenlineageGet(ctx).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Export Asset Catalog

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
	resp, r, err := apiClient.AssetsAPI.ExportAssetCatalogApiV1AssetsExportOpenlineageGet(context.Background()).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AssetsAPI.ExportAssetCatalogApiV1AssetsExportOpenlineageGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExportAssetCatalogApiV1AssetsExportOpenlineageGet`: AssetCatalogExport
	fmt.Fprintf(os.Stdout, "Response from `AssetsAPI.ExportAssetCatalogApiV1AssetsExportOpenlineageGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiExportAssetCatalogApiV1AssetsExportOpenlineageGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AssetCatalogExport**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAssetCatalogEntryApiV1AssetsAssetIdGet

> AssetCatalogEntry GetAssetCatalogEntryApiV1AssetsAssetIdGet(ctx, assetId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Asset Catalog Entry

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
	assetId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AssetsAPI.GetAssetCatalogEntryApiV1AssetsAssetIdGet(context.Background(), assetId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AssetsAPI.GetAssetCatalogEntryApiV1AssetsAssetIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAssetCatalogEntryApiV1AssetsAssetIdGet`: AssetCatalogEntry
	fmt.Fprintf(os.Stdout, "Response from `AssetsAPI.GetAssetCatalogEntryApiV1AssetsAssetIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**assetId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAssetCatalogEntryApiV1AssetsAssetIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AssetCatalogEntry**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAssetsApiV1AssetsGet

> []PersistedAsset ListAssetsApiV1AssetsGet(ctx).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Assets

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
	resp, r, err := apiClient.AssetsAPI.ListAssetsApiV1AssetsGet(context.Background()).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AssetsAPI.ListAssetsApiV1AssetsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAssetsApiV1AssetsGet`: []PersistedAsset
	fmt.Fprintf(os.Stdout, "Response from `AssetsAPI.ListAssetsApiV1AssetsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAssetsApiV1AssetsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]PersistedAsset**](PersistedAsset.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RecordAssetObservationApiV1AssetsObservationsPost

> AssetObservation RecordAssetObservationApiV1AssetsObservationsPost(ctx).AssetObservationCreate(assetObservationCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Record Asset Observation

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
	assetObservationCreate := *openapiclient.NewAssetObservationCreate(openapiclient.AssetAccessMode("READ"), *openapiclient.NewAssetMetadata("AssetId_example", "AssetType_example", "DisplayName_example", "ExternalKey_example", "Provider_example")) // AssetObservationCreate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AssetsAPI.RecordAssetObservationApiV1AssetsObservationsPost(context.Background()).AssetObservationCreate(assetObservationCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AssetsAPI.RecordAssetObservationApiV1AssetsObservationsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RecordAssetObservationApiV1AssetsObservationsPost`: AssetObservation
	fmt.Fprintf(os.Stdout, "Response from `AssetsAPI.RecordAssetObservationApiV1AssetsObservationsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRecordAssetObservationApiV1AssetsObservationsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **assetObservationCreate** | **AssetObservationCreate** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AssetObservation**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RegisterAssetApiV1AssetsPost

> PersistedAsset RegisterAssetApiV1AssetsPost(ctx).AssetMetadata(assetMetadata).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Register Asset

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
	assetMetadata := *openapiclient.NewAssetMetadata("AssetId_example", "AssetType_example", "DisplayName_example", "ExternalKey_example", "Provider_example") // AssetMetadata |
	expectedVersion := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AssetsAPI.RegisterAssetApiV1AssetsPost(context.Background()).AssetMetadata(assetMetadata).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AssetsAPI.RegisterAssetApiV1AssetsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RegisterAssetApiV1AssetsPost`: PersistedAsset
	fmt.Fprintf(os.Stdout, "Response from `AssetsAPI.RegisterAssetApiV1AssetsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRegisterAssetApiV1AssetsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **assetMetadata** | **AssetMetadata** |  |
 **expectedVersion** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**PersistedAsset**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
